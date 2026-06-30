from __future__ import annotations

from datetime import date
import json
import subprocess
import sys

from ruankao_agent.learning import (
    DEFAULT_CHEKO_SNAPSHOT,
    ReferencePage,
    ensure_learning_resources,
    render_cheko_sync,
    render_learning_index,
    render_reference_page,
    render_today,
    today_tasks,
)


def test_learning_resources_generate_html_study_desk(tmp_path) -> None:
    root = tmp_path / "demo"

    learning = ensure_learning_resources(root)

    index = learning / "index.html"
    lesson = learning / "lessons" / "0001-scene-before-solution.html"
    reference = learning / "reference" / "quality-attributes-tactics.html"
    seed = learning / "notebooklm-seed.html"
    cheko = learning / "cheko-sync.html"
    today = learning / "today.html"
    snapshot = learning / "data" / "cheko-snapshot.json"

    assert index.exists()
    assert lesson.exists()
    assert reference.exists()
    assert seed.exists()
    assert cheko.exists()
    assert today.exists()
    assert snapshot.exists()
    assert "软考达人学习台" in index.read_text(encoding="utf-8")
    assert "Learning Desk" not in index.read_text(encoding="utf-8")
    assert "芝士架构同步信号" in index.read_text(encoding="utf-8")
    assert "今日三任务" in index.read_text(encoding="utf-8")
    assert "系统架构设计" in index.read_text(encoding="utf-8")
    assert "第 1 天" in index.read_text(encoding="utf-8")
    assert "场景先于方案" in lesson.read_text(encoding="utf-8")
    assert "Lesson 0001" not in lesson.read_text(encoding="utf-8")
    assert "四大质量属性" in reference.read_text(encoding="utf-8")
    assert "Reference" not in reference.read_text(encoding="utf-8")
    assert "NotebookLM" in seed.read_text(encoding="utf-8")
    assert "正确率" in cheko.read_text(encoding="utf-8")
    assert "Cheko Sync" not in cheko.read_text(encoding="utf-8")
    assert "69.4" in cheko.read_text(encoding="utf-8")
    assert "只做这三件事" in today.read_text(encoding="utf-8")
    assert "Today" not in today.read_text(encoding="utf-8")
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


def test_today_tasks_are_derived_from_cheko_weak_areas() -> None:
    tasks = today_tasks(DEFAULT_CHEKO_SNAPSHOT)

    assert len(tasks) == 3
    assert tasks[0].title == "系统架构设计错题回炉"
    assert [task.minutes for task in tasks] == [25, 15, 20]
    assert "164" in tasks[0].why
    assert "质量属性" in tasks[0].action
    assert tasks[1].title == "软件工程对比卡"
    assert "82" in tasks[1].why
    assert tasks[2].title == "论文最低触达"
    assert "300 字以内摘要" in tasks[2].action
    assert "表达卡" in tasks[2].output


def test_today_page_is_one_screen_action_plan() -> None:
    html = render_today(DEFAULT_CHEKO_SNAPSHOT)

    assert "今日三任务" in html
    assert "第 1 件" in html
    assert "第 2 件" in html
    assert "第 3 件" in html
    assert "时间盒" in html
    assert "60 分钟" in html
    assert "建议时长：25 分钟" in html
    assert "系统架构设计错题回炉" in html
    assert "论文最低触达" in html
    assert "如果今天只能做一件事" in html
    assert "Task 1" not in html


def test_reference_page_localizes_front_codes() -> None:
    html = render_reference_page(
        ReferencePage(
            filename="demo.html",
            title="题型映射演示",
            purpose="验证内部题型代码不会泄漏到学习页面。",
            outline=("先识别题型。",),
            fronts=("choice", "case", "essay"),
            drill="把一个质量属性场景分别映射到三种题型。",
            cards=("概念卡：题型入口",),
        )
    )

    assert "选择题" in html
    assert "案例题" in html
    assert "论文题" in html
    assert ">choice<" not in html
    assert ">case<" not in html
    assert ">essay<" not in html


def test_learning_index_shows_campaign_orientation() -> None:
    html = render_learning_index(DEFAULT_CHEKO_SNAPSHOT, as_of=date(2026, 6, 30))

    assert "战役导航" in html
    assert "当前位置" in html
    assert "启动诊断" in html
    assert "第 1 天；D-116" in html
    assert "下一站" in html
    assert "诊断建模" in html
    assert "终点" in html
    assert "2026-10-24" in html


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
