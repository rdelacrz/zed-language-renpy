# Ren'Py Language for Zed

Work-in-progress Zed extension for Ren'Py.

Disclaimer: if this extension summons a curse, eats your GPU, or launches your laptop into the sun, please remember: this is a chaotic vibe-coded gremlin artifact, forged with love, hubris, and questionable snacks.

## Features
- Ren'Py file association for `.rpy`, `.rpym`, `.rpymc`, `.rpyc`
- Python-based syntax highlighting via Tree-sitter Python
- Ren'Py snippets
- Basic outline and bracket support

## Notes
This first pass uses Python grammar as the parser base because Ren'Py is Python-like and Zed needs a Tree-sitter grammar. Next step is to replace this with a Ren'Py-specific grammar if needed and expand support for Ren'Py-specific syntax such as screen language, ATL, and injections.
