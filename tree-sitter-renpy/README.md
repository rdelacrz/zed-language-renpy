# tree-sitter-renpy

Tree-sitter grammar package for the Ren'Py Zed extension.

This subdirectory is the **syntax layer only**. It parses Ren'Py source into syntax nodes that Zed can use for editor-native features.

## What it supports in Zed

- syntax highlighting
- bracket matching / pairing
- indentation
- outline / symbol view
- injections for embedded Python blocks
- syntax overrides such as completion query characters
- structural support for snippets and other query-driven editor behavior

## Exact file-to-feature map

### `grammar.js`
Main Tree-sitter grammar source.

Used by Zed for:
- parsing Ren'Py statements, expressions, blocks, identifiers, and punctuation
- generating node types used by the query files
- keeping highlight / outline / indent / injection queries aligned with the grammar

### `src/parser.c`
Generated parser output from Tree-sitter.

Used by Zed for:
- runtime parsing of Ren'Py files

### `src/scanner.c`
Generated external scanner.

Used by Zed for:
- custom tokenization that the grammar needs but a pure grammar cannot express

### `src/node-types.json`
Generated node catalog.

Used by Zed for:
- authoring and validating Tree-sitter queries
- keeping highlight, outline, indent, and injection queries aligned with real node names

### `src/grammar.json`
Generated grammar metadata.

Used by Zed for:
- parser generation artifact
- debugging grammar output

### `tree-sitter.json`
Tree-sitter package manifest.

Used by Zed for:
- grammar package metadata
- build/toolchain discovery for the grammar package

### `test.js`
Tree-sitter grammar tests.

Used by Zed for:
- validating the grammar before the extension consumes it

### `package.json`, `package-lock.json`
Node package metadata and lockfile for the grammar toolchain.

Used by Zed for:
- local grammar build and test dependencies

## Relationship to `languages/renpy/`

The files under `languages/renpy/` consume this grammar through Tree-sitter queries:

- `highlights.scm` → syntax highlighting
- `outline.scm` → symbol tree / outline
- `indents.scm` → block indentation
- `brackets.scm` → bracket pairing
- `injections.scm` → embedded Python handling
- `overrides.scm` → query/completion behavior tweaks
- `config.toml` → file association and editor settings

## Relationship to the Rust backend

The Rust backend in `src/lib.rs` handles project-aware features that the grammar alone cannot provide, such as JSON-backed completions, go-to-definition, and diagnostics.

## Practical note

The grammar is Ren'Py-shaped but still close to Python in a few places. That is intentional for now: it gives Zed a useful syntax surface while keeping the backend split narrow.
