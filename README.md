# Ren'Py Language for Zed

[![Zed](https://img.shields.io/badge/Zed-extension-blue?logo=zed)](https://zed.dev/)
[![Ren'Py](https://img.shields.io/badge/Ren'Py-supported-purple.svg)](https://www.renpy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

Ren'Py Language for Zed is a language extension for the Zed editor that adds Ren'Py-aware editing support for visual novel projects. It targets `.rpy`, `.rpym`, `.rpymc`, and `.rpyc` files and combines Tree-sitter parsing, snippets, and a Ren'Py language server for a smoother authoring experience.

## Features

- Ren'Py file association for `.rpy`, `.rpym`, `.rpymc`, and `.rpyc`
- Syntax highlighting powered by the Tree-sitter Ren'Py grammar
- Auto-indent and bracket matching
- Outline / symbol navigation
- Snippets for common Ren'Py constructs
- LSP-backed language features, including:
  - completion
  - hover
  - diagnostics
  - go-to-definition

## Installation

### Install as a dev extension in Zed

1. Clone this repository locally.
2. Open the repository folder in Zed.
3. Install or load the package using Zed's extension development workflow.
4. Open a Ren'Py project and verify that `.rpy` files are recognized as Ren'Py sources.

### Updating after changes

When you modify the extension, reload or reinstall the dev extension so Zed picks up the latest manifest, queries, snippets, and backend changes.

## Requirements

- Zed
- Rust toolchain for building the extension backend
- Ren'Py SDK if you want LSP or navigation features that depend on the engine's project data

## Configuration

This extension keeps configuration intentionally small. The main behavior is defined in `extension.toml` and the shipped query/snippet files.

Current conventions include:

- `extension.toml` declares the Ren'Py language server and grammar wiring
- `backend.index_path` is set to `./.internal/navigation_index.json`
- navigation data may be read from `game/navigation.json`, `game/navigation_definitions.json`, and `game/navigation_diagnostics.json`, with a fallback to the workspace root

If additional user-facing settings are added later, document them here and in the extension manifest.

## Screenshots

Placeholder screenshot section.

Add example screenshots here once the UI and syntax highlighting are finalized.

## Development

### Build and test

From the repository root:

```bash
cargo fmt --all -- --check
cargo check
cargo test --lib
```

### Zed dev workflow

1. Open the extension package in Zed.
2. Load it in dev mode.
3. Open a sample Ren'Py project.
4. Confirm syntax highlighting, indentation, outline, snippets, and LSP features behave as expected.

See `TESTING.md` for a more detailed manual verification checklist.

### Contributing

Contributions are welcome. Good changes to make include:

- expanding the Tree-sitter grammar
- improving syntax highlighting and injections
- refining snippets
- strengthening navigation and LSP coverage
- adding test fixtures and manual verification samples

Before opening a PR, run the local checks above and update documentation when behavior changes.

## Links

- Zed extension docs: https://zed.dev/
- VS Code extension: https://marketplace.visualstudio.com/items?itemName=renpy.renpy
- Ren'Py documentation: https://www.renpy.org/doc/html/
- Tree-sitter grammar: https://github.com/tree-sitter/tree-sitter-python

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

