#!/usr/bin/env python3
"""Drive an isolated Zed GUI with real X11 input; record screenshots and LSP evidence.

The session must already have this dev extension installed and use lsp-trace.py.
Only run against a disposable project. Never point this at a user's active desktop.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

from PIL import ImageGrab


class Gui:
    def __init__(self, args):
        self.args = args
        self.env = {**os.environ, "DISPLAY": args.display}
        self.out = args.output.resolve()
        self.out.mkdir(parents=True, exist_ok=True)
        self.project = args.project.resolve()
        if not (self.project / ".zed-gui-test-project").is_file():
            raise RuntimeError("Refusing to edit a project without the disposable-session marker")
        self.results = []
        report_path = self.out / "report.json"
        if args.only and report_path.exists():
            previous = json.loads(report_path.read_text())
            assert previous["project"] == str(self.project) and previous["display"] == args.display
            self.results = [result for result in previous["results"] if result["name"] not in args.only]
        self.probe = self.project / "game/gui_checks.rpy"
        if self.probe.exists() and not args.reuse_probe:
            raise RuntimeError(f"Refusing to overwrite existing probe: {self.probe}")
        if not self.probe.exists():
            self.probe.write_text("label gui_probe:\n    pass\n")

    def xdo(self, *args):
        return subprocess.check_output([str(self.args.xdotool), *map(str, args)], env=self.env, text=True)

    def focus(self):
        windows = self.xdo("search", "--onlyvisible", "--class", "dev.zed.Zed").splitlines()
        assert len(windows) == 1, f"Expected one isolated Zed window, got {windows}"
        self.xdo("windowactivate", "--sync", windows[0])
        self.xdo("windowfocus", "--sync", windows[0])

    def key(self, chord):
        self.xdo("key", "--clearmodifiers", chord)
        time.sleep(.2)

    def type(self, text):
        self.xdo("type", "--clearmodifiers", "--delay", "25", text)
        time.sleep(.2)

    def paste(self, text):
        process = subprocess.Popen([str(self.args.xclip), "-selection", "clipboard", "-quiet"],
                                   stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, env=self.env)
        assert process.stdin is not None
        try:
            process.stdin.write(text.encode())
            process.stdin.close()
            time.sleep(.15)
            self.key("ctrl+v")
            time.sleep(.3)
        finally:
            process.terminate()
            process.wait(timeout=3)

    def snapshot(self, name):
        time.sleep(.5)
        path = self.out / f"{name}.png"
        image = ImageGrab.grab(xdisplay=self.args.display)
        image.save(path)
        text = subprocess.check_output(["tesseract", str(path), "stdout"], stderr=subprocess.DEVNULL, text=True)
        (self.out / f"{name}.txt").write_text(text)
        return text, image

    def palette(self, action):
        self.focus()
        self.key("ctrl+shift+p")
        self.type(action)
        self.key("Return")
        time.sleep(.3)

    def open_file(self, name):
        self.focus()
        self.key("Escape")
        self.key("ctrl+p")
        self.type("game/" + name)
        time.sleep(.6)
        self.key("Return")
        time.sleep(.4)

    def goto(self, row, column=1):
        self.key("Escape")
        self.key("ctrl+g")
        self.type(f"{row}:{column}")
        self.key("Return")

    def replace(self, text):
        self.key("Escape")
        self.key("ctrl+a")
        self.paste(text)

    def save(self):
        self.key("Escape")
        self.key("ctrl+s")
        time.sleep(.3)
        return self.probe.read_text()

    def trace(self):
        if not self.args.trace.exists():
            return []
        lines = self.args.trace.read_text().splitlines()
        records = []
        for line in lines:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass  # A concurrently appended final line may not yet be complete.
        return records

    def response(self, method, since, predicate=lambda value: value is not None):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            records = self.trace()[since:]
            requests = [r["message"] for r in records
                        if r["direction"] == "client_to_server" and r["message"].get("method") == method]
            ids = {r["id"] for r in requests if "id" in r}
            for record in records:
                message = record["message"]
                if record["direction"] == "server_to_client" and message.get("id") in ids:
                    assert "error" not in message, message
                    if predicate(message.get("result")):
                        return message["result"]
            time.sleep(.1)
        raise AssertionError(f"No qualifying actual Zed LSP response for {method}")

    def diagnostic(self, since, has_errors):
        deadline = time.monotonic() + 10
        uri = self.probe.as_uri()
        while time.monotonic() < deadline:
            for record in self.trace()[since:]:
                m = record["message"]
                if (m.get("method") == "textDocument/publishDiagnostics"
                    and m["params"]["uri"] == uri
                    and bool(m["params"]["diagnostics"]) == has_errors):
                    return m["params"]["diagnostics"]
            time.sleep(.1)
        raise AssertionError("Expected diagnostic notification did not reach Zed")

    def run_test(self, name, function):
        try:
            detail = function()
            self.results.append({"name": name, "passed": True, "detail": detail})
            print("PASS", name, detail, flush=True)
        except Exception as error:
            self.snapshot(name + "-failure")
            self.results.append({"name": name, "passed": False, "error": str(error)})
            print("FAIL", name, str(error), flush=True)
            self.write_report()
            raise
        self.write_report()

    def write_report(self):
        (self.out / "report.json").write_text(json.dumps({
            "display": self.args.display, "project": str(self.project),
            "results": self.results,
        }, indent=2) + "\n")

    def syntax(self):
        self.open_file("script.rpy")
        self.goto(20)
        text, image = self.snapshot("syntax-highlighting")
        assert "fade_in" in text and "vbox" in text and "Character" in text, text
        pixels = image.convert("RGB").getcolors(image.width * image.height)
        assert pixels is not None
        colors = {color: count for count, color in pixels if isinstance(color, tuple) and len(color) == 3}
        # One Dark's keyword and string colors; allow antialiasing tolerance.
        purple = sum(n for (r, g, b), n in colors.items() if r > 130 and b > 130 and r > g * 1.25 and b > g * 1.25)
        green = sum(n for (r, g, b), n in colors.items() if g > 120 and g > r * 1.15 and g > b * 1.15)
        assert purple > 30 and green > 30, (purple, green)
        return {"keyword_colored_pixels": purple, "string_colored_pixels": green}

    def outline(self):
        self.open_file("script.rpy")
        self.key("ctrl+shift+o")
        text, _ = self.snapshot("outline")
        assert "fade_in" in text and "hud" in text and "start" in text, text
        self.key("Escape")
        return "GUI outline contains transform, screen, and label names"

    def definition(self):
        self.open_file("script.rpy")
        target_uri = (self.project / "game/chapter_two.rpy").as_uri()
        assert not any(r["message"].get("method") == "textDocument/didOpen" and
                       r["message"]["params"]["textDocument"]["uri"] == target_uri for r in self.trace()), "Target was already open"
        source = (self.project / "game/script.rpy").read_text().splitlines()
        row = next(i for i, line in enumerate(source, 1) if "jump chapter_two" in line)
        self.goto(row, source[row - 1].index("chapter_two") + 4)
        since = len(self.trace())
        self.key("F12")
        result = self.response("textDocument/definition", since)
        assert result["uri"] == target_uri, result
        text, _ = self.snapshot("go-to-definition")
        assert "chapter_two" in text and "different file" in text, text
        return "F12 opened the previously unopened chapter_two.rpy"

    def completion(self, nested=False):
        self.open_file("gui_checks.rpy")
        self.replace("label gui_probe:\n    $ " + ("renpy.music." if nested else "renpy."))
        since = len(self.trace())
        self.key("ctrl+space")
        result = self.response("textDocument/completion", since)
        items = result if isinstance(result, list) else result["items"]
        wanted = "play" if nested else "pause"
        assert wanted in {item["label"] for item in items}
        if nested:
            assert "music.play" not in {item["label"] for item in items}
        text, _ = self.snapshot("completion-nested" if nested else "completion")
        assert any(item["label"] in text for item in items[:20]), text
        self.key("Escape")
        self.save()
        return {"requested_by_zed": True, "expected_item": wanted, "items": len(items)}

    def hover(self):
        self.open_file("gui_checks.rpy")
        self.replace("label gui_probe:\n    $ renpy.pause(0.5)\n")
        self.goto(2, 14)
        since = len(self.trace())
        self.palette("editor: hover")
        result = self.response("textDocument/hover", since)
        assert "renpy.pause" in result["contents"]["value"]
        text, _ = self.snapshot("hover")
        assert "renpy.pause" in text and ("seconds" in text.lower() or "delay" in text.lower()), text
        self.key("Escape")
        self.save()
        return "Hover documentation rendered for a cursor inside renpy.pause"

    def indentation_and_brackets(self):
        self.open_file("gui_checks.rpy")
        self.replace("label gui_indent:")
        self.key("Return")
        self.type("pass")
        content = self.save()
        assert content.rstrip() == "label gui_indent:\n    pass", repr(content)
        self.replace("label gui_pair:\n    $ value = ")
        self.type("(")
        content = self.save()
        assert "$ value = ()" in content, repr(content)
        self.snapshot("indentation-and-brackets")
        return "Enter inserted four spaces; '(' inserted its matching ')'"

    def snippet(self):
        self.open_file("gui_checks.rpy")
        self.replace("label gui_snippet:\n    ")
        self.type("rpause")
        self.key("ctrl+space")
        text, _ = self.snapshot("snippet-menu")
        assert "rpause" in text or "Renpy Pause" in text, text
        self.key("Return")
        self.type("0.5")
        self.key("Tab")
        content = self.save()
        assert "$ renpy.pause(0.5)" in content, repr(content)
        self.snapshot("snippet-expanded")
        return "Repaired rpause snippet inserts a literal '$' and editable argument"

    def diagnostics(self):
        self.open_file("gui_checks.rpy")
        since = len(self.trace())
        self.replace("default 1bad = 1\n")
        self.save()
        diagnostics = self.diagnostic(since, True)
        assert any("Invalid variable name" in d["message"] for d in diagnostics)
        self.palette("diagnostics: deploy")
        text, _ = self.snapshot("diagnostic-visible")
        assert "Invalid variable name" in text, text
        self.open_file("gui_checks.rpy")
        since = len(self.trace())
        self.replace("default valid_name = 1\n")
        self.save()
        self.diagnostic(since, False)
        self.palette("diagnostics: deploy")
        text, _ = self.snapshot("diagnostic-cleared")
        assert "Invalid variable name" not in text, text
        return "GUI showed invalid-name diagnostic, then cleared it after editing"

    def run(self):
        tests = {
            "syntax-highlighting": self.syntax,
            "outline": self.outline,
            "go-to-definition": self.definition,
            "completion": self.completion,
            "nested-completion": lambda: self.completion(True),
            "hover": self.hover,
            "indentation-and-brackets": self.indentation_and_brackets,
            "snippet": self.snippet,
            "diagnostics": self.diagnostics,
        }
        for name in self.args.only or tests:
            self.run_test(name, tests[name])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--display", required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--xdotool", type=Path, default=Path("xdotool"))
    parser.add_argument("--xclip", type=Path, default=Path("xclip"))
    parser.add_argument("--reuse-probe", action="store_true", help="reuse only this disposable session's existing probe")
    parser.add_argument("--only", nargs="+", help="rerun selected checks in the same session, preserving other results")
    args = parser.parse_args()
    Gui(args).run()


if __name__ == "__main__":
    main()
