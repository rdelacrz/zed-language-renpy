# Ren'Py language support for Zed

A Zed language extension for `.rpy` and `.rpym` files, with an indentation-aware
Tree-sitter grammar and the native `renpy-language-server`.

## Use it

Requirements: Git, [Rust installed with rustup](https://rustup.rs), a native C
linker, and Python 3.11+ for the build helper. Use a current Zed release; the
Rust extension API is `0.6.0` (Zed's documented API minimum is 0.192).

```sh
git clone --recurse-submodules https://github.com/rdelacrz/zed-language-renpy
cd zed-language-renpy
python3 scripts/build.py
```

After pulling updates to an existing checkout, run
`git submodule update --init --recursive` before building (commit or stash any
local server edits first). The build helper initializes the server submodule if
necessary, verifies the published pinned revision, builds the native server and
the WASI extension, and writes **`target/zed-settings.json`**.
It does **not** change your global PATH or overwrite your Zed settings.

1. Open Zed's settings and **merge** `target/zed-settings.json` into them. It
   contains the absolute path to your newly built server. Alternatively put
   `server/target/release/renpy-language-server` on your shell's PATH.
2. Open **Extensions → Install Dev Extension** and select **this repository
   root** (the directory containing `extension.toml`, not `server/`). Zed
   compiles the Rust extension and downloads/compiles the pinned grammar.
3. Open your Ren'Py project folder, then an `.rpy` file. Its language should be
   **Ren'Py**. `examples/game/script.rpy` is a small editor smoke fixture.

The settings have this shape; use the generated absolute path, not this example:

```json
{
  "lsp": {
    "renpy-language-server": {
      "binary": {
        "path": "/absolute/path/to/zed-language-renpy/server/target/release/renpy-language-server",
        "arguments": [],
        "env": {}
      }
    }
  }
}
```

The server uses **stdio with no arguments**. Explicit binary path, arguments,
and environment settings are honored before PATH lookup. The upstream server
has no published release assets, so this extension does not pretend to offer
a working automatic binary download. A Ren'Py SDK is not required for editing.
On Windows the generated server path ends in `.exe`; builds on Windows/macOS
have not been exercised here.

## Features

- Nested dialogue, labels, menus, conditionals, screens, ATL/transforms, styles,
  image statements, translations, text tags, interpolation, and comments.
- Zed outline, indentation ranges, bracket configuration, Vim text objects,
  string/comment scopes, and snippets.
- Python highlighting in `python:` / `init python:` blocks, `$` statements,
  expressions, and bracketed arguments. Plain `init:` blocks remain Ren'Py.
  This uses Zed's Python language support; it does not attach a Python LSP.
- LSP keyword/API/workspace-symbol completion, hover documentation, signature
  help, definition navigation, references, document symbols/highlights,
  indentation folding, color presentations, and push diagnostics.
- Workspace indexing of unopened `.rpy` / `.rpym` files, file-change watching
  when the client supports registration, and correct disk restoration after
  closing an unsaved buffer.

## Build and test

For the test suite, install Node/npm and the Python parser binding:

```sh
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r tests/requirements.txt
python3 scripts/build.py --test
```

Without uv: `python3 -m venv .venv`, then use that environment's pip to install
`tests/requirements.txt`.

To build a standalone extension payload, install
[wasi-sdk](https://github.com/WebAssembly/wasi-sdk/releases), then:

```sh
export WASI_SDK_PATH=/absolute/path/to/wasi-sdk
python3 scripts/build.py --package --test
python3 scripts/test-official-examples.py   # optional network-backed test
```

`--package` produces:

- `dist/renpy/extension.wasm` — WASI Preview 2 extension component.
- `dist/renpy/grammars/renpy.wasm` — Tree-sitter WASM module.
- `dist/renpy-extension.tar.gz` and `dist/SHA256SUMS.json`.

The native server remains separate in `server/target/release/`. The archive is
a built payload, **not a marketplace publication**, and the recommended install
route remains Zed's **Install Dev Extension** on the source checkout.

Tests exercise the actual server via Content-Length-framed stdio JSON-RPC,
compile every Zed query, assert meaningful syntax captures, check incremental
recovery/CRLF/EOF handling, and load the exact grammar WASM in Tree-sitter's
Wasmtime runtime. The WASM harness asserts `language.is_wasm()` and rejects an
invalid module, rather than relying on a CLI flag that may fall back to native
parsing. See [docs/verification.md](docs/verification.md) for the verified scope.

## Source layout and reproducibility

| Path | Purpose |
| --- | --- |
| `extension.toml`, `src/lib.rs` | Zed registration and LSP command/settings adapter |
| `languages/renpy/` | Language metadata and seven Tree-sitter query files |
| `tree-sitter-renpy/` | Vendored, pinned upstream grammar with external indentation scanner |
| `server/` | Pinned upstream Rust LSP submodule |
| `tests/` | Native parser, WASM parser, and real LSP regression tests |
| `docs/zed-integration.md` | Research findings, architecture, and source links |

Zed fetches grammars from the manifest's repository/revision; it does **not**
use arbitrary edits in the vendored grammar directory. If you change the
parser, publish a grammar commit and update `rev`, or temporarily use a local
Git `file://` URL and committed revision for dev installation. Regenerate and
commit `src/parser.c`, `src/grammar.json`, and `src/node-types.json` together.

The server fixes are published in `renpy-lsp-server` and included in the pinned
submodule revision; no compatibility patch is needed. For future server changes,
commit and push the server repository first, then update both the parent
repository's `server` gitlink and `SERVER_REV` in `scripts/build.py`. This keeps
fresh clones reproducible without pointing at unpublished commits.

## Limits and troubleshooting

- The LSP is a regex/indentation-based editor aid, **not the Ren'Py compiler**.
  Diagnostics are heuristic (including per-file persistent/store checks);
  semantic tokens, formatting, rename, and full Python type checking are not
  implemented. Use Ren'Py's own lint/compiler for authoritative validation.
- The grammar's Python expressions and some bracket groups are opaque tokens
  interpreted by Python injection. Not every Ren'Py extension/custom statement
  or advanced expression is guaranteed to have a precise syntax tree.
- Workspace scanning skips symlinks, dot-directories, `node_modules`, `target`,
  `renpy`, `cache`, and `saves`; it is bounded to 100,000 directory entries and
  8 MiB per file. New workspace folders require a server restart.
- The adapter forwards initialization options/workspace settings, but the
  server currently uses its built-in diagnostics defaults.
- If the LSP is missing, verify the generated binary path and restart language
  servers. Inspect **zed: open log** or launch `zed --foreground`.
- This machine could not create a Zed window under Xvfb; interactive highlighting,
  completion UI, and dev-install UI remain a manual smoke check on a desktop.
- Nothing is committed, pushed, globally installed, or published by the helper.
  Confirm extension/server licensing and inherited data/snippet attribution
  before publication; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
