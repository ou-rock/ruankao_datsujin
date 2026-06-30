from __future__ import annotations

from datetime import date
from html import escape

from .memory import MemoryDiagnostic
from .storage import MemoryCard, PracticeSession
from .web_labels import (
    _card_type_label,
    _date_text,
    _duration_text,
    _front_label,
    _fronts_label,
    _memory_status_label,
    _score_ratio_text,
    _score_text,
    _value_text,
)


def _card_list(cards: list[MemoryCard], *, with_review: bool, today: date) -> str:
    if not cards:
        return '<div class="empty">还没有内容。下一步先沉淀一条材料或创建一张卡。</div>'
    items = []
    for card in reversed(cards):
        review_form = ""
        if with_review:
            review_form = f"""
            <form method="post" action="/reviews" style="margin-top:8px;">
              <input type="hidden" name="card_id" value="{card.id}">
              <input type="hidden" name="reviewed_on" value="{escape(today.isoformat())}">
              <div class="grade-row" aria-label="复习评分">
                {_review_grade_buttons()}
              </div>
            </form>
            """
        items.append(
            f"""<div class="item">
  <div class="item-title"><span>#{card.id} {escape(card.title)}</span><span>{escape(_card_type_label(card.card_type))}</span></div>
  <div class="meta-row">
    <span>题型：{escape(_fronts_label(card.fronts))}</span>
    <span>到期：{escape(_date_text(card.next_due))}</span>
    <span>复习：{card.review_count}次</span>
  </div>
  <div class="meta">{escape(card.prompt[:140])}</div>
  {review_form}
</div>"""
        )
    return '<div class="list">' + "".join(items) + "</div>"


def _review_grade_buttons() -> str:
    labels = (
        (5, "很稳"),
        (4, "会"),
        (3, "勉强"),
        (2, "模糊"),
        (1, "不会"),
        (0, "空白"),
    )
    buttons = []
    for grade, label in labels:
        low = " low" if grade < 3 else ""
        buttons.append(
            f"""<button class="grade-button{low}" type="submit" name="grade" value="{grade}" title="{grade} {escape(label)}">
  <span>{grade}</span><small>{escape(label)}</small>
</button>"""
        )
    return "".join(buttons)


def _practice_list(sessions: list[PracticeSession]) -> str:
    if not sessions:
        return '<div class="empty">还没有练习记录。先记录一次选择、案例或论文练习。</div>'
    items = []
    for session in reversed(sessions):
        score = _score_text(session.score, session.max_score)
        ratio = _score_ratio_text(session.score, session.max_score)
        items.append(
            f"""<div class="item">
  <div class="item-title"><span>#{session.id} {escape(session.topic)}</span><span>{escape(_front_label(session.front))}</span></div>
  <div class="meta-row">
    <span>得分：{escape(score)}</span>
    <span>得分率：{escape(ratio)}</span>
    <span>来源：{escape(_value_text(session.source))}</span>
    <span>耗时：{escape(_duration_text(session.duration_minutes))}</span>
    <span>日期：{escape(_date_text(session.created_on))}</span>
  </div>
  <div class="meta">{escape(session.summary[:140])}</div>
</div>"""
        )
    return '<div class="list">' + "".join(items) + "</div>"


def _risk_reason_list(reasons: tuple[str, ...]) -> str:
    items = [f'<div class="item">{escape(reason)}</div>' for reason in reasons]
    return '<div class="list">' + "".join(items) + "</div>"


def _diagnostic_list(diagnostics: list[MemoryDiagnostic]) -> str:
    if not diagnostics:
        return '<div class="empty">暂无薄弱诊断。先完成今日复习。</div>'
    items = []
    for diagnostic in diagnostics:
        items.append(
            f"""<div class="item">
  <div class="item-title"><span>#{diagnostic.card_id} {escape(diagnostic.title)}</span><span>{escape(_memory_status_label(diagnostic.status))}</span></div>
  <div class="meta">{escape(diagnostic.action)}</div>
  <div class="meta-row">
    <span>低分：{diagnostic.low_grade_reviews}次</span>
    <span>最近：{escape(_value_text(diagnostic.last_grade))}</span>
    <span>平均：{escape(_value_text(diagnostic.average_grade))}</span>
  </div>
</div>"""
        )
    return '<div class="list">' + "".join(items) + "</div>"
