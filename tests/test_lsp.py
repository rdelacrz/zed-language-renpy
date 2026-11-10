#!/usr/bin/env python3
"""Exercise the built native server using real Content-Length framed JSON-RPC."""
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import tempfile
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
BINARY = Path(os.environ.get("RENPY_LSP_BINARY", ROOT / "server/target/release/renpy-language-server"))


class Client:
    def __init__(self):
        self.stderr = tempfile.TemporaryFile()
        self.process = subprocess.Popen([str(BINARY)], stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=self.stderr)
        stdin, stdout = self.process.stdin, self.process.stdout
        assert stdin is not None and stdout is not None
        self.stdin, self.stdout = stdin, stdout
        self.messages = queue.Queue()
        self.pending = []
        self.sequence = 0
        self.reader = threading.Thread(target=self.read, daemon=True)
        self.reader.start()

    def read(self):
        try:
            while True:
                headers = {}
                while True:
                    line = self.stdout.readline()
                    if not line:
                        raise EOFError("language server closed stdout")
                    if line == b"\r\n":
                        break
                    key, value = line.decode().split(":", 1)
                    headers[key.lower()] = value.strip()
                self.messages.put(json.loads(self.stdout.read(int(headers["content-length"]))))
        except Exception as error:
            self.messages.put(error)

    def send(self, message):
        if message.get("params", False) is None:
            message = {key: value for key, value in message.items() if key != "params"}
        body = json.dumps({"jsonrpc": "2.0", **message}, ensure_ascii=False).encode()
        self.stdin.write(f"Content-Length: {len(body)}\r\n\r\n".encode() + body)
        self.stdin.flush()

    def notify(self, method, params):
        self.send({"method": method, "params": params})

    def wait(self, predicate, timeout=10):
        deadline = time.monotonic() + timeout
        while True:
            for i, message in enumerate(self.pending):
                if predicate(message):
                    return self.pending.pop(i)
            message = self.messages.get(timeout=max(0.01, deadline - time.monotonic()))
            if isinstance(message, Exception):
                raise message
            if "method" in message and "id" in message:
                # The client supports the file-watch registration exercised below.
                self.send({"id": message["id"], "result": None})
            else:
                self.pending.append(message)
            if time.monotonic() >= deadline:
                raise TimeoutError(f"No matching LSP response; pending={self.pending!r}")

    def request(self, method, params):
        self.sequence += 1
        request_id = self.sequence
        self.send({"id": request_id, "method": method, "params": params})
        response = self.wait(lambda message: message.get("id") == request_id)
        if "error" in response:
            raise AssertionError(response["error"])
        return response.get("result")

    def close(self):
        try:
            self.request("shutdown", None)
            self.notify("exit", None)
            self.process.wait(timeout=5)
            if self.process.returncode != 0:
                raise AssertionError(f"server exited {self.process.returncode}")
        finally:
            if self.process.poll() is None:
                self.process.kill()
                self.process.wait()
            self.stdin.close()
            self.stdout.close()
            self.stderr.close()


class LifecycleTests(unittest.TestCase):
    def test_exit_without_shutdown_is_nonzero(self):
        body = json.dumps({"jsonrpc": "2.0", "method": "exit"}).encode()
        result = subprocess.run([str(BINARY)],
                                input=f"Content-Length: {len(body)}\r\n\r\n".encode() + body,
                                capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 1)


class LspTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="renpy-lsp-test-")
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        shutil.copytree(ROOT / "examples/game", self.project / "game")
        self.path = self.project / "game/script.rpy"
        self.uri = self.path.as_uri()
        self.text = self.path.read_text()
        self.client = Client()
        self.addCleanup(self.client.close)
        self.initialize = self.client.request("initialize", {
            "processId": os.getpid(), "rootUri": self.project.as_uri(),
            "workspaceFolders": [{"uri": self.project.as_uri(), "name": "test"}],
            "capabilities": {"workspace": {"didChangeWatchedFiles": {"dynamicRegistration": True}}},
        })
        self.client.notify("initialized", {})
        self.open(self.uri, self.text)

    def diagnostics(self, uri, version):
        return self.client.wait(lambda m: m.get("method") == "textDocument/publishDiagnostics"
                                and m["params"]["uri"] == uri
                                and m["params"].get("version") == version)["params"]["diagnostics"]

    def open(self, uri, text):
        self.client.notify("textDocument/didOpen", {"textDocument": {
            "uri": uri, "languageId": "renpy", "version": 1, "text": text}})
        return self.diagnostics(uri, 1)

    def change(self, text, version=2):
        self.text = text
        self.client.notify("textDocument/didChange", {
            "textDocument": {"uri": self.uri, "version": version},
            "contentChanges": [{"text": text}]})
        return self.diagnostics(self.uri, version)

    def at(self, substring, offset=0):
        index = self.text.index(substring) + offset
        before = self.text[:index]
        return {"textDocument": {"uri": self.uri}, "position": {
            "line": before.count("\n"),
            "character": len(before.rsplit("\n", 1)[-1].encode("utf-16-le")) // 2}}

    def test_capabilities(self):
        caps = self.initialize["capabilities"]
        self.assertEqual(caps["positionEncoding"], "utf-16")
        self.assertEqual(caps["textDocumentSync"]["change"], 1)
        self.assertNotIn("semanticTokensProvider", caps)

    def test_completion_after_dot_and_workspace_symbols(self):
        self.change(self.text + "\n$ renpy.\n")
        items = self.client.request("textDocument/completion", self.at("$ renpy.\n", len("$ renpy.")))
        self.assertIn("pause", [item["label"] for item in items])
        self.change(self.text + "jump chapter_\n", 3)
        items = self.client.request("textDocument/completion", self.at("jump chapter_\n", len("jump chapter_")))
        self.assertIn("chapter_two", [item["label"] for item in items])
        self.change(self.text + "# renpy.\n", 4)
        self.assertFalse(self.client.request("textDocument/completion", self.at("# renpy.\n", 8)))

    def test_nested_api_completion(self):
        self.change("label start:\n    $ renpy.music.\n")
        items = self.client.request("textDocument/completion", self.at("renpy.music.", len("renpy.music.")))
        labels = [item["label"] for item in items]
        self.assertIn("play", labels)
        self.assertNotIn("music.play", labels)

    def test_hover_at_middle_and_signature(self):
        result = self.client.request("textDocument/hover", self.at("renpy.pause", 8))
        self.assertIn("renpy.pause", result["contents"]["value"])
        result = self.client.request("textDocument/signatureHelp", self.at("renpy.pause(", len("renpy.pause(")))
        self.assertTrue(result["signatures"])

    def test_definition_in_unopened_file_and_after_close(self):
        target = self.project / "game/chapter_two.rpy"
        params = self.at("jump chapter_two", len("jump cha"))
        definition = self.client.request("textDocument/definition", params)
        self.assertEqual(definition["uri"], target.as_uri())
        self.open(target.as_uri(), "label unsaved_name:\n    return\n")
        self.assertIsNone(self.client.request("textDocument/definition", params))
        self.client.notify("textDocument/didClose", {"textDocument": {"uri": target.as_uri()}})
        self.diagnostics(target.as_uri(), None)
        self.assertEqual(self.client.request("textDocument/definition", params)["uri"], target.as_uri())

    def test_references_and_unicode_ranges(self):
        text = 'default score = 0\nlabel start:\n    $ message = "😀 score"; score += 1 # score\n    "score"\n'
        self.change(text)
        params = self.at("score =", 2)
        refs = self.client.request("textDocument/references", {**params, "context": {"includeDeclaration": False}})
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0]["range"]["start"], self.at("score +=")["position"])
        highlights = self.client.request("textDocument/documentHighlight", params)
        self.assertEqual(len(highlights), 2)

    def test_diagnostics_change_save_and_clear(self):
        self.assertTrue(self.change("label start:\n\treturn\n"))
        self.assertFalse(self.change("label start:\n    return\n", 3))
        self.client.notify("textDocument/didSave", {"textDocument": {"uri": self.uri}})
        self.assertFalse(self.diagnostics(self.uri, 3))

    def test_symbols_folding_and_colors(self):
        params = {"textDocument": {"uri": self.uri}}
        symbols = self.client.request("textDocument/documentSymbol", params)
        self.assertTrue({"start", "hud", "fade_in"} <= {s["name"] for s in symbols})
        self.assertTrue(self.client.request("textDocument/foldingRange", params))
        colors = self.client.request("textDocument/documentColor", params)
        self.assertTrue(colors)
        self.assertTrue(self.client.request("textDocument/colorPresentation", {**params, **colors[0]}))

    def test_unicode_symbol_ranges(self):
        self.change('default 名前 = "こんにちは"\nlabel start:\n    "😀"\n')
        result = self.client.request("textDocument/documentSymbol", {"textDocument": {"uri": self.uri}})
        name = next(symbol for symbol in result if symbol["name"] == "名前")
        self.assertEqual(name["selectionRange"]["start"]["character"], len("default "))
        self.assertEqual(name["selectionRange"]["end"]["character"], len("default 名前"))
        start = next(symbol for symbol in result if symbol["name"] == "start")
        self.assertEqual(start["range"]["end"]["character"], 8)

    def test_watched_file_deletion(self):
        target = self.project / "game/chapter_two.rpy"
        target.unlink()
        self.client.notify("workspace/didChangeWatchedFiles", {"changes": [{"uri": target.as_uri(), "type": 3}]})
        # Notifications and requests are ordered by tower-lsp's service.
        result = self.client.request("textDocument/definition", self.at("jump chapter_two", 8))
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
