# renpy-tree-sitter

Tree-sitter grammar for [Ren'Py](https://www.renpy.org) scripts, used by the
[`renpy-zed`](https://github.com/rockettap/renpy-zed) Zed extension.

This repository is standalone: Zed clones it at a pinned revision when the
extension is installed, then compiles `src/parser.c` directly. It never runs
`tree-sitter generate`, so the generated files in `src/` must stay committed.

## Provenance

The grammar started from
[`ZeynTheDev/tree-sitter-renpy`](https://github.com/ZeynTheDev/tree-sitter-renpy)
at commit `8a98470c0eba8d9c41d12e5a75118fa6aed4cfb7` (v0.4.0, MIT), was
extended by [`Ozicom23/zed-renpy`](https://github.com/Ozicom23/zed-renpy) at
commit `333e6167b4fbd8397ee6a09a0122d929dc5b5c5d`, and is maintained here from
that point.

Original copyright: Copyright (c) 2026 M. A. Azzam. See [LICENSE](LICENSE).
The smoke example is adapted from `Ozicom23/zed-renpy` (MIT).

## Layout

- `grammar.js` — the grammar definition (edit this)
- `src/scanner.c` — external scanner handling `INDENT`/`DEDENT`/`NEWLINE`
  (including several DEDENTs for one line, trailing whitespace, blank lines and
  a missing final newline), `python_content`, which spans a Python _logical_
  line (it continues across newlines inside open brackets and triple-quoted
  strings), and `bracketed`, one balanced bracket group with the same
  multi-line rules
- `src/parser.c`, `src/grammar.json`, `src/node-types.json` — **generated** by
  the tree-sitter CLI; must be committed
- `test/corpus/` — `tree-sitter test` cases
- `examples/smoke.rpy` — a file that exercises every supported construct

## Coverage

Beyond the v0.4.0 statements (labels, dialogue, menus, images, audio, python,
conditionals), the grammar parses:

- screens (`screen`, `show/hide/call screen`), transforms and ATL blocks on
  `show`/`scene`/`image`/`camera`, styles, layered images and testcases. Their
  bodies share one generic line shape, `element`: a name, arguments, and an
  optional `:` block. Queries tell keywords from properties by name.
- translations: `translate <lang> <id>:`, `strings:` (`old`/`new`), `python:`
  and `style`.
- strings parsed into `interpolation` (`[name]`), `text_tag` (`{b}`) and
  `escape_sequence` (`\n`, `[[`, `{{`) parts.
- `nvl clear/show/hide`, `init offset`, `init <priority> <statement>`,
  `python early`, `id` clauses on dialogue, translated speaker names
  (`_("Name") "..."`).
- creator-defined statements (`user_statement`), chosen only when no built-in
  statement parses the line.

## Development

```bash
# generate src/parser.c after editing grammar.js or src/scanner.c
npx --yes tree-sitter-cli@0.25.10 generate

# run the corpus tests
npx --yes tree-sitter-cli@0.25.10 test

# parse the smoke fixture; expect no ERROR nodes
npx --yes tree-sitter-cli@0.25.10 parse examples/smoke.rpy
```

The external scanner is the only hand-written C file. Format it and check it
with the same commands CI uses:

```bash
clang-format -i src/scanner.c
clang-format --dry-run --Werror src/scanner.c

clang -fsyntax-only -Isrc -std=c11 \
  -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror \
  src/scanner.c

clang-tidy src/scanner.c -- -Isrc -std=c11
```

`.clang-format` and `.clang-tidy` apply here; do not format the generated
`src/parser.c` or the vendored `src/tree_sitter/*.h` files.

`src/parser.c` is generated with tree-sitter CLI `0.25.10`. CI regenerates it
and fails if the committed output differs.

When changing node names or fields, update the query files in the Zed extension
repository (`languages/renpy/*.scm`) at the same time. A stale node name makes
the whole query fail to compile, and Zed then renders no highlighting at all.

## License

MIT. See [LICENSE](LICENSE).
