from __future__ import annotations

import errno
import webbrowser
from datetime import date
from http.server import ThreadingHTTPServer
from pathlib import Path

from .web_app import WorkbenchApp, WorkbenchConfig
from .web_handlers import (
    _export_relative_path,
    _handler_for,
    _learning_relative_path,
    _report_relative_path,
    _vault_relative_path,
)


def serve_workbench(
    root: Path,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    as_of: date | None = None,
    open_browser: bool = False,
) -> None:
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=as_of))
    app.initialize()
    handler_cls = _handler_for(app)
    server = _bind_workbench_server(host, port, handler_cls)
    url = f"http://{host}:{server.server_port}/"
    print(_workbench_launch_message(url), flush=True)
    if open_browser:
        webbrowser.open(url)
    server.serve_forever()


def _bind_workbench_server(
    host: str,
    port: int,
    handler_cls,
    *,
    attempts: int = 20,
) -> ThreadingHTTPServer:
    if port == 0:
        return ThreadingHTTPServer((host, port), handler_cls)
    last_error: OSError | None = None
    stop = min(65536, port + max(1, attempts))
    for candidate in range(port, stop):
        try:
            return ThreadingHTTPServer((host, candidate), handler_cls)
        except OSError as exc:
            if exc.errno != errno.EADDRINUSE:
                raise
            last_error = exc
    if last_error is not None:
        raise last_error
    raise OSError(f"Cannot bind workbench server from port {port}")


def _workbench_launch_message(url: str) -> str:
    return f"软考达人工作台已启动：{url}\n按 Ctrl-C 停止。"
