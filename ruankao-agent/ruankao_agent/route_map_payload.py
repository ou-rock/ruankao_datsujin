from __future__ import annotations

from datetime import date
from pathlib import Path

from .domain import ExamFront
from .memory import MemoryDiagnostic, diagnose_memory
from .storage import MemoryCard, PracticeSession, RuankaoStore


FRONT_LABELS = {
    ExamFront.CHOICE: "选择题",
    ExamFront.CASE: "案例题",
    ExamFront.ESSAY: "论文题",
}


def build_route_map_payload(root: Path | str, day: date) -> dict[str, object]:
    root_path = Path(root)
    store = RuankaoStore(root_path / "data" / "ruankao.db")
    store.initialize()
    cards = store.list_memory_cards()
    practice_sessions = store.list_practice_sessions()
    diagnostics = diagnose_memory(cards, store.list_review_logs(), as_of=day)
    return _route_map_payload(day, cards, diagnostics, practice_sessions)


def _route_map_payload(
    day: date,
    cards: list[MemoryCard],
    diagnostics: tuple[MemoryDiagnostic, ...],
    practice_sessions: list[PracticeSession],
) -> dict[str, object]:
    diagnostic_by_card = {diagnostic.card_id: diagnostic for diagnostic in diagnostics}
    return {
        "version": 1,
        "as_of": day.isoformat(),
        "routes": [
            _front_route(front, cards, diagnostic_by_card, practice_sessions, day)
            for front in (ExamFront.CHOICE, ExamFront.CASE, ExamFront.ESSAY)
        ],
    }


def _front_route(
    front: ExamFront,
    cards: list[MemoryCard],
    diagnostic_by_card: dict[int, MemoryDiagnostic],
    practice_sessions: list[PracticeSession],
    day: date,
) -> dict[str, object]:
    route_cards = [card for card in cards if front in card.fronts]
    route_practice = [session for session in practice_sessions if session.front == front]
    practice_today = [session for session in route_practice if session.created_on == day]
    due_cards = [card for card in route_cards if card.next_due is not None and card.next_due <= day]
    route_diagnostics = [diagnostic_by_card[card.id] for card in route_cards if card.id in diagnostic_by_card]
    weak = [item for item in route_diagnostics if item.status in {"leech", "unstable"}]
    untested = [item for item in route_diagnostics if item.status == "untested"]
    status, action = _route_status_and_action(route_cards, due_cards, weak, untested, route_practice)
    focus_titles = [item.title for item in weak[:3]] or [card.title for card in due_cards[:3]]
    last_practice = max(
        (session.created_on for session in route_practice if session.created_on is not None),
        default=None,
    )
    return {
        "front": front.value,
        "label": FRONT_LABELS[front],
        "status": status,
        "action": action,
        "total_cards": len(route_cards),
        "due_cards": len(due_cards),
        "weak_cards": len(weak),
        "untested_cards": len(untested),
        "practice_sessions": len(route_practice),
        "practice_today": len(practice_today),
        "average_score_ratio": _average_score_ratio(route_practice),
        "last_practice_on": last_practice.isoformat() if last_practice else None,
        "focus_titles": focus_titles,
    }


def _route_status_and_action(
    cards: list[MemoryCard],
    due_cards: list[MemoryCard],
    weak: list[MemoryDiagnostic],
    untested: list[MemoryDiagnostic],
    practice_sessions: list[PracticeSession],
) -> tuple[str, str]:
    if not cards:
        return ("red", "这条战线没有记忆卡，先补 3 张基础卡。")
    if weak:
        return ("red", "先修复薄弱卡，再追加新题。")
    if due_cards:
        return ("yellow", "先清空到期卡，再做新练习。")
    if not practice_sessions:
        return ("yellow", "这条战线还没有实战记录，先补一次练习。")
    if len(untested) > len(cards) / 2:
        return ("yellow", "未测卡过多，安排首次检索。")
    return ("green", "维持当前节奏，继续积累题型素材。")


def _average_score_ratio(sessions: list[PracticeSession]) -> float | None:
    ratios = [
        float(session.score) / float(session.max_score)
        for session in sessions
        if session.score is not None and session.max_score not in (None, 0)
    ]
    if not ratios:
        return None
    return round(sum(ratios) / len(ratios), 4)
