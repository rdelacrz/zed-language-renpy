# Ren'Py Language for Zed

Work-in-progress Zed extension for Ren'Py.

Disclaimer: if this extension summons a curse, eats your GPU, or launches your laptop into the sun, please remember: this is a chaotic vibe-coded gremlin artifact, forged with love, hubris, and questionable snacks.

## Features
- Ren'Py file association for `.rpy`, `.rpym`, `.rpymc`, `.rpyc`
- Python-based syntax highlighting via Tree-sitter Python
- Ren'Py snippets
- Basic outline and bracket support

## Navigation JSON producer

The backend reads three JSON artifacts from either `game/` or the workspace root:

- `navigation.json`
- `navigation_definitions.json`
- `navigation_diagnostics.json`

### Format

- `navigation.json`: object with optional `name`, `version`, and arrays for `labels`, `screens`, `transforms`, `audio`, `config_keys`, `renpy_keys`, `gui_keys`
- `navigation_definitions.json`: array of `{ kind, name, file, line, column }`
- `navigation_diagnostics.json`: array of `{ severity, message, file, line, column }`

### Sample producer

A small fixture-driven producer lives at:

- `tools/sample_navigation_producer.py`

It reads `src/navigation-fixture.json` and writes the three navigation files.

Usage:

```bash
python3 tools/sample_navigation_producer.py --fixture src/navigation-fixture.json --out-dir game
```

To refresh the extension's cached navigation index from `navigation.json`, use the slash command:

```text
/renpy.refresh_index
```

## Testing

See `TESTING.md` in the package root for step-by-step instructions to test the extension in Zed dev-mode and run local checks (`cargo test`, `cargo check`).

### Notes

This producer is intentionally minimal. It is good for local refreshes and test fixtures, but it does not scan a live Ren'Py workspace yet.

## Notes
This first pass uses Python grammar as the parser base because Ren'Py is Python-like and Zed needs a Tree-sitter grammar. Next step is to replace this with a Ren'Py-specific grammar if needed and expand support for Ren'Py-specific syntax such as screen language, ATL, and injections.
