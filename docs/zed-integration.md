# How this integration works

## Zed's language stack

1. `extension.toml` registers the extension, grammar repository/revision,
   language servers, and snippet paths. Top-level TOML keys must occur before
   table headers; the old `snippets` entry was accidentally inside the grammar
   table. `rev` is the documented grammar key (`commit` remains a supported
   legacy alias in Zed's source).
2. `languages/renpy/config.toml` maps suffixes to the display name `Ren'Py` and
   grammar `renpy`. That display name must match the server's language list.
   `language_ids` explicitly maps it to LSP `renpy`.
3. Zed clones the grammar's real Git repository at the pinned revision and
   compiles its generated C parser plus external scanner to WASM with wasi-sdk.
   It does not run `tree-sitter generate` and does not automatically consume the
   vendored `tree-sitter-renpy/` directory.
4. Zed compiles Rust extension code to `wasm32-wasip2`. The sandboxed component
   resolves the native LSP using worktree settings and `worktree.which`, not
   the WASM process's own environment. The editor spawns the command and handles
   JSON-RPC/stdio communication.
5. Tree-sitter queries independently power highlights, outlines, indentation,
   injections, brackets, scopes, and text objects. A query containing a stale
   node name can fail entirely even when the Rust extension builds.
6. Snippet files match the lowercase language display name, including punctuation:
   `Ren'Py` needs `ren'py.json`. Literal dollars must be escaped in snippet bodies;
   otherwise Zed interprets them as tabstop starts. Loading the extension in the
   actual GUI exposed both issues, now covered by regression tests.

## Decisions

- Keep Zed extension API `0.6.0`; the authoritative compatibility table lists
  support starting at Zed 0.192.
- Replace the original opaque-block grammar with the pinned MIT-licensed
  `rockettap/renpy-tree-sitter` parser. Its external scanner handles indentation,
  dedentation, missing final newlines, multiline bracket groups, and Python
  logical lines. Real Ren'Py example scripts are part of the verification.
- Keep Python injections distinct from Ren'Py `init:` blocks. Inject complete
  Python blocks together, rather than losing function/class context by treating
  every physical line as a separate Python source file.
- Keep the native Rust server, but patch failures found by exercising editor
  behavior: trailing-dot completion, middle-of-name hover/navigation, unsupported
  lookaround regexes in references, UTF-16 symbol ranges, workspace indexing,
  stale disk/open-buffer state, and stdio exit handling.
- Do not advertise unimplemented semantic tokens: doing so could cause users
  enabling semantic-only highlighting to lose the working Tree-sitter colors.
- No invented download URL: upstream has no binary releases. Build the pinned
  server locally, with a settings fragment generated for its actual path.
- Publish server fixes in the server repository before updating the parent
  submodule pin. The build helper verifies the pinned revision and no longer
  applies a compatibility patch.

## Authoritative references consulted

- [Zed extension development](https://zed.dev/docs/extensions/developing-extensions)
- [Zed language extensions and query captures](https://zed.dev/docs/extensions/languages)
- [Zed snippet extension filename rules](https://zed.dev/docs/extensions/snippets)
- [Extension API and Zed compatibility](https://github.com/zed-industries/zed/tree/main/crates/extension_api)
- [Manifest schema](https://github.com/zed-industries/zed/blob/main/crates/extension/src/extension_manifest.rs)
- [Zed extension builder: Rust/WASI and grammar compilation](https://github.com/zed-industries/zed/blob/main/crates/extension/src/extension_builder.rs)
- [Grammar source](https://github.com/rockettap/renpy-tree-sitter/tree/0e9ea0d0dcb8860ea1d5f3ac6356855bf58cc556)
- [Native language server](https://github.com/rdelacrz/renpy-lsp-server/tree/91d66e0c96a90674d817907cffd2e189cf02969a)
- [Official Ren'Py example](https://github.com/renpy/renpy/tree/ac8054a5c326011529894c0fc6e8fc8fff294ea2/the_question/game)
- [LSP specification](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/)

See `THIRD_PARTY_NOTICES.md` for source provenance and licenses.
