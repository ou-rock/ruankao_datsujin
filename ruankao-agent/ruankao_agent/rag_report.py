from __future__ import annotations

from datetime import date
from html import escape
from pathlib import Path

from .rag_observability import rag_observability_payload
from .rag_report_style import RAG_REPORT_STYLE
from .rag_types import RagBrief


def rag_brief_json_path(root: Path | str, as_of: date) -> Path:
    return Path(root) / "data" / "rag" / f"{as_of.isoformat()}.json"


def rag_brief_html_path(root: Path | str, as_of: date) -> Path:
    return Path(root) / "reports" / "rag" / f"{as_of.isoformat()}.html"


def rag_brief_to_payload(
    brief: RagBrief,
    *,
    root: Path | str | None = None,
) -> dict[str, object]:
    return {
        "version": 1,
        "query": brief.query,
        "as_of": brief.as_of.isoformat(),
        "retrieval_strategy": brief.retrieval_strategy,
        "corpus_size": brief.corpus_size,
        "chunk_count": brief.chunk_count,
        "recommended_action": brief.recommended_action,
        "answer_contract": list(brief.answer_contract),
        "observability": rag_observability_payload(root, brief.as_of),
        "progress_gates": [
            {
                "severity": gate.severity,
                "kind": gate.kind,
                "title": gate.title,
                "reason": gate.reason,
                "action": gate.action,
            }
            for gate in brief.progress_gates
        ],
        "hits": [
            {
                "ref": hit.document.ref,
                "chunk_ref": hit.chunk_ref,
                "kind": hit.document.kind,
                "source_label": hit.document.source_label,
                "title": hit.document.title,
                "fronts": [front.value for front in hit.document.fronts],
                "topics": list(hit.document.topics),
                "progress_status": hit.document.progress_status,
                "score": hit.score,
                "reasons": list(hit.reasons),
                "retrieval_strategy": hit.retrieval_strategy,
                "score_breakdown": [
                    {"name": name, "value": value}
                    for name, value in hit.score_breakdown
                ],
                "snippet": hit.snippet,
                "action_hint": hit.document.action_hint,
            }
            for hit in brief.hits
        ],
    }


def render_rag_brief(payload: dict[str, object]) -> str:
    gates = payload.get("progress_gates", [])
    hits = payload.get("hits", [])
    contract = payload.get("answer_contract", [])
    observability = payload.get("observability", {})
    assert isinstance(gates, list)
    assert isinstance(hits, list)
    assert isinstance(contract, list)
    assert isinstance(observability, dict)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RAG 记忆与进步控制 {escape(str(payload["as_of"]))}</title>
  <style>
{RAG_REPORT_STYLE}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>RAG 记忆与进步控制</h1>
      <p class="lead">查询：{escape(str(payload["query"]))}</p>
      <p class="lead">检索策略：{escape(str(payload.get("retrieval_strategy", "token-hybrid-progress")))}；语料 {escape(str(payload.get("corpus_size", 0)))} 条；切块 {escape(str(payload.get("chunk_count", 0)))} 个</p>
      <p class="lead">建议动作：{escape(str(payload["recommended_action"]))}</p>
    </header>
    <section>
      <h2>可观察链路</h2>
      <div class="trace-grid">{_observability_items(observability.get("trace", []))}</div>
    </section>
    <section>
      <h2>存储与后端边界</h2>
      <div class="trace-grid">{_observability_items(observability.get("storage", []))}</div>
      <div class="trace-grid policy">{_observability_items(observability.get("backend_policy", []))}</div>
    </section>
    <section>
      <h2>进步闸门</h2>
      <div class="list">{_gate_items(gates)}</div>
    </section>
    <section>
      <h2>召回证据</h2>
      <div class="list">{_hit_items(hits)}</div>
    </section>
    <section>
      <h2>回答契约</h2>
      <div class="list">{_contract_items(contract)}</div>
    </section>
  </main>
</body>
</html>
"""


def _gate_items(gates: list[object]) -> str:
    if not gates:
        return '<div class="item green">暂无进步闸门。保持今日闭环。</div>'
    items = []
    for gate in gates:
        assert isinstance(gate, dict)
        items.append(
            f"""<div class="item {escape(str(gate["severity"]))}">
  <strong>{escape(str(gate["title"]))}</strong>
  <div>{escape(str(gate["reason"]))}</div>
  <div class="meta-row">
    <span>{escape(_severity_label(gate["severity"]))}</span>
    <span>{escape(str(gate["kind"]))}</span>
  </div>
  <div>{escape(str(gate["action"]))}</div>
</div>"""
        )
    return "".join(items)


def _hit_items(hits: list[object]) -> str:
    if not hits:
        return '<div class="item">暂无召回证据。先录入三源材料或记忆卡。</div>'
    items = []
    for hit in hits:
        assert isinstance(hit, dict)
        items.append(
            f"""<div class="item">
  <strong>{escape(str(hit["title"]))}</strong>
  <div>{escape(str(hit["snippet"]))}</div>
  <div class="meta-row">
    <span>{escape(str(hit["source_label"]))}</span>
    <span>{escape(str(hit["ref"]))}</span>
    <span>{escape(str(hit.get("chunk_ref", "")))}</span>
    <span>{escape(str(hit.get("retrieval_strategy", "")))}</span>
    <span>得分：{escape(str(hit["score"]))}</span>
    <span>题型：{escape(_fronts_text(hit["fronts"]))}</span>
    <span>状态：{escape(_status_label(str(hit["progress_status"])))}</span>
  </div>
  <div class="meta-row">{_reason_spans(hit["reasons"])}</div>
  <div class="meta-row">{_breakdown_spans(hit.get("score_breakdown", []))}</div>
  <div>{escape(str(hit["action_hint"]))}</div>
</div>"""
        )
    return "".join(items)


def _contract_items(contract: list[object]) -> str:
    if not contract:
        return '<div class="item">暂无回答契约。</div>'
    return "".join(f'<div class="item">{escape(str(item))}</div>' for item in contract)


def _observability_items(items: object) -> str:
    if not isinstance(items, list) or not items:
        return '<div class="item">暂无可观察信息。</div>'
    rendered = []
    for item in items:
        if not isinstance(item, dict):
            continue
        rendered.append(
            f"""<div class="item trace-item">
  <strong>{escape(str(item.get("label", "")))}</strong>
  <div>{escape(str(item.get("detail", "")))}</div>
</div>"""
        )
    return "".join(rendered) or '<div class="item">暂无可观察信息。</div>'


def _reason_spans(reasons: object) -> str:
    if not isinstance(reasons, list):
        return ""
    return "".join(f"<span>{escape(str(reason))}</span>" for reason in reasons)


def _breakdown_spans(breakdown: object) -> str:
    if not isinstance(breakdown, list):
        return ""
    spans = []
    for item in breakdown:
        if not isinstance(item, dict):
            continue
        spans.append(
            f"<span>{escape(str(item.get('name', 'score')))}：{escape(str(item.get('value', 0)))}</span>"
        )
    return "".join(spans)


def _fronts_text(fronts: object) -> str:
    if not isinstance(fronts, list) or not fronts:
        return "未标注"
    labels = {
        "choice": "选择题",
        "case": "案例题",
        "essay": "论文题",
    }
    return "、".join(labels.get(str(front), str(front)) for front in fronts)


def _status_label(status: str) -> str:
    return {
        "leech": "反复低分",
        "unstable": "不稳定",
        "due": "到期",
        "untested": "未检验",
        "low_score": "练习低分",
    }.get(status, status)


def _severity_label(severity: object) -> str:
    return {
        "red": "红色闸门",
        "yellow": "黄色闸门",
        "green": "绿色",
    }.get(str(severity), str(severity))
