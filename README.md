# Ren'Py Extension for Zed

Provides Ren'Py language support in [Zed](https://zed.dev) with syntax highlighting, snippets, and language server integration.

## Components

1. **Root WASM crate** — This directory. The Zed extension entry point compiled to `wasm32-wasip2`.
2. **`tree-sitter-renpy/`** — Tree-sitter grammar for Ren'Py syntax highlighting and structure queries.
3. **`server/`** — Native `renpy-language-server` binary (tower-lsp) providing diagnostics, completions, and hover.

## Development Setup

### 1. Build the language server

```sh
cd server && cargo build --release
```

Add the binary to your PATH, or set `lsp.renpy-language-server.binary.path` in Zed settings:

```json
{
  "lsp": {
    "renpy-language-server": {
      "binary": {
        "path": "/absolute/path/to/server/target/release/renpy-language-server"
      }
    }
  }
}
```

### 2. Add the WASM target

```sh
rustup target add wasm32-wasip2
```

### 3. Install as a dev extension

In Zed: **Extensions → Install Dev Extension** → select this repo root.

Zed will compile the WASM crate and load the extension automatically.

## Further Reading

- [server/README.md](server/README.md) — Language server details
- [tree-sitter-renpy/README.md](tree-sitter-renpy/README.md) — Grammar details
