from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .domain import ExamFront


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
class RagChunk:
    chunk_ref: str
    document: RagDocument
    text: str
    chunk_index: int


@dataclass(frozen=True, slots=True)
class RagHit:
    document: RagDocument
    score: float
    reasons: tuple[str, ...]
    snippet: str
    chunk_ref: str = ""
    retrieval_strategy: str = "token-hybrid-progress"
    score_breakdown: tuple[tuple[str, float], ...] = ()


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
    retrieval_strategy: str
    corpus_size: int
    chunk_count: int


@dataclass(frozen=True, slots=True)
class RagBriefResult:
    as_of: date
    json_path: Path
    html_path: Path
    hit_count: int
    gate_count: int
    recommended_action: str
