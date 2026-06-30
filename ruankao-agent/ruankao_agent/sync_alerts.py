from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal

from .loop import build_daily_loop_snapshot
from .storage import PracticeSession, RuankaoStore


SyncSentinelMode = Literal["offline-reconnect", "realtime"]
LOW_SCORE_THRESHOLD = 0.60


@dataclass(frozen=True, slots=True)
class SyncSentinelResult:
    mode: SyncSentinelMode
    alert_count: int
    seen_low_score_practice_ids: tuple[int, ...]


def run_sync_sentinel(
    root: Path | str,
    *,
    mode: SyncSentinelMode,
    as_of: date | None = None,
    discord_log: Path | str | None = None,
    state_path: Path | str | None = None,
) -> SyncSentinelResult:
    root_path = Path(root)
    day = as_of or date.today()
    store = RuankaoStore(root_path / "data" / "ruankao.db")
    store.initialize()

    practice_sessions = store.list_practice_sessions()
    state_file = Path(state_path) if state_path is not None else _default_state_path(root_path)
    seen_ids = _load_seen_low_score_ids(state_file)
    low_score_sessions = _low_score_sessions(practice_sessions)

    if mode == "offline-reconnect":
        seen_ids.update(
            session.id
            for session in low_score_sessions
            if session.created_on is not None and session.created_on <= day
        )
        _save_seen_low_score_ids(state_file, seen_ids)
        return SyncSentinelResult(
            mode=mode,
            alert_count=0,
            seen_low_score_practice_ids=tuple(sorted(seen_ids)),
        )
    if mode != "realtime":
        raise ValueError(f"Unsupported sync sentinel mode: {mode}")

    due_cards = store.count_due_cards(day)
    backlog = store.review_backlog_ratio(day)
    snapshot = build_daily_loop_snapshot(
        as_of=day,
        due_cards=due_cards,
        review_backlog_ratio=backlog,
        practice_sessions=practice_sessions,
    )
    new_low_scores = [
        session
        for session in low_score_sessions
        if session.created_on == day and session.id not in seen_ids
    ]
    alerts = [
        _low_score_alert(session, risk_text=snapshot.risk_text, risk_reasons=snapshot.risk_reasons)
        for session in new_low_scores
    ]
    if alerts:
        _append_discord_alerts(
            Path(discord_log) if discord_log is not None else _default_discord_log(root_path),
            alerts,
        )
    seen_ids.update(session.id for session in new_low_scores)
    _save_seen_low_score_ids(state_file, seen_ids)
    return SyncSentinelResult(
        mode=mode,
        alert_count=len(alerts),
        seen_low_score_practice_ids=tuple(sorted(seen_ids)),
    )


def _default_state_path(root: Path) -> Path:
    return root / "data" / "sync-alert-state.json"


def _default_discord_log(root: Path) -> Path:
    return root / "data" / "discord-alerts.jsonl"


def _load_seen_low_score_ids(path: Path) -> set[int]:
    if not path.exists():
        return set()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    raw_ids = payload.get("seen_low_score_practice_ids", [])
    return {int(value) for value in raw_ids if str(value).isdigit()}


def _save_seen_low_score_ids(path: Path, ids: set[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"seen_low_score_practice_ids": sorted(ids)}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _low_score_sessions(sessions: list[PracticeSession]) -> list[PracticeSession]:
    return [
        session
        for session in sessions
        if (ratio := _score_ratio(session)) is not None and ratio < LOW_SCORE_THRESHOLD
    ]


def _score_ratio(session: PracticeSession) -> float | None:
    if session.score is None or session.max_score in (None, 0):
        return None
    return float(session.score) / float(session.max_score)


def _low_score_alert(
    session: PracticeSession,
    *,
    risk_text: str,
    risk_reasons: tuple[str, ...],
) -> dict[str, object]:
    ratio = _score_ratio(session) or 0.0
    reasons = _risk_reasons_with_low_score(risk_reasons)
    score_text = _score_text(session)
    ratio_text = f"{ratio:.0%}"
    return {
        "kind": "low_score",
        "practice_id": session.id,
        "topic": session.topic,
        "front": session.front.value,
        "score": session.score,
        "max_score": session.max_score,
        "score_ratio": round(ratio, 3),
        "risk_status": risk_text,
        "risk_reasons": reasons,
        "message": (
            f"练习低分预警：{session.topic}（{_front_label(session)} {score_text}，{ratio_text}）。"
            f"原因：{'；'.join(reasons)}。"
        ),
    }


def _risk_reasons_with_low_score(risk_reasons: tuple[str, ...]) -> list[str]:
    reasons = ["练习得分低于 60%"]
    for reason in risk_reasons:
        if reason != "当前风险信号正常" and reason not in reasons:
            reasons.append(reason)
    return reasons


def _score_text(session: PracticeSession) -> str:
    if session.score is None:
        return "未记录"
    if session.max_score is None:
        return f"{session.score:g}"
    return f"{session.score:g}/{session.max_score:g}"


def _front_label(session: PracticeSession) -> str:
    return {
        "choice": "选择题",
        "case": "案例题",
        "essay": "论文题",
    }[session.front.value]


def _append_discord_alerts(path: Path, alerts: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for alert in alerts:
            handle.write(json.dumps(alert, ensure_ascii=False, sort_keys=True) + "\n")
