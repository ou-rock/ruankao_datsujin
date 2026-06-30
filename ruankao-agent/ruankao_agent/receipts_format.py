from __future__ import annotations

from html import escape
from typing import Callable


def _metric(label: str, value: object) -> str:
    return (
        f'<div class="metric"><span>{escape(label)}</span>'
        f"<strong>{escape(str(value))}</strong></div>"
    )


def _count_cards(counts: dict[object, object], *, labeler: Callable[[object], str] = str) -> str:
    if not counts:
        return '<div class="item">暂无数据</div>'
    return "".join(_metric(labeler(key), value) for key, value in counts.items())


def _score_text(score: object, max_score: object) -> str:
    if score is None:
        return "未记录"
    if max_score is None:
        return _number_text(score)
    return f"{_number_text(score)}/{_number_text(max_score)}"


def _number_text(value: object) -> str:
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def _duration_text(duration_minutes: object) -> str:
    if duration_minutes is None:
        return "未记录"
    return f"{duration_minutes}分钟"


def _value_text(value: object) -> str:
    if value is None or value == "":
        return "未记录"
    return str(value)


def _joined_text(values: object) -> str:
    if not isinstance(values, list):
        return _value_text(values)
    if not values:
        return "未记录"
    return "、".join(str(value) for value in values)


def _source_label(value: object) -> str:
    return {
        "mein": "Mein",
        "du": "Du",
        "uns": "Uns",
    }.get(str(value), str(value))


def _promotion_status_label(value: object) -> str:
    return {
        "raw": "原始",
        "extracted": "已提炼",
        "tested": "已检验",
        "promoted": "已升格",
        "rejected": "已淘汰",
    }.get(str(value), str(value))


def _memory_status_label(value: object) -> str:
    return {
        "leech": "反复低分",
        "unstable": "不稳定",
        "due": "到期",
        "untested": "未检验",
        "stable": "稳定",
    }.get(str(value), str(value))


def _card_type_label(value: object) -> str:
    return {
        "principle": "原则卡",
        "concept": "概念卡",
        "comparison": "对比卡",
        "scenario": "场景卡",
        "expression": "表达卡",
    }.get(str(value), str(value))


def _front_label(value: object) -> str:
    return {
        "choice": "选择题",
        "case": "案例题",
        "essay": "论文题",
    }.get(str(value), str(value))


def _fronts_label(values: object) -> str:
    if not isinstance(values, list):
        return _front_label(values)
    if not values:
        return "未记录"
    return "、".join(_front_label(value) for value in values)


def _ratio_text(value: object) -> str:
    if value is None:
        return "未记录"
    return f"{float(value):.0%}"
