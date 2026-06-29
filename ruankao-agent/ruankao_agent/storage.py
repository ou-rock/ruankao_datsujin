from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable, Sequence

from .domain import (
    CardType,
    ExamFront,
    PrincipleRelationType,
    SourceIdentity,
)


def _dump_enum_values(values: Sequence[object]) -> str:
    return json.dumps([getattr(value, "value", value) for value in values], ensure_ascii=False)


def _load_enum_values(payload: str, enum_cls):
    return tuple(enum_cls(item) for item in json.loads(payload))


@dataclass(frozen=True, slots=True)
class RawRecord:
    id: int
    source: SourceIdentity
    text: str
    summary: str
    topics: tuple[str, ...]
    fronts: tuple[ExamFront, ...]
    promotion_status: str = "raw"
    created_on: date | None = None


@dataclass(frozen=True, slots=True)
class MemoryCard:
    id: int
    card_type: CardType
    title: str
    prompt: str
    answer: str
    source_record_id: int | None
    fronts: tuple[ExamFront, ...]
    review_count: int
    retrieval_strength: float
    storage_strength: float
    next_due: date | None
    created_on: date | None = None
    updated_on: date | None = None
    last_reviewed_on: date | None = None


@dataclass(frozen=True, slots=True)
class PrincipleRelation:
    id: int
    from_card_id: int
    to_card_id: int
    relation: PrincipleRelationType
    rationale: str


class RuankaoStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")

    def initialize(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS raw_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                text TEXT NOT NULL,
                summary TEXT NOT NULL,
                topics_json TEXT NOT NULL,
                fronts_json TEXT NOT NULL,
                promotion_status TEXT NOT NULL DEFAULT 'raw',
                created_on TEXT NOT NULL DEFAULT (date('now'))
            );

            CREATE TABLE IF NOT EXISTS memory_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_type TEXT NOT NULL,
                title TEXT NOT NULL,
                prompt TEXT NOT NULL,
                answer TEXT NOT NULL,
                source_record_id INTEGER REFERENCES raw_records(id) ON DELETE SET NULL,
                fronts_json TEXT NOT NULL,
                review_count INTEGER NOT NULL DEFAULT 0,
                retrieval_strength REAL NOT NULL DEFAULT 1.0,
                storage_strength REAL NOT NULL DEFAULT 1.0,
                next_due TEXT,
                created_on TEXT NOT NULL DEFAULT (date('now')),
                updated_on TEXT NOT NULL DEFAULT (date('now')),
                last_reviewed_on TEXT
            );

            CREATE TABLE IF NOT EXISTS principle_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_card_id INTEGER NOT NULL REFERENCES memory_cards(id) ON DELETE CASCADE,
                to_card_id INTEGER NOT NULL REFERENCES memory_cards(id) ON DELETE CASCADE,
                relation TEXT NOT NULL,
                rationale TEXT NOT NULL,
                created_on TEXT NOT NULL DEFAULT (date('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_raw_records_source ON raw_records(source);
            CREATE INDEX IF NOT EXISTS idx_memory_cards_type ON memory_cards(card_type);
            CREATE INDEX IF NOT EXISTS idx_memory_cards_next_due ON memory_cards(next_due);
            CREATE INDEX IF NOT EXISTS idx_principle_relations_from ON principle_relations(from_card_id);
            """
        )
        self._ensure_column("raw_records", "promotion_status", "TEXT NOT NULL DEFAULT 'raw'")
        self._conn.commit()

    def _ensure_column(self, table: str, column: str, definition: str) -> None:
        existing = {
            row["name"]
            for row in self._conn.execute(f"PRAGMA table_info({table})").fetchall()
        }
        if column not in existing:
            self._conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def add_raw_record(
        self,
        source: SourceIdentity,
        text: str,
        summary: str,
        topics: Sequence[str] = (),
        fronts: Sequence[ExamFront] = (),
        promotion_status: str = "raw",
    ) -> int:
        cur = self._conn.execute(
            """
            INSERT INTO raw_records (
                source, text, summary, topics_json, fronts_json, promotion_status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                source.value,
                text,
                summary,
                _dump_enum_values(tuple(topics)),
                _dump_enum_values(tuple(fronts)),
                promotion_status,
            ),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def list_raw_records(self) -> list[RawRecord]:
        rows = self._conn.execute(
            """
            SELECT id, source, text, summary, topics_json, fronts_json, promotion_status, created_on
            FROM raw_records
            ORDER BY id
            """
        ).fetchall()
        return [
            RawRecord(
                id=row["id"],
                source=SourceIdentity(row["source"]),
                text=row["text"],
                summary=row["summary"],
                topics=tuple(json.loads(row["topics_json"])),
                fronts=_load_enum_values(row["fronts_json"], ExamFront),
                promotion_status=row["promotion_status"],
                created_on=date.fromisoformat(row["created_on"]) if row["created_on"] else None,
            )
            for row in rows
        ]

    def add_memory_card(
        self,
        card_type: CardType,
        title: str,
        prompt: str,
        answer: str,
        source_record_id: int | None = None,
        fronts: Sequence[ExamFront] = (),
        next_due: date | None = None,
    ) -> int:
        cur = self._conn.execute(
            """
            INSERT INTO memory_cards (
                card_type, title, prompt, answer, source_record_id, fronts_json, next_due
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                card_type.value,
                title,
                prompt,
                answer,
                source_record_id,
                _dump_enum_values(tuple(fronts)),
                next_due.isoformat() if next_due else None,
            ),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def _row_to_memory_card(self, row: sqlite3.Row) -> MemoryCard:
        return MemoryCard(
            id=row["id"],
            card_type=CardType(row["card_type"]),
            title=row["title"],
            prompt=row["prompt"],
            answer=row["answer"],
            source_record_id=row["source_record_id"],
            fronts=_load_enum_values(row["fronts_json"], ExamFront),
            review_count=row["review_count"],
            retrieval_strength=row["retrieval_strength"],
            storage_strength=row["storage_strength"],
            next_due=date.fromisoformat(row["next_due"]) if row["next_due"] else None,
            created_on=date.fromisoformat(row["created_on"]) if row["created_on"] else None,
            updated_on=date.fromisoformat(row["updated_on"]) if row["updated_on"] else None,
            last_reviewed_on=date.fromisoformat(row["last_reviewed_on"]) if row["last_reviewed_on"] else None,
        )

    def list_memory_cards(self) -> list[MemoryCard]:
        rows = self._conn.execute(
            """
            SELECT id, card_type, title, prompt, answer, source_record_id, fronts_json,
                   review_count, retrieval_strength, storage_strength, next_due,
                   created_on, updated_on, last_reviewed_on
            FROM memory_cards
            ORDER BY id
            """
        ).fetchall()
        return [self._row_to_memory_card(row) for row in rows]

    def get_memory_card(self, card_id: int) -> MemoryCard:
        row = self._conn.execute(
            """
            SELECT id, card_type, title, prompt, answer, source_record_id, fronts_json,
                   review_count, retrieval_strength, storage_strength, next_due,
                   created_on, updated_on, last_reviewed_on
            FROM memory_cards
            WHERE id = ?
            """,
            (card_id,),
        ).fetchone()
        if row is None:
            raise KeyError(card_id)
        return self._row_to_memory_card(row)

    def add_principle_relation(
        self,
        from_card_id: int,
        to_card_id: int,
        relation: PrincipleRelationType,
        rationale: str,
    ) -> int:
        cur = self._conn.execute(
            """
            INSERT INTO principle_relations (from_card_id, to_card_id, relation, rationale)
            VALUES (?, ?, ?, ?)
            """,
            (from_card_id, to_card_id, relation.value, rationale),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def list_principle_relations(self, from_card_id: int) -> list[PrincipleRelation]:
        rows = self._conn.execute(
            """
            SELECT id, from_card_id, to_card_id, relation, rationale
            FROM principle_relations
            WHERE from_card_id = ?
            ORDER BY id
            """,
            (from_card_id,),
        ).fetchall()
        return [
            PrincipleRelation(
                id=row["id"],
                from_card_id=row["from_card_id"],
                to_card_id=row["to_card_id"],
                relation=PrincipleRelationType(row["relation"]),
                rationale=row["rationale"],
            )
            for row in rows
        ]

    def record_review(self, card_id: int, reviewed_on: date, grade: int) -> None:
        card = self.get_memory_card(card_id)
        quality = max(0, min(int(grade), 5))

        if quality < 3:
            retrieval_strength = max(0.5, card.retrieval_strength * 0.85)
            interval_days = 1
        else:
            retrieval_strength = round(card.retrieval_strength + 0.2 + quality * 0.1, 3)
            base_interval = max(1, card.review_count + 1)
            interval_days = max(1, int(round(base_interval * (1 + retrieval_strength / 2))))

        next_due = reviewed_on + timedelta(days=interval_days)

        self._conn.execute(
            """
            UPDATE memory_cards
            SET review_count = review_count + 1,
                retrieval_strength = ?,
                next_due = ?,
                updated_on = ?,
                last_reviewed_on = ?
            WHERE id = ?
            """,
            (
                retrieval_strength,
                next_due.isoformat(),
                reviewed_on.isoformat(),
                reviewed_on.isoformat(),
                card_id,
            ),
        )
        self._conn.commit()

    def count_due_cards(self, as_of: date) -> int:
        row = self._conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM memory_cards
            WHERE next_due IS NOT NULL AND next_due <= ?
            """,
            (as_of.isoformat(),),
        ).fetchone()
        return int(row["count"])

    def review_backlog_ratio(self, as_of: date) -> float:
        total_row = self._conn.execute("SELECT COUNT(*) AS count FROM memory_cards").fetchone()
        total = int(total_row["count"])
        if total == 0:
            return 0.0
        return self.count_due_cards(as_of) / total
