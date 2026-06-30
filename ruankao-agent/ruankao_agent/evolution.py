from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path
from typing import Any

from .receipts import write_daily_receipt
from .theme import THEME_HEAD_SCRIPT, THEME_SCRIPT, THEME_STYLE, THEME_TOGGLE


@dataclass(frozen=True, slots=True)
class NightEvolutionResult:
    as_of: date
    json_path: Path
    html_path: Path
    action_count: int
    stage_only: bool


def night_evolution_json_path(root: Path | str, as_of: date) -> Path:
    return Path(root) / "evolution" / "staged" / f"{as_of.isoformat()}.json"


def night_evolution_html_path(root: Path | str, as_of: date) -> Path:
    return Path(root) / "reports" / "nightly" / f"{as_of.isoformat()}.html"


def write_night_evolution_plan(
    root: Path | str,
    *,
    as_of: date | None = None,
) -> NightEvolutionResult:
    root_path = Path(root)
    receipt = write_daily_receipt(root_path, as_of=as_of)
    payload = json.loads(receipt.json_path.read_text(encoding="utf-8"))
    plan = _evolution_payload(payload, receipt_json=receipt.json_path)

    json_path = night_evolution_json_path(root_path, receipt.as_of)
    html_path = night_evolution_html_path(root_path, receipt.as_of)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(render_night_evolution_plan(plan), encoding="utf-8")

    actions = plan["actions"]
    assert isinstance(actions, list)
    return NightEvolutionResult(
        as_of=receipt.as_of,
        json_path=json_path,
        html_path=html_path,
        action_count=len(actions),
        stage_only=True,
    )


def render_night_evolution_plan(plan: dict[str, object]) -> str:
    actions = plan["actions"]
    night_focus = plan.get("night_focus", {})
    assert isinstance(actions, list)
    assert isinstance(night_focus, dict)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>夜间进化草案 {escape(str(plan["as_of"]))}</title>
  {THEME_HEAD_SCRIPT}
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
      margin: 0 0 12px;
      font-size: 19px;
      line-height: 1.3;
    }}
    .status {{
      color: var(--muted);
      margin: 8px 0 0;
    }}
    .focus {{
      border-left: 4px solid var(--accent);
    }}
    .focus span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 4px;
    }}
    .focus strong {{
      display: block;
      font-size: 18px;
      line-height: 1.25;
    }}
    .focus p {{
      margin: 6px 0 0;
      color: var(--muted);
    }}
    section {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      padding: 16px;
      margin-top: 14px;
    }}
    .list {{
      display: grid;
      gap: 10px;
    }}
    .item {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--band);
      padding: 12px;
    }}
    .meta {{
      color: var(--muted);
      font-size: 12px;
      margin-top: 4px;
    }}
    .status-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 8px;
    }}
    .status-row span {{
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      color: var(--muted);
      padding: 5px 8px;
      font-size: 12px;
    }}
{THEME_STYLE}
  </style>
</head>
<body>
  {THEME_TOGGLE}
  <main>
    <header>
      <h1>夜间进化草案 {escape(str(plan["as_of"]))}</h1>
      <div class="status-row">
        <span>仅暂存：{escape(_yes_no(plan["stage_only"]))}</span>
        <span>来源日结：{escape(str(plan["receipt_json"]))}</span>
      </div>
    </header>
    {_night_focus_band(night_focus)}
    <section>
      <h2>明晚前只做这些</h2>
      <div class="list">{_action_items(actions)}</div>
    </section>
  </main>
  {THEME_SCRIPT}
</body>
</html>
"""


def _evolution_payload(receipt_payload: dict[str, Any], *, receipt_json: Path) -> dict[str, object]:
    metrics = receipt_payload.get("metrics", {})
    diagnostics = receipt_payload.get("memory_diagnostics", [])
    night_focus = receipt_payload.get("night_focus", {})
    assert isinstance(metrics, dict)
    assert isinstance(diagnostics, list)
    assert isinstance(night_focus, dict)
    actions = _build_actions(metrics, diagnostics, receipt_payload)
    return {
        "version": 1,
        "stage_only": True,
        "as_of": receipt_payload["as_of"],
        "receipt_json": str(receipt_json),
        "status": receipt_payload["status"],
        "night_focus": night_focus,
        "actions": actions,
    }


def _night_focus_band(focus: dict[object, object]) -> str:
    return f"""<section class="focus">
  <span>日结焦点</span>
  <strong>{escape(str(focus.get("title", "今晚沉淀今天的增量")))}</strong>
  <p>{escape(str(focus.get("reason", "暂无额外风险。")))}</p>
  <p>{escape(str(focus.get("action", "维持当前学习闭环。")))}</p>
</section>"""


def _build_actions(
    metrics: dict[str, Any],
    diagnostics: list[Any],
    receipt_payload: dict[str, Any],
) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    weak_count = int(metrics.get("weak_memory_cards", 0))
    due_count = int(metrics.get("due_cards", 0))
    reviews_today = int(metrics.get("reviews_today", 0))
    practice_today = int(metrics.get("practice_today", 0))
    cheko_cards = int(metrics.get("cheko_cards", 0))
    raw_records = int(metrics.get("raw_records", 0))
    memory_cards = int(metrics.get("memory_cards", 0))

    leech_titles = [
        str(item.get("title"))
        for item in diagnostics
        if isinstance(item, dict) and item.get("status") == "leech"
    ][:3]
    if weak_count:
        detail = "；".join(leech_titles) if leech_titles else "查看日结里的记忆诊断。"
        actions.append(
            _action(
                "repair-memory",
                "high",
                "修复薄弱记忆卡",
                f"优先处理 {weak_count} 张薄弱卡：{detail}",
            )
        )
    if due_count:
        actions.append(
            _action(
                "clear-due-cards",
                "high",
                "清空到期复习",
                f"明天先清 {due_count} 张到期卡，再做新题。",
            )
        )
    if reviews_today == 0 and memory_cards:
        actions.append(
            _action(
                "protect-retrieval",
                "medium",
                "保护检索练习",
                "今天没有复习记录，明天第一动作必须是检索而不是阅读。",
            )
        )
    if practice_today == 0:
        actions.append(
            _action(
                "protect-exam-practice",
                "medium",
                "保护实战练习",
                "今天没有选择/案例/论文练习记录，明天至少补一条实战记录。",
            )
        )
    if cheko_cards == 0:
        actions.append(
            _action(
                "seed-cheko",
                "medium",
                "把 Cheko 弱点入队",
                "Cheko 卡片数为 0，先运行 Cheko 入队动作。",
            )
        )
    if raw_records > memory_cards:
        actions.append(
            _action(
                "promote-raw-material",
                "medium",
                "把原始材料提升为卡片",
                "原始材料多于记忆卡，明天至少推广 1 条 Mein/Du/Uns。",
            )
        )
    if not actions:
        actions.append(
            _action(
                "maintain-loop",
                "low",
                "保持当前闭环",
                f"状态稳定：{receipt_payload.get('status', '')}",
            )
        )
    actions.append(
        _action(
            "write-tomorrow-plan",
            "low",
            "写明日三动作",
            "把明天的选择、案例或论文、记忆动作各写一句。",
        )
    )
    return actions


def _action(action_id: str, priority: str, title: str, detail: str) -> dict[str, str]:
    return {
        "id": action_id,
        "priority": priority,
        "title": title,
        "detail": detail,
    }


def _action_items(actions: list[object]) -> str:
    if not actions:
        return '<div class="item">暂无动作。</div>'
    items = []
    for action in actions:
        assert isinstance(action, dict)
        items.append(
            f"""<div class="item">
  <strong>{escape(str(action["title"]))}</strong>
  <div>{escape(str(action["detail"]))}</div>
  <div class="meta">优先级：{escape(_priority_label(action["priority"]))}</div>
</div>"""
        )
    return "".join(items)


def _yes_no(value: object) -> str:
    return "是" if bool(value) else "否"


def _priority_label(value: object) -> str:
    return {
        "high": "高",
        "medium": "中",
        "low": "低",
    }.get(str(value), str(value))
