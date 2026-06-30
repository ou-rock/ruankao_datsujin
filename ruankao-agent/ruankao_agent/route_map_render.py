from __future__ import annotations

from html import escape


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
  <style>
    :root {{
      color-scheme: light;
      --ink: #172026;
      --muted: #5e6b73;
      --line: #cfd8dc;
      --paper: #ffffff;
      --band: #f5f7f5;
      --accent: #0f766e;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: #fbfcfb;
      line-height: 1.55;
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 24px 20px 48px;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      padding-bottom: 18px;
      margin-bottom: 16px;
    }}
    h1 {{
      margin: 0;
      font-size: 28px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 0 0 8px;
      font-size: 19px;
      line-height: 1.3;
    }}
    .status {{
      color: var(--muted);
      margin: 8px 0 0;
    }}
    .priority {{
      border: 1px solid var(--line);
      border-left: 4px solid var(--accent);
      border-radius: 8px;
      background: #ffffff;
      padding: 14px 16px;
      margin-bottom: 14px;
    }}
    .priority span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 4px;
    }}
    .priority strong {{
      display: block;
      font-size: 18px;
      line-height: 1.25;
    }}
    .priority p {{
      margin: 6px 0 0;
      color: var(--muted);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 12px;
    }}
    .route {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      padding: 16px;
    }}
    .route-head {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
    }}
    .route-head h2 {{
      margin-bottom: 0;
    }}
    .route-state {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 3px 8px;
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
      background: var(--band);
    }}
    .route-state.red {{
      color: #8a1f11;
      border-color: #f0b6ad;
      background: #fff1f0;
    }}
    .route-state.yellow {{
      color: #7a5600;
      border-color: #ead18a;
      background: #fff8db;
    }}
    .route-state.green {{
      color: #17623a;
      border-color: #a9d5b8;
      background: #eefaf1;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
      margin-top: 10px;
    }}
    .metric {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--band);
      padding: 10px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 4px;
    }}
    .metric strong {{
      display: block;
      font-size: 18px;
      line-height: 1.25;
    }}
    .meta {{
      color: var(--muted);
      font-size: 12px;
      margin-top: 8px;
    }}
    .route-foot {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
    }}
    .route-foot span {{
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      color: var(--muted);
      padding: 5px 8px;
      font-size: 12px;
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>三题型覆盖图 {escape(str(payload["as_of"]))}</h1>
      <p class="status">选择、案例、论文三条战线的记忆库存与薄弱状态。</p>
    </header>
    {_priority_band(priority)}
    <div class="grid">{_route_cards(routes)}</div>
  </main>
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
