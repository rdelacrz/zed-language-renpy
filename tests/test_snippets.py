"""Regression for literal dollars rejected by Zed's snippet parser."""
import json
from pathlib import Path
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]


def validate_dollars(body):
    i = 0
    while i < len(body):
        if body[i] == "\\":
            i += 2
            continue
        if body[i] == "$":
            after = body[i + 1:]
            if not (after and (after[0].isdigit() or
                               (after.startswith("{") and len(after) > 1 and after[1].isdigit()))):
                raise ValueError(f"Unescaped literal dollar at offset {i}")
        i += 1


class SnippetTests(unittest.TestCase):
    def test_all_snippet_dollars_are_escaped_or_tabstops(self):
        manifest = tomllib.loads((ROOT / "extension.toml").read_text())
        language = tomllib.loads((ROOT / "languages/renpy/config.toml").read_text())
        paths = [Path(path) for path in manifest["snippets"]]
        self.assertTrue(paths)
        self.assertTrue(all(path.stem == language["name"].lower() for path in paths),
                        "Zed matches snippet filenames to the lowercase display name, including punctuation")
        snippets = {}
        for path in paths:
            snippets.update(json.loads((ROOT / path).read_text()))
        for name, snippet in snippets.items():
            with self.subTest(snippet=name):
                body = snippet["body"]
                validate_dollars("\n".join(body) if isinstance(body, list) else body)

    def test_rejects_unescaped_renpy_statement(self):
        with self.assertRaises(ValueError):
            validate_dollars("$ renpy.pause($1)")
        validate_dollars("\\$ renpy.pause($1)")
        validate_dollars("${1:class} $0 ${2:default}")
        with self.assertRaises(ValueError):
            validate_dollars("\\\\$ not_a_tabstop")


if __name__ == "__main__":
    unittest.main()
