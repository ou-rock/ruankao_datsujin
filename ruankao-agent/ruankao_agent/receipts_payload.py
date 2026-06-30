from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
from typing import Iterable

from .loop import build_daily_loop_snapshot, status_line
from .memory import MemoryDiagnostic, diagnose_memory
from .rag import DEFAULT_RAG_QUERY, build_rag_brief, rag_brief_to_payload
from .storage import MemoryCard, PracticeSession, RawRecord, ReviewLog, RuankaoStore


def build_daily_receipt_payload(root: Path | str, day: date) -> dict[str, object]:
    root_path = Path(root)
    store = RuankaoStore(root_path / "data" / "ruankao.db")
    store.initialize()
    schema_version = store.schema_version()

    records = store.list_raw_records()
    cards = store.list_memory_cards()
    review_logs = store.list_review_logs()
    practice_sessions = store.list_practice_sessions()
    reviews_today = [log for log in review_logs if log.reviewed_on == day]
    practice_today = [session for session in practice_sessions if session.created_on == day]
    due_cards = [card for card in cards if card.next_due is not None and card.next_due <= day]
    cheko_cards = [card for card in cards if card.title.startswith("Cheko")]
    cheko_due_cards = [card for card in cheko_cards if card.next_due is not None and card.next_due <= day]
    diagnostics = diagnose_memory(cards, review_logs, as_of=day)
    rag_brief = build_rag_brief(
        store,
        query=DEFAULT_RAG_QUERY,
        as_of=day,
        limit=4,
    )

    snapshot = build_daily_loop_snapshot(
        as_of=day,
        due_cards=len(due_cards),
        review_backlog_ratio=store.review_backlog_ratio(day),
    )
    return _receipt_payload(
        day=day,
        status=status_line(snapshot),
        phase=snapshot.phase_name,
        countdown=snapshot.countdown,
        risk=snapshot.risk_text,
        schema_version=schema_version,
        reserve_days_consumed=snapshot.reserve_days_consumed,
        review_backlog_ratio=snapshot.dashboard.review_backlog_ratio,
        records=records,
        cards=cards,
        review_logs=review_logs,
        reviews_today=reviews_today,
        practice_sessions=practice_sessions,
        practice_today=practice_today,
        diagnostics=list(diagnostics),
        due_cards=due_cards,
        cheko_cards=cheko_cards,
        cheko_due_cards=cheko_due_cards,
        rag_brief=rag_brief_to_payload(rag_brief),
    )


def _receipt_payload(
    *,
    day: date,
    status: str,
    phase: str,
    countdown: str,
    risk: str,
    schema_version: str,
    reserve_days_consumed: int,
    review_backlog_ratio: float,
    records: list[RawRecord],
    cards: list[MemoryCard],
    review_logs: list[ReviewLog],
    reviews_today: list[ReviewLog],
    practice_sessions: list[PracticeSession],
    practice_today: list[PracticeSession],
    diagnostics: list[MemoryDiagnostic],
    due_cards: list[MemoryCard],
    cheko_cards: list[MemoryCard],
    cheko_due_cards: list[MemoryCard],
    rag_brief: dict[str, object],
) -> dict[str, object]:
    metrics = {
        "raw_records": len(records),
        "memory_cards": len(cards),
        "review_logs": len(review_logs),
        "reviews_today": len(reviews_today),
        "practice_sessions": len(practice_sessions),
        "practice_today": len(practice_today),
        "practice_score_ratio": _average_practice_score_ratio(practice_sessions),
        "weak_memory_cards": sum(
            1 for diagnostic in diagnostics if diagnostic.status in {"leech", "unstable"}
        ),
        "due_cards": len(due_cards),
        "cheko_cards": len(cheko_cards),
        "cheko_due_cards": len(cheko_due_cards),
    }
    return {
        "version": 1,
        "as_of": day.isoformat(),
        "status": status,
        "phase": phase,
        "countdown": countdown,
        "risk": risk,
        "schema_version": schema_version,
        "reserve_days_consumed": reserve_days_consumed,
        "review_backlog_ratio": review_backlog_ratio,
        "metrics": metrics,
        "night_focus": _night_focus(metrics, diagnostics),
        "rag_brief": rag_brief,
        "source_counts": _count(record.source.value for record in records),
        "card_type_counts": _count(card.card_type.value for card in cards),
        "front_counts": _count(front.value for card in cards for front in card.fronts),
        "practice_front_counts": _count(session.front.value for session in practice_sessions),
        "memory_diagnostics": [
            {
                "card_id": diagnostic.card_id,
                "title": diagnostic.title,
                "card_type": diagnostic.card_type,
                "fronts": list(diagnostic.fronts),
                "status": diagnostic.status,
                "action": diagnostic.action,
                "total_reviews": diagnostic.total_reviews,
                "low_grade_reviews": diagnostic.low_grade_reviews,
                "last_grade": diagnostic.last_grade,
                "average_grade": diagnostic.average_grade,
                "next_due": diagnostic.next_due.isoformat() if diagnostic.next_due else None,
            }
            for diagnostic in diagnostics
            if diagnostic.status != "stable"
        ][:8],
        "recent_records": [
            {
                "id": record.id,
                "source": record.source.value,
                "summary": record.summary,
                "topics": list(record.topics),
                "promotion_status": record.promotion_status,
            }
            for record in records[-5:]
        ],
        "recent_cards": [
            {
                "id": card.id,
                "title": card.title,
                "card_type": card.card_type.value,
                "fronts": [front.value for front in card.fronts],
                "next_due": card.next_due.isoformat() if card.next_due else None,
                "review_count": card.review_count,
            }
            for card in cards[-8:]
        ],
        "recent_reviews": [
            {
                "id": log.id,
                "card_id": log.card_id,
                "reviewed_on": log.reviewed_on.isoformat(),
                "grade": log.grade,
                "retrieval_strength": log.retrieval_strength,
                "next_due": log.next_due.isoformat(),
            }
            for log in review_logs[-8:]
        ],
        "recent_practice": [
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
            for session in practice_sessions[-8:]
        ],
    }


def _count(values: Iterable[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def _night_focus(
    metrics: dict[str, object],
    diagnostics: list[MemoryDiagnostic],
) -> dict[str, str]:
    weak_count = int(metrics.get("weak_memory_cards", 0))
    due_count = int(metrics.get("due_cards", 0))
    reviews_today = int(metrics.get("reviews_today", 0))
    practice_today = int(metrics.get("practice_today", 0))
    memory_cards = int(metrics.get("memory_cards", 0))
    weak_title = next(
        (
            diagnostic.title
            for diagnostic in diagnostics
            if diagnostic.status in {"leech", "unstable"}
        ),
        "",
    )

    if weak_count:
        reason = f"薄弱卡 {weak_count} 张"
        if weak_title:
            reason = f"{reason}，先看「{weak_title}」"
        return {
            "title": "今晚先修复薄弱记忆",
            "reason": reason,
            "action": "从记忆诊断第一条开始，拆小卡、补反例或重写提示。",
        }
    if due_count:
        return {
            "title": "今晚先清空到期复习",
            "reason": f"到期卡 {due_count} 张，先保护检索节奏。",
            "action": "先做检索，再把低于 3 分的卡片放入明天修复。",
        }
    if reviews_today == 0 and memory_cards:
        return {
            "title": "今晚先补一次主动回忆",
            "reason": "今天还没有复习记录，记忆闭环断了一次。",
            "action": "挑 3 张核心卡闭卷回答，再记录评分。",
        }
    if practice_today == 0:
        return {
            "title": "今晚先补一条实战记录",
            "reason": "今天还没有选择、案例或论文练习。",
            "action": "选最弱题型做一次可评分练习，再记录错因。",
        }
    return {
        "title": "今晚沉淀今天的增量",
        "reason": "复习与实战都有记录，可以把材料转成长期资产。",
        "action": "从 Mein/Du/Uns 中挑一条，升级为记忆卡或练习素材。",
    }


def _average_practice_score_ratio(sessions: list[PracticeSession]) -> float | None:
    ratios = [
        float(session.score) / float(session.max_score)
        for session in sessions
        if session.score is not None and session.max_score not in (None, 0)
    ]
    if not ratios:
        return None
    return round(sum(ratios) / len(ratios), 4)
