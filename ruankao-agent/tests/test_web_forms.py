from __future__ import annotations

from datetime import date
from urllib.parse import parse_qs

from ruankao_agent.domain import CardType, ExamFront, PrincipleRelationType, SourceIdentity
from ruankao_agent.web_forms import (
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


def test_parse_raw_record_form_normalizes_source_topics_and_fronts() -> None:
    form = parse_qs(
        "source=mein&text=  我的判断  &summary=  场景优先  "
        "&topics=质量属性%0A架构评估,性能&fronts=case&fronts=essay"
        "&promotion_status=extracted"
    )

    data = parse_raw_record_form(form)

    assert data.source is SourceIdentity.MEIN
    assert data.text == "我的判断"
    assert data.summary == "场景优先"
    assert data.topics == ("质量属性", "架构评估", "性能")
    assert data.fronts == (ExamFront.CASE, ExamFront.ESSAY)
    assert data.promotion_status == "extracted"


def test_parse_memory_card_form_returns_typed_optional_fields() -> None:
    form = parse_qs(
        "card_type=principle&title=边界先行&prompt=  为什么先划边界  "
        "&answer=先定职责再谈技术&source_record_id=12&fronts=choice"
        "&fronts=case&next_due=2026-07-01&conflicts=技术先行%0A局部最优"
    )

    data = parse_memory_card_form(form)

    assert data.card_type is CardType.PRINCIPLE
    assert data.title == "边界先行"
    assert data.prompt == "为什么先划边界"
    assert data.answer == "先定职责再谈技术"
    assert data.source_record_id == 12
    assert data.fronts == (ExamFront.CHOICE, ExamFront.CASE)
    assert data.next_due == date(2026, 7, 1)
    assert data.conflicts == ("技术先行", "局部最优")


def test_parse_practice_session_form_keeps_blank_numbers_as_none() -> None:
    form = parse_qs(
        "front=case&topic=质量属性场景&source=真题&score=&max_score="
        "&duration_minutes=&summary=响应度量不清&mistakes=漏写环境"
        "&created_on=2026-06-30",
        keep_blank_values=True,
    )

    data = parse_practice_session_form(form)

    assert data.front is ExamFront.CASE
    assert data.score is None
    assert data.max_score is None
    assert data.duration_minutes is None
    assert data.created_on == date(2026, 6, 30)


def test_parse_action_forms_and_common_flags() -> None:
    relation = parse_principle_relation_form(
        parse_qs("from_card_id=1&to_card_id=2&relation=constrains&rationale=性能约束一致性")
    )
    review = parse_review_form(parse_qs("card_id=7&reviewed_on=2026-07-02&grade=4"))
    study = parse_study_turn_form(
        parse_qs(
            "topic=高可用&user_text=备用机制&assistant_text=补充故障边界"
            "&fronts=case&learner_position=会列点&codex_position=追问者&destination=会写场景"
        )
    )

    assert relation.relation is PrincipleRelationType.CONSTRAINS
    assert relation.from_card_id == 1
    assert relation.to_card_id == 2
    assert review.card_id == 7
    assert review.reviewed_on == date(2026, 7, 2)
    assert review.grade == 4
    assert study.fronts == (ExamFront.CASE,)
    assert study.learner_position == "会列点"
    assert report_date(parse_qs("as_of=2026-07-03"), date(2026, 6, 30)) == date(2026, 7, 3)
    assert next_due_date(parse_qs("next_due=2026-07-04"), date(2026, 6, 30)) == date(2026, 7, 4)
    assert query_text(parse_qs("query=  高并发  "), "默认") == "高并发"
    assert overwrite_requested(parse_qs("overwrite=1")) is True
