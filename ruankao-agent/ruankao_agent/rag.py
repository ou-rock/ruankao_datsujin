from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path
from typing import Iterable, Sequence

from .domain import ExamFront
from .memory import MemoryDiagnostic, diagnose_memory
from .storage import MemoryCard, PracticeSession, RawRecord, RuankaoStore


DEFAULT_RAG_QUERY = "今天如何用记忆、错因和三题型进步信号安排学习？"

_ASCII_RE = re.compile(r"[a-z0-9_+#.-]+")
_CJK_RE = re.compile(r"[\u4e00-\u9fff]+")


@dataclass(frozen=True, slots=True)
class RagDocument:
    ref: str
    kind: str
    source_label: str
    title: str
    body: str
    fronts: tuple[ExamFront, ...]
    topics: tuple[str, ...]
    progress_status: str
    priority: float
    action_hint: str


@dataclass(frozen=True, slots=True)
class RagHit:
    document: RagDocument
    score: float
    reasons: tuple[str, ...]
    snippet: str


@dataclass(frozen=True, slots=True)
class ProgressGate:
    severity: str
    kind: str
    title: str
    reason: str
    action: str


@dataclass(frozen=True, slots=True)
class RagBrief:
    query: str
    as_of: date
    hits: tuple[RagHit, ...]
    progress_gates: tuple[ProgressGate, ...]
    recommended_action: str
    answer_contract: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RagBriefResult:
    as_of: date
    json_path: Path
    html_path: Path
    hit_count: int
    gate_count: int
    recommended_action: str


def build_rag_brief(
    store: RuankaoStore,
    *,
    query: str = DEFAULT_RAG_QUERY,
    fronts: Sequence[ExamFront] = (),
    as_of: date | None = None,
    limit: int = 6,
) -> RagBrief:
    day = as_of or date.today()
    records = store.list_raw_records()
    cards = store.list_memory_cards()
    review_logs = store.list_review_logs()
    practice_sessions = store.list_practice_sessions()
    diagnostics = diagnose_memory(cards, review_logs, as_of=day)
    documents = build_rag_documents(
        records=records,
        cards=cards,
        practice_sessions=practice_sessions,
        diagnostics=diagnostics,
        as_of=day,
    )
    hits = retrieve_rag_documents(
        documents,
        query=query,
        fronts=fronts,
        limit=limit,
    )
    gates = build_progress_gates(
        records=records,
        cards=cards,
        practice_sessions=practice_sessions,
        diagnostics=diagnostics,
        as_of=day,
    )
    return RagBrief(
        query=query.strip() or DEFAULT_RAG_QUERY,
        as_of=day,
        hits=hits,
        progress_gates=gates,
        recommended_action=_recommended_action(hits, gates),
        answer_contract=(
            "先处理最高优先级进步闸门，再展开资料解释。",
            "回答必须引用召回证据，区分 Mein、Du、Uns、记忆卡和练习记录。",
            "每次学习结束必须产出下一张卡、一次练习或一条三源沉淀。",
        ),
    )


def build_rag_documents(
    *,
    records: Iterable[RawRecord],
    cards: Iterable[MemoryCard],
    practice_sessions: Iterable[PracticeSession],
    diagnostics: Iterable[MemoryDiagnostic],
    as_of: date,
) -> tuple[RagDocument, ...]:
    diagnostic_by_card = {diagnostic.card_id: diagnostic for diagnostic in diagnostics}
    documents: list[RagDocument] = []
    for card in cards:
        diagnostic = diagnostic_by_card.get(card.id)
        status = diagnostic.status if diagnostic else "stable"
        action = diagnostic.action if diagnostic else "保持当前间隔。"
        documents.append(_memory_card_document(card, status=status, action=action, as_of=as_of))
    for record in records:
        documents.append(_raw_record_document(record))
    for session in practice_sessions:
        documents.append(_practice_document(session))
    return tuple(documents)


def retrieve_rag_documents(
    documents: Iterable[RagDocument],
    *,
    query: str,
    fronts: Sequence[ExamFront] = (),
    limit: int = 6,
) -> tuple[RagHit, ...]:
    clean_query = query.strip() or DEFAULT_RAG_QUERY
    query_tokens = _tokens(clean_query)
    front_filter = set(fronts)
    hits: list[RagHit] = []
    for document in documents:
        scored = _score_document(document, query_tokens, clean_query, front_filter)
        if scored is None:
            continue
        score, reasons = scored
        if score <= 0:
            continue
        hits.append(
            RagHit(
                document=document,
                score=round(score, 3),
                reasons=tuple(reasons),
                snippet=_snippet(document.body, query_tokens),
            )
        )
    return tuple(sorted(hits, key=lambda hit: (-hit.score, hit.document.ref))[: max(1, limit)])


def build_progress_gates(
    *,
    records: Iterable[RawRecord],
    cards: Iterable[MemoryCard],
    practice_sessions: Iterable[PracticeSession],
    diagnostics: Iterable[MemoryDiagnostic],
    as_of: date,
) -> tuple[ProgressGate, ...]:
    gates: list[ProgressGate] = []
    for diagnostic in diagnostics:
        if diagnostic.status == "leech":
            gates.append(
                ProgressGate(
                    severity="red",
                    kind="weak-memory",
                    title=diagnostic.title,
                    reason=f"反复低分 {diagnostic.low_grade_reviews} 次，检索强度不可信。",
                    action=diagnostic.action,
                )
            )
        elif diagnostic.status == "unstable":
            gates.append(
                ProgressGate(
                    severity="red",
                    kind="unstable-memory",
                    title=diagnostic.title,
                    reason="最近一次主动回忆低于 3 分。",
                    action=diagnostic.action,
                )
            )
        elif diagnostic.status == "due":
            gates.append(
                ProgressGate(
                    severity="yellow",
                    kind="due-review",
                    title=diagnostic.title,
                    reason=f"下次复习日已到：{diagnostic.next_due.isoformat() if diagnostic.next_due else as_of.isoformat()}。",
                    action=diagnostic.action,
                )
            )

    cards_list = list(cards)
    practice_list = list(practice_sessions)
    for front in ExamFront:
        front_cards = [card for card in cards_list if front in card.fronts]
        front_practice = [session for session in practice_list if session.front is front]
        if not front_cards:
            gates.append(
                ProgressGate(
                    severity="red",
                    kind="front-card-gap",
                    title=_front_label(front),
                    reason="这条战线还没有可检索的记忆卡。",
                    action="先从三源材料或错题中生成 3 张基础卡。",
                )
            )
        elif not front_practice:
            gates.append(
                ProgressGate(
                    severity="yellow",
                    kind="front-practice-gap",
                    title=_front_label(front),
                    reason="这条战线有记忆卡，但还没有实战记录验证。",
                    action="安排一次可评分练习，并记录错因。",
                )
            )

    for session in practice_list:
        ratio = _score_ratio(session)
        if ratio is not None and ratio < 0.6:
            gates.append(
                ProgressGate(
                    severity="red",
                    kind="low-practice-score",
                    title=session.topic,
                    reason=f"{_front_label(session.front)}练习得分率 {ratio:.0%}。",
                    action="先复盘错因，再把混淆点转成对比卡或场景卡。",
                )
            )

    raw_backlog = [
        record
        for record in records
        if record.promotion_status in {"raw", "extracted"} and record.source.value in {"mein", "du", "uns"}
    ]
    if len(raw_backlog) >= 3:
        gates.append(
            ProgressGate(
                severity="yellow",
                kind="raw-promotion-backlog",
                title="三源材料未升格",
                reason=f"还有 {len(raw_backlog)} 条材料停留在原始或已提炼状态。",
                action="挑最高频主题，升级为记忆卡、练习素材或原则候选。",
            )
        )

    return tuple(sorted(gates, key=_gate_sort_key)[:8])


def write_rag_brief(
    root: Path | str,
    *,
    query: str = DEFAULT_RAG_QUERY,
    fronts: Sequence[ExamFront] = (),
    as_of: date | None = None,
    limit: int = 6,
) -> RagBriefResult:
    root_path = Path(root)
    day = as_of or date.today()
    store = RuankaoStore(root_path / "data" / "ruankao.db")
    store.initialize()
    brief = build_rag_brief(store, query=query, fronts=fronts, as_of=day, limit=limit)
    payload = rag_brief_to_payload(brief)
    json_path = rag_brief_json_path(root_path, day)
    html_path = rag_brief_html_path(root_path, day)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(render_rag_brief(payload), encoding="utf-8")
    return RagBriefResult(
        as_of=day,
        json_path=json_path,
        html_path=html_path,
        hit_count=len(brief.hits),
        gate_count=len(brief.progress_gates),
        recommended_action=brief.recommended_action,
    )


def rag_brief_json_path(root: Path | str, as_of: date) -> Path:
    return Path(root) / "data" / "rag" / f"{as_of.isoformat()}.json"


def rag_brief_html_path(root: Path | str, as_of: date) -> Path:
    return Path(root) / "reports" / "rag" / f"{as_of.isoformat()}.html"


def rag_brief_to_payload(brief: RagBrief) -> dict[str, object]:
    return {
        "version": 1,
        "query": brief.query,
        "as_of": brief.as_of.isoformat(),
        "recommended_action": brief.recommended_action,
        "answer_contract": list(brief.answer_contract),
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
                "kind": hit.document.kind,
                "source_label": hit.document.source_label,
                "title": hit.document.title,
                "fronts": [front.value for front in hit.document.fronts],
                "topics": list(hit.document.topics),
                "progress_status": hit.document.progress_status,
                "score": hit.score,
                "reasons": list(hit.reasons),
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
    assert isinstance(gates, list)
    assert isinstance(hits, list)
    assert isinstance(contract, list)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RAG 记忆与进步控制 {escape(str(payload["as_of"]))}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172026;
      --muted: #5e6b73;
      --line: #cfd8dc;
      --paper: #ffffff;
      --band: #f5f7f5;
      --accent: #0f766e;
      --danger: #b91c1c;
      --warn: #b45309;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: #fbfcfb;
      line-height: 1.55;
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 24px 20px 48px;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      padding-bottom: 18px;
      margin-bottom: 16px;
    }}
    h1 {{ margin: 0; font-size: 28px; line-height: 1.2; letter-spacing: 0; }}
    h2 {{ margin: 0 0 12px; font-size: 19px; line-height: 1.3; }}
    section {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      padding: 16px;
      margin-top: 14px;
    }}
    .lead {{ color: var(--muted); margin: 8px 0 0; }}
    .item {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--band);
      padding: 11px;
    }}
    .list {{ display: grid; gap: 10px; }}
    .meta-row {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }}
    .meta-row span {{
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      color: var(--muted);
      padding: 4px 7px;
      font-size: 12px;
    }}
    .red {{ border-left: 4px solid var(--danger); }}
    .yellow {{ border-left: 4px solid var(--warn); }}
    .green {{ border-left: 4px solid var(--accent); }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>RAG 记忆与进步控制</h1>
      <p class="lead">查询：{escape(str(payload["query"]))}</p>
      <p class="lead">建议动作：{escape(str(payload["recommended_action"]))}</p>
    </header>
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


def _memory_card_document(
    card: MemoryCard,
    *,
    status: str,
    action: str,
    as_of: date,
) -> RagDocument:
    priority = {
        "leech": 6.0,
        "unstable": 5.0,
        "due": 4.0,
        "untested": 2.0,
        "stable": 0.5,
    }.get(status, 0.5)
    if card.next_due is not None and card.next_due <= as_of:
        priority += 1.0
    body = (
        f"问题：{card.prompt}\n"
        f"答案：{card.answer}\n"
        f"类型：{card.card_type.value}\n"
        f"复习次数：{card.review_count}\n"
        f"检索强度：{card.retrieval_strength}\n"
        f"存储强度：{card.storage_strength}"
    )
    return RagDocument(
        ref=f"memory:{card.id}",
        kind="memory_card",
        source_label="记忆卡",
        title=card.title,
        body=body,
        fronts=card.fronts,
        topics=(card.card_type.value,),
        progress_status=status,
        priority=priority,
        action_hint=action,
    )


def _raw_record_document(record: RawRecord) -> RagDocument:
    priority = {
        "raw": 2.0,
        "extracted": 1.5,
        "tested": 1.0,
        "promoted": 0.4,
        "rejected": -2.0,
    }.get(record.promotion_status, 0.5)
    source_label = {
        "mein": "Mein",
        "du": "Du",
        "uns": "Uns",
    }.get(record.source.value, record.source.value)
    return RagDocument(
        ref=f"raw:{record.id}",
        kind="raw_record",
        source_label=source_label,
        title=record.summary,
        body=record.text,
        fronts=record.fronts,
        topics=record.topics,
        progress_status=record.promotion_status,
        priority=priority,
        action_hint="判断它是否应该升格为记忆卡、练习素材或原则候选。",
    )


def _practice_document(session: PracticeSession) -> RagDocument:
    ratio = _score_ratio(session)
    priority = 1.0
    status = "recorded"
    if ratio is not None and ratio < 0.6:
        priority = 5.0
        status = "low_score"
    elif ratio is not None and ratio < 0.75:
        priority = 3.0
        status = "needs_review"
    if session.mistakes:
        priority += 1.0
    body = (
        f"摘要：{session.summary}\n"
        f"错因：{session.mistakes or '未记录'}\n"
        f"来源：{session.source or '未记录'}\n"
        f"得分：{_score_text(session)}"
    )
    return RagDocument(
        ref=f"practice:{session.id}",
        kind="practice_session",
        source_label="练习记录",
        title=session.topic,
        body=body,
        fronts=(session.front,),
        topics=(session.source,) if session.source else (),
        progress_status=status,
        priority=priority,
        action_hint="复盘错因，并把可复用边界转成卡片或下一次练习。",
    )


def _score_document(
    document: RagDocument,
    query_tokens: set[str],
    query: str,
    front_filter: set[ExamFront],
) -> tuple[float, list[str]] | None:
    if front_filter and document.fronts and front_filter.isdisjoint(document.fronts):
        return None
    haystack = f"{document.title}\n{document.body}\n{' '.join(document.topics)}".lower()
    doc_tokens = _tokens(haystack)
    overlap = query_tokens & doc_tokens
    score = document.priority
    reasons = [f"进步权重 {document.priority:g}"]
    if overlap:
        score += len(overlap) * 2.0
        reasons.append("命中：" + "、".join(sorted(overlap)[:5]))
    if query and query.lower() in haystack:
        score += 4.0
        reasons.append("完整短语命中")
    if front_filter and not front_filter.isdisjoint(document.fronts):
        score += 2.0
        reasons.append("题型匹配")
    if document.progress_status in {"leech", "unstable", "due", "low_score"}:
        reasons.append(_status_label(document.progress_status))
    if query_tokens and not overlap and document.priority < 3:
        return None
    return score, reasons


def _tokens(text: str) -> set[str]:
    lowered = text.lower()
    tokens = set(_ASCII_RE.findall(lowered))
    for run in _CJK_RE.findall(lowered):
        if len(run) <= 2:
            tokens.add(run)
        else:
            tokens.update(run[index : index + 2] for index in range(len(run) - 1))
            tokens.update(run[index : index + 3] for index in range(len(run) - 2))
    return {token for token in tokens if token.strip()}


def _snippet(body: str, query_tokens: set[str], *, length: int = 96) -> str:
    clean = " ".join(body.split())
    if len(clean) <= length:
        return clean
    for token in sorted(query_tokens, key=len, reverse=True):
        index = clean.find(token)
        if index >= 0:
            start = max(0, index - 20)
            end = min(len(clean), start + length)
            prefix = "..." if start else ""
            suffix = "..." if end < len(clean) else ""
            return f"{prefix}{clean[start:end]}{suffix}"
    return f"{clean[:length]}..."


def _recommended_action(hits: Sequence[RagHit], gates: Sequence[ProgressGate]) -> str:
    if gates:
        gate = gates[0]
        return f"先处理「{gate.title}」：{gate.action}"
    if hits:
        hit = hits[0]
        return f"围绕「{hit.document.title}」开启学习回合：先闭卷回答，再沉淀 Mein/Du。"
    return "先录入一条三源材料或创建一张基础记忆卡，让 RAG 有可召回证据。"


def _gate_sort_key(gate: ProgressGate) -> tuple[int, str, str]:
    severity = {"red": 0, "yellow": 1, "green": 2}
    kind = {
        "weak-memory": 0,
        "unstable-memory": 1,
        "due-review": 2,
        "low-practice-score": 3,
        "front-card-gap": 4,
        "front-practice-gap": 5,
        "raw-promotion-backlog": 6,
    }
    return (severity.get(gate.severity, 9), f"{kind.get(gate.kind, 99):02d}", gate.title)


def _score_ratio(session: PracticeSession) -> float | None:
    if session.score is None or session.max_score in (None, 0):
        return None
    return float(session.score) / float(session.max_score)


def _score_text(session: PracticeSession) -> str:
    if session.score is None:
        return "未记录"
    if session.max_score is None:
        return f"{session.score:g}"
    return f"{session.score:g}/{session.max_score:g}"


def _front_label(front: ExamFront) -> str:
    return {
        ExamFront.CHOICE: "选择题",
        ExamFront.CASE: "案例题",
        ExamFront.ESSAY: "论文题",
    }[front]


def _status_label(status: str) -> str:
    return {
        "leech": "反复低分",
        "unstable": "不稳定",
        "due": "到期",
        "untested": "未检验",
        "low_score": "练习低分",
    }.get(status, status)


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
    <span>得分：{escape(str(hit["score"]))}</span>
    <span>题型：{escape(_fronts_text(hit["fronts"]))}</span>
    <span>状态：{escape(_status_label(str(hit["progress_status"])))}</span>
  </div>
  <div class="meta-row">{_reason_spans(hit["reasons"])}</div>
  <div>{escape(str(hit["action_hint"]))}</div>
</div>"""
        )
    return "".join(items)


def _contract_items(contract: list[object]) -> str:
    if not contract:
        return '<div class="item">暂无回答契约。</div>'
    return "".join(f'<div class="item">{escape(str(item))}</div>' for item in contract)


def _reason_spans(reasons: object) -> str:
    if not isinstance(reasons, list):
        return ""
    return "".join(f"<span>{escape(str(reason))}</span>" for reason in reasons)


def _fronts_text(fronts: object) -> str:
    if not isinstance(fronts, list) or not fronts:
        return "未标注"
    labels = {
        "choice": "选择题",
        "case": "案例题",
        "essay": "论文题",
    }
    return "、".join(labels.get(str(front), str(front)) for front in fronts)


def _severity_label(severity: object) -> str:
    return {
        "red": "红色闸门",
        "yellow": "黄色闸门",
        "green": "绿色",
    }.get(str(severity), str(severity))
