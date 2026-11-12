#!/usr/bin/env python3
"""Launch Zed on a private software-rendered Xvfb/Openbox desktop.

No system driver configuration, user Zed profile, or active desktop is changed.
Stop with Ctrl-C; child processes are terminated, while session logs remain.
"""
import argparse
import json
import os
from pathlib import Path
import select
import shutil
import signal
import subprocess
import sys
import sysconfig
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zed", type=Path, required=True, help="zed-editor executable, not a shell alias")
    parser.add_argument("--session-dir", type=Path, required=True, help="new empty directory for this disposable session")
    parser.add_argument("--tools-root", type=Path, help="optional root of locally extracted Debian packages")
    parser.add_argument("--icd-file", type=Path, help="Mesa lavapipe ICD JSON; defaults to lvp_icd*.json")
    parser.add_argument("--built-extension", type=Path, help="optional dist/renpy payload; otherwise install via GUI")
    parser.add_argument("--size", default="1600x1100")
    args = parser.parse_args()
    args.zed = args.zed.resolve()
    if not args.zed.is_file():
        parser.error("--zed must name an existing zed-editor executable")
    session = args.session_dir.resolve()
    if session.exists() and any(session.iterdir()):
        parser.error("--session-dir must be empty; refusing to overwrite an existing profile")
    tools = args.tools_root.resolve() if args.tools_root else None
    multiarch = sysconfig.get_config_var("MULTIARCH")
    if not multiarch:
        parser.error("This launcher currently requires a Debian/Ubuntu-style Linux library layout")
    system_libs = Path("/usr/lib") / multiarch
    library_dirs = ([tools / "usr/lib" / multiarch] if tools else []) + [system_libs]
    icds = ([tools / "usr/share/vulkan/icd.d"] if tools else []) + [Path("/usr/share/vulkan/icd.d")]
    icd = args.icd_file or next((p for directory in icds for p in directory.glob("lvp_icd*.json")), None)
    if icd is None or not icd.is_file():
        parser.error("Mesa lavapipe not found; install/extract mesa-vulkan-drivers or pass --icd-file")

    def executable(name):
        local = tools / "usr/bin" / name if tools else None
        path = str(local) if local and local.is_file() else shutil.which(name)
        if not path:
            parser.error(f"Missing executable: {name}")
        return path

    xvfb, openbox, dbus = executable("Xvfb"), executable("openbox"), executable("dbus-run-session")
    for path in ("home", "config", "data/config", "runtime", "cache", "logs"):
        (session / path).mkdir(parents=True, exist_ok=True)
    (session / "runtime").chmod(0o700)
    project = session / "project"
    shutil.copytree(ROOT / "examples", project)
    (project / ".zed-gui-test-project").write_text("Disposable project created by zed-virtual-display.py\n")
    # Keep Zed from searching unrelated ancestor repositories in a shared scratch area.
    subprocess.run(["git", "init", "--quiet", str(project)], check=True)
    settings = {
        "auto_update": False, "disable_ai": True,
        "telemetry": {"diagnostics": False, "metrics": False},
        "theme": "One Dark", "buffer_font_family": "DejaVu Sans Mono",
        "buffer_font_size": 18, "ui_font_size": 16, "vim_mode": False,
        "restore_on_startup": "none",
        "lsp": {"renpy-language-server": {"binary": {
            "path": sys.executable,
            "arguments": [str(ROOT / "scripts/lsp-trace.py"), str(session / "lsp.jsonl"),
                          str(ROOT / "server/target/release/renpy-language-server")], "env": {},
        }}},
    }
    (session / "data/config/settings.json").write_text(json.dumps(settings, indent=2) + "\n")
    if args.built_extension:
        payload = args.built_extension.resolve()
        for name in ("extension.toml", "extension.wasm", "grammars/renpy.wasm"):
            if not (payload / name).is_file():
                parser.error(f"Incomplete built extension: missing {name}")
        shutil.copytree(payload, session / "data/extensions/installed/renpy")

    real_home = Path.home()
    env = {**os.environ,
           "HOME": str(session / "home"), "WAYLAND_DISPLAY": "",
           "XDG_CONFIG_HOME": str(session / "config"),
           "XDG_DATA_HOME": str(session / "xdg-data"),
           "XDG_CACHE_HOME": str(session / "cache"),
           "XDG_RUNTIME_DIR": str(session / "runtime"),
           "VK_DRIVER_FILES": str(icd.resolve()), "VK_ICD_FILENAMES": str(icd.resolve()),
           "LD_LIBRARY_PATH": os.pathsep.join(map(str, library_dirs)),
           "DISABLE_WSI_LAYER": "1", "LIBGL_ALWAYS_SOFTWARE": "1",
           "MESA_LOADER_DRIVER_OVERRIDE": "llvmpipe", "GALLIUM_DRIVER": "llvmpipe",
           "GPUI_X11_SCALE_FACTOR": "1", "ZED_ALLOW_EMULATED_GPU": "1",
           "CARGO_HOME": os.environ.get("CARGO_HOME", str(real_home / ".cargo")),
           "RUSTUP_HOME": os.environ.get("RUSTUP_HOME", str(real_home / ".rustup"))}
    if os.geteuid() == 0:
        env["ZED_ALLOW_ROOT"] = "true"  # Only this isolated profile, never the user's Zed data.
    if tools:
        env["XDG_DATA_DIRS"] = str(tools / "usr/share") + ":/usr/local/share:/usr/share"
    env["PATH"] = str(Path(env["CARGO_HOME"]) / "bin") + os.pathsep + env.get("PATH", "")
    if env.get("WASI_SDK_PATH") and not (Path(env["WASI_SDK_PATH"]) / "bin/clang").is_file():
        env.pop("WASI_SDK_PATH")  # Let Zed download a usable SDK instead.
    processes = []
    log_files = []

    def stop(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    def launch(command, name, **kwargs):
        log = (session / "logs" / f"{name}.log").open("wb")
        log_files.append(log)
        process = subprocess.Popen(command, env=env, start_new_session=True,
                                   stderr=log, stdout=kwargs.pop("stdout", log), **kwargs)
        processes.append(process)
        return process

    try:
        display = launch([xvfb, "-displayfd", "1", "-screen", "0", args.size + "x24",
                          "-dpi", "96", "-nolisten", "tcp", "-ac"], "xvfb", stdout=subprocess.PIPE)
        assert display.stdout is not None
        if not select.select([display.stdout], [], [], 10)[0]:
            raise RuntimeError("Xvfb did not return a display number; inspect logs/xvfb.log")
        number = display.stdout.readline().decode().strip()
        if not number.isdecimal():
            raise RuntimeError(f"Xvfb failed: {number!r}; inspect logs/xvfb.log")
        env["DISPLAY"] = ":" + number
        wm_args = [openbox]
        config = tools / "etc/xdg/openbox/rc.xml" if tools else Path("/etc/xdg/openbox/rc.xml")
        if config.is_file():
            wm_args += ["--config-file", str(config)]
        wm = launch(wm_args, "openbox")
        # A window manager must be ready before Zed opens a window.
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if wm.poll() is not None:
                raise RuntimeError("Openbox failed; inspect logs/openbox.log for missing dependencies")
            check = subprocess.run([executable("xprop"), "-root", "_NET_SUPPORTING_WM_CHECK"],
                                   env=env, capture_output=True, text=True)
            if "window id" in check.stdout:
                break
            time.sleep(.1)
        else:
            raise RuntimeError("Openbox did not claim the virtual display")
        zed = launch([dbus, "--", str(args.zed), "--user-data-dir", str(session / "data"),
                      str(project), str(project / "game/script.rpy")], "zed-process")
        details = {"display": env["DISPLAY"], "project": str(project), "trace": str(session / "lsp.jsonl"),
                   "data": str(session / "data"), "icd": str(icd.resolve()), "zed": str(args.zed)}
        (session / "session.json").write_text(json.dumps(details, indent=2) + "\n")
        print(json.dumps(details, indent=2), flush=True)
        print("Trust only this disposable project in Zed; cancel any keyring prompt. Ctrl-C stops the session.", flush=True)
        return zed.wait()
    except KeyboardInterrupt:
        return 0
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
        for log in log_files:
            log.close()


if __name__ == "__main__":
    sys.exit(main())
