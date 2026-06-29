from __future__ import annotations

from datetime import date

from ruankao_agent.domain import CardType, ExamFront
from ruankao_agent.memory import diagnose_memory
from ruankao_agent.storage import RuankaoStore


def test_memory_diagnostics_rank_leech_unstable_due_and_untested_cards(tmp_path) -> None:
    store = RuankaoStore(tmp_path / "ruankao.db")
    store.initialize()
    leech = store.add_memory_card(
        card_type=CardType.CONCEPT,
        title="ATAM 权衡点",
        prompt="权衡点是什么？",
        answer="影响多个质量属性、需要取舍的架构决策。",
        fronts=(ExamFront.CASE,),
        next_due=date(2026, 6, 29),
    )
    unstable = store.add_memory_card(
        card_type=CardType.COMPARISON,
        title="敏感点 vs 权衡点",
        prompt="二者边界？",
        answer="敏感点影响一个属性，权衡点牵动多个属性。",
        fronts=(ExamFront.CHOICE, ExamFront.CASE),
    )
    due = store.add_memory_card(
        card_type=CardType.EXPRESSION,
        title="论文取舍句",
        prompt="如何表达取舍？",
        answer="在该约束下，我们优先保证...",
        fronts=(ExamFront.ESSAY,),
        next_due=date(2026, 6, 29),
    )
    untested = store.add_memory_card(
        card_type=CardType.SCENARIO,
        title="高可用场景",
        prompt="如何拆场景？",
        answer="刺激、环境、响应和响应度量。",
        fronts=(ExamFront.CASE,),
    )
    stable = store.add_memory_card(
        card_type=CardType.CONCEPT,
        title="质量属性",
        prompt="定义？",
        answer="架构必须满足的非功能诉求。",
        fronts=(ExamFront.CHOICE,),
    )

    store.record_review(leech, reviewed_on=date(2026, 6, 27), grade=1)
    store.record_review(leech, reviewed_on=date(2026, 6, 28), grade=2)
    store.record_review(unstable, reviewed_on=date(2026, 6, 28), grade=2)
    store.record_review(stable, reviewed_on=date(2026, 6, 28), grade=5)

    diagnostics = diagnose_memory(
        store.list_memory_cards(),
        store.list_review_logs(),
        as_of=date(2026, 6, 29),
    )

    assert [item.card_id for item in diagnostics] == [leech, unstable, due, untested, stable]
    assert [item.status for item in diagnostics] == [
        "leech",
        "unstable",
        "due",
        "untested",
        "stable",
    ]
    assert diagnostics[0].low_grade_reviews == 2
    assert diagnostics[0].last_grade == 2
    assert "拆成更小卡片" in diagnostics[0].action
    assert diagnostics[1].average_grade == 2.0
    assert diagnostics[-1].average_grade == 5.0
