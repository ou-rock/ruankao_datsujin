from __future__ import annotations

from datetime import date
from html import escape

from .storage import MemoryCard
from .web_labels import (
    _card_type_label,
    _date_text,
    _fronts_label,
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
