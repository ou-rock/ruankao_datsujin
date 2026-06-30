from __future__ import annotations

import pytest

from ruankao_agent.web_files import (
    WorkbenchFileContext,
    render_learning_file,
    safe_export_file,
    safe_learning_file,
)


def test_learning_file_renderer_initializes_before_reading(tmp_path) -> None:
    root = tmp_path / "demo"
    learning_path = root / "learning"
    reports_path = root / "reports"
    exports_path = root / "exports"

    initialized = []

    def initialize() -> None:
        initialized.append(True)
        learning_path.mkdir(parents=True, exist_ok=True)
        (learning_path / "index.html").write_text("<h1>学习台</h1>", encoding="utf-8")

    context = WorkbenchFileContext(
        root=root,
        learning_path=learning_path,
        reports_path=reports_path,
        exports_path=exports_path,
        initialize=initialize,
    )

    assert render_learning_file(context) == "<h1>学习台</h1>"
    assert initialized == [True]


def test_safe_file_lookup_rejects_parent_directory_escape(tmp_path) -> None:
    root = tmp_path / "demo"
    learning_path = root / "learning"
    learning_path.mkdir(parents=True)
    (tmp_path / "outside.html").write_text("outside", encoding="utf-8")
    context = WorkbenchFileContext(
        root=root,
        learning_path=learning_path,
        reports_path=root / "reports",
        exports_path=root / "exports",
        initialize=lambda: None,
    )

    with pytest.raises(PermissionError):
        safe_learning_file(context, "../outside.html")


def test_safe_file_lookup_reports_missing_files(tmp_path) -> None:
    root = tmp_path / "demo"
    context = WorkbenchFileContext(
        root=root,
        learning_path=root / "learning",
        reports_path=root / "reports",
        exports_path=root / "exports",
        initialize=lambda: None,
    )

    with pytest.raises(FileNotFoundError):
        safe_export_file(context, "state-2026-06-30.json")
