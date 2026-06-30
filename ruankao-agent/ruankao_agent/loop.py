from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Sequence

from .dashboard import DashboardSnapshot
from .notebooklm import DEFAULT_NOTEBOOK_SOURCE


@dataclass(frozen=True, slots=True)
class DailyLoopSnapshot:
    dashboard: DashboardSnapshot
    phase_name: str
    countdown: str
    risk_text: str
    risk_reasons: tuple[str, ...]
    reserve_days_consumed: int
    notebook_source_name: str


def _load_domain() -> Any | None:
    try:
        from . import domain as domain_module  # type: ignore
    except Exception:
        return None
    return domain_module


def _campaign_default() -> Any:
    domain_module = _load_domain()
    if domain_module is not None and hasattr(domain_module, "Campaign"):
        campaign_cls = getattr(domain_module, "Campaign")
        if hasattr(campaign_cls, "default"):
            return campaign_cls.default()
    return _FallbackCampaign()


def _risk_status_green() -> Any:
    domain_module = _load_domain()
    if domain_module is not None and hasattr(domain_module, "RiskStatus"):
        return getattr(domain_module.RiskStatus, "GREEN")
    return "green"


def _evaluate_risk(signals: Any) -> Any:
    domain_module = _load_domain()
    if domain_module is not None and hasattr(domain_module, "evaluate_risk"):
        return domain_module.evaluate_risk(signals)
    return _risk_status_green()


def _build_signals(
    as_of: date,
    campaign: Any,
    review_backlog_ratio: float,
    practice_sessions: Sequence[Any] = (),
) -> Any:
    domain_module = _load_domain()
    days_remaining = campaign.days_remaining(as_of)
    practice_signal = _practice_signal(as_of, practice_sessions)
    if domain_module is not None and hasattr(domain_module, "DailySignals"):
        daily_signals = getattr(domain_module, "DailySignals")
        return daily_signals(
            consecutive_missed_minimum_days=0,
            absent_fronts_this_week=practice_signal["absent_fronts_this_week"],
            review_backlog_ratio=review_backlog_ratio,
            days_since_essay=practice_signal["days_since_essay"],
            days_since_case=practice_signal["days_since_case"],
            reserve_days_consumed=campaign.reserve_days_consumed(as_of),
            days_to_exam=days_remaining,
            completed_essay_count=practice_signal["completed_essay_count"],
        )
    return _FallbackSignals(
        consecutive_missed_minimum_days=0,
        absent_fronts_this_week=practice_signal["absent_fronts_this_week"],
        review_backlog_ratio=review_backlog_ratio,
        days_since_essay=practice_signal["days_since_essay"],
        days_since_case=practice_signal["days_since_case"],
        reserve_days_consumed=campaign.reserve_days_consumed(as_of),
        days_to_exam=days_remaining,
        completed_essay_count=practice_signal["completed_essay_count"],
    )


def build_daily_loop_snapshot(
    *,
    as_of: date | None = None,
    notebook_source_name: str = DEFAULT_NOTEBOOK_SOURCE.title,
    due_cards: int = 0,
    review_backlog_ratio: float = 0.0,
    practice_sessions: Sequence[Any] = (),
    campaign: Any | None = None,
) -> DailyLoopSnapshot:
    current_date = as_of or date.today()
    current_campaign = campaign or _campaign_default()
    signals = _build_signals(
        current_date,
        current_campaign,
        review_backlog_ratio,
        practice_sessions,
    )
    risk = _evaluate_risk(signals)
    risk_reasons = _risk_reasons(signals)
    dashboard = DashboardSnapshot(
        campaign=current_campaign,
        as_of=current_date,
        risk=risk,
        notebook_name=notebook_source_name,
        due_cards=due_cards,
        review_backlog_ratio=review_backlog_ratio,
    )
    phase = current_campaign.phase_for(current_date)
    phase_name = getattr(phase, "name", str(phase))
    countdown_days = current_campaign.days_remaining(current_date)
    countdown = f"D-{countdown_days}" if countdown_days >= 0 else f"D+{-countdown_days}"
    reserve_days_consumed = current_campaign.reserve_days_consumed(current_date)
    risk_text = getattr(risk, "value", getattr(risk, "name", str(risk))).lower()
    return DailyLoopSnapshot(
        dashboard=dashboard,
        phase_name=phase_name,
        countdown=countdown,
        risk_text=risk_text,
        risk_reasons=risk_reasons,
        reserve_days_consumed=reserve_days_consumed,
        notebook_source_name=notebook_source_name,
    )


def _practice_signal(as_of: date, practice_sessions: Sequence[Any]) -> dict[str, Any]:
    sessions = [
        session
        for session in practice_sessions
        if getattr(session, "created_on", None) is not None
    ]
    if not sessions:
        return {
            "absent_fronts_this_week": (),
            "days_since_essay": 0,
            "days_since_case": 0,
            "completed_essay_count": 0,
        }

    front_dates: dict[str, list[date]] = {"choice": [], "case": [], "essay": []}
    for session in sessions:
        front = getattr(getattr(session, "front", ""), "value", getattr(session, "front", ""))
        created_on = getattr(session, "created_on")
        if front in front_dates and isinstance(created_on, date):
            front_dates[front].append(created_on)

    week_start = as_of - timedelta(days=6)
    recent_fronts = {
        front
        for front, dates in front_dates.items()
        if any(week_start <= day <= as_of for day in dates)
    }
    absent_fronts = tuple(front for front in ("choice", "case", "essay") if front not in recent_fronts)
    return {
        "absent_fronts_this_week": absent_fronts,
        "days_since_essay": _days_since_latest(as_of, front_dates["essay"]),
        "days_since_case": _days_since_latest(as_of, front_dates["case"]),
        "completed_essay_count": len(front_dates["essay"]),
    }


def _days_since_latest(as_of: date, dates: list[date]) -> int:
    if not dates:
        return 999
    return max(0, (as_of - max(dates)).days)


def _risk_reasons(signals: Any) -> tuple[str, ...]:
    reasons: list[str] = []
    absent_front_count = len(getattr(signals, "absent_fronts_this_week", ()))
    backlog = float(getattr(signals, "review_backlog_ratio", 0.0))
    missed_days = int(getattr(signals, "consecutive_missed_minimum_days", 0))
    days_since_essay = int(getattr(signals, "days_since_essay", 0))
    days_since_case = int(getattr(signals, "days_since_case", 0))
    reserve_days = int(getattr(signals, "reserve_days_consumed", 0))
    days_to_exam = int(getattr(signals, "days_to_exam", 9999))
    essay_count = int(getattr(signals, "completed_essay_count", 0))

    if missed_days >= 4:
        reasons.append("连续 4 天以上未完成最小闭环")
    elif missed_days >= 2:
        reasons.append("连续 2 天以上未完成最小闭环")
    if absent_front_count >= 2:
        reasons.append("本周缺席 2 个以上题型")
    elif absent_front_count >= 1:
        reasons.append("本周有题型缺席")
    if backlog > 0.40:
        reasons.append("复习积压超过 40%")
    elif backlog > 0.20:
        reasons.append("复习积压超过 20%")
    if days_since_essay > 14:
        reasons.append("论文超过 14 天未触达")
    elif days_since_essay > 7:
        reasons.append("论文超过 7 天未触达")
    if days_since_case > 10:
        reasons.append("案例超过 10 天未触达")
    elif days_since_case > 5:
        reasons.append("案例超过 5 天未触达")
    if reserve_days >= 7:
        reasons.append("冗余消耗达到 7 天")
    elif reserve_days >= 3:
        reasons.append("冗余消耗达到 3 天")
    if days_to_exam <= 30 and essay_count < 2:
        reasons.append("考前 30 天内完整论文少于 2 篇")
    return tuple(reasons) if reasons else ("当前风险信号正常",)


def status_line(snapshot: DailyLoopSnapshot) -> str:
    backlog = snapshot.dashboard.review_backlog_ratio
    due_cards = snapshot.dashboard.due_cards
    return (
        f"{snapshot.countdown} · {snapshot.phase_name} · {_risk_text_label(snapshot.risk_text)} "
        f"· 到期 {due_cards} · 积压 {backlog:.0%}"
    )


def _risk_text_label(value: str) -> str:
    return {
        "green": "绿灯",
        "yellow": "黄灯",
        "red": "红灯",
    }.get(value, value)


def write_dashboard(root: Path, *, as_of: date | None = None) -> Path:
    from .dashboard import render_dashboard

    snapshot = build_daily_loop_snapshot(as_of=as_of)
    dashboard_path = root / "dashboard.html"
    dashboard_path.write_text(render_dashboard(snapshot.dashboard), encoding="utf-8")
    return dashboard_path


@dataclass(frozen=True, slots=True)
class _FallbackPhase:
    key: str
    name: str


@dataclass(frozen=True, slots=True)
class _FallbackSignals:
    consecutive_missed_minimum_days: int
    absent_fronts_this_week: tuple[Any, ...]
    review_backlog_ratio: float
    days_since_essay: int
    days_since_case: int
    reserve_days_consumed: int
    days_to_exam: int
    completed_essay_count: int


class _FallbackCampaign:
    exam_date = date(2026, 10, 24)

    @classmethod
    def default(cls) -> "_FallbackCampaign":
        return cls()

    def days_remaining(self, as_of: date) -> int:
        return (self.exam_date - as_of).days

    def phase_for(self, as_of: date) -> _FallbackPhase:
        if as_of <= date(2026, 6, 29):
            return _FallbackPhase(key="stage-0", name="启动诊断")
        if as_of <= date(2026, 7, 13):
            return _FallbackPhase(key="stage-1", name="诊断建模")
        if as_of <= date(2026, 8, 17):
            return _FallbackPhase(key="stage-2", name="系统突破")
        if as_of <= date(2026, 9, 14):
            return _FallbackPhase(key="stage-3", name="真题强化")
        if as_of <= date(2026, 10, 5):
            return _FallbackPhase(key="stage-4", name="保分护航")
        return _FallbackPhase(key="stage-5", name="冗余救火")

    def reserve_days_consumed(self, as_of: date) -> int:
        return max(0, (as_of - date(2026, 10, 5)).days)
