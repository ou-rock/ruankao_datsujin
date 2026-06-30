from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .storage import RuankaoStore, copy_rolling_backup


@dataclass(frozen=True, slots=True)
class StateImportResult:
    json_path: Path
    db_path: Path
    raw_records: int
    memory_cards: int
    review_logs: int
    practice_sessions: int
    principle_relations: int


def import_state_snapshot(
    snapshot_path: Path | str,
    *,
    root: Path | str | None = None,
) -> StateImportResult:
    json_path = Path(snapshot_path)
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    root_path = Path(root) if root is not None else _infer_root(json_path)
    db_path = root_path / "data" / "ruankao.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    copy_rolling_backup(db_path)

    temp_path = db_path.with_name(f"{db_path.name}.importing")
    if temp_path.exists():
        temp_path.unlink()
    store = RuankaoStore(temp_path)
    store.initialize()
    store.close()

    _load_payload_into_database(temp_path, payload)
    temp_path.replace(db_path)
    metrics = payload.get("metrics", {})
    return StateImportResult(
        json_path=json_path,
        db_path=db_path,
        raw_records=int(metrics.get("raw_records", len(payload.get("raw_records", [])))),
        memory_cards=int(metrics.get("memory_cards", len(payload.get("memory_cards", [])))),
        review_logs=int(metrics.get("review_logs", len(payload.get("review_logs", [])))),
        practice_sessions=int(
            metrics.get("practice_sessions", len(payload.get("practice_sessions", [])))
        ),
        principle_relations=int(
            metrics.get("principle_relations", len(payload.get("principle_relations", [])))
        ),
    )


def _infer_root(snapshot_path: Path) -> Path:
    if snapshot_path.parent.name == "exports":
        return snapshot_path.parent.parent
    return Path.cwd()


def _load_payload_into_database(db_path: Path, payload: dict[str, Any]) -> None:
    as_of = str(payload.get("as_of") or date.today().isoformat())
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        _insert_raw_records(conn, payload.get("raw_records", []), fallback_date=as_of)
        _insert_memory_cards(conn, payload.get("memory_cards", []), fallback_date=as_of)
        _insert_principle_relations(conn, payload.get("principle_relations", []))
        _insert_review_logs(conn, payload.get("review_logs", []), fallback_date=as_of)
        _insert_practice_sessions(conn, payload.get("practice_sessions", []), fallback_date=as_of)
        conn.commit()


def _insert_raw_records(
    conn: sqlite3.Connection,
    rows: list[dict[str, Any]],
    *,
    fallback_date: str,
) -> None:
    for row in rows:
        conn.execute(
            """
            INSERT INTO raw_records (
                id, source, text, summary, topics_json, fronts_json,
                promotion_status, created_on
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["id"],
                row["source"],
                row["text"],
                row["summary"],
                json.dumps(row.get("topics", []), ensure_ascii=False),
                json.dumps(row.get("fronts", []), ensure_ascii=False),
                row.get("promotion_status", "raw"),
                row.get("created_on") or fallback_date,
            ),
        )


def _insert_memory_cards(
    conn: sqlite3.Connection,
    rows: list[dict[str, Any]],
    *,
    fallback_date: str,
) -> None:
    for row in rows:
        conn.execute(
            """
            INSERT INTO memory_cards (
                id, card_type, title, prompt, answer, source_record_id, fronts_json,
                review_count, retrieval_strength, storage_strength, next_due,
                created_on, updated_on, last_reviewed_on
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["id"],
                row["card_type"],
                row["title"],
                row["prompt"],
                row["answer"],
                row.get("source_record_id"),
                json.dumps(row.get("fronts", []), ensure_ascii=False),
                row.get("review_count", 0),
                row.get("retrieval_strength", 1.0),
                row.get("storage_strength", 1.0),
                row.get("next_due"),
                fallback_date,
                fallback_date,
                row.get("last_reviewed_on"),
            ),
        )


def _insert_principle_relations(
    conn: sqlite3.Connection,
    rows: list[dict[str, Any]],
) -> None:
    for row in rows:
        conn.execute(
            """
            INSERT INTO principle_relations (
                id, from_card_id, to_card_id, relation, rationale
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                row["id"],
                row["from_card_id"],
                row["to_card_id"],
                row["relation"],
                row["rationale"],
            ),
        )


def _insert_review_logs(
    conn: sqlite3.Connection,
    rows: list[dict[str, Any]],
    *,
    fallback_date: str,
) -> None:
    for row in rows:
        conn.execute(
            """
            INSERT INTO review_logs (
                id, card_id, reviewed_on, grade, retrieval_strength, next_due, created_on
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["id"],
                row["card_id"],
                row["reviewed_on"],
                row["grade"],
                row["retrieval_strength"],
                row["next_due"],
                fallback_date,
            ),
        )


def _insert_practice_sessions(
    conn: sqlite3.Connection,
    rows: list[dict[str, Any]],
    *,
    fallback_date: str,
) -> None:
    for row in rows:
        conn.execute(
            """
            INSERT INTO practice_sessions (
                id, front, topic, source, score, max_score, duration_minutes,
                summary, mistakes, created_on
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["id"],
                row["front"],
                row["topic"],
                row.get("source", ""),
                row.get("score"),
                row.get("max_score"),
                row.get("duration_minutes"),
                row["summary"],
                row.get("mistakes", ""),
                row.get("created_on") or fallback_date,
            ),
        )
