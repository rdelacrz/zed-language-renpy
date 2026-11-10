# Local grammar snapshot

This directory is a vendored snapshot, not the old opaque-block implementation.

- Upstream: https://github.com/rockettap/renpy-tree-sitter
- Revision: `0e9ea0d0dcb8860ea1d5f3ac6356855bf58cc556`
- The generated grammar, scanner, corpus, and example match that revision.
- `package.json` / `package-lock.json` pin tree-sitter-cli 0.25.10 locally.
- `LICENSE` is retained unchanged.

Zed loads the **remote pinned revision in `../extension.toml`**, not this folder.
The local snapshot is for regression testing and package builds. A parser edit
must be accompanied by a committed, accessible grammar revision and manifest
update before Zed's dev installer will use it. See `../README.md`.

The extension's Zed queries live in `../languages/renpy/`. Run
`python3 scripts/build.py --package --test` from the repository root as
documented in the root README to test both the native and WASM parser runtimes.
