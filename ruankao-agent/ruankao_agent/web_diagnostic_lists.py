from __future__ import annotations

from html import escape

from .memory import MemoryDiagnostic
from .web_labels import (
    _memory_status_label,
    _value_text,
)


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
