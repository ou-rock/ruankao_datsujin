from __future__ import annotations

import json
import subprocess
import sys
from datetime import date

from ruankao_agent.cheko import seed_cheko_cards
from ruankao_agent.domain import CardType, ExamFront, SourceIdentity
from ruankao_agent.receipts import write_daily_receipt
from ruankao_agent.storage import RuankaoStore


def test_daily_receipt_writes_json_and_html_summary(tmp_path) -> None:
    root = tmp_path / "demo"
    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    store.add_raw_record(
        source=SourceIdentity.MEIN,
        text="今天把系统架构设计错题按质量属性归因。",
        summary="错题归因完成",
        topics=("系统架构设计",),
        fronts=(ExamFront.CHOICE, ExamFront.CASE),
    )
    card_id = store.add_memory_card(
        card_type=CardType.CONCEPT,
        title="质量属性场景",
        prompt="六要素是什么？",
        answer="刺激源、刺激、环境、制品、响应、响应度量。",
        fronts=(ExamFront.CHOICE, ExamFront.CASE),
        next_due=date(2026, 6, 29),
    )
    store.record_review(card_id=card_id, reviewed_on=date(2026, 6, 29), grade=4)
    store.add_practice_session(
        front=ExamFront.CHOICE,
        topic="系统架构设计错题",
        source="Cheko",
        score=7,
        max_score=10,
        duration_minutes=18,
        summary="质量属性题仍然不稳。",
        mistakes="把可用性和可靠性混在一起。",
        created_on=date(2026, 6, 29),
    )
    seed_cheko_cards(root, next_due=date(2026, 6, 29))

    result = write_daily_receipt(root, as_of=date(2026, 6, 29))

    assert result.json_path.exists()
    assert result.html_path.exists()
    assert "D-117" in result.status

    payload = json.loads(result.json_path.read_text(encoding="utf-8"))
    assert payload["as_of"] == "2026-06-29"
    assert payload["schema_version"] != "unknown"
    assert payload["metrics"]["raw_records"] == 2
    assert payload["metrics"]["memory_cards"] == 5
    assert payload["metrics"]["due_cards"] == 4
    assert payload["metrics"]["cheko_cards"] == 4
    assert payload["metrics"]["review_logs"] == 1
    assert payload["metrics"]["reviews_today"] == 1
    assert payload["metrics"]["practice_sessions"] == 1
    assert payload["metrics"]["practice_today"] == 1
    assert payload["metrics"]["practice_score_ratio"] == 0.7
    assert payload["metrics"]["weak_memory_cards"] == 0
    assert payload["memory_diagnostics"][0]["status"] == "due"
    assert payload["practice_front_counts"] == {"choice": 1}
    assert payload["recent_practice"][0]["topic"] == "系统架构设计错题"
    assert payload["source_counts"] == {"mein": 1, "uns": 1}
    assert payload["front_counts"]["choice"] == 4
    assert payload["front_counts"]["essay"] == 1

    html = result.html_path.read_text(encoding="utf-8")
    assert "日结回执 2026-06-29" in html
    assert "数据版本" in html
    assert "Schema" not in html
    assert "Cheko 到期" in html
    assert "质量属性场景" in html
    assert "错题归因完成" in html
    assert "记忆诊断" in html
    assert "最近练习" in html
    assert "系统架构设计错题" in html
    assert "70%" in html
    assert "最近复习" in html
    assert "评分=4" in html
    assert "得分：7/10" in html
    assert "耗时：18分钟" in html
    assert "得分=7/10" not in html
    assert "状态：原始" in html
    assert "主题：系统架构设计" in html
    assert "状态=原始" not in html
    assert "类型：概念卡" in html
    assert "题型：选择题、案例题" in html
    assert "类型=概念卡" not in html
    assert "grade=4" not in html
    assert "score=7/10" not in html


def test_daily_receipt_marks_repeated_low_grade_card_as_leech(tmp_path) -> None:
    root = tmp_path / "demo"
    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    card_id = store.add_memory_card(
        card_type=CardType.COMPARISON,
        title="敏感点 vs 权衡点",
        prompt="二者边界？",
        answer="敏感点影响一个质量属性，权衡点影响多个质量属性。",
        fronts=(ExamFront.CHOICE, ExamFront.CASE),
        next_due=date(2026, 6, 29),
    )
    store.record_review(card_id=card_id, reviewed_on=date(2026, 6, 27), grade=1)
    store.record_review(card_id=card_id, reviewed_on=date(2026, 6, 28), grade=2)

    result = write_daily_receipt(root, as_of=date(2026, 6, 29))

    payload = json.loads(result.json_path.read_text(encoding="utf-8"))
    assert payload["metrics"]["weak_memory_cards"] == 1
    assert payload["memory_diagnostics"][0]["status"] == "leech"
    assert payload["memory_diagnostics"][0]["title"] == "敏感点 vs 权衡点"
    assert "拆成更小卡片" in result.html_path.read_text(encoding="utf-8")


def test_daily_receipt_renders_missing_practice_ratio_as_unrecorded(tmp_path) -> None:
    root = tmp_path / "demo"

    result = write_daily_receipt(root, as_of=date(2026, 6, 29))

    payload = json.loads(result.json_path.read_text(encoding="utf-8"))
    html = result.html_path.read_text(encoding="utf-8")

    assert payload["metrics"]["practice_score_ratio"] is None
    assert '<span>练习得分率</span><strong>未记录</strong>' in html
    assert '<span>练习得分率</span><strong>none</strong>' not in html


def test_cli_daily_receipt_prints_hook_friendly_paths(tmp_path) -> None:
    root = tmp_path / "demo"
    seed_cheko_cards(root, next_due=date(2026, 6, 29))

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "daily-receipt",
            "--root",
            str(root),
            "--as-of",
            "2026-06-29",
        ],
        cwd=".",
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "html=" in result.stdout
    assert "json=" in result.stdout
    assert "status=D-117" in result.stdout
    assert (root / "reports" / "daily" / "2026-06-29.html").exists()
    assert (root / "data" / "daily-receipts" / "2026-06-29.json").exists()
