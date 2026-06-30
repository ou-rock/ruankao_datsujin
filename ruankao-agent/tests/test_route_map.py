from __future__ import annotations

import json
import subprocess
import sys
from datetime import date

from ruankao_agent.domain import CardType, ExamFront
from ruankao_agent.route_map import write_route_map
from ruankao_agent.storage import RuankaoStore


def test_route_map_summarizes_choice_case_and_essay_fronts(tmp_path) -> None:
    root = tmp_path / "demo"
    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    weak = store.add_memory_card(
        card_type=CardType.COMPARISON,
        title="敏感点 vs 权衡点",
        prompt="二者边界？",
        answer="敏感点影响一个属性，权衡点影响多个属性。",
        fronts=(ExamFront.CHOICE, ExamFront.CASE),
        next_due=date(2026, 6, 29),
    )
    store.add_memory_card(
        card_type=CardType.EXPRESSION,
        title="论文背景段",
        prompt="怎么写项目背景？",
        answer="业务目标、约束、本人职责和系统规模。",
        fronts=(ExamFront.ESSAY,),
    )
    store.record_review(weak, reviewed_on=date(2026, 6, 27), grade=1)
    store.record_review(weak, reviewed_on=date(2026, 6, 28), grade=2)
    store.add_practice_session(
        front=ExamFront.ESSAY,
        topic="项目背景段",
        source="自写",
        score=3,
        max_score=4,
        summary="写了项目背景段。",
        mistakes="项目规模不够具体。",
        created_on=date(2026, 6, 29),
    )

    result = write_route_map(root, as_of=date(2026, 6, 29))

    payload = json.loads(result.json_path.read_text(encoding="utf-8"))
    by_front = {route["front"]: route for route in payload["routes"]}

    assert by_front["choice"]["status"] == "red"
    assert by_front["choice"]["weak_cards"] == 1
    assert by_front["case"]["focus_titles"] == ["敏感点 vs 权衡点"]
    assert by_front["essay"]["total_cards"] == 1
    assert by_front["essay"]["untested_cards"] == 1
    assert by_front["essay"]["practice_sessions"] == 1
    assert by_front["essay"]["practice_today"] == 1
    assert by_front["essay"]["average_score_ratio"] == 0.75
    assert by_front["essay"]["last_practice_on"] == "2026-06-29"

    html = result.html_path.read_text(encoding="utf-8")
    assert "三题型覆盖图 2026-06-29" in html
    assert "选择题" in html
    assert "案例题" in html
    assert "论文题" in html
    assert "今日练习" in html
    assert "75%" in html
    assert "状态：红灯" in html
    assert "状态：黄灯" in html
    assert "最近练习：2026-06-29" in html
    assert "焦点：敏感点 vs 权衡点" in html
    assert "最近练习=2026-06-29" not in html
    assert "焦点=敏感点 vs 权衡点" not in html
    assert "未记录" in html
    assert "status=red" not in html
    assert "last_practice=" not in html


def test_cli_route_map_prints_report_paths(tmp_path) -> None:
    root = tmp_path / "demo"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "route-map",
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
    assert (root / "reports" / "routes" / "2026-06-29.html").exists()
    assert (root / "reports" / "routes" / "2026-06-29.json").exists()
