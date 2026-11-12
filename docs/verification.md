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
| Native language-server Rust tests | 73 passed |
| Upstream grammar corpus | 5 passed |
| Native parser/query, stdio LSP, and snippet regression tests | 21 passed |
| Exact grammar WASM loaded in Tree-sitter/Wasmtime | Passed; `language.is_wasm()` asserted |
| Local/example fixture WASM parses | 3 passed |
| All Zed query files compiled against the WASM language | 7 passed |
| Official Ren'Py “The Question” scripts | 5 passed in WASM |
| Clean server checkout | Published pinned revision; no compatibility patch required |
| Generated source snapshot | Matches pinned upstream grammar |
| Extension WASI Preview 2 release build | Passed |
| Native Linux AArch64 server release build | Passed |
| Dev extension installed through Zed's GUI | Passed |
| Interactive GUI feature checks in a fresh isolated profile | 9 passed |
| Stdio LSP suite through the transparent GUI-test recorder | 11 passed |

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

## GUI verification

Zed v1.27.0 Linux AArch64 now renders successfully on a private Xvfb/Openbox
desktop using Mesa lavapipe (software Vulkan). The original X11 failure was
preceded by a Mali Vulkan surface failure and an EGL fallback failure. Scoped
driver/library overrides fixed rendering without changing the host's real
desktop or system graphics configuration.

The dev extension was installed through Zed's GUI. Actual keyboard/clipboard
input, screenshots/OCR, saved files, and Zed-originated LSP traffic verify syntax
colors, outline, unopened-file definition navigation, API and nested API
completion, hover, indentation/brackets, snippet expansion, and diagnostics
appearing and clearing. All nine checks also passed in one uninterrupted run
in a fresh profile using the rebuilt extension payload.

The GUI uncovered two snippet bugs missed by the original tests: unescaped
literal dollars and a filename that did not match the lowercase `Ren'Py`
display name. Both are fixed and covered by regression tests.

See [gui-verification.md](gui-verification.md) for root-cause evidence and the
reusable launcher/test commands. Evidence is retained under
`target/gui-verification/clean/` (report, screenshots, OCR), with Zed logs and
actual LSP traces alongside it in `target/gui-verification/`.

Physical-GPU performance, Windows/macOS, other display backends, and marketplace
installation remain unverified. These are local results, not hosted CI results.

### Desktop acceptance checklist exercised

1. Merge `target/zed-settings.json` into Zed settings.
2. Run **zed: install dev extension** and select the repository root.
3. Open `examples/game/script.rpy`; confirm the language is **Ren'Py**.
4. Check nested dialogue/menu/screen/ATL highlights and the outline.
5. Type `$ renpy.` / `$ renpy.music.`; inspect completion and hover.
6. Go to definition on `chapter_two` without first opening its file.
7. Enter an invalid variable name and check the diagnostic; fix it and confirm it clears.
8. Test Enter after a colon, bracket pairing, and snippets in the editor.
9. Inspect **zed: open log** for grammar/query/server errors.
