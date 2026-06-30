from __future__ import annotations

from datetime import date

from .domain import CardType, ExamFront


def _gate_severity_label(value: object) -> str:
    return {
        "red": "红色闸门",
        "yellow": "黄色闸门",
        "green": "绿色",
    }.get(str(value), str(value))


def _rag_status_label(value: object) -> str:
    return {
        "leech": "反复低分",
        "unstable": "不稳定",
        "due": "到期",
        "untested": "未检验",
        "stable": "稳定",
        "low_score": "练习低分",
        "needs_review": "需要复盘",
        "recorded": "已记录",
        "raw": "原始",
        "extracted": "已提炼",
        "tested": "已检验",
        "promoted": "已升格",
    }.get(str(value), str(value))


def _risk_label(value: str) -> str:
    return {
        "red": "红灯",
        "yellow": "黄灯",
        "green": "绿灯",
    }.get(value, value)


def _card_type_label(card_type: CardType) -> str:
    return {
        CardType.PRINCIPLE: "原则卡",
        CardType.CONCEPT: "概念卡",
        CardType.COMPARISON: "对比卡",
        CardType.SCENARIO: "场景卡",
        CardType.EXPRESSION: "表达卡",
    }[card_type]


def _score_text(score: float | None, max_score: float | None) -> str:
    if score is None:
        return "未记录"
    if max_score is None:
        return f"{score:g}"
    return f"{score:g}/{max_score:g}"


def _score_ratio_text(score: float | None, max_score: float | None) -> str:
    if score is None or max_score is None or max_score <= 0:
        return "未记录"
    return f"{score / max_score:.0%}"


def _duration_text(duration_minutes: int | None) -> str:
    if duration_minutes is None:
        return "未记录"
    return f"{duration_minutes}分钟"


def _date_text(value: date | None) -> str:
    if value is None:
        return "未记录"
    return value.isoformat()


def _value_text(value: object) -> str:
    if value is None or value == "":
        return "未记录"
    return str(value)


def _front_label(front: ExamFront) -> str:
    return {
        ExamFront.CHOICE: "选择题",
        ExamFront.CASE: "案例题",
        ExamFront.ESSAY: "论文题",
    }[front]


def _fronts_label(fronts: tuple[ExamFront, ...]) -> str:
    if not fronts:
        return "未记录"
    return "、".join(_front_label(front) for front in fronts)


def _memory_status_label(value: str) -> str:
    return {
        "leech": "反复低分",
        "unstable": "不稳定",
        "due": "到期",
        "untested": "未检验",
        "stable": "稳定",
    }.get(value, value)
