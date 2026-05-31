# Testing Ren'Py Zed extension

This file explains how to test the extension in Zed IDE and locally.

## What can be tested here

- Ren'Py file association
- syntax highlighting
- bracket matching / indentation
- outline / structure view
- embedded Python injections
- snippets
- backend slash commands backed by JSON files
- Rust unit tests

## Local checks first

Run these from `renpy-zed-extension/`:

```bash
cargo fmt --all -- --check
cargo check
cargo test --lib
```

Expected result:
- `cargo fmt` passes or reports only formatting changes
- `cargo check` passes
- `cargo test --lib` passes

## Test in Zed IDE

### 1) Open the extension in Zed dev mode

- Open the `renpy-zed-extension/` package in Zed.
- Load the extension in Zed dev mode.
- Make sure Zed recognizes the package without load errors.

If the extension fails to load:
- check the Zed developer console / logs
- verify the Rust backend builds cleanly with the commands above

### 2) Open a Ren'Py file

Open a `.rpy` file in a Ren'Py project.

Check that Zed treats it as Ren'Py and not plain text.

### 3) Verify syntax highlighting

Look for:
- keyword coloring on Ren'Py statements
- correct token coloring in dialogue lines
- embedded Python areas highlighted as Python where expected
- no obvious syntax breakage around blocks, strings, or labels

### 4) Verify bracket matching and indentation

Type or inspect:
- `if` / `else` blocks
- `menu:` blocks
- `label` blocks
- `python:` or `init python:` blocks

Check that:
- brackets pair correctly
- indentation follows block structure
- inserting new lines inside blocks behaves sensibly

### 5) Verify outline / symbol view

Open the outline panel or symbol view.

Check that it shows useful Ren'Py structure such as:
- labels
- screens
- transforms
- other grammar-derived symbols

### 6) Verify snippets

Try typing known snippet triggers from `snippets/snippets.json`.

Check that:
- completions appear
- snippet expansion inserts the expected template
- removed or stale snippets do not appear

### 7) Verify backend commands if JSON inputs exist

The backend reads these files from the project:

- `game/navigation.json`
- `game/navigation_definitions.json`
- `game/navigation_diagnostics.json`

It also falls back to the project root if needed.

If your project has these files, test the slash commands:

- `renpy.refresh_index`
- `renpy.completions`
- `renpy.definition`
- `renpy.diagnostics`

Expected behavior:
- `renpy.refresh_index` returns a compact JSON copy of the index
- `renpy.completions` returns matching completion candidates
- `renpy.definition` returns matching definition locations
- `renpy.diagnostics` returns matching diagnostics

If those files are missing, the commands should return empty results or a clear "not found" style response rather than crash.

## Suggested manual test file

Use a small `.rpy` file with content like this:

```renpy
label start:
    scene bg room
    "Hello, world."

    menu:
        "Go on":
            jump next_scene

init python:
    x = 1
```

This gives you a simple way to check:
- labels
- dialogue
- menus
- indentation
- Python injection

## What to record

If a test fails, record:
- the exact file tested
- the command or action taken
- the error or bad behavior observed
- whether the issue is syntax/query/backend related

Put durable test notes in `.tasks/TESTING_PROGRESS.md`.

## Known gap

Live Zed verification cannot be fully automated from this repo alone. If the Zed dev-mode session is not available, record that as unverified rather than guessing.
