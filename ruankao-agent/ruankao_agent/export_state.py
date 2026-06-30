from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

from .storage import RuankaoStore


@dataclass(frozen=True, slots=True)
class StateExportResult:
    as_of: date
    json_path: Path
    raw_records: int
    memory_cards: int
    practice_sessions: int


def state_export_path(root: Path | str, as_of: date) -> Path:
    return Path(root) / "exports" / f"state-{as_of.isoformat()}.json"


def write_state_export(root: Path | str, *, as_of: date | None = None) -> StateExportResult:
    root_path = Path(root)
    day = as_of or date.today()
    store = RuankaoStore(root_path / "data" / "ruankao.db")
    store.initialize()
    payload = _state_payload(store, day)

    path = state_export_path(root_path, day)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    metrics = payload["metrics"]
    assert isinstance(metrics, dict)
    return StateExportResult(
        as_of=day,
        json_path=path,
        raw_records=int(metrics["raw_records"]),
        memory_cards=int(metrics["memory_cards"]),
        practice_sessions=int(metrics["practice_sessions"]),
    )


def _state_payload(store: RuankaoStore, as_of: date) -> dict[str, object]:
    raw_records = store.list_raw_records()
    cards = store.list_memory_cards()
    review_logs = store.list_review_logs()
    practice_sessions = store.list_practice_sessions()
    relations_by_card = {
        card.id: store.list_principle_relations(card.id)
        for card in cards
        if card.card_type.value == "principle"
    }
    relations = [relation for group in relations_by_card.values() for relation in group]
    return {
        "version": 1,
        "as_of": as_of.isoformat(),
        "schema_version": store.schema_version(),
        "metrics": {
            "raw_records": len(raw_records),
            "memory_cards": len(cards),
            "review_logs": len(review_logs),
            "practice_sessions": len(practice_sessions),
            "principle_relations": len(relations),
        },
        "source_counts": _count(record.source.value for record in raw_records),
        "front_counts": _count(front.value for card in cards for front in card.fronts),
        "card_type_counts": _count(card.card_type.value for card in cards),
        "promotion_status_counts": _count(record.promotion_status for record in raw_records),
        "raw_records": [
            {
                "id": record.id,
                "source": record.source.value,
                "text": record.text,
                "summary": record.summary,
                "topics": list(record.topics),
                "fronts": [front.value for front in record.fronts],
                "promotion_status": record.promotion_status,
                "created_on": record.created_on.isoformat() if record.created_on else None,
            }
            for record in raw_records
        ],
        "memory_cards": [
            {
                "id": card.id,
                "card_type": card.card_type.value,
                "title": card.title,
                "prompt": card.prompt,
                "answer": card.answer,
                "source_record_id": card.source_record_id,
                "fronts": [front.value for front in card.fronts],
                "review_count": card.review_count,
                "retrieval_strength": card.retrieval_strength,
                "storage_strength": card.storage_strength,
                "next_due": card.next_due.isoformat() if card.next_due else None,
                "last_reviewed_on": card.last_reviewed_on.isoformat() if card.last_reviewed_on else None,
            }
            for card in cards
        ],
        "review_logs": [
            {
                "id": log.id,
                "card_id": log.card_id,
                "reviewed_on": log.reviewed_on.isoformat(),
                "grade": log.grade,
                "retrieval_strength": log.retrieval_strength,
                "next_due": log.next_due.isoformat(),
            }
            for log in review_logs
        ],
        "practice_sessions": [
            {
                "id": session.id,
                "front": session.front.value,
                "topic": session.topic,
                "source": session.source,
                "score": session.score,
                "max_score": session.max_score,
                "duration_minutes": session.duration_minutes,
                "summary": session.summary,
                "mistakes": session.mistakes,
                "created_on": session.created_on.isoformat() if session.created_on else None,
            }
            for session in practice_sessions
        ],
        "principle_relations": [
            {
                "id": relation.id,
                "from_card_id": relation.from_card_id,
                "to_card_id": relation.to_card_id,
                "relation": relation.relation.value,
                "rationale": relation.rationale,
            }
            for relation in relations
        ],
    }


def _count(values: Iterable[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))
