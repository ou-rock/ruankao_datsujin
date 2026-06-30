from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .cheko import ChekoSeedResult, seed_cheko_cards as seed_cheko_memory_cards
from .domain import CardType
from .evolution import write_night_evolution_plan
from .export_state import write_state_export as write_local_state_export
from .rag import DEFAULT_RAG_QUERY, write_rag_brief as write_local_rag_brief
from .receipts import write_daily_receipt
from .route_map import write_route_map
from .storage import RuankaoStore
from .study import StudyTurnResult, capture_study_turn as capture_learning_turn
from .vault import (
    sync_memory_cards_to_vault,
    sync_raw_records_to_vault,
    write_principle_note,
)
from .web_forms import (
    FormData,
    next_due_date,
    overwrite_requested,
    parse_memory_card_form,
    parse_practice_session_form,
    parse_principle_relation_form,
    parse_raw_record_form,
    parse_review_form,
    parse_study_turn_form,
    query_text,
    report_date,
)


@dataclass(frozen=True, slots=True)
class WorkbenchActionContext:
    root: Path
    vault_path: Path
    today: date
    store: Callable[[], RuankaoStore]
    write_dashboard: Callable[[], Path]

    def initialized_store(self) -> RuankaoStore:
        store = self.store()
        store.initialize()
        return store


def add_raw_record(context: WorkbenchActionContext, form: FormData) -> int:
    store = context.initialized_store()
    data = parse_raw_record_form(form)
    return store.add_raw_record(
        source=data.source,
        text=data.text,
        summary=data.summary,
        topics=data.topics,
        fronts=data.fronts,
        promotion_status=data.promotion_status,
    )


def add_memory_card(context: WorkbenchActionContext, form: FormData) -> int:
    store = context.initialized_store()
    data = parse_memory_card_form(form)
    card_id = store.add_memory_card(
        card_type=data.card_type,
        title=data.title,
        prompt=data.prompt,
        answer=data.answer,
        source_record_id=data.source_record_id,
        fronts=data.fronts,
        next_due=data.next_due,
    )
    if data.card_type is CardType.PRINCIPLE:
        applies_when = data.prompt or "待补充"
        write_principle_note(
            context.vault_path,
            title=data.title,
            core_statement=data.answer,
            applies_when=applies_when,
            conflicts=data.conflicts,
        )
    return card_id


def add_principle_relation(context: WorkbenchActionContext, form: FormData) -> int:
    store = context.initialized_store()
    data = parse_principle_relation_form(form)
    return store.add_principle_relation(
        from_card_id=data.from_card_id,
        to_card_id=data.to_card_id,
        relation=data.relation,
        rationale=data.rationale,
    )


def add_practice_session(context: WorkbenchActionContext, form: FormData) -> int:
    store = context.initialized_store()
    data = parse_practice_session_form(form)
    return store.add_practice_session(
        front=data.front,
        topic=data.topic,
        source=data.source,
        score=data.score,
        max_score=data.max_score,
        duration_minutes=data.duration_minutes,
        summary=data.summary,
        mistakes=data.mistakes,
        created_on=data.created_on or context.today,
    )


def capture_study_turn(
    context: WorkbenchActionContext,
    form: FormData,
) -> StudyTurnResult:
    data = parse_study_turn_form(form)
    result = capture_learning_turn(
        context.root,
        topic=data.topic,
        user_text=data.user_text,
        assistant_text=data.assistant_text,
        fronts=data.fronts,
        learner_position=data.learner_position,
        codex_position=data.codex_position,
        destination=data.destination,
    )
    context.write_dashboard()
    return result


def record_review(context: WorkbenchActionContext, form: FormData) -> None:
    store = context.initialized_store()
    data = parse_review_form(form)
    store.record_review(
        card_id=data.card_id,
        reviewed_on=data.reviewed_on or context.today,
        grade=data.grade,
    )


def seed_cheko_cards(context: WorkbenchActionContext, form: FormData) -> ChekoSeedResult:
    next_due = next_due_date(form, context.today)
    result = seed_cheko_memory_cards(context.root, next_due=next_due)
    context.write_dashboard()
    return result


def write_daily_receipt_action(context: WorkbenchActionContext, form: FormData) -> Path:
    return write_daily_receipt(context.root, as_of=report_date(form, context.today))


def write_night_evolution_plan_action(
    context: WorkbenchActionContext,
    form: FormData,
) -> Path:
    return write_night_evolution_plan(context.root, as_of=report_date(form, context.today))


def write_route_map_action(context: WorkbenchActionContext, form: FormData) -> Path:
    return write_route_map(context.root, as_of=report_date(form, context.today))


def write_rag_brief_action(context: WorkbenchActionContext, form: FormData) -> Path:
    return write_local_rag_brief(
        context.root,
        query=query_text(form, DEFAULT_RAG_QUERY),
        as_of=report_date(form, context.today),
    )


def write_state_export_action(context: WorkbenchActionContext, form: FormData) -> Path:
    return write_local_state_export(context.root, as_of=report_date(form, context.today))


def sync_memory_cards_to_vault_action(
    context: WorkbenchActionContext,
    form: FormData,
):
    store = context.initialized_store()
    return sync_memory_cards_to_vault(
        context.vault_path,
        store.list_memory_cards(),
        overwrite=overwrite_requested(form),
    )


def sync_raw_records_to_vault_action(
    context: WorkbenchActionContext,
    form: FormData,
):
    store = context.initialized_store()
    return sync_raw_records_to_vault(
        context.vault_path,
        store.list_raw_records(),
        overwrite=overwrite_requested(form),
    )
