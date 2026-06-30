from __future__ import annotations

import re
import sqlite3
from collections.abc import Iterable, Sequence

from .rag_types import RagChunk, RagDocument


_ASCII_RE = re.compile(r"[a-z0-9_+#.-]+")
_CJK_RE = re.compile(r"[\u4e00-\u9fff]+")


def build_rag_chunks(
    documents: Iterable[RagDocument],
    *,
    max_chars: int = 420,
    overlap: int = 80,
) -> tuple[RagChunk, ...]:
    chunks: list[RagChunk] = []
    for document in documents:
        pieces = _chunk_text(
            "\n".join(
                item
                for item in (
                    document.title,
                    " ".join(document.topics),
                    document.body,
                )
                if item
            ),
            max_chars=max_chars,
            overlap=overlap,
        )
        for index, piece in enumerate(pieces):
            chunks.append(
                RagChunk(
                    chunk_ref=f"{document.ref}#c{index + 1}",
                    document=document,
                    text=piece,
                    chunk_index=index,
                )
            )
    return tuple(chunks)


def fts5_chunk_scores(chunks: Sequence[RagChunk], query_tokens: set[str]) -> dict[str, float]:
    if not chunks or not query_tokens:
        return {}
    query = fts_query(query_tokens)
    if not query:
        return {}
    try:
        con = sqlite3.connect(":memory:")
        con.execute("CREATE VIRTUAL TABLE rag_chunks USING fts5(chunk_ref UNINDEXED, title, body)")
        con.executemany(
            "INSERT INTO rag_chunks(chunk_ref, title, body) VALUES (?, ?, ?)",
            (
                (
                    chunk.chunk_ref,
                    chunk.document.title,
                    fts_search_text(chunk),
                )
                for chunk in chunks
            ),
        )
        rows = con.execute(
            """
            SELECT chunk_ref, bm25(rag_chunks) AS rank
            FROM rag_chunks
            WHERE rag_chunks MATCH ?
            ORDER BY rank
            LIMIT 40
            """,
            (query,),
        ).fetchall()
    except sqlite3.Error:
        return {}
    finally:
        try:
            con.close()
        except Exception:
            pass
    scores: dict[str, float] = {}
    for index, (chunk_ref, rank) in enumerate(rows):
        scores[str(chunk_ref)] = round(8.0 / (index + 1) + max(0.0, -float(rank)), 3)
    return scores


def fts_search_text(chunk: RagChunk) -> str:
    source = f"{chunk.document.title}\n{chunk.text}\n{' '.join(chunk.document.topics)}"
    tokens = sorted(tokens_from_text(source))
    return " ".join(tokens)


def fts_query(tokens: set[str]) -> str:
    selected = [
        token
        for token in sorted(tokens, key=lambda item: (-len(item), item))[:16]
        if token.strip()
    ]
    return " OR ".join(f'"{token.replace(chr(34), chr(34) + chr(34))}"' for token in selected)


def retrieval_strategy_name(chunks: Sequence[RagChunk]) -> str:
    if not chunks:
        return "token-hybrid-progress"
    try:
        con = sqlite3.connect(":memory:")
        con.execute("CREATE VIRTUAL TABLE rag_probe USING fts5(body)")
        return "sqlite-fts5-hybrid-progress"
    except sqlite3.Error:
        return "token-hybrid-progress"
    finally:
        try:
            con.close()
        except Exception:
            pass


def tokens_from_text(text: str) -> set[str]:
    lowered = text.lower()
    tokens = set(_ASCII_RE.findall(lowered))
    for run in _CJK_RE.findall(lowered):
        if len(run) <= 2:
            tokens.add(run)
        else:
            tokens.update(run[index : index + 2] for index in range(len(run) - 1))
            tokens.update(run[index : index + 3] for index in range(len(run) - 2))
    return {token for token in tokens if token.strip()}


def snippet(body: str, query_tokens: set[str], *, length: int = 96) -> str:
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


def _chunk_text(text: str, *, max_chars: int, overlap: int) -> tuple[str, ...]:
    clean_parts = [part.strip() for part in re.split(r"\n{2,}|\n", text) if part.strip()]
    chunks: list[str] = []
    current = ""
    for part in clean_parts:
        candidate = f"{current}\n{part}".strip() if current else part
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.extend(_split_long_chunk(current, max_chars=max_chars, overlap=overlap))
        current = part
    if current:
        chunks.extend(_split_long_chunk(current, max_chars=max_chars, overlap=overlap))
    return tuple(chunks or (text.strip(),))


def _split_long_chunk(text: str, *, max_chars: int, overlap: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    chunks: list[str] = []
    start = 0
    step = max(1, max_chars - overlap)
    while start < len(text):
        end = min(len(text), start + max_chars)
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start += step
    return [chunk for chunk in chunks if chunk]
