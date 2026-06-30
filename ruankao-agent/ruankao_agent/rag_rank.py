from __future__ import annotations

from collections.abc import Iterable, Sequence

from .domain import ExamFront
from .rag_index import build_rag_chunks, fts5_chunk_scores, snippet, tokens_from_text
from .rag_types import RagChunk, RagDocument, RagHit


def retrieve_rag_documents(
    documents: Iterable[RagDocument],
    *,
    query: str,
    default_query: str,
    fronts: Sequence[ExamFront] = (),
    limit: int = 6,
) -> tuple[RagHit, ...]:
    clean_query = query.strip() or default_query
    query_tokens = tokens_from_text(clean_query)
    front_filter = set(fronts)
    chunks = build_rag_chunks(documents)
    fts_scores = fts5_chunk_scores(chunks, query_tokens)
    strategy = "sqlite-fts5-hybrid-progress" if fts_scores else "token-hybrid-progress"
    best_by_document: dict[str, RagHit] = {}
    for chunk in chunks:
        document = chunk.document
        scored = _score_chunk(
            chunk,
            query_tokens,
            clean_query,
            front_filter,
            fts_score=fts_scores.get(chunk.chunk_ref, 0.0),
            retrieval_strategy=strategy,
        )
        if scored is None:
            continue
        score, reasons, breakdown = scored
        if score <= 0:
            continue
        hit = RagHit(
            document=document,
            score=round(score, 3),
            reasons=tuple(reasons),
            snippet=snippet(chunk.text, query_tokens),
            chunk_ref=chunk.chunk_ref,
            retrieval_strategy=strategy,
            score_breakdown=tuple((label, round(value, 3)) for label, value in breakdown),
        )
        previous = best_by_document.get(document.ref)
        if previous is None or hit.score > previous.score:
            best_by_document[document.ref] = hit
    hits = list(best_by_document.values())
    return tuple(sorted(hits, key=lambda hit: (-hit.score, hit.document.ref))[: max(1, limit)])


def _score_chunk(
    chunk: RagChunk,
    query_tokens: set[str],
    query: str,
    front_filter: set[ExamFront],
    *,
    fts_score: float,
    retrieval_strategy: str,
) -> tuple[float, list[str], list[tuple[str, float]]] | None:
    document = chunk.document
    if front_filter and document.fronts and front_filter.isdisjoint(document.fronts):
        return None
    haystack = f"{document.title}\n{chunk.text}\n{' '.join(document.topics)}".lower()
    doc_tokens = tokens_from_text(haystack)
    overlap = query_tokens & doc_tokens
    token_score = float(len(overlap) * 2.0)
    phrase_score = 4.0 if query and query.lower() in haystack else 0.0
    front_score = 2.0 if front_filter and not front_filter.isdisjoint(document.fronts) else 0.0
    status_score = 1.0 if document.progress_status in {"leech", "unstable", "due", "low_score"} else 0.0
    score = document.priority + token_score + phrase_score + front_score + status_score + fts_score
    breakdown = [
        ("progress", document.priority),
        ("token", token_score),
        ("fts_bm25", fts_score),
        ("phrase", phrase_score),
        ("front", front_score),
        ("status", status_score),
    ]
    reasons = [f"进步权重 {document.priority:g}"]
    if retrieval_strategy == "sqlite-fts5-hybrid-progress":
        reasons.append(f"FTS/BM25 切块命中 {chunk.chunk_ref}")
    if overlap:
        reasons.append("命中：" + "、".join(sorted(overlap)[:5]))
    if phrase_score:
        reasons.append("完整短语命中")
    if front_score:
        reasons.append("题型匹配")
    if status_score:
        reasons.append(_status_label(document.progress_status))
    if query_tokens and not overlap and fts_score <= 0 and document.priority < 3:
        return None
    return score, reasons, breakdown


def _status_label(status: str) -> str:
    return {
        "leech": "反复低分",
        "unstable": "不稳定",
        "due": "到期",
        "untested": "未检验",
        "low_score": "练习低分",
    }.get(status, status)
