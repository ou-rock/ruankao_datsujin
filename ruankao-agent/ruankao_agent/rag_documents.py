from __future__ import annotations

from collections.abc import Iterable
from datetime import date

from .memory import MemoryDiagnostic
from .rag_types import RagDocument
from .storage import MemoryCard, PracticeSession, RawRecord


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
