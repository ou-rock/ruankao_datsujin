from __future__ import annotations

from html import escape


def _front_checks(default_all: bool = False) -> str:
    checked = " checked" if default_all else ""
    return f"""<div class="checks" aria-label="题型">
  <label><input type="checkbox" name="fronts" value="choice"{checked}>选择</label>
  <label><input type="checkbox" name="fronts" value="case"{checked}>案例</label>
  <label><input type="checkbox" name="fronts" value="essay"{checked}>论文</label>
</div>"""


def _promotion_status_radios() -> str:
    statuses = (
        ("raw", "原始", True),
        ("extracted", "已提炼", False),
        ("tested", "已检验", False),
        ("promoted", "已升格", False),
        ("rejected", "已淘汰", False),
    )
    buttons = []
    for value, label, checked in statuses:
        checked_attr = " checked" if checked else ""
        buttons.append(
            f'<label><input type="radio" name="promotion_status" value="{value}"{checked_attr}>{escape(label)}</label>'
        )
    return "\n                ".join(buttons)


def _relation_radios() -> str:
    relations = (
        ("supports", "支撑", True),
        ("constrains", "制约", False),
        ("conflicts_with", "冲突", False),
        ("derived_from", "派生", False),
    )
    buttons = []
    for value, label, checked in relations:
        checked_attr = " checked" if checked else ""
        buttons.append(
            f'<label><input type="radio" name="relation" value="{value}"{checked_attr}>{escape(label)}</label>'
        )
    return "\n                ".join(buttons)
