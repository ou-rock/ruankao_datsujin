from __future__ import annotations

import subprocess
import sys

from ruankao_agent.learning import ensure_learning_resources


def test_learning_resources_generate_html_study_desk(tmp_path) -> None:
    root = tmp_path / "demo"

    learning = ensure_learning_resources(root)

    index = learning / "index.html"
    lesson = learning / "lessons" / "0001-scene-before-solution.html"
    reference = learning / "reference" / "quality-attributes-tactics.html"
    seed = learning / "notebooklm-seed.html"

    assert index.exists()
    assert lesson.exists()
    assert reference.exists()
    assert seed.exists()
    assert "软考达人学习台" in index.read_text(encoding="utf-8")
    assert "场景先于方案" in lesson.read_text(encoding="utf-8")
    assert "四大质量属性" in reference.read_text(encoding="utf-8")
    assert "NotebookLM" in seed.read_text(encoding="utf-8")


def test_learning_generation_preserves_manual_edits_by_default(tmp_path) -> None:
    root = tmp_path / "demo"
    learning = ensure_learning_resources(root)
    index = learning / "index.html"
    index.write_text("manual study notes", encoding="utf-8")

    ensure_learning_resources(root)

    assert index.read_text(encoding="utf-8") == "manual study notes"


def test_learning_generation_can_overwrite_when_explicit(tmp_path) -> None:
    root = tmp_path / "demo"
    learning = ensure_learning_resources(root)
    index = learning / "index.html"
    index.write_text("manual study notes", encoding="utf-8")

    ensure_learning_resources(root, overwrite=True)

    assert "软考达人学习台" in index.read_text(encoding="utf-8")


def test_cli_learning_generates_learning_desk(tmp_path) -> None:
    root = tmp_path / "demo"

    result = subprocess.run(
        [sys.executable, "-m", "ruankao_agent.cli", "learning", "--root", str(root)],
        cwd=".",
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "learning/index.html" in result.stdout
    assert (root / "learning" / "index.html").exists()
