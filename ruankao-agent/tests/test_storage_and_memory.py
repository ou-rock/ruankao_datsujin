from datetime import date

from ruankao_agent.domain import CardType, ExamFront, PrincipleRelationType, SourceIdentity
from ruankao_agent.storage import SCHEMA_VERSION, RuankaoStore


def test_store_preserves_raw_records_and_memory_cards(tmp_path) -> None:
    store = RuankaoStore(tmp_path / "ruankao.db")
    store.initialize()

    raw_id = store.add_raw_record(
        source=SourceIdentity.MEIN,
        text="我觉得质量属性要从场景里识别，而不是背名词。",
        summary="质量属性要场景化",
        topics=("质量属性", "案例题"),
        fronts=(ExamFront.CASE,),
    )

    card_id = store.add_memory_card(
        card_type=CardType.PRINCIPLE,
        title="场景先于方案",
        prompt="为什么不能先谈技术方案？",
        answer="业务目标、约束和质量属性决定架构选择。",
        source_record_id=raw_id,
        fronts=(ExamFront.CHOICE, ExamFront.CASE, ExamFront.ESSAY),
    )

    records = store.list_raw_records()
    cards = store.list_memory_cards()

    assert records[0].id == raw_id
    assert records[0].source == SourceIdentity.MEIN
    assert records[0].promotion_status == "raw"
    assert records[0].topics == ("质量属性", "案例题")
    assert cards[0].id == card_id
    assert cards[0].card_type == CardType.PRINCIPLE
    assert cards[0].source_record_id == raw_id


def test_store_records_schema_version(tmp_path) -> None:
    db_path = tmp_path / "ruankao.db"
    store = RuankaoStore(db_path)
    store.initialize()

    reopened = RuankaoStore(db_path)
    reopened.initialize()

    assert store.schema_version() == SCHEMA_VERSION
    assert reopened.schema_version() == SCHEMA_VERSION


def test_store_preserves_all_source_identities_and_promotion_status(tmp_path) -> None:
    store = RuankaoStore(tmp_path / "ruankao.db")
    store.initialize()

    store.add_raw_record(
        source=SourceIdentity.DU,
        text="我之前把 agent 定位压得太窄，需要修正。",
        summary="agent 自我修正",
        promotion_status="extracted",
    )
    store.add_raw_record(
        source=SourceIdentity.UNS,
        text="NotebookLM 引用资料总结质量属性场景六要素。",
        summary="外部证据进入 Uns",
        promotion_status="tested",
    )

    records = store.list_raw_records()

    assert [record.source for record in records] == [SourceIdentity.DU, SourceIdentity.UNS]
    assert [record.promotion_status for record in records] == ["extracted", "tested"]


def test_store_counts_due_cards_and_survives_reopen(tmp_path) -> None:
    db_path = tmp_path / "ruankao.db"
    store = RuankaoStore(db_path)
    store.initialize()
    store.add_memory_card(
        card_type=CardType.CONCEPT,
        title="质量属性",
        prompt="质量属性是什么？",
        answer="架构必须显性满足的非功能诉求。",
        next_due=date(2026, 6, 29),
    )
    store.add_memory_card(
        card_type=CardType.EXPRESSION,
        title="论文过渡句",
        prompt="如何引出权衡？",
        answer="在该约束下，我们优先保证...",
        next_due=date(2026, 7, 5),
    )

    reopened = RuankaoStore(db_path)
    reopened.initialize()

    assert reopened.count_due_cards(date(2026, 6, 29)) == 1
    assert reopened.review_backlog_ratio(date(2026, 6, 29)) == 0.5


def test_principle_relations_are_directional_and_typed(tmp_path) -> None:
    store = RuankaoStore(tmp_path / "ruankao.db")
    store.initialize()

    first = store.add_memory_card(
        card_type=CardType.PRINCIPLE,
        title="简单可演进优先",
        prompt="何时优先简单可演进？",
        answer="当前复杂度不足以证明重方案时。",
    )
    second = store.add_memory_card(
        card_type=CardType.PRINCIPLE,
        title="高可用需要冗余",
        prompt="何时必须引入冗余？",
        answer="故障恢复目标明确且停机代价高时。",
    )

    store.add_principle_relation(
        from_card_id=first,
        to_card_id=second,
        relation=PrincipleRelationType.CONFLICTS_WITH,
        rationale="简单设计可能与高可用冗余产生复杂度冲突。",
    )

    relations = store.list_principle_relations(first)

    assert len(relations) == 1
    assert relations[0].from_card_id == first
    assert relations[0].to_card_id == second
    assert relations[0].relation == PrincipleRelationType.CONFLICTS_WITH


def test_review_updates_retrieval_and_next_due_date(tmp_path) -> None:
    store = RuankaoStore(tmp_path / "ruankao.db")
    store.initialize()

    card_id = store.add_memory_card(
        card_type=CardType.CONCEPT,
        title="权衡点",
        prompt="什么是权衡点？",
        answer="影响多个质量属性、需要取舍的架构特性。",
    )

    store.record_review(card_id=card_id, reviewed_on=date(2026, 6, 29), grade=4)
    card = store.get_memory_card(card_id)
    logs = store.list_review_logs(card_id)

    assert card.review_count == 1
    assert card.retrieval_strength > 1.0
    assert card.next_due > date(2026, 6, 29)
    assert len(logs) == 1
    assert logs[0].card_id == card_id
    assert logs[0].reviewed_on == date(2026, 6, 29)
    assert logs[0].grade == 4
    assert logs[0].retrieval_strength == card.retrieval_strength
    assert logs[0].next_due == card.next_due


def test_review_logs_preserve_each_review_attempt(tmp_path) -> None:
    db_path = tmp_path / "ruankao.db"
    store = RuankaoStore(db_path)
    store.initialize()

    card_id = store.add_memory_card(
        card_type=CardType.CONCEPT,
        title="敏感点",
        prompt="什么是敏感点？",
        answer="影响某个质量属性响应的架构决策点。",
    )

    store.record_review(card_id=card_id, reviewed_on=date(2026, 6, 29), grade=1)
    store.record_review(card_id=card_id, reviewed_on=date(2026, 6, 30), grade=5)

    reopened = RuankaoStore(db_path)
    reopened.initialize()
    logs = reopened.list_review_logs(card_id)
    all_logs = reopened.list_review_logs()

    assert [log.grade for log in logs] == [1, 5]
    assert [log.reviewed_on for log in logs] == [date(2026, 6, 29), date(2026, 6, 30)]
    assert len(all_logs) == 2


def test_practice_sessions_preserve_exam_front_scores_and_mistakes(tmp_path) -> None:
    db_path = tmp_path / "ruankao.db"
    store = RuankaoStore(db_path)
    store.initialize()

    choice_id = store.add_practice_session(
        front=ExamFront.CHOICE,
        topic="系统架构设计错题",
        source="Cheko",
        score=7,
        max_score=10,
        duration_minutes=18,
        summary="质量属性题仍然不稳。",
        mistakes="把可用性和可靠性混在一起。",
        created_on=date(2026, 6, 29),
    )
    store.add_practice_session(
        front=ExamFront.ESSAY,
        topic="项目背景段",
        source="自写",
        summary="补了一段项目背景。",
        mistakes="业务价值不够具体。",
        created_on=date(2026, 6, 29),
    )

    reopened = RuankaoStore(db_path)
    reopened.initialize()
    sessions = reopened.list_practice_sessions()
    choice_sessions = reopened.list_practice_sessions(ExamFront.CHOICE)

    assert sessions[0].id == choice_id
    assert sessions[0].front == ExamFront.CHOICE
    assert sessions[0].score == 7
    assert sessions[0].max_score == 10
    assert sessions[0].duration_minutes == 18
    assert "可用性" in sessions[0].mistakes
    assert [session.front for session in sessions] == [ExamFront.CHOICE, ExamFront.ESSAY]
    assert len(choice_sessions) == 1
