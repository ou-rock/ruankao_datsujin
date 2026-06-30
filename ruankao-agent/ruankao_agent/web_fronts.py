from __future__ import annotations

from datetime import date
from html import escape

from .domain import ExamFront
from .storage import MemoryCard, PracticeSession
from .web_labels import _front_label, _risk_label


def _front_overview(
    cards: list[MemoryCard],
    due_cards: list[MemoryCard],
    practice_sessions: list[PracticeSession],
    today: date,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for front in (ExamFront.CHOICE, ExamFront.CASE, ExamFront.ESSAY):
        front_cards = [card for card in cards if front in card.fronts]
        front_due = [card for card in due_cards if front in card.fronts]
        front_practice = [session for session in practice_sessions if session.front == front]
        practice_today = [session for session in front_practice if session.created_on == today]
        if front_due:
            state = "red"
            action = "先清到期卡"
        elif not practice_today:
            state = "yellow"
            action = "今天补一次练习"
        else:
            state = "green"
            action = "保持节奏"
        rows.append(
            {
                "front": front.value,
                "label": _front_label(front),
                "state": state,
                "cards": len(front_cards),
                "due": len(front_due),
                "practice_today": len(practice_today),
                "action": action,
            }
        )
    return rows


def _front_cards(rows: list[dict[str, object]]) -> str:
    cards = []
    for row in rows:
        raw_state = str(row["state"])
        state = escape(raw_state)
        state_label = escape(_risk_label(raw_state))
        cards.append(
            f"""<div class="front-card {state}">
  <div class="front-head"><span>{escape(str(row["label"]))}</span><span class="front-state {state}">{state_label}</span></div>
  <div class="front-metrics">
    <div class="front-mini"><span>卡片</span><strong>{escape(str(row["cards"]))}</strong></div>
    <div class="front-mini"><span>到期</span><strong>{escape(str(row["due"]))}</strong></div>
    <div class="front-mini"><span>今日练习</span><strong>{escape(str(row["practice_today"]))}</strong></div>
  </div>
  <div class="front-action">{escape(str(row["action"]))}</div>
</div>"""
        )
    return "".join(cards)
