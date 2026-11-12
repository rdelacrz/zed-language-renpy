# Zed GUI verification on a virtual display

## Root cause of the original failure

The final `X11 connection: Unsupported extension` message was not the primary
failure. Zed's log shows this sequence on the original Xvfb session:

1. The only installed Vulkan ICD was the proprietary Mali driver. Its surface
   capability query failed with `ERROR_SURFACE_LOST_KHR` on Xvfb.
2. Zed tried its OpenGL llvmpipe fallback, but EGL window-surface creation failed
   with `BadAlloc`, followed by `Invalid surface`.
3. Cleanup then failed with the reported X11 error, obscuring those renderer
   failures. Zed's `gpui_linux/.../x11/window.rs` checks `destroy_window` when
   window setup fails, explaining the misleading final error.

Xvfb did not advertise DRI3. The host's loader cache also puts CIX compatibility
GL/EGL libraries ahead of the distribution Mesa libraries; default `glxinfo`
failed trying Zink/DRI3. With a process-local Mesa library path and software
renderer selection, `glxinfo` succeeded with llvmpipe. Installing nothing
system-wide, an extracted Mesa lavapipe Vulkan ICD provided a working Xvfb
surface. Zed then selected **llvmpipe (LLVM 20.1.2, 128 bits), Vulkan** and logged
**Rendered first frame**.

This establishes a working software path, not that the physical Mali GPU or
normal Wayland desktop is broken. No `/etc` driver configuration, display
manager, system graphics packages, or user Zed settings were changed.

## Working configuration

- Xvfb with a 24-bit screen and TCP listening disabled.
- Openbox running **before Zed**, for reliable activation, focus, geometry,
  and repainting. Xvfb alone was insufficient for reliable GUI automation.
- Mesa lavapipe explicitly selected with `VK_DRIVER_FILES` /
  `VK_ICD_FILENAMES`, pointing at `lvp_icd.json`.
- `LD_LIBRARY_PATH` scoped to the extracted Mesa libraries and the distribution's
  architecture-specific library directory, ahead of CIX compatibility libraries.
- `DISABLE_WSI_LAYER=1` disables the host's Mali-specific implicit Vulkan layer
  only in the test process.
- `LIBGL_ALWAYS_SOFTWARE=1`, `MESA_LOADER_DRIVER_OVERRIDE=llvmpipe`, and
  `GALLIUM_DRIVER=llvmpipe` keep the fallback renderer software-only.
- `ZED_ALLOW_EMULATED_GPU=1` accepts Zed's software-GPU warning.
- Isolated `HOME`, XDG directories, D-Bus session, and `--user-data-dir`.
  `ZED_ALLOW_ROOT=true` is used only when this isolated test runs as root.
- Disposable copies of `examples/`, not edits to the real project fixtures.

`scripts/zed-virtual-display.py` implements this configuration, records its
selected display/project/trace paths in `session.json`, and shuts down its child
process groups on Ctrl-C. It refuses a nonempty session directory. The X server
uses `-ac` for test automation; it has no TCP listener, but other local users can
access the test display. Do not use this setup for private documents or on a
shared untrusted machine.

## Reproduce

On a Debian/Ubuntu desktop or CI host, requirements are Xvfb, Openbox, Mesa
Vulkan drivers (lavapipe), D-Bus, xprop, xdotool, xclip, and Tesseract. For Python:

```sh
uv pip install --python .venv/bin/python -r tests/gui-requirements.txt
```

The investigation downloaded Debian packages and extracted them under
`target/gui-tools/`, instead of installing or replacing system drivers:
`mesa-vulkan-drivers`, `openbox`, `libobrender32v5`, `libobt2v5`, `libimlib2t64`,
`xdotool`, `libxdo3`, and `xclip`. Their other shared-library dependencies were
already installed. The downloaded Zed archive was extracted there too. These
ignored artifacts are local tools, not part of the extension package.

```sh
.venv/bin/python scripts/zed-virtual-display.py \
  --zed target/gui-tools/zed.app/libexec/zed-editor \
  --tools-root target/gui-tools \
  --session-dir "$TMPDIR/zed-renpy-gui-session"
```

With system-installed dependencies, omit `--tools-root` and supply the installed
`zed-editor` path. Use `--icd-file` if the lavapipe manifest is elsewhere. The
launcher targets the Debian/Ubuntu library layout used for this verification.

Trust **only** the copied project in Zed, cancel any keyring prompt, then use
**zed: install dev extension** to select this repository. The GUI dev installer
was exercised: Zed fetched/compiled the grammar, built the extension component,
and displayed **Ren'Py v0.1.0 (dev)** with Rebuild/Uninstall controls.

For a repeatable payload smoke test after `scripts/build.py --package`, add
`--built-extension dist/renpy`; this installs a copy in the disposable profile,
not in the user's extension directory. This option does not exercise the dev
installer itself.

The launcher configures a transparent `scripts/lsp-trace.py` recorder between
Zed and the **real native server**. The trace contains test document contents;
use it only with disposable fixtures. It emits no extra stdout. The ordinary
11 stdio LSP tests also pass through the recorder.

After installation, restart the language server from the command palette if
Zed stopped it during extension reload. Use the display/project/trace values
from the launcher's `session.json`:

```sh
LD_LIBRARY_PATH="$PWD/target/gui-tools/usr/lib/aarch64-linux-gnu:/usr/lib/aarch64-linux-gnu" \
.venv/bin/python scripts/test-zed-gui.py \
  --display :DISPLAY_NUMBER \
  --project "$TMPDIR/zed-renpy-gui-session/project" \
  --trace "$TMPDIR/zed-renpy-gui-session/lsp.jsonl" \
  --output target/gui-verification/clean \
  --xdotool target/gui-tools/usr/bin/xdotool \
  --xclip target/gui-tools/usr/bin/xclip
```

Adjust the architecture-specific library directory on x86_64. With system
packages, omit the library override and executable overrides. The tester
requires the launcher's disposable-project marker and refuses to overwrite an
existing probe unless `--reuse-probe` is explicitly supplied. `--only` permits
focused retries while retaining other results for the same session.

## What the GUI tests exercise

The test driver sends actual keyboard/mouse/clipboard input to Zed. It records
PNG screenshots, OCR text, saved buffer contents, and actual Zed-originated LSP
requests/responses. No synthetic LSP results are used.

1. Syntax colors: Ren'Py keywords and strings have distinct One Dark colors.
2. Outline: screen `hud`, transform `fade_in`, and label `start` appear.
3. F12 definition: jumps to `chapter_two.rpy` before that file has been opened.
4. `renpy.` completion: displays real API items, including `pause`.
5. `renpy.music.` completion: includes `play`, not a duplicated `music.play`.
6. Hover: documentation appears with the cursor inside `renpy.pause`.
7. Enter after a colon indents four spaces; opening parentheses auto-close.
8. `rpause` snippet expands into `$ renpy.pause(0.5)` with working tabstops.
9. Invalid-variable diagnostics appear in Zed's diagnostics view and clear after
   fixing the document.

## Bugs found only by loading the extension in Zed

- Seven Python-statement snippets had unescaped literal dollars, causing
  `failed to parse snippet: expected an integer`. Those dollars are now escaped
  at the snippet level, while numeric tabstops remain unchanged.
- `snippets/renpy.json` did not match the language's lowercase display name,
  `ren'py`. It was renamed to `snippets/ren'py.json` and the manifest updated.
  Otherwise even valid snippets never appeared in a Ren'Py buffer.

`tests/test_snippets.py` now guards both issues. After rebuilding in Zed, the
snippet errors disappeared and actual GUI expansion passed.

Evidence is in `target/gui-verification/`, including feature reports,
screenshots, OCR transcripts, and the recorded Zed/LSP logs. Setup attempts are
retained separately from successful feature checks. Keyring cancellation,
no physical XInput mouse, and missing optional local AI providers can produce
unrelated startup messages in a virtual desktop; this is not a claim of zero
messages across all of Zed. Physical-GPU performance, other display backends,
Windows/macOS, and marketplace distribution are not covered.

## References

- https://zed.dev/docs/linux#graphics-issues
- https://zed.dev/docs/extensions/snippets
- https://github.com/zed-industries/zed/blob/c84af5b99cbc366d675064e52b23664a015b6e35/crates/gpui_linux/src/linux/x11/window.rs
- https://github.com/zed-industries/zed/blob/c84af5b99cbc366d675064e52b23664a015b6e35/crates/gpui_wgpu/src/wgpu_context.rs
