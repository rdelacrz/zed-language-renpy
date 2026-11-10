#!/usr/bin/env python3
"""Reproducible local build. Never edits the user's Zed settings or installs globally."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
SERVER_REV = "91d66e0c96a90674d817907cffd2e189cf02969a"


def run(*args, cwd=ROOT, **kwargs):
    print("+", " ".join(map(str, args)), flush=True)
    return subprocess.run(list(map(str, args)), cwd=cwd, check=True, **kwargs)


def prepare_server():
    if not (ROOT / "server/Cargo.toml").is_file():
        run("git", "submodule", "update", "--init", "--recursive")
    revision = run("git", "rev-parse", "HEAD", cwd=ROOT / "server", capture_output=True, text=True).stdout.strip()
    if revision != SERVER_REV:
        raise RuntimeError(f"server is at {revision}, expected {SERVER_REV}; refusing to reset local work. "
                           "Commit or stash server edits, then run `git submodule update --init --recursive`.")
    print(f"Using published server revision {revision}; no patch required.")


def build_grammar():
    sdk = os.environ.get("WASI_SDK_PATH")
    if not sdk:
        raise RuntimeError("--package requires WASI_SDK_PATH (wasi-sdk root containing bin/clang). "
                           "Zed downloads it automatically when installing a dev extension.")
    clang = Path(sdk) / "bin" / ("clang.exe" if os.name == "nt" else "clang")
    src = ROOT / "tree-sitter-renpy/src"
    # Same compilation model used by Zed's ExtensionBuilder.
    run(clang, "-fPIC", "-shared", "-Os", "-Wl,--export=tree_sitter_renpy",
        "-Wl,--max-memory=4294967296", "-I", src, src / "parser.c", src / "scanner.c",
        "-o", ROOT / "target/renpy.wasm")


def package():
    dest = ROOT / "dist/renpy"
    if dest.exists():
        shutil.rmtree(dest)
    (dest / "grammars").mkdir(parents=True)
    shutil.copytree(ROOT / "languages", dest / "languages")
    shutil.copytree(ROOT / "snippets", dest / "snippets")
    shutil.copy(ROOT / "target/renpy.wasm", dest / "grammars/renpy.wasm")
    shutil.copy(ROOT / "target/wasm32-wasip2/release/zed_renpy_extension.wasm", dest / "extension.wasm")
    manifest = (ROOT / "extension.toml").read_text()
    manifest = 'languages = ["languages/renpy"]\n' + manifest
    manifest += '\n[lib]\nkind = "Rust"\nversion = "0.6.0"\n'
    tomllib.loads(manifest)
    (dest / "extension.toml").write_text(manifest)
    shutil.copy(ROOT / "THIRD_PARTY_NOTICES.md", dest)
    shutil.copy(ROOT / "tree-sitter-renpy/LICENSE", dest / "GRAMMAR_LICENSE")
    archive = ROOT / "dist/renpy-extension.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        for child in sorted(dest.iterdir()):
            tar.add(child, arcname=child.name)
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (archive, dest / "extension.wasm", dest / "grammars/renpy.wasm")}
    (ROOT / "dist/SHA256SUMS.json").write_text(json.dumps(hashes, indent=2) + "\n")
    print(f"Built extension package: {archive}")
    print("The native LSP is separate; this is not a marketplace publication.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", action="store_true", help="also compile grammar WASM and create dist/ package")
    parser.add_argument("--test", action="store_true", help="run Rust, grammar, and real LSP regression tests")
    args = parser.parse_args()
    # rustup installs here; GUI-launched shells may not have loaded .cargo/env.
    cargo_home = Path(os.environ.get("CARGO_HOME", Path.home() / ".cargo"))
    if not shutil.which("cargo"):
        os.environ["PATH"] = str(cargo_home / "bin") + os.pathsep + os.environ.get("PATH", "")
    if not shutil.which("cargo"):
        raise RuntimeError("Install Rust with rustup: https://rustup.rs")
    prepare_server()
    run("rustup", "target", "add", "wasm32-wasip2")
    run("cargo", "build", "--locked", "--release", "--manifest-path", "server/Cargo.toml",
        "--target-dir", ROOT / "server/target")
    run("cargo", "build", "--locked", "--release", "--target", "wasm32-wasip2",
        "--target-dir", ROOT / "target")
    binary = ROOT / "server/target/release" / ("renpy-language-server.exe" if os.name == "nt" else "renpy-language-server")
    settings = {"lsp": {"renpy-language-server": {"binary": {
        "path": str(binary), "arguments": [], "env": {}
    }}}}
    (ROOT / "target/zed-settings.json").write_text(json.dumps(settings, indent=2) + "\n")
    if args.package:
        build_grammar()
    if args.test:
        run("cargo", "test", "--locked")
        run("cargo", "test", "--locked", "--manifest-path", "server/Cargo.toml")
        run("npm", "ci", cwd=ROOT / "tree-sitter-renpy")
        run("npm", "test", cwd=ROOT / "tree-sitter-renpy")
        python = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        if not python.exists():
            raise RuntimeError("Create .venv and install tests/requirements.txt first; see README.md")
        run(python, "-m", "unittest", "discover", "-s", "tests", "-v")
        if args.package:
            run("cargo", "run", "--locked", "--manifest-path", "tests/wasm/Cargo.toml")
    if args.package:
        package()
    print(f"Native server: {binary}")
    print("Merge target/zed-settings.json into Zed settings; then install this checkout as a dev extension.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        sys.exit(1)
