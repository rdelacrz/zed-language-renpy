#!/usr/bin/env python3
"""Optional network test against pinned official Ren'Py example scripts."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REVISION = "ac8054a5c326011529894c0fc6e8fc8fff294ea2"
NAMES = ("gui.rpy", "options.rpy", "screens.rpy", "script.rpy", "testcases.rpy")


def main():
    with tempfile.TemporaryDirectory(prefix="renpy-official-") as directory:
        paths = []
        report = {"repository": "https://github.com/renpy/renpy", "revision": REVISION, "files": {}}
        for name in NAMES:
            url = f"https://raw.githubusercontent.com/renpy/renpy/{REVISION}/the_question/game/{name}"
            with urllib.request.urlopen(url, timeout=30) as response:
                data = response.read()
            path = Path(directory) / name
            path.write_bytes(data)
            paths.append(str(path))
            report["files"][name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        env = os.environ.copy()
        if not shutil.which("cargo"):
            env["PATH"] = str(Path.home() / ".cargo/bin") + os.pathsep + env.get("PATH", "")
        subprocess.run(["cargo", "run", "--locked", "--manifest-path", "tests/wasm/Cargo.toml", "--", *paths],
                       cwd=ROOT, env=env, check=True, timeout=600)
        (ROOT / "target/official-examples.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
