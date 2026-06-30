from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from datetime import date
from pathlib import Path

from .domain import ExamFront
from .memory import diagnose_memory
from .rag_documents import build_rag_documents
from .rag_index import build_rag_chunks, retrieval_strategy_name
from .rag_progress import build_progress_gates, recommend_rag_action
from .rag_rank import retrieve_rag_documents as _retrieve_rag_documents
from .rag_report import (
    rag_brief_html_path,
    rag_brief_json_path,
    rag_brief_to_payload,
    render_rag_brief,
)
from .rag_types import (
    RagBrief,
    RagBriefResult,
    RagDocument,
    RagHit,
)
from .storage import RuankaoStore


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
        recommended_action=recommend_rag_action(hits, gates),
        answer_contract=(
            "先处理最高优先级进步闸门，再展开资料解释。",
            "回答必须引用召回证据，区分 Mein、Du、Uns、记忆卡和练习记录。",
            "每次学习结束必须产出下一张卡、一次练习或一条三源沉淀。",
        ),
        retrieval_strategy=retrieval_strategy_name(chunks),
        corpus_size=len(documents),
        chunk_count=len(chunks),
    )


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
    json_path = rag_brief_json_path(root_path, day)
    html_path = rag_brief_html_path(root_path, day)
    payload = rag_brief_to_payload(brief, root=root_path)
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
