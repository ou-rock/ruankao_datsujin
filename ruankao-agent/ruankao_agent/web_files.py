from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class WorkbenchFileContext:
    root: Path
    learning_path: Path
    reports_path: Path
    exports_path: Path
    initialize: Callable[[], None]


def render_dashboard_page(context: WorkbenchFileContext) -> str:
    context.initialize()
    return (context.root / "dashboard.html").read_text(encoding="utf-8")


def render_learning_file(
    context: WorkbenchFileContext,
    relative: str = "index.html",
) -> str:
    context.initialize()
    return safe_learning_file(context, relative).read_text(encoding="utf-8")


def render_report_file(context: WorkbenchFileContext, relative: str) -> str:
    return safe_report_file(context, relative).read_text(encoding="utf-8")


def render_export_file(context: WorkbenchFileContext, relative: str) -> str:
    return safe_export_file(context, relative).read_text(encoding="utf-8")


def safe_learning_file(context: WorkbenchFileContext, relative: str) -> Path:
    return _safe_child_file(context.learning_path, relative)


def safe_report_file(context: WorkbenchFileContext, relative: str) -> Path:
    return _safe_child_file(context.reports_path, relative)


def safe_export_file(context: WorkbenchFileContext, relative: str) -> Path:
    return _safe_child_file(context.exports_path, relative)


def _safe_child_file(root: Path, relative: str) -> Path:
    resolved_root = root.resolve()
    target = (resolved_root / relative).resolve()
    if resolved_root not in target.parents and target != resolved_root:
        raise PermissionError(relative)
    if not target.exists() or not target.is_file():
        raise FileNotFoundError(relative)
    return target
