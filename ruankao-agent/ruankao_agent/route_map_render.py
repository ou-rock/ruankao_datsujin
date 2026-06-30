from __future__ import annotations

from html import escape

from .route_map_style import ROUTE_MAP_STYLE
from .theme import THEME_HEAD_SCRIPT, THEME_SCRIPT, THEME_STYLE, THEME_TOGGLE


def render_route_map(payload: dict[str, object]) -> str:
    routes = payload["routes"]
    assert isinstance(routes, list)
    priority = _priority_route(routes)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>三题型覆盖图 {escape(str(payload["as_of"]))}</title>
  {THEME_HEAD_SCRIPT}
  <style>
{ROUTE_MAP_STYLE}
{THEME_STYLE}
  </style>
</head>
<body>
  {THEME_TOGGLE}
  <main>
    <header>
      <h1>三题型覆盖图 {escape(str(payload["as_of"]))}</h1>
      <p class="status">选择、案例、论文三条战线的记忆库存与薄弱状态。</p>
    </header>
    {_priority_band(priority)}
    <div class="grid">{_route_cards(routes)}</div>
  </main>
  {THEME_SCRIPT}
</body>
</html>
"""


def _route_cards(routes: list[object]) -> str:
    items = []
    for route in routes:
        assert isinstance(route, dict)
        focus_titles = route["focus_titles"]
        assert isinstance(focus_titles, list)
        focus = "；".join(str(title) for title in focus_titles) if focus_titles else "暂无"
        status = str(route["status"])
        items.append(
            f"""<section class="route">
  <div class="route-head">
    <h2>{escape(str(route["label"]))}</h2>
    <span class="route-state {escape(status)}">状态：{escape(_route_status_label(status))}</span>
  </div>
  <div>{escape(str(route["action"]))}</div>
  <div class="metrics">
    {_metric("总卡片", route["total_cards"])}
    {_metric("到期", route["due_cards"])}
    {_metric("薄弱", route["weak_cards"])}
    {_metric("未测", route["untested_cards"])}
    {_metric("练习", route["practice_sessions"])}
    {_metric("今日练习", route["practice_today"])}
    {_metric("均分率", _ratio_text(route["average_score_ratio"]))}
  </div>
  <div class="route-foot">
    <span>最近练习：{escape(_value_text(route["last_practice_on"]))}</span>
    <span>焦点：{escape(focus)}</span>
  </div>
</section>"""
        )
    return "".join(items)


def _priority_route(routes: list[object]) -> dict[str, object]:
    parsed = [route for route in routes if isinstance(route, dict)]
    if not parsed:
        return {"label": "未标注", "action": "暂无路线数据，先生成三题型覆盖图。"}
    severity = {"red": 0, "yellow": 1, "green": 2}
    return min(parsed, key=lambda route: severity.get(str(route.get("status")), 3))


def _priority_band(route: dict[str, object]) -> str:
    label = escape(str(route.get("label", "未标注")))
    action = escape(str(route.get("action", "维持当前节奏。")))
    return f"""<section class="priority">
  <span>今日先打</span>
  <strong>{label}</strong>
  <p>{action}</p>
</section>"""


def _metric(label: str, value: object) -> str:
    return (
        f'<div class="metric"><span>{escape(label)}</span>'
        f"<strong>{escape(str(value))}</strong></div>"
    )


def _ratio_text(value: object) -> str:
    if value is None:
        return "未记录"
    return f"{float(value):.0%}"


def _value_text(value: object) -> str:
    if value is None or value == "":
        return "未记录"
    return str(value)


def _route_status_label(value: str) -> str:
    return {
        "red": "红灯",
        "yellow": "黄灯",
        "green": "绿灯",
    }.get(value, value)
