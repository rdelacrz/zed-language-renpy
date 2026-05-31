#!/usr/bin/env python3
"""Sample producer for Ren'Py navigation JSON artifacts.

Reads a workspace fixture and emits the three JSON files consumed by the
extension backend:
- navigation.json
- navigation_definitions.json
- navigation_diagnostics.json

This is intentionally small and fixture-driven. It is useful for local refreshes
and end-to-end testing, but it is not a full workspace crawler.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_FIXTURE = Path(__file__).resolve().parents[1] / "src" / "navigation-fixture.json"


def load_fixture(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def derive_navigation_index(fixture: dict[str, Any]) -> dict[str, Any]:
    navigation = fixture.get("navigation", {})
    return {
        "name": navigation.get("name", "sample-renpy-workspace"),
        "version": navigation.get("version", "1"),
        "labels": navigation.get("labels", []),
        "screens": navigation.get("screens", []),
        "transforms": navigation.get("transforms", []),
        "audio": navigation.get("audio", []),
        "config_keys": navigation.get("config_keys", []),
        "renpy_keys": navigation.get("renpy_keys", []),
        "gui_keys": navigation.get("gui_keys", []),
    }


def derive_definitions(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    return list(fixture.get("definitions", []))


def derive_diagnostics(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    return list(fixture.get("diagnostics", []))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--out-dir", type=Path, default=Path.cwd())
    args = parser.parse_args()

    fixture = load_fixture(args.fixture)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        "navigation.json": derive_navigation_index(fixture),
        "navigation_definitions.json": derive_definitions(fixture),
        "navigation_diagnostics.json": derive_diagnostics(fixture),
    }

    for name, payload in outputs.items():
        (args.out_dir / name).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    print(f"wrote {len(outputs)} files to {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
