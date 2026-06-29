from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path

from .domain import ExamFront
from .memory import MemoryDiagnostic, diagnose_memory
from .storage import MemoryCard, RuankaoStore


FRONT_LABELS = {
    ExamFront.CHOICE: "选择题",
    ExamFront.CASE: "案例题",
    ExamFront.ESSAY: "论文题",
}


@dataclass(frozen=True, slots=True)
class RouteMapResult:
    as_of: date
    json_path: Path
    html_path: Path


def route_map_json_path(root: Path | str, as_of: date) -> Path:
    return Path(root) / "reports" / "routes" / f"{as_of.isoformat()}.json"


def route_map_html_path(root: Path | str, as_of: date) -> Path:
    return Path(root) / "reports" / "routes" / f"{as_of.isoformat()}.html"


def write_route_map(root: Path | str, *, as_of: date | None = None) -> RouteMapResult:
    root_path = Path(root)
    day = as_of or date.today()
    store = RuankaoStore(root_path / "data" / "ruankao.db")
    store.initialize()
    cards = store.list_memory_cards()
    diagnostics = diagnose_memory(cards, store.list_review_logs(), as_of=day)
    payload = _route_map_payload(day, cards, diagnostics)

    json_path = route_map_json_path(root_path, day)
    html_path = route_map_html_path(root_path, day)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(render_route_map(payload), encoding="utf-8")
    return RouteMapResult(as_of=day, json_path=json_path, html_path=html_path)


def render_route_map(payload: dict[str, object]) -> str:
    routes = payload["routes"]
    assert isinstance(routes, list)
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
  </style>
</head>
<body>
  <main>
    <header>
      <h1>三题型覆盖图 {escape(str(payload["as_of"]))}</h1>
      <p class="status">选择、案例、论文三条战线的记忆库存与薄弱状态。</p>
    </header>
    <div class="grid">{_route_cards(routes)}</div>
  </main>
</body>
</html>
"""


def _route_map_payload(
    day: date,
    cards: list[MemoryCard],
    diagnostics: tuple[MemoryDiagnostic, ...],
) -> dict[str, object]:
    diagnostic_by_card = {diagnostic.card_id: diagnostic for diagnostic in diagnostics}
    return {
        "version": 1,
        "as_of": day.isoformat(),
        "routes": [
            _front_route(front, cards, diagnostic_by_card, day)
            for front in (ExamFront.CHOICE, ExamFront.CASE, ExamFront.ESSAY)
        ],
    }


def _front_route(
    front: ExamFront,
    cards: list[MemoryCard],
    diagnostic_by_card: dict[int, MemoryDiagnostic],
    day: date,
) -> dict[str, object]:
    route_cards = [card for card in cards if front in card.fronts]
    due_cards = [card for card in route_cards if card.next_due is not None and card.next_due <= day]
    route_diagnostics = [diagnostic_by_card[card.id] for card in route_cards if card.id in diagnostic_by_card]
    weak = [item for item in route_diagnostics if item.status in {"leech", "unstable"}]
    untested = [item for item in route_diagnostics if item.status == "untested"]
    status, action = _route_status_and_action(route_cards, due_cards, weak, untested)
    focus_titles = [item.title for item in weak[:3]] or [card.title for card in due_cards[:3]]
    return {
        "front": front.value,
        "label": FRONT_LABELS[front],
        "status": status,
        "action": action,
        "total_cards": len(route_cards),
        "due_cards": len(due_cards),
        "weak_cards": len(weak),
        "untested_cards": len(untested),
        "focus_titles": focus_titles,
    }


def _route_status_and_action(
    cards: list[MemoryCard],
    due_cards: list[MemoryCard],
    weak: list[MemoryDiagnostic],
    untested: list[MemoryDiagnostic],
) -> tuple[str, str]:
    if not cards:
        return ("red", "这条战线没有记忆卡，先补 3 张基础卡。")
    if weak:
        return ("red", "先修复薄弱卡，再追加新题。")
    if due_cards:
        return ("yellow", "先清空到期卡，再做新练习。")
    if len(untested) > len(cards) / 2:
        return ("yellow", "未测卡过多，安排首次检索。")
    return ("green", "维持当前节奏，继续积累题型素材。")


def _route_cards(routes: list[object]) -> str:
    items = []
    for route in routes:
        assert isinstance(route, dict)
        focus_titles = route["focus_titles"]
        assert isinstance(focus_titles, list)
        focus = "；".join(str(title) for title in focus_titles) if focus_titles else "暂无"
        items.append(
            f"""<section class="route">
  <h2>{escape(str(route["label"]))}</h2>
  <div class="meta">status={escape(str(route["status"]))}</div>
  <div>{escape(str(route["action"]))}</div>
  <div class="metrics">
    {_metric("总卡片", route["total_cards"])}
    {_metric("到期", route["due_cards"])}
    {_metric("薄弱", route["weak_cards"])}
    {_metric("未测", route["untested_cards"])}
  </div>
  <div class="meta">focus={escape(focus)}</div>
</section>"""
        )
    return "".join(items)


def _metric(label: str, value: object) -> str:
    return (
        f'<div class="metric"><span>{escape(label)}</span>'
        f"<strong>{escape(str(value))}</strong></div>"
    )
