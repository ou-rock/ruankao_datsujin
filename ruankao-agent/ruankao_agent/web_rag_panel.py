from __future__ import annotations

from html import escape

from .web_labels import _gate_severity_label, _rag_status_label


def _rag_panel(brief: dict[str, object]) -> str:
    gates = brief.get("progress_gates", [])
    hits = brief.get("hits", [])
    assert isinstance(gates, list)
    assert isinstance(hits, list)
    gate = gates[0] if gates else None
    hit = hits[0] if hits else None
    return f"""<div class="split">
  <div>
    <h3>建议动作</h3>
    <div class="list">
      <div class="item">
        <div class="item-title">{escape(str(brief.get("recommended_action", "维持今日闭环。")))}</div>
        <div class="meta">查询：{escape(str(brief.get("query", "")))}</div>
      </div>
      {_rag_gate_item(gate)}
    </div>
  </div>
  <div>
    <h3>最高召回证据</h3>
    <div class="list">{_rag_hit_item(hit)}</div>
  </div>
</div>"""


def _rag_gate_item(gate: object) -> str:
    if not isinstance(gate, dict):
        return '<div class="item">暂无进步闸门。</div>'
    return f"""<div class="item">
  <div class="item-title"><span>{escape(str(gate.get("title", "")))}</span><span>{escape(_gate_severity_label(gate.get("severity")))}</span></div>
  <div>{escape(str(gate.get("reason", "")))}</div>
  <div class="meta">{escape(str(gate.get("action", "")))}</div>
</div>"""


def _rag_hit_item(hit: object) -> str:
    if not isinstance(hit, dict):
        return '<div class="item">暂无召回证据。</div>'
    return f"""<div class="item">
  <div class="item-title"><span>{escape(str(hit.get("title", "")))}</span><span>{escape(str(hit.get("source_label", "")))}</span></div>
  <div>{escape(str(hit.get("snippet", "")))}</div>
  <div class="meta-row">
    <span>{escape(str(hit.get("ref", "")))}</span>
    <span>{escape(str(hit.get("chunk_ref", "")))}</span>
    <span>{escape(str(hit.get("retrieval_strategy", "")))}</span>
    <span>得分：{escape(str(hit.get("score", "")))}</span>
    <span>状态：{escape(_rag_status_label(hit.get("progress_status")))}</span>
  </div>
  <div class="meta">{escape(str(hit.get("action_hint", "")))}</div>
</div>"""
