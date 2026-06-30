from __future__ import annotations

from html import escape

from .storage import PracticeSession
from .web_labels import (
    _date_text,
    _duration_text,
    _front_label,
    _score_ratio_text,
    _score_text,
    _value_text,
)


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
