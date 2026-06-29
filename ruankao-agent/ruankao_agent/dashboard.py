from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from html import escape
from typing import Any


@dataclass(frozen=True, slots=True)
class DashboardSnapshot:
    campaign: Any
    as_of: date
    risk: Any
    notebook_name: str
    due_cards: int
    review_backlog_ratio: float


def _text_value(value: Any) -> str:
    if hasattr(value, "value"):
        candidate = getattr(value, "value")
        if isinstance(candidate, str):
            return candidate
    if hasattr(value, "name"):
        candidate = getattr(value, "name")
        if isinstance(candidate, str):
            return candidate.lower()
    return str(value)


def _phase_name(campaign: Any, as_of: date) -> str:
    phase = campaign.phase_for(as_of)
    if hasattr(phase, "name"):
        candidate = getattr(phase, "name")
        if isinstance(candidate, str):
            return candidate
    return str(phase)


def render_dashboard(snapshot: DashboardSnapshot) -> str:
    campaign = snapshot.campaign
    exam_date = campaign.exam_date
    days_remaining = campaign.days_remaining(snapshot.as_of)
    countdown = f"D-{days_remaining}" if days_remaining >= 0 else f"D+{-days_remaining}"
    phase_name = _phase_name(campaign, snapshot.as_of)
    phase_key = getattr(campaign.phase_for(snapshot.as_of), "key", "")
    reserve_days_consumed = campaign.reserve_days_consumed(snapshot.as_of)
    elapsed_days = max(0, (snapshot.as_of - campaign.start_date).days)
    main_battle_weeks_done = min(14, elapsed_days // 7)
    risk_text = _text_value(snapshot.risk)

    route_links = (
        ("选择题", "choice"),
        ("案例题", "case"),
        ("论文题", "essay"),
    )
    triad_links = (
        ("Mein", "20-mein/"),
        ("Du", "30-du/"),
        ("Uns", "40-uns/"),
    )
    war_room_links = (
        ("Memory War Room", "vault/10-memory-war-room/"),
        ("原则网络", "vault/00-map/原则网络.md"),
        ("战役总图", "vault/00-map/战役总图.md"),
        ("NotebookLM source map", "notebooklm"),
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Ruankao Agent Dashboard</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #1f2937;
      --muted: #6b7280;
      --line: #d1d5db;
      --panel: #f9fafb;
      --accent: #0f766e;
    }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: #ffffff;
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 32px 24px 48px;
    }}
    .hero {{
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 8px;
      padding: 24px;
    }}
    .eyebrow {{
      margin: 0 0 8px;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0;
      color: var(--muted);
    }}
    h1 {{
      margin: 0;
      font-size: 30px;
      line-height: 1.2;
    }}
    .meta {{
      margin-top: 12px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
    }}
    .metric {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      padding: 12px;
    }}
    .metric .label {{
      display: block;
      font-size: 12px;
      color: var(--muted);
      margin-bottom: 4px;
    }}
    .metric .value {{
      font-size: 18px;
      line-height: 1.3;
      font-weight: 600;
    }}
    section {{
      margin-top: 20px;
    }}
    h2 {{
      margin: 0 0 10px;
      font-size: 18px;
      line-height: 1.3;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
    }}
    .panel {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      padding: 14px;
    }}
    .panel p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.5;
    }}
    nav ul {{
      list-style: none;
      padding: 0;
      margin: 0;
      display: grid;
      gap: 8px;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    }}
    nav a {{
      color: var(--accent);
      text-decoration: none;
      font-weight: 600;
    }}
    .small {{
      font-size: 13px;
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <main>
    <div class="hero">
      <p class="eyebrow">System Architecture Designer</p>
      <h1>2026 H2 System Architecture Designer pass</h1>
      <div class="meta">
        <div class="metric">
          <span class="label">Countdown</span>
          <span class="value">{escape(countdown)}</span>
        </div>
        <div class="metric">
          <span class="label">Exam date</span>
          <span class="value">{escape(exam_date.isoformat())}</span>
        </div>
        <div class="metric">
          <span class="label">Campaign phase</span>
          <span class="value">{escape(phase_name)}</span>
          <div class="small">{escape(phase_key)}</div>
        </div>
        <div class="metric">
          <span class="label">Risk</span>
          <span class="value">{escape(risk_text)}</span>
        </div>
        <div class="metric">
          <span class="label">Main battle progress</span>
          <span class="value">{main_battle_weeks_done} / 14 weeks</span>
        </div>
        <div class="metric">
          <span class="label">Reserve pool</span>
          <span class="value">2 weeks</span>
          <div class="small">Consumed: {reserve_days_consumed} days</div>
        </div>
        <div class="metric">
          <span class="label">Reserve days consumed</span>
          <span class="value">{reserve_days_consumed}</span>
        </div>
        <div class="metric">
          <span class="label">Review backlog</span>
          <span class="value">{snapshot.review_backlog_ratio:.0%}</span>
        </div>
      </div>
    </div>

    <section>
      <h2>Today&#x27;s minimum loop</h2>
      <div class="grid">
        <div class="panel"><p>到期记忆复习</p></div>
        <div class="panel"><p>选择题 10 道并记录错因</p></div>
        <div class="panel"><p>案例题或论文题轮换触达</p></div>
        <div class="panel"><p>Mein / Du / Uns 三源沉淀</p></div>
      </div>
    </section>

    <section>
      <h2>Memory War Room</h2>
      <div class="grid">
        <div class="panel">
          <p>Due cards: {snapshot.due_cards}</p>
          <p>NotebookLM source: {escape(snapshot.notebook_name)}</p>
        </div>
        <div class="panel">
          <p>Mein / Du / Uns preserve raw material, agent analysis, and external evidence.</p>
        </div>
      </div>
    </section>

    <section>
      <h2>Routes</h2>
      <nav>
        <ul>
          {"".join(f'<li><a href="#{escape(route_id)}">{escape(label)}</a></li>' for label, route_id in route_links)}
        </ul>
      </nav>
      <div class="grid" style="margin-top: 12px;">
        <div class="panel" id="choice"><p>选择题：概念卡、对比卡、错因回炉。</p></div>
        <div class="panel" id="case"><p>案例题：质量属性、架构评估、图表和得分点。</p></div>
        <div class="panel" id="essay"><p>论文题：项目素材、结构模板、表达卡和架构论证。</p></div>
      </div>
    </section>

    <section>
      <h2>Knowledge Flow</h2>
      <div class="grid">
        {"".join(f'<div class="panel"><p><strong>{escape(label)}</strong> <span class="small">{escape(path)}</span></p></div>' for label, path in triad_links)}
      </div>
    </section>

    <section>
      <h2>Navigation</h2>
      <div class="grid">
        {"".join(f'<div class="panel"><p><a href="{escape(path)}">{escape(label)}</a></p></div>' for label, path in war_room_links)}
      </div>
    </section>
  </main>
</body>
</html>
"""
