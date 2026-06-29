from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class StrEnum(str, Enum):
    """String-valued enum with stable JSON-friendly values."""


class RiskStatus(StrEnum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class ExamFront(StrEnum):
    CHOICE = "choice"
    CASE = "case"
    ESSAY = "essay"


class SourceIdentity(StrEnum):
    MEIN = "mein"
    DU = "du"
    UNS = "uns"


class CardType(StrEnum):
    PRINCIPLE = "principle"
    CONCEPT = "concept"
    COMPARISON = "comparison"
    SCENARIO = "scenario"
    EXPRESSION = "expression"


class PrincipleRelationType(StrEnum):
    SUPPORTS = "supports"
    CONSTRAINS = "constrains"
    CONFLICTS_WITH = "conflicts_with"
    DERIVED_FROM = "derived_from"


@dataclass(frozen=True, slots=True)
class CampaignPhase:
    key: str
    name: str
    start_day: int
    end_day: int


@dataclass(frozen=True, slots=True)
class Campaign:
    start_date: date
    exam_date: date
    phases: tuple[CampaignPhase, ...]

    @classmethod
    def default(cls) -> "Campaign":
        phases = (
            CampaignPhase("stage-0", "启动诊断", 0, 2),
            CampaignPhase("stage-1", "诊断建模", 3, 16),
            CampaignPhase("stage-2", "系统突破", 17, 51),
            CampaignPhase("stage-3", "真题强化", 52, 79),
            CampaignPhase("stage-4", "分数保护", 80, 100),
            CampaignPhase("stage-5", "冗余救火", 101, 9999),
        )
        return cls(
            start_date=date(2026, 6, 29),
            exam_date=date(2026, 10, 24),
            phases=phases,
        )

    def days_remaining(self, on_date: date) -> int:
        return max(0, (self.exam_date - on_date).days)

    def phase_for(self, on_date: date) -> CampaignPhase:
        elapsed_days = max(0, (on_date - self.start_date).days)
        for phase in self.phases:
            if phase.start_day <= elapsed_days <= phase.end_day:
                return phase
        return self.phases[-1]

    def reserve_days_consumed(self, on_date: date) -> int:
        elapsed_days = max(0, (on_date - self.start_date).days)
        reserve_start = self.phases[4].end_day + 1
        return max(0, elapsed_days - reserve_start + 1)


@dataclass(frozen=True, slots=True)
class DailySignals:
    consecutive_missed_minimum_days: int
    absent_fronts_this_week: tuple[ExamFront, ...]
    review_backlog_ratio: float
    days_since_essay: int
    days_since_case: int
    reserve_days_consumed: int
    days_to_exam: int
    completed_essay_count: int


def evaluate_risk(signals: DailySignals) -> RiskStatus:
    absent_front_count = len(signals.absent_fronts_this_week)

    red_conditions = (
        signals.consecutive_missed_minimum_days >= 4,
        absent_front_count >= 2,
        signals.review_backlog_ratio > 0.40,
        signals.days_since_essay > 14,
        signals.days_since_case > 10,
        signals.reserve_days_consumed >= 7,
        signals.days_to_exam <= 30 and signals.completed_essay_count < 2,
    )
    if any(red_conditions):
        return RiskStatus.RED

    yellow_conditions = (
        signals.consecutive_missed_minimum_days >= 2,
        absent_front_count >= 1,
        signals.review_backlog_ratio > 0.20,
        signals.days_since_essay > 7,
        signals.days_since_case > 5,
        signals.reserve_days_consumed >= 3,
    )
    if any(yellow_conditions):
        return RiskStatus.YELLOW

    return RiskStatus.GREEN
