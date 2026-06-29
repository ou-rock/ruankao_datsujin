from datetime import date

from ruankao_agent.domain import (
    Campaign,
    DailySignals,
    ExamFront,
    RiskStatus,
    evaluate_risk,
)


def test_campaign_countdown_and_phase() -> None:
    campaign = Campaign.default()

    assert campaign.exam_date == date(2026, 10, 24)
    assert campaign.days_remaining(date(2026, 6, 29)) == 117

    phase = campaign.phase_for(date(2026, 6, 29))
    assert phase.key == "stage-0"
    assert phase.name == "启动诊断"


def test_campaign_enters_reserve_after_main_battle() -> None:
    campaign = Campaign.default()

    phase = campaign.phase_for(date(2026, 10, 12))

    assert phase.key == "stage-5"
    assert phase.name == "冗余救火"
    assert campaign.reserve_days_consumed(date(2026, 10, 12)) > 0


def test_risk_green_when_minimum_loop_is_healthy() -> None:
    signals = DailySignals(
        consecutive_missed_minimum_days=0,
        absent_fronts_this_week=(),
        review_backlog_ratio=0.05,
        days_since_essay=2,
        days_since_case=1,
        reserve_days_consumed=0,
        days_to_exam=117,
        completed_essay_count=0,
    )

    assert evaluate_risk(signals) == RiskStatus.GREEN


def test_risk_yellow_for_medium_slippage() -> None:
    signals = DailySignals(
        consecutive_missed_minimum_days=2,
        absent_fronts_this_week=(ExamFront.ESSAY,),
        review_backlog_ratio=0.21,
        days_since_essay=8,
        days_since_case=2,
        reserve_days_consumed=3,
        days_to_exam=90,
        completed_essay_count=0,
    )

    assert evaluate_risk(signals) == RiskStatus.YELLOW


def test_risk_red_for_late_essay_gap() -> None:
    signals = DailySignals(
        consecutive_missed_minimum_days=0,
        absent_fronts_this_week=(),
        review_backlog_ratio=0.1,
        days_since_essay=3,
        days_since_case=3,
        reserve_days_consumed=0,
        days_to_exam=29,
        completed_essay_count=1,
    )

    assert evaluate_risk(signals) == RiskStatus.RED


def test_risk_threshold_boundaries_are_deterministic() -> None:
    base = dict(
        consecutive_missed_minimum_days=0,
        absent_fronts_this_week=(),
        review_backlog_ratio=0.20,
        days_since_essay=7,
        days_since_case=5,
        reserve_days_consumed=2,
        days_to_exam=31,
        completed_essay_count=1,
    )

    assert evaluate_risk(DailySignals(**base)) == RiskStatus.GREEN

    yellow = base | {"review_backlog_ratio": 0.21}
    assert evaluate_risk(DailySignals(**yellow)) == RiskStatus.YELLOW

    red = base | {"days_since_case": 11}
    assert evaluate_risk(DailySignals(**red)) == RiskStatus.RED
