# Third-party sources

## Tree-sitter grammar

`tree-sitter-renpy/` vendors
[rockettap/renpy-tree-sitter](https://github.com/rockettap/renpy-tree-sitter)
at **0e9ea0d0dcb8860ea1d5f3ac6356855bf58cc556**. The manifest fetches that exact
revision. `grammar.js`, `src/`, corpus tests, and the upstream smoke example
are unmodified; local package metadata pins the CLI for reproducibility.

The grammar originated in ZeynTheDev/tree-sitter-renpy and was extended by
Ozicom23/zed-renpy and rockettap. Its MIT license and original notice,
Copyright (c) 2026 M. A. Azzam, are retained in `tree-sitter-renpy/LICENSE`.

The Zed query implementation was informed by the documented node contract
and by [rockettap/renpy-zed](https://github.com/rockettap/renpy-zed) at
9af837eb7bb3d53cc9bd42c965dcbd663cc5d4ff. Its license notice is retained below.
No debugger, task execution, SDK discovery, or server-installation code from
that extension is included here.

## Language server

`server/` is the existing
[rdelacrz/renpy-lsp-server](https://github.com/rdelacrz/renpy-lsp-server)
submodule at **91d66e0c96a90674d817907cffd2e189cf02969a**. This published commit
includes the integration fixes previously carried as a local compatibility
patch. Fresh clones use the server directly without applying patches.
The server's README describes its embedded Ren'Py API data sources.

This notice does not assign a license to the original extension/server.
Their repository owner should choose/confirm licenses and audit the inherited
snippet/API-data attribution before marketplace publication.

## Reference extension license

MIT License

Copyright (c) 2026 Oleksandr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
