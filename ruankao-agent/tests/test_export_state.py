import json
import subprocess
import sys
from datetime import date

from ruankao_agent.domain import CardType, ExamFront, PrincipleRelationType, SourceIdentity
from ruankao_agent.export_state import write_state_export
from ruankao_agent.storage import RuankaoStore


def test_state_export_captures_store_tables_as_json(tmp_path) -> None:
    root = tmp_path / "demo"
    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    raw_id = store.add_raw_record(
        source=SourceIdentity.MEIN,
        text="我把质量属性场景写得太抽象。",
        summary="质量属性需要度量",
        topics=("质量属性",),
        fronts=(ExamFront.CASE,),
    )
    first = store.add_memory_card(
        card_type=CardType.PRINCIPLE,
        title="质量属性可度量",
        prompt="什么时候要写度量？",
        answer="案例和论文都要把响应写成可验证指标。",
        source_record_id=raw_id,
        fronts=(ExamFront.CASE, ExamFront.ESSAY),
        next_due=date(2026, 6, 29),
    )
    second = store.add_memory_card(
        card_type=CardType.PRINCIPLE,
        title="风险驱动验证",
        prompt="何时先验证？",
        answer="关键质量属性存在不确定性时。",
    )
    store.add_principle_relation(
        first,
        second,
        PrincipleRelationType.SUPPORTS,
        "度量让风险验证有判定标准。",
    )
    store.record_review(first, reviewed_on=date(2026, 6, 29), grade=4)
    store.add_practice_session(
        front=ExamFront.CASE,
        topic="质量属性效用树",
        source="真题",
        score=8,
        max_score=15,
        duration_minutes=35,
        summary="场景能写出，但响应度量偏虚。",
        mistakes="响应和响应度量混写。",
        created_on=date(2026, 6, 29),
    )

    result = write_state_export(root, as_of=date(2026, 6, 29))
    payload = json.loads(result.json_path.read_text(encoding="utf-8"))

    assert result.json_path == root / "exports" / "state-2026-06-29.json"
    assert payload["as_of"] == "2026-06-29"
    assert payload["metrics"] == {
        "raw_records": 1,
        "memory_cards": 2,
        "review_logs": 1,
        "practice_sessions": 1,
        "principle_relations": 1,
    }
    assert payload["raw_records"][0]["source"] == "mein"
    assert payload["memory_cards"][0]["title"] == "质量属性可度量"
    assert payload["review_logs"][0]["grade"] == 4
    assert payload["practice_sessions"][0]["score"] == 8
    assert payload["principle_relations"][0]["relation"] == "supports"


def test_cli_export_state_prints_backup_path(tmp_path) -> None:
    root = tmp_path / "demo"
    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    store.add_memory_card(
        card_type=CardType.CONCEPT,
        title="敏感点",
        prompt="什么是敏感点？",
        answer="影响单一质量属性响应的架构决策点。",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "export-state",
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
    assert "json=" in result.stdout
    assert "cards=1" in result.stdout
    assert (root / "exports" / "state-2026-06-29.json").exists()
