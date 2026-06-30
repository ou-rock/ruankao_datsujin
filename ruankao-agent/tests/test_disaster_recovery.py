from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from datetime import date
from pathlib import Path
from time import monotonic

from ruankao_agent.domain import CardType, ExamFront, PrincipleRelationType, SourceIdentity
from ruankao_agent.export_state import write_state_export
from ruankao_agent.storage import RuankaoStore


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_gitignore_allows_state_exports_for_git_snapshot_workflow() -> None:
    lines = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert "ruankao-agent/exports/" not in lines
    assert "!ruankao-agent/exports/state-*.json" in lines


def test_store_writes_create_weekday_rolling_binary_backup(tmp_path) -> None:
    root = tmp_path / "demo"
    db_path = root / "data" / "ruankao.db"
    store = RuankaoStore(db_path)
    store.initialize()
    store.add_memory_card(
        card_type=CardType.CONCEPT,
        title="写前备份第一版",
        prompt="第一版问题",
        answer="第一版答案",
        fronts=(ExamFront.CASE,),
    )

    store.add_memory_card(
        card_type=CardType.CONCEPT,
        title="写前备份第二版",
        prompt="第二版问题",
        answer="第二版答案",
        fronts=(ExamFront.ESSAY,),
    )

    backup_path = root / "data" / "backups" / f"ruankao.db.bak.{date.today().isoweekday()}"
    assert backup_path.exists()
    with sqlite3.connect(backup_path) as backup_conn:
        rows = backup_conn.execute(
            "SELECT title FROM memory_cards ORDER BY id"
        ).fetchall()

    assert rows == [("写前备份第一版",)]


def test_cli_import_state_rebuilds_deleted_sqlite_from_export(tmp_path) -> None:
    root = tmp_path / "demo"
    db_path = root / "data" / "ruankao.db"
    store = RuankaoStore(db_path)
    store.initialize()
    raw_id = store.add_raw_record(
        source=SourceIdentity.MEIN,
        text="我把灾备响应度量写散了。",
        summary="灾备响应度量复盘",
        topics=("灾备", "响应度量"),
        fronts=(ExamFront.CASE,),
    )
    first = store.add_memory_card(
        card_type=CardType.PRINCIPLE,
        title="灾备先定 RTO",
        prompt="灾备场景先写什么？",
        answer="先写恢复目标、降级边界和成功率。",
        source_record_id=raw_id,
        fronts=(ExamFront.CASE, ExamFront.ESSAY),
        next_due=date(2026, 6, 30),
    )
    second = store.add_memory_card(
        card_type=CardType.CONCEPT,
        title="备用机制",
        prompt="备用机制怎么验证？",
        answer="验证触发条件、切换路径和回退策略。",
        fronts=(ExamFront.CASE,),
    )
    store.add_principle_relation(
        first,
        second,
        PrincipleRelationType.SUPPORTS,
        "明确 RTO 后才能选择备用机制。",
    )
    store.record_review(first, reviewed_on=date(2026, 6, 30), grade=4)
    store.add_practice_session(
        front=ExamFront.CASE,
        topic="灾备响应度量",
        source="manual",
        score=12.5,
        max_score=15,
        duration_minutes=18,
        summary="写出了 1s/2s/3s 三段响应。",
        mistakes="备用机制边界略散。",
        created_on=date(2026, 6, 30),
    )
    export = write_state_export(root, as_of=date(2026, 6, 30))
    payload = json.loads(export.json_path.read_text(encoding="utf-8"))
    db_path.unlink()

    start = monotonic()
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "import-state",
            "--file",
            str(export.json_path),
        ],
        cwd=".",
        text=True,
        capture_output=True,
        check=False,
    )
    elapsed = monotonic() - start

    assert result.returncode == 0, result.stderr
    assert elapsed < 5
    assert "状态快照已导入：" in result.stdout
    assert db_path.exists()
    restored = RuankaoStore(db_path)
    restored.initialize()

    assert [record.summary for record in restored.list_raw_records()] == [
        item["summary"] for item in payload["raw_records"]
    ]
    assert [
        {
            "id": card.id,
            "title": card.title,
            "review_count": card.review_count,
            "retrieval_strength": card.retrieval_strength,
            "next_due": card.next_due.isoformat() if card.next_due else None,
            "fronts": [front.value for front in card.fronts],
        }
        for card in restored.list_memory_cards()
    ] == [
        {
            "id": item["id"],
            "title": item["title"],
            "review_count": item["review_count"],
            "retrieval_strength": item["retrieval_strength"],
            "next_due": item["next_due"],
            "fronts": item["fronts"],
        }
        for item in payload["memory_cards"]
    ]
    assert [log.grade for log in restored.list_review_logs()] == [
        item["grade"] for item in payload["review_logs"]
    ]
    assert [session.topic for session in restored.list_practice_sessions()] == [
        item["topic"] for item in payload["practice_sessions"]
    ]
    assert [relation.rationale for relation in restored.list_principle_relations(first)] == [
        item["rationale"] for item in payload["principle_relations"]
    ]
