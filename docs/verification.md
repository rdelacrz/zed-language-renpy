# Verification record

Verified on the available Linux AArch64 host with Rust 1.96.0, Node 22.23.1,
wasi-sdk 34, and tree-sitter-cli 0.25.10.

## Executed successfully

```sh
WASI_SDK_PATH=/path/to/wasi-sdk-34.0-arm64-linux \
  python3 scripts/build.py --package --test
python3 scripts/test-official-examples.py
```

| Check | Result |
| --- | --- |
| Extension command/settings Rust tests | 4 passed |
| Patched native language-server Rust tests | 73 passed |
| Upstream grammar corpus | 5 passed |
| Native parser/query and real stdio LSP regression tests | 19 passed |
| Exact grammar WASM loaded in Tree-sitter/Wasmtime | Passed; `language.is_wasm()` asserted |
| Local/example fixture WASM parses | 3 passed |
| All Zed query files compiled against the WASM language | 7 passed |
| Official Ren'Py “The Question” scripts | 5 passed in WASM |
| Clean server checkout + compatibility patch | Applies; second application safely recognized |
| Generated source snapshot | Matches pinned upstream grammar |
| Extension WASI Preview 2 release build | Passed |
| Native Linux AArch64 server release build | Passed |

The official example test downloads `gui.rpy`, `options.rpy`, `screens.rpy`,
`script.rpy`, and `testcases.rpy` at Ren'Py revision
`ac8054a5c326011529894c0fc6e8fc8fff294ea2`. It records source sizes and hashes in
`target/official-examples.json`; no invented fixture content substitutes for
those downloads.

The protocol tests verify initialization/capabilities, trailing-dot and nested
API completion, workspace-symbol completion, hover from inside a name,
signature help, definitions in unopened files, restoring saved symbols after
closing unsaved buffers, references excluding strings/comments, UTF-16 ranges,
diagnostics on change/save, symbols, folding, colors/presentations, watched
file deletion, and lifecycle exit codes. Every normal client test performs a
`shutdown`/`exit` exchange and waits for a zero exit **without closing stdin**.

The native server still emits upstream dead-code warnings. These are not build
or test failures. Its diagnostic/parser limitations are documented in README.

## Artifacts

- `dist/renpy-extension.tar.gz`
- `dist/renpy/extension.wasm`
- `dist/renpy/grammars/renpy.wasm`
- `dist/SHA256SUMS.json`
- `server/target/release/renpy-language-server`
- `target/zed-settings.json`

The archive contains extension code, grammar, queries, configuration, snippets,
and third-party notices. It does not bundle a platform-specific language server.

## Not verified interactively

A downloaded Zed v1.27.0 Linux AArch64 binary was launched with isolated data
and configuration directories under Xvfb. It failed before a window opened:

> X11 connection: Unsupported extension

Therefore this record does **not** claim a successful Zed dev-install UI run,
visual highlighting review, interactive indentation/completion check, or
marketplace installation. Those need a functioning desktop session.
Windows/macOS builds and hosted CI execution have not been run here. CI
configuration is included, but no remote workflow or publication was triggered.

### Desktop acceptance checklist

1. Merge `target/zed-settings.json` into Zed settings.
2. Run **zed: install dev extension** and select the repository root.
3. Open `examples/game/script.rpy`; confirm the language is **Ren'Py**.
4. Check nested dialogue/menu/screen/ATL highlights and the outline.
5. Type `$ renpy.` / `$ renpy.music.`; inspect completion and hover.
6. Go to definition on `chapter_two` without first opening its file.
7. Enter a tab-indented line and check the diagnostic; fix it and confirm it clears.
8. Test Enter after a colon, bracket pairing, and snippets in the editor.
9. Inspect **zed: open log** for grammar/query/server errors.
