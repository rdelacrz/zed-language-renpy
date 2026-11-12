#!/usr/bin/env python3
"""Transparent stdio LSP recorder for isolated GUI tests; never logs on stdout.

Usage: python3 scripts/lsp-trace.py LOG.jsonl /absolute/path/to/server [args...]
Only use with disposable test projects: the trace includes document contents.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time


def main():
    log_path = Path(sys.argv[1])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    server = subprocess.Popen(sys.argv[2:], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=sys.stderr)
    assert server.stdin is not None and server.stdout is not None
    lock = threading.Lock()
    with log_path.open("a", buffering=1) as log:
        def forward(source, destination, direction):
            try:
                while True:
                    headers = bytearray()
                    length = None
                    while True:
                        line = source.readline()
                        if not line:
                            return
                        headers.extend(line)
                        if line in (b"\r\n", b"\n"):
                            break
                        key, value = line.split(b":", 1)
                        if key.lower() == b"content-length":
                            length = int(value.strip())
                    if length is None or not 0 <= length <= 64 * 1024 * 1024:
                        raise ValueError("Invalid Content-Length from LSP transport")
                    body = bytearray()
                    while len(body) < length:
                        part = source.read(length - len(body))
                        if not part:
                            raise EOFError("Truncated LSP frame")
                        body.extend(part)
                    message = json.loads(body)
                    with lock:
                        log.write(json.dumps({"time": time.time(), "direction": direction,
                                              "message": message}, ensure_ascii=False) + "\n")
                    destination.write(headers + body)
                    destination.flush()
            except (BrokenPipeError, OSError):
                pass
            finally:
                if direction == "client_to_server":
                    destination.close()

        incoming = threading.Thread(target=forward, args=(sys.stdin.buffer, server.stdin, "client_to_server"), daemon=True)
        outgoing = threading.Thread(target=forward, args=(server.stdout, sys.stdout.buffer, "server_to_client"), daemon=True)
        incoming.start()
        outgoing.start()
        code = server.wait()
        outgoing.join(timeout=2)
        log.flush()
    # The client may keep stdin open after exit. Do not wait for its reader thread.
    os._exit(code if code >= 0 else 1)


if __name__ == "__main__":
    main()
