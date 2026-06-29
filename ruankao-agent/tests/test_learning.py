from __future__ import annotations

import json
import subprocess
import sys

from ruankao_agent.learning import DEFAULT_CHEKO_SNAPSHOT, ensure_learning_resources, render_cheko_sync


def test_learning_resources_generate_html_study_desk(tmp_path) -> None:
    root = tmp_path / "demo"

    learning = ensure_learning_resources(root)

    index = learning / "index.html"
    lesson = learning / "lessons" / "0001-scene-before-solution.html"
    reference = learning / "reference" / "quality-attributes-tactics.html"
    seed = learning / "notebooklm-seed.html"
    cheko = learning / "cheko-sync.html"
    snapshot = learning / "data" / "cheko-snapshot.json"

    assert index.exists()
    assert lesson.exists()
    assert reference.exists()
    assert seed.exists()
    assert cheko.exists()
    assert snapshot.exists()
    assert "软考达人学习台" in index.read_text(encoding="utf-8")
    assert "芝士架构同步信号" in index.read_text(encoding="utf-8")
    assert "系统架构设计" in index.read_text(encoding="utf-8")
    assert "场景先于方案" in lesson.read_text(encoding="utf-8")
    assert "四大质量属性" in reference.read_text(encoding="utf-8")
    assert "NotebookLM" in seed.read_text(encoding="utf-8")
    assert "正确率" in cheko.read_text(encoding="utf-8")
    assert "69.4" in cheko.read_text(encoding="utf-8")
    assert json.loads(snapshot.read_text(encoding="utf-8"))["wrong"] == 194


def test_learning_generation_preserves_manual_edits_by_default(tmp_path) -> None:
    root = tmp_path / "demo"
    learning = ensure_learning_resources(root)
    index = learning / "index.html"
    index.write_text("manual study notes", encoding="utf-8")

    ensure_learning_resources(root)

    assert index.read_text(encoding="utf-8") == "manual study notes"


def test_learning_generation_preserves_cheko_snapshot_by_default(tmp_path) -> None:
    root = tmp_path / "demo"
    learning = ensure_learning_resources(root)
    snapshot = learning / "data" / "cheko-snapshot.json"
    payload = json.loads(snapshot.read_text(encoding="utf-8"))
    payload["answered"] = 777
    payload["weak_areas"][0]["title"] = "手工同步重点"
    snapshot.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    ensure_learning_resources(root, overwrite=True)

    regenerated = json.loads(snapshot.read_text(encoding="utf-8"))
    assert regenerated["answered"] == DEFAULT_CHEKO_SNAPSHOT.answered

    payload["answered"] = 777
    snapshot.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    ensure_learning_resources(root)

    preserved = json.loads(snapshot.read_text(encoding="utf-8"))
    assert preserved["answered"] == 777
    assert preserved["weak_areas"][0]["title"] == "手工同步重点"


def test_learning_generation_can_overwrite_when_explicit(tmp_path) -> None:
    root = tmp_path / "demo"
    learning = ensure_learning_resources(root)
    index = learning / "index.html"
    index.write_text("manual study notes", encoding="utf-8")

    ensure_learning_resources(root, overwrite=True)

    assert "软考达人学习台" in index.read_text(encoding="utf-8")


def test_cheko_sync_renders_learning_signal_not_account_identity() -> None:
    html = render_cheko_sync(DEFAULT_CHEKO_SNAPSHOT)

    assert "总答题" in html
    assert "634" in html
    assert "错题数" in html
    assert "194" in html
    assert "预估分" in html
    assert "43.75" in html
    assert "系统架构设计" in html
    assert "论文助手算力 15 / 15" in html
    assert "不保存账号、头像、邮箱" in html
    assert "nav_avatar" not in html
    assert "cookie" not in html.lower()


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
