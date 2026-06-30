from __future__ import annotations

from html import escape

from .receipts_format import (
    _card_type_label,
    _duration_text,
    _front_label,
    _fronts_label,
    _joined_text,
    _memory_status_label,
    _promotion_status_label,
    _score_text,
    _source_label,
    _value_text,
)


def _recent_records(records: list[object]) -> str:
    if not records:
        return '<div class="item">暂无材料</div>'
    items = []
    for item in records:
        assert isinstance(item, dict)
        items.append(
            f"""<div class="item">
  <strong>#{escape(str(item["id"]))} {escape(_source_label(item["source"]))}</strong>
  <div>{escape(str(item["summary"]))}</div>
  <div class="meta-row">
    <span>状态：{escape(_promotion_status_label(item["promotion_status"]))}</span>
    <span>主题：{escape(_joined_text(item["topics"]))}</span>
  </div>
</div>"""
        )
    return "".join(items)


def _memory_diagnostics(diagnostics: list[object]) -> str:
    if not diagnostics:
        return '<div class="item">暂无薄弱诊断。继续保持复习节奏。</div>'
    items = []
    for item in diagnostics:
        assert isinstance(item, dict)
        items.append(
            f"""<div class="item">
  <strong>#{escape(str(item["card_id"]))} {escape(str(item["title"]))}</strong>
  <div>{escape(str(item["action"]))}</div>
  <div class="meta-row">
    <span>状态：{escape(_memory_status_label(item["status"]))}</span>
    <span>类型：{escape(_card_type_label(item["card_type"]))}</span>
    <span>低分：{escape(str(item["low_grade_reviews"]))}次</span>
    <span>最近：{escape(_value_text(item["last_grade"]))}</span>
    <span>平均：{escape(_value_text(item["average_grade"]))}</span>
  </div>
</div>"""
        )
    return "".join(items)


def _rag_brief(brief: dict[object, object]) -> str:
    gates = brief.get("progress_gates", [])
    hits = brief.get("hits", [])
    assert isinstance(gates, list)
    assert isinstance(hits, list)
    gate = gates[0] if gates else None
    hit = hits[0] if hits else None
    gate_html = (
        _rag_gate(gate)
        if isinstance(gate, dict)
        else '<div class="item">暂无进步闸门。</div>'
    )
    hit_html = (
        _rag_hit(hit)
        if isinstance(hit, dict)
        else '<div class="item">暂无召回证据。</div>'
    )
    return f"""<div class="list">
  <div class="item focus">
    <span>建议动作</span>
    <strong>{escape(str(brief.get("recommended_action", "维持今日闭环。")))}</strong>
    <p>{escape(str(brief.get("query", "")))}</p>
  </div>
  {gate_html}
  {hit_html}
</div>"""


def _rag_gate(gate: dict[object, object]) -> str:
    return f"""<div class="item">
  <strong>进步闸门：{escape(str(gate.get("title", "")))}</strong>
  <div>{escape(str(gate.get("reason", "")))}</div>
  <div class="meta-row">
    <span>{escape(str(gate.get("severity", "")))}</span>
    <span>{escape(str(gate.get("kind", "")))}</span>
  </div>
  <div>{escape(str(gate.get("action", "")))}</div>
</div>"""


def _rag_hit(hit: dict[object, object]) -> str:
    return f"""<div class="item">
  <strong>召回证据：{escape(str(hit.get("title", "")))}</strong>
  <div>{escape(str(hit.get("snippet", "")))}</div>
  <div class="meta-row">
    <span>{escape(str(hit.get("source_label", "")))}</span>
    <span>{escape(str(hit.get("ref", "")))}</span>
    <span>{escape(str(hit.get("chunk_ref", "")))}</span>
    <span>{escape(str(hit.get("retrieval_strategy", "")))}</span>
    <span>得分：{escape(str(hit.get("score", "")))}</span>
  </div>
</div>"""


def _recent_cards(cards: list[object]) -> str:
    if not cards:
        return '<div class="item">暂无卡片</div>'
    items = []
    for item in cards:
        assert isinstance(item, dict)
        items.append(
            f"""<div class="item">
  <strong>#{escape(str(item["id"]))} {escape(str(item["title"]))}</strong>
  <div class="meta-row">
    <span>类型：{escape(_card_type_label(item["card_type"]))}</span>
    <span>题型：{escape(_fronts_label(item["fronts"]))}</span>
    <span>到期：{escape(_value_text(item["next_due"]))}</span>
    <span>复习：{escape(str(item["review_count"]))}次</span>
  </div>
</div>"""
        )
    return "".join(items)


def _recent_reviews(reviews: list[object]) -> str:
    if not reviews:
        return '<div class="item">暂无复习记录</div>'
    items = []
    for item in reviews:
        assert isinstance(item, dict)
        items.append(
            f"""<div class="item">
  <strong>复习 #{escape(str(item["id"]))} 卡片 #{escape(str(item["card_id"]))}</strong>
  <div class="meta-row">
    <span>日期：{escape(str(item["reviewed_on"]))}</span>
    <span>评分：{escape(str(item["grade"]))}</span>
    <span>强度：{escape(str(item["retrieval_strength"]))}</span>
    <span>下次：{escape(str(item["next_due"]))}</span>
  </div>
</div>"""
        )
    return "".join(items)


def _recent_practice(sessions: list[object]) -> str:
    if not sessions:
        return '<div class="item">暂无练习记录</div>'
    items = []
    for item in sessions:
        assert isinstance(item, dict)
        score = _score_text(item["score"], item["max_score"])
        items.append(
            f"""<div class="item">
  <strong>#{escape(str(item["id"]))} {escape(_front_label(item["front"]))} {escape(str(item["topic"]))}</strong>
  <div>{escape(str(item["summary"]))}</div>
  <div class="meta-row">
    <span>得分：{escape(score)}</span>
    <span>来源：{escape(_value_text(item["source"]))}</span>
    <span>耗时：{escape(_duration_text(item["duration_minutes"]))}</span>
    <span>日期：{escape(_value_text(item["created_on"]))}</span>
  </div>
  <div class="meta">错因：{escape(_value_text(item["mistakes"]))}</div>
</div>"""
        )
    return "".join(items)
