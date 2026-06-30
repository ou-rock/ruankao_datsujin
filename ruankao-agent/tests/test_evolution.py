from __future__ import annotations

import json
import subprocess
import sys
from datetime import date

from ruankao_agent.domain import CardType, ExamFront
from ruankao_agent.evolution import write_night_evolution_plan
from ruankao_agent.storage import RuankaoStore


def test_night_evolution_plan_stages_actions_from_daily_receipt(tmp_path) -> None:
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

    result = write_night_evolution_plan(root, as_of=date(2026, 6, 29))

    assert result.stage_only is True
    assert result.action_count >= 2
    assert result.json_path.exists()
    assert result.html_path.exists()
    assert (root / "data" / "daily-receipts" / "2026-06-29.json").exists()

    payload = json.loads(result.json_path.read_text(encoding="utf-8"))
    action_ids = [action["id"] for action in payload["actions"]]
    assert payload["stage_only"] is True
    assert payload["actions"][0]["id"] == "repair-memory"
    assert payload["actions"][0]["priority"] == "high"
    assert "protect-exam-practice" in action_ids
    assert "敏感点 vs 权衡点" in payload["actions"][0]["detail"]

    html = result.html_path.read_text(encoding="utf-8")
    assert "夜间进化草案 2026-06-29" in html
    assert "仅暂存：是" in html
    assert "来源日结：" in html
    assert "修复薄弱记忆卡" in html
    assert "优先级：高" in html
    assert "stage_only=true" not in html
    assert "id=repair-memory" not in html
    assert "优先级=高" not in html
    assert "priority=high" not in html


def test_cli_night_evolve_prints_staged_plan_paths(tmp_path) -> None:
    root = tmp_path / "demo"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "night-evolve",
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
    assert "stage_only=true" in result.stdout
    assert (root / "evolution" / "staged" / "2026-06-29.json").exists()
    assert (root / "reports" / "nightly" / "2026-06-29.html").exists()
