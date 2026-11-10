#!/usr/bin/env python3
"""Compile the real parser and validate Zed queries against it (no mocks)."""
import ctypes
import json
import os
from pathlib import Path
import subprocess
import tomllib
import unittest
import warnings

from tree_sitter import Language, Parser, Query, QueryCursor

ROOT = Path(__file__).resolve().parents[1]


class GrammarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        library = ROOT / "target/renpy-test.so"
        library.parent.mkdir(exist_ok=True)
        src = ROOT / "tree-sitter-renpy/src"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(src), str(src / "parser.c"), str(src / "scanner.c"),
                        "-o", str(library)], check=True)
        cls.library = ctypes.CDLL(str(library))
        cls.library.tree_sitter_renpy.restype = ctypes.c_void_p
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            cls.language = Language(cls.library.tree_sitter_renpy())
        cls.parser = Parser(cls.language)
        cls.source = (ROOT / "examples/game/script.rpy").read_bytes()
        cls.tree = cls.parser.parse(cls.source)

    def captures(self, query):
        q = Query(self.language, (ROOT / f"languages/renpy/{query}.scm").read_text())
        return QueryCursor(q).captures(self.tree.root_node)

    def test_manifest(self):
        manifest = tomllib.loads((ROOT / "extension.toml").read_text())
        language = tomllib.loads((ROOT / "languages/renpy/config.toml").read_text())
        grammar = manifest["grammars"][language["grammar"]]
        self.assertRegex(grammar["rev"], r"^[a-f0-9]{40}$")
        self.assertNotIn("snippets", grammar)
        self.assertEqual(manifest["language_servers"]["renpy-language-server"]["language_ids"]["Ren'Py"], "renpy")
        for path in manifest["snippets"]:
            snippets = json.loads((ROOT / path).read_text())
            self.assertTrue(snippets)
            self.assertTrue(all("prefix" in s and "body" in s for s in snippets.values()))

    def test_all_queries_compile(self):
        for path in (ROOT / "languages/renpy").glob("*.scm"):
            with self.subTest(query=path.name):
                Query(self.language, path.read_text())

    def test_real_examples(self):
        paths = list((ROOT / "examples").rglob("*.rpy"))
        paths += list((ROOT / "tree-sitter-renpy/examples").glob("*.rpy"))
        for path in paths:
            with self.subTest(path=path.name):
                tree = self.parser.parse(path.read_bytes())
                self.assertFalse(tree.root_node.has_error, str(tree.root_node))

    def test_newlines_and_eof(self):
        for source in (self.source, self.source.rstrip(), self.source.replace(b"\n", b"\r\n")):
            with self.subTest(ending=repr(source[-30:])):
                self.assertFalse(self.parser.parse(source).root_node.has_error)

    def test_nested_highlights(self):
        captures = self.captures("highlights")
        keywords = {(n.text or b"").decode() for n in captures["keyword"]}
        self.assertTrue({"label", "menu", "jump", "if", "else", "vbox", "textbutton", "linear"} <= keywords)
        self.assertIn(b"{b}", [n.text for n in captures["tag"]])
        self.assertIn(b"[score]", [n.text for n in captures["variable.special"]])
        self.assertIn(b'"Waiting."', [n.text for n in captures["string"]])

    def test_outline_does_not_swallow_following_blocks(self):
        names = {(n.text or b"").decode() for n in self.captures("outline")["name"]}
        self.assertTrue({"start", "hud", "fade_in", "dialogue_text", "inventory", "bg room"} <= names)
        items = self.captures("outline")["item"]
        start = next(n for n in items if n.type == "label_statement")
        self.assertNotIn(b"translate french", start.text or b"")

    def test_python_injection_boundaries(self):
        contents = self.captures("injections")["injection.content"]
        self.assertTrue(any(b"def greeting" in (n.text or b"") and b"return" in (n.text or b"") for n in contents))
        self.assertFalse(any(b"define narrator" in (n.text or b"") for n in contents))
        self.assertFalse(any(b"jump chapter_two" in (n.text or b"") for n in contents))
        self.assertTrue(any(b"renpy.pause" in (n.text or b"") for n in contents))

    def test_recovery_and_incremental_edit(self):
        # Incomplete input is normal while editing; it must recover, not hang.
        broken = self.source.replace(b"label start:", b"label start")
        tree = self.parser.parse(broken)
        self.assertTrue(tree.root_node.has_error)
        offset = broken.index(b"label start") + len(b"label start")
        row = broken[:offset].count(b"\n")
        column = offset - broken.rfind(b"\n", 0, offset) - 1
        tree.edit(start_byte=offset, old_end_byte=offset, new_end_byte=offset + 1,
                  start_point=(row, column), old_end_point=(row, column), new_end_point=(row, column + 1))
        self.assertFalse(self.parser.parse(self.source, tree).root_node.has_error)


if __name__ == "__main__":
    unittest.main(verbosity=2)
