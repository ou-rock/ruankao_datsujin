from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from datetime import date
from pathlib import Path

from .domain import ExamFront
from .memory import MemoryDiagnostic, diagnose_memory
from .rag_index import build_rag_chunks, retrieval_strategy_name
from .rag_rank import retrieve_rag_documents as _retrieve_rag_documents
from .rag_report import (
    rag_brief_html_path,
    rag_brief_json_path,
    rag_brief_to_payload,
    render_rag_brief,
)
from .rag_types import (
    ProgressGate,
    RagBrief,
    RagBriefResult,
    RagChunk,
    RagDocument,
    RagHit,
)
from .storage import MemoryCard, PracticeSession, RawRecord, RuankaoStore


DEFAULT_RAG_QUERY = "今天如何用记忆、错因和三题型进步信号安排学习？"


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
    chunks = build_rag_chunks(documents)
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
        retrieval_strategy=retrieval_strategy_name(chunks),
        corpus_size=len(documents),
        chunk_count=len(chunks),
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
    return _retrieve_rag_documents(
        documents,
        query=query,
        default_query=DEFAULT_RAG_QUERY,
        fronts=fronts,
        limit=limit,
    )


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
