from __future__ import annotations

from collections.abc import Iterable
from datetime import date

from .domain import ExamFront
from .memory import MemoryDiagnostic
from .rag_types import ProgressGate
from .storage import MemoryCard, PracticeSession, RawRecord


def build_progress_gates(
    *,
    records: Iterable[RawRecord],
    cards: Iterable[MemoryCard],
    practice_sessions: Iterable[PracticeSession],
    diagnostics: Iterable[MemoryDiagnostic],
    as_of: date,
) -> tuple[ProgressGate, ...]:
    gates: list[ProgressGate] = []
    gates.extend(_memory_gates(diagnostics, as_of=as_of))

    cards_list = list(cards)
    practice_list = list(practice_sessions)
    gates.extend(_front_coverage_gates(cards_list, practice_list))
    gates.extend(_practice_score_gates(practice_list))
    gates.extend(_raw_promotion_gates(records))

    return tuple(sorted(gates, key=_gate_sort_key)[:8])


def _memory_gates(
    diagnostics: Iterable[MemoryDiagnostic],
    *,
    as_of: date,
) -> list[ProgressGate]:
    gates: list[ProgressGate] = []
    for diagnostic in diagnostics:
        if diagnostic.status == "leech":
            gates.append(
                ProgressGate(
                    severity="red",
                    kind="weak-memory",
                    title=diagnostic.title,
                    reason=f"反复低分 {diagnostic.low_grade_reviews} 次，检索强度不可信。",
                    action=diagnostic.action,
                )
            )
        elif diagnostic.status == "unstable":
            gates.append(
                ProgressGate(
                    severity="red",
                    kind="unstable-memory",
                    title=diagnostic.title,
                    reason="最近一次主动回忆低于 3 分。",
                    action=diagnostic.action,
                )
            )
        elif diagnostic.status == "due":
            due_date = diagnostic.next_due.isoformat() if diagnostic.next_due else as_of.isoformat()
            gates.append(
                ProgressGate(
                    severity="yellow",
                    kind="due-review",
                    title=diagnostic.title,
                    reason=f"下次复习日已到：{due_date}。",
                    action=diagnostic.action,
                )
            )
    return gates


def _front_coverage_gates(
    cards: list[MemoryCard],
    practice_sessions: list[PracticeSession],
) -> list[ProgressGate]:
    gates: list[ProgressGate] = []
    for front in ExamFront:
        front_cards = [card for card in cards if front in card.fronts]
        front_practice = [session for session in practice_sessions if session.front is front]
        if not front_cards:
            gates.append(
                ProgressGate(
                    severity="red",
                    kind="front-card-gap",
                    title=_front_label(front),
                    reason="这条战线还没有可检索的记忆卡。",
                    action="先从三源材料或错题中生成 3 张基础卡。",
                )
            )
        elif not front_practice:
            gates.append(
                ProgressGate(
                    severity="yellow",
                    kind="front-practice-gap",
                    title=_front_label(front),
                    reason="这条战线有记忆卡，但还没有实战记录验证。",
                    action="安排一次可评分练习，并记录错因。",
                )
            )
    return gates


def _practice_score_gates(practice_sessions: list[PracticeSession]) -> list[ProgressGate]:
    gates: list[ProgressGate] = []
    for session in practice_sessions:
        ratio = _score_ratio(session)
        if ratio is not None and ratio < 0.6:
            gates.append(
                ProgressGate(
                    severity="red",
                    kind="low-practice-score",
                    title=session.topic,
                    reason=f"{_front_label(session.front)}练习得分率 {ratio:.0%}。",
                    action="先复盘错因，再把混淆点转成对比卡或场景卡。",
                )
            )
    return gates


def _raw_promotion_gates(records: Iterable[RawRecord]) -> list[ProgressGate]:
    raw_backlog = [
        record
        for record in records
        if record.promotion_status in {"raw", "extracted"} and record.source.value in {"mein", "du", "uns"}
    ]
    if len(raw_backlog) < 3:
        return []
    return [
        ProgressGate(
            severity="yellow",
            kind="raw-promotion-backlog",
            title="三源材料未升格",
            reason=f"还有 {len(raw_backlog)} 条材料停留在原始或已提炼状态。",
            action="挑最高频主题，升级为记忆卡、练习素材或原则候选。",
        )
    ]


def _gate_sort_key(gate: ProgressGate) -> tuple[int, str, str]:
    severity = {"red": 0, "yellow": 1, "green": 2}
    kind = {
        "weak-memory": 0,
        "unstable-memory": 1,
        "due-review": 2,
        "low-practice-score": 3,
        "front-card-gap": 4,
        "front-practice-gap": 5,
        "raw-promotion-backlog": 6,
    }
    return (severity.get(gate.severity, 9), f"{kind.get(gate.kind, 99):02d}", gate.title)


def _score_ratio(session: PracticeSession) -> float | None:
    if session.score is None or session.max_score in (None, 0):
        return None
    return float(session.score) / float(session.max_score)


def _front_label(front: ExamFront) -> str:
    return {
        ExamFront.CHOICE: "选择题",
        ExamFront.CASE: "案例题",
        ExamFront.ESSAY: "论文题",
    }[front]
