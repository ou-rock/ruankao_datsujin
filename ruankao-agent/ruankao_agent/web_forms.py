from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Mapping

from .domain import CardType, ExamFront, PrincipleRelationType, SourceIdentity


FormData = Mapping[str, list[str]]


@dataclass(frozen=True, slots=True)
class RawRecordForm:
    source: SourceIdentity
    text: str
    summary: str
    topics: tuple[str, ...]
    fronts: tuple[ExamFront, ...]
    promotion_status: str


@dataclass(frozen=True, slots=True)
class MemoryCardForm:
    card_type: CardType
    title: str
    prompt: str
    answer: str
    source_record_id: int | None
    fronts: tuple[ExamFront, ...]
    next_due: date | None
    conflicts: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PrincipleRelationForm:
    from_card_id: int
    to_card_id: int
    relation: PrincipleRelationType
    rationale: str


@dataclass(frozen=True, slots=True)
class PracticeSessionForm:
    front: ExamFront
    topic: str
    source: str
    score: float | None
    max_score: float | None
    duration_minutes: int | None
    summary: str
    mistakes: str
    created_on: date | None


@dataclass(frozen=True, slots=True)
class StudyTurnForm:
    topic: str
    user_text: str
    assistant_text: str
    fronts: tuple[ExamFront, ...]
    learner_position: str
    codex_position: str
    destination: str


@dataclass(frozen=True, slots=True)
class ReviewForm:
    card_id: int
    reviewed_on: date | None
    grade: int


def parse_raw_record_form(form: FormData) -> RawRecordForm:
    return RawRecordForm(
        source=SourceIdentity(one(form, "source", SourceIdentity.MEIN.value)),
        text=one(form, "text"),
        summary=one(form, "summary"),
        topics=split_lines(one(form, "topics")),
        fronts=fronts(form),
        promotion_status=one(form, "promotion_status", "raw"),
    )


def parse_memory_card_form(form: FormData) -> MemoryCardForm:
    return MemoryCardForm(
        card_type=CardType(one(form, "card_type", CardType.CONCEPT.value)),
        title=one(form, "title"),
        prompt=one(form, "prompt"),
        answer=one(form, "answer"),
        source_record_id=optional_int(one(form, "source_record_id")),
        fronts=fronts(form),
        next_due=optional_date(one(form, "next_due")),
        conflicts=split_lines(one(form, "conflicts")),
    )


def parse_principle_relation_form(form: FormData) -> PrincipleRelationForm:
    return PrincipleRelationForm(
        from_card_id=int(one(form, "from_card_id")),
        to_card_id=int(one(form, "to_card_id")),
        relation=PrincipleRelationType(one(form, "relation")),
        rationale=one(form, "rationale"),
    )


def parse_practice_session_form(form: FormData) -> PracticeSessionForm:
    return PracticeSessionForm(
        front=ExamFront(one(form, "front", ExamFront.CHOICE.value)),
        topic=one(form, "topic"),
        source=one(form, "source"),
        score=optional_float(one(form, "score")),
        max_score=optional_float(one(form, "max_score")),
        duration_minutes=optional_int(one(form, "duration_minutes")),
        summary=one(form, "summary"),
        mistakes=one(form, "mistakes"),
        created_on=optional_date(one(form, "created_on")),
    )


def parse_study_turn_form(form: FormData) -> StudyTurnForm:
    return StudyTurnForm(
        topic=one(form, "topic"),
        user_text=one(form, "user_text"),
        assistant_text=one(form, "assistant_text"),
        fronts=fronts(form),
        learner_position=one(form, "learner_position"),
        codex_position=one(form, "codex_position"),
        destination=one(form, "destination"),
    )


def parse_review_form(form: FormData) -> ReviewForm:
    return ReviewForm(
        card_id=int(one(form, "card_id")),
        reviewed_on=optional_date(one(form, "reviewed_on")),
        grade=int(one(form, "grade", "3")),
    )


def report_date(form: FormData, default: date) -> date:
    return optional_date(one(form, "as_of")) or default


def next_due_date(form: FormData, default: date) -> date:
    return optional_date(one(form, "next_due")) or default


def query_text(form: FormData, default: str) -> str:
    return one(form, "query", default)


def overwrite_requested(form: FormData) -> bool:
    return one(form, "overwrite") == "1"


def one(form: FormData, key: str, default: str = "") -> str:
    values = form.get(key)
    if not values:
        return default
    return values[0].strip()


def optional_int(value: str) -> int | None:
    return int(value) if value.strip() else None


def optional_float(value: str) -> float | None:
    return float(value) if value.strip() else None


def optional_date(value: str) -> date | None:
    return date.fromisoformat(value) if value.strip() else None


def split_lines(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.replace(",", "\n").splitlines() if item.strip())


def fronts(form: FormData) -> tuple[ExamFront, ...]:
    values = form.get("fronts") or []
    return tuple(ExamFront(value) for value in values if value)
