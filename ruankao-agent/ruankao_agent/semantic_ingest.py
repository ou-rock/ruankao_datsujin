from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from .domain import ExamFront, SourceIdentity
from .storage import RuankaoStore


class PracticeIngestPayload(BaseModel):
    model_config = ConfigDict(use_enum_values=False)

    intent: Literal["practice_session"] = "practice_session"
    front: ExamFront
    topic: str = Field(min_length=1)
    score: float
    max_score: float
    summary: str = Field(min_length=1)
    source: str = "semantic-ingest"

    @field_validator("score", "max_score")
    @classmethod
    def _score_must_be_non_negative(cls, value: float) -> float:
        if value < 0:
            raise ValueError("score values must be non-negative")
        return value

    @model_validator(mode="after")
    def _score_cannot_exceed_max_score(self) -> "PracticeIngestPayload":
        if self.score > self.max_score:
            raise ValueError("score cannot exceed max_score")
        return self


@dataclass(frozen=True, slots=True)
class SemanticParseResult:
    status: str
    intent: str | None = None
    payload: PracticeIngestPayload | None = None
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SemanticIngestResult:
    status: str
    intent: str | None = None
    payload: PracticeIngestPayload | None = None
    practice_session_id: int | None = None
    raw_record_id: int | None = None
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        output: dict[str, object] = {
            "status": self.status,
            "warnings": list(self.warnings),
        }
        if self.intent:
            output["intent"] = self.intent
        if self.payload:
            output["payload"] = self.payload.model_dump(mode="json")
        if self.practice_session_id is not None:
            output["practice_session_id"] = self.practice_session_id
        if self.raw_record_id is not None:
            output["raw_record_id"] = self.raw_record_id
            output["source"] = SourceIdentity.MEIN.value
            output["promotion_status"] = "raw"
        return output


def parse_semantic_input(text: str) -> SemanticParseResult:
    clean_text = text.strip()
    if not clean_text:
        return SemanticParseResult(status="rejected", warnings=("empty_input",))

    front = _front_from_text(clean_text)
    has_practice_intent = "打卡" in clean_text or "得了" in clean_text or "满分" in clean_text
    if not has_practice_intent:
        return SemanticParseResult(status="failed", warnings=("low_confidence",))

    if front is None:
        return SemanticParseResult(
            status="rejected",
            intent="practice_session",
            warnings=("front_missing",),
        )

    score = _number_after(clean_text, r"得(?:了)?\s*([0-9]+(?:\.[0-9]+)?)\s*分")
    max_score = _number_after(clean_text, r"满分\s*([0-9]+(?:\.[0-9]+)?)")
    if score is None or max_score is None:
        return SemanticParseResult(
            status="rejected",
            intent="practice_session",
            warnings=("score_missing",),
        )

    try:
        payload = PracticeIngestPayload(
            front=front,
            topic=f"{_front_label(front)}打卡",
            score=score,
            max_score=max_score,
            summary=clean_text,
        )
    except ValidationError:
        return SemanticParseResult(
            status="rejected",
            intent="practice_session",
            warnings=("physical_validation_failed",),
        )

    return SemanticParseResult(
        status="parsed",
        intent="practice_session",
        payload=payload,
    )


def ingest_semantic_input(
    root: Path | str,
    text: str,
    *,
    as_of: date | None = None,
) -> SemanticIngestResult:
    store = RuankaoStore(Path(root) / "data" / "ruankao.db")
    store.initialize()
    parsed = parse_semantic_input(text)

    if parsed.status == "parsed" and parsed.payload is not None:
        payload = parsed.payload
        practice_session_id = store.add_practice_session(
            front=payload.front,
            topic=payload.topic,
            source=payload.source,
            score=payload.score,
            max_score=payload.max_score,
            summary=payload.summary,
            created_on=as_of,
        )
        return SemanticIngestResult(
            status="parsed",
            intent=parsed.intent,
            payload=payload,
            practice_session_id=practice_session_id,
            warnings=parsed.warnings,
        )

    if parsed.status == "failed":
        raw_record_id = store.add_raw_record(
            source=SourceIdentity.MEIN,
            text=text.strip(),
            summary="语义解析降级：日常碎片",
            promotion_status="raw",
        )
        return SemanticIngestResult(
            status="fallback_raw",
            raw_record_id=raw_record_id,
            warnings=parsed.warnings,
        )

    return SemanticIngestResult(
        status="rejected",
        intent=parsed.intent,
        warnings=parsed.warnings,
    )


def _front_from_text(text: str) -> ExamFront | None:
    if "案例" in text:
        return ExamFront.CASE
    if "选择" in text:
        return ExamFront.CHOICE
    if "论文" in text or "范文" in text:
        return ExamFront.ESSAY
    return None


def _front_label(front: ExamFront) -> str:
    return {
        ExamFront.CHOICE: "选择题",
        ExamFront.CASE: "案例题",
        ExamFront.ESSAY: "论文题",
    }[front]


def _number_after(text: str, pattern: str) -> float | None:
    match = re.search(pattern, text)
    return float(match.group(1)) if match else None
