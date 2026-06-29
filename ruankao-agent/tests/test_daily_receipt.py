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
    seed_cheko_cards(root, next_due=date(2026, 6, 29))

    result = write_daily_receipt(root, as_of=date(2026, 6, 29))

    assert result.json_path.exists()
    assert result.html_path.exists()
    assert "D-117" in result.status

    payload = json.loads(result.json_path.read_text(encoding="utf-8"))
    assert payload["as_of"] == "2026-06-29"
    assert payload["metrics"]["raw_records"] == 2
    assert payload["metrics"]["memory_cards"] == 5
    assert payload["metrics"]["due_cards"] == 4
    assert payload["metrics"]["cheko_cards"] == 4
    assert payload["metrics"]["review_logs"] == 1
    assert payload["metrics"]["reviews_today"] == 1
    assert payload["source_counts"] == {"mein": 1, "uns": 1}
    assert payload["front_counts"]["choice"] == 4
    assert payload["front_counts"]["essay"] == 1

    html = result.html_path.read_text(encoding="utf-8")
    assert "日结回执 2026-06-29" in html
    assert "Cheko 到期" in html
    assert "质量属性场景" in html
    assert "错题归因完成" in html
    assert "最近复习" in html
    assert "grade=4" in html


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
