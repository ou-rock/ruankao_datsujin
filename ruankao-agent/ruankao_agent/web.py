from __future__ import annotations

import json
import webbrowser
from dataclasses import dataclass
from datetime import date
from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Mapping
from urllib.parse import parse_qs, unquote, urlparse

from .cheko import ChekoSeedResult, seed_cheko_cards as seed_cheko_memory_cards
from .dashboard import render_dashboard
from .domain import CardType, ExamFront, PrincipleRelationType, SourceIdentity
from .evolution import night_evolution_html_path, write_night_evolution_plan
from .export_state import state_export_path, write_state_export as write_local_state_export
from .learning import ensure_learning_resources
from .loop import build_daily_loop_snapshot, status_line
from .memory import MemoryDiagnostic, diagnose_memory
from .receipts import daily_receipt_html_path, write_daily_receipt
from .route_map import route_map_html_path, write_route_map
from .storage import MemoryCard, PracticeSession, RuankaoStore
from .vault import (
    initialize_vault,
    sync_memory_cards_to_vault,
    sync_raw_records_to_vault,
    write_principle_note,
)


@dataclass(frozen=True, slots=True)
class WorkbenchConfig:
    root: Path
    as_of: date | None = None


class WorkbenchApp:
    def __init__(self, config: WorkbenchConfig) -> None:
        self.config = config

    @property
    def root(self) -> Path:
        return self.config.root

    @property
    def db_path(self) -> Path:
        return self.root / "data" / "ruankao.db"

    @property
    def vault_path(self) -> Path:
        return self.root / "vault"

    @property
    def learning_path(self) -> Path:
        return self.root / "learning"

    @property
    def reports_path(self) -> Path:
        return self.root / "reports"

    @property
    def exports_path(self) -> Path:
        return self.root / "exports"

    @property
    def today(self) -> date:
        return self.config.as_of or date.today()

    def initialize(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.store().initialize()
        initialize_vault(self.vault_path)
        self._ensure_seed_principle()
        ensure_learning_resources(self.root)
        self.write_dashboard()

    def store(self) -> RuankaoStore:
        return RuankaoStore(self.db_path)

    def _ensure_seed_principle(self) -> None:
        note = self.vault_path / "10-memory-war-room" / "principles" / "场景先于方案.md"
        if note.exists():
            return
        write_principle_note(
            self.vault_path,
            title="场景先于方案",
            core_statement="先确认业务目标、边界和约束，再谈技术方案。",
            applies_when="任何架构设计、案例题、论文题。",
            conflicts=("技术先行",),
        )

    def snapshot(self):
        store = self.store()
        store.initialize()
        return build_daily_loop_snapshot(
            as_of=self.today,
            due_cards=store.count_due_cards(self.today),
            review_backlog_ratio=store.review_backlog_ratio(self.today),
            practice_sessions=store.list_practice_sessions(),
        )

    def write_dashboard(self) -> Path:
        snapshot = self.snapshot()
        dashboard_path = self.root / "dashboard.html"
        dashboard_path.write_text(render_dashboard(snapshot.dashboard), encoding="utf-8")
        return dashboard_path

    def add_raw_record(self, form: Mapping[str, list[str]]) -> int:
        store = self.store()
        store.initialize()
        return store.add_raw_record(
            source=SourceIdentity(_one(form, "source", SourceIdentity.MEIN.value)),
            text=_one(form, "text"),
            summary=_one(form, "summary"),
            topics=_split_lines(_one(form, "topics")),
            fronts=_fronts(form),
            promotion_status=_one(form, "promotion_status", "raw"),
        )

    def add_memory_card(self, form: Mapping[str, list[str]]) -> int:
        store = self.store()
        store.initialize()
        card_type = CardType(_one(form, "card_type", CardType.CONCEPT.value))
        title = _one(form, "title")
        prompt = _one(form, "prompt")
        answer = _one(form, "answer")
        source_record_id = _optional_int(_one(form, "source_record_id"))
        next_due = _optional_date(_one(form, "next_due"))
        card_id = store.add_memory_card(
            card_type=card_type,
            title=title,
            prompt=prompt,
            answer=answer,
            source_record_id=source_record_id,
            fronts=_fronts(form),
            next_due=next_due,
        )
        if card_type is CardType.PRINCIPLE:
            conflicts = _split_lines(_one(form, "conflicts"))
            applies_when = prompt or "待补充"
            write_principle_note(
                self.vault_path,
                title=title,
                core_statement=answer,
                applies_when=applies_when,
                conflicts=conflicts,
            )
        return card_id

    def add_principle_relation(self, form: Mapping[str, list[str]]) -> int:
        store = self.store()
        store.initialize()
        return store.add_principle_relation(
            from_card_id=int(_one(form, "from_card_id")),
            to_card_id=int(_one(form, "to_card_id")),
            relation=PrincipleRelationType(_one(form, "relation")),
            rationale=_one(form, "rationale"),
        )

    def add_practice_session(self, form: Mapping[str, list[str]]) -> int:
        store = self.store()
        store.initialize()
        return store.add_practice_session(
            front=ExamFront(_one(form, "front", ExamFront.CHOICE.value)),
            topic=_one(form, "topic"),
            source=_one(form, "source"),
            score=_optional_float(_one(form, "score")),
            max_score=_optional_float(_one(form, "max_score")),
            duration_minutes=_optional_int(_one(form, "duration_minutes")),
            summary=_one(form, "summary"),
            mistakes=_one(form, "mistakes"),
            created_on=_optional_date(_one(form, "created_on")) or self.today,
        )

    def record_review(self, form: Mapping[str, list[str]]) -> None:
        store = self.store()
        store.initialize()
        store.record_review(
            card_id=int(_one(form, "card_id")),
            reviewed_on=_optional_date(_one(form, "reviewed_on")) or self.today,
            grade=int(_one(form, "grade", "3")),
        )

    def seed_cheko_cards(self, form: Mapping[str, list[str]]) -> ChekoSeedResult:
        next_due = _optional_date(_one(form, "next_due")) or self.today
        result = seed_cheko_memory_cards(self.root, next_due=next_due)
        self.write_dashboard()
        return result

    def write_daily_receipt(self, form: Mapping[str, list[str]]):
        receipt_date = _optional_date(_one(form, "as_of")) or self.today
        return write_daily_receipt(self.root, as_of=receipt_date)

    def write_night_evolution_plan(self, form: Mapping[str, list[str]]):
        evolution_date = _optional_date(_one(form, "as_of")) or self.today
        return write_night_evolution_plan(self.root, as_of=evolution_date)

    def write_route_map(self, form: Mapping[str, list[str]]):
        route_date = _optional_date(_one(form, "as_of")) or self.today
        return write_route_map(self.root, as_of=route_date)

    def write_state_export(self, form: Mapping[str, list[str]]):
        export_date = _optional_date(_one(form, "as_of")) or self.today
        return write_local_state_export(self.root, as_of=export_date)

    def sync_memory_cards_to_vault(self, form: Mapping[str, list[str]]):
        store = self.store()
        store.initialize()
        overwrite = _one(form, "overwrite") == "1"
        return sync_memory_cards_to_vault(
            self.vault_path,
            store.list_memory_cards(),
            overwrite=overwrite,
        )

    def sync_raw_records_to_vault(self, form: Mapping[str, list[str]]):
        store = self.store()
        store.initialize()
        overwrite = _one(form, "overwrite") == "1"
        return sync_raw_records_to_vault(
            self.vault_path,
            store.list_raw_records(),
            overwrite=overwrite,
        )

    def render_home(self, message: str = "") -> str:
        self.initialize()
        store = self.store()
        records = store.list_raw_records()
        cards = store.list_memory_cards()
        practice_sessions = store.list_practice_sessions()
        review_logs = store.list_review_logs()
        snapshot = self.snapshot()
        due_cards = [card for card in cards if card.next_due is not None and card.next_due <= self.today]
        diagnostics = diagnose_memory(cards, review_logs, as_of=self.today)
        active_diagnostics = [
            diagnostic for diagnostic in diagnostics if diagnostic.status != "stable"
        ][:5]
        cheko_cards = [card for card in cards if card.title.startswith("Cheko")]
        cheko_due_cards = [
            card for card in cheko_cards if card.next_due is not None and card.next_due <= self.today
        ]
        principle_cards = [card for card in cards if card.card_type is CardType.PRINCIPLE]
        receipt_path = daily_receipt_html_path(self.root, self.today)
        receipt_link = (
            f'<a class="button secondary" href="/reports/daily/{escape(self.today.isoformat())}.html">打开今日日结</a>'
            if receipt_path.exists()
            else ""
        )
        evolution_path = night_evolution_html_path(self.root, self.today)
        evolution_link = (
            f'<a class="button secondary" href="/reports/nightly/{escape(self.today.isoformat())}.html">打开夜间草案</a>'
            if evolution_path.exists()
            else ""
        )
        route_path = route_map_html_path(self.root, self.today)
        route_link = (
            f'<a class="button secondary" href="/reports/routes/{escape(self.today.isoformat())}.html">打开三题型覆盖图</a>'
            if route_path.exists()
            else ""
        )
        export_path = state_export_path(self.root, self.today)
        export_link = (
            f'<a class="button secondary" href="/exports/state-{escape(self.today.isoformat())}.json">打开本地状态导出</a>'
            if export_path.exists()
            else ""
        )
        primary_action = _today_primary_action(
            due_cards=due_cards,
            diagnostics=active_diagnostics,
            practice_sessions=practice_sessions,
        )
        primary_reason = _today_primary_reason(snapshot.risk_reasons, due_cards)
        front_overview = _front_overview(cards, due_cards, practice_sessions, self.today)
        page_title = f"软考达人工作台 · {snapshot.countdown} · {snapshot.risk_text}"

        return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(page_title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172026;
      --muted: #5e6b73;
      --line: #cfd8dc;
      --paper: #ffffff;
      --band: #f4f7f5;
      --accent: #0f766e;
      --accent-ink: #063f3b;
      --warn: #b45309;
      --danger: #b91c1c;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: #fbfcfb;
    }}
    .skip-link {{
      position: absolute;
      left: 12px;
      top: 12px;
      transform: translateY(-160%);
      border: 1px solid var(--accent);
      border-radius: 6px;
      background: #fff;
      color: var(--accent-ink);
      padding: 8px 10px;
      font-weight: 750;
      text-decoration: none;
      z-index: 10;
    }}
    .skip-link:focus {{
      transform: translateY(0);
    }}
    header {{
      border-bottom: 1px solid var(--line);
      background: var(--paper);
    }}
    .top {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 20px 24px;
      display: grid;
      gap: 14px;
    }}
    .title-row {{
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      justify-content: space-between;
      gap: 12px;
    }}
    h1 {{
      margin: 0;
      font-size: 28px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    .status {{
      font-size: 14px;
      color: var(--muted);
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(148px, 1fr));
      gap: 10px;
    }}
    .metric {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px 12px;
      background: var(--band);
      min-height: 68px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 5px;
    }}
    .metric strong {{
      display: block;
      font-size: 18px;
      line-height: 1.25;
    }}
    .action-strip {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 12px;
      align-items: center;
      border: 1px solid var(--line);
      border-left: 5px solid var(--accent);
      border-radius: 8px;
      background: #fff;
      padding: 12px 14px;
    }}
    .action-strip.risk-red {{ border-left-color: var(--danger); }}
    .action-strip.risk-yellow {{ border-left-color: var(--warn); }}
    .action-kicker {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 750;
      margin-bottom: 4px;
    }}
    .action-title {{
      font-size: 18px;
      font-weight: 800;
      line-height: 1.35;
    }}
    .action-reason {{
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
      margin-top: 4px;
    }}
    .action-buttons {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: flex-end;
    }}
    .front-strip {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }}
    .front-card {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 10px 12px;
      display: grid;
      gap: 8px;
      min-height: 116px;
    }}
    .front-card.red {{ border-top: 4px solid var(--danger); }}
    .front-card.yellow {{ border-top: 4px solid var(--warn); }}
    .front-card.green {{ border-top: 4px solid var(--accent); }}
    .front-head {{
      display: flex;
      justify-content: space-between;
      gap: 8px;
      align-items: baseline;
      font-weight: 800;
    }}
    .front-state {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 750;
    }}
    .front-metrics {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 6px;
    }}
    .front-mini {{
      background: var(--band);
      border-radius: 6px;
      padding: 6px;
      min-height: 46px;
    }}
    .front-mini span {{
      display: block;
      color: var(--muted);
      font-size: 10px;
      line-height: 1.1;
    }}
    .front-mini strong {{
      display: block;
      font-size: 15px;
      line-height: 1.35;
    }}
    .front-action {{
      color: var(--accent-ink);
      font-size: 12px;
      font-weight: 750;
      line-height: 1.35;
    }}
    main {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 18px 24px 48px;
      display: grid;
      grid-template-columns: minmax(220px, 280px) minmax(0, 1fr);
      gap: 18px;
      align-items: start;
    }}
    aside {{
      position: sticky;
      top: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      padding: 12px;
    }}
    aside a {{
      display: block;
      padding: 9px 10px;
      border-radius: 6px;
      color: var(--accent-ink);
      text-decoration: none;
      font-weight: 600;
    }}
    aside a:hover {{ background: var(--band); }}
    .content {{
      display: grid;
      gap: 16px;
    }}
    section {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      padding: 16px;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 19px;
      line-height: 1.3;
    }}
    h3 {{
      margin: 0 0 8px;
      font-size: 15px;
      line-height: 1.3;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 12px;
    }}
    form {{
      display: grid;
      gap: 10px;
    }}
    label {{
      display: grid;
      gap: 5px;
      font-size: 13px;
      color: var(--muted);
      font-weight: 600;
    }}
    .field {{
      display: grid;
      gap: 5px;
    }}
    .field-label {{
      font-size: 13px;
      color: var(--muted);
      font-weight: 600;
    }}
    input, textarea, select {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 9px 10px;
      font: inherit;
      color: var(--ink);
      background: #fff;
    }}
    textarea {{
      min-height: 92px;
      resize: vertical;
      line-height: 1.45;
    }}
    .checks {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .checks label {{
      display: inline-flex;
      grid-template-columns: none;
      align-items: center;
      gap: 6px;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 6px 9px;
      background: var(--band);
    }}
    .checks input {{ width: auto; }}
    .segmented {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 6px;
    }}
    .segmented.flow {{
      grid-template-columns: repeat(auto-fit, minmax(96px, 1fr));
    }}
    .segmented label {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      min-height: 40px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--accent-ink);
      cursor: pointer;
      font-size: 13px;
      text-align: center;
    }}
    .segmented input {{
      width: auto;
      margin: 0;
      accent-color: var(--accent);
    }}
    button, .button {{
      appearance: none;
      border: 1px solid var(--accent);
      border-radius: 6px;
      background: var(--accent);
      color: #fff;
      font: inherit;
      font-weight: 700;
      padding: 9px 12px;
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      justify-content: center;
      align-items: center;
      min-height: 40px;
    }}
    .button.secondary, button.secondary {{
      border-color: var(--line);
      color: var(--accent-ink);
      background: #fff;
    }}
    .grade-row {{
      display: grid;
      grid-template-columns: repeat(6, minmax(44px, 1fr));
      gap: 6px;
      margin-top: 8px;
    }}
    .grade-button {{
      border-color: var(--line);
      background: #fff;
      color: var(--accent-ink);
      min-height: 46px;
      padding: 6px 4px;
      display: grid;
      gap: 2px;
      justify-items: center;
      align-content: center;
    }}
    .grade-button span {{
      font-size: 15px;
      line-height: 1;
    }}
    .grade-button small {{
      color: var(--muted);
      font-size: 10px;
      line-height: 1;
    }}
    .grade-button.low {{
      color: var(--danger);
    }}
    .grade-button:hover {{
      border-color: var(--accent);
      background: var(--band);
    }}
    .message {{
      border: 1px solid #99f6e4;
      background: #ecfdf5;
      color: #065f46;
      border-radius: 6px;
      padding: 10px 12px;
      font-weight: 650;
    }}
    .list {{
      display: grid;
      gap: 10px;
    }}
    .item {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      background: #fff;
    }}
    .item-title {{
      display: flex;
      justify-content: space-between;
      gap: 8px;
      font-weight: 750;
    }}
    .meta {{
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
      margin-top: 4px;
    }}
    .empty {{
      color: var(--muted);
      border: 1px dashed var(--line);
      border-radius: 6px;
      padding: 12px;
      background: var(--band);
    }}
    .split {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 14px;
    }}
    .footer-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
    }}
    @media (max-width: 820px) {{
      main {{ grid-template-columns: 1fr; padding: 14px 14px 40px; }}
      aside {{ position: static; }}
      .top {{ padding: 18px 14px; }}
      h1 {{ font-size: 24px; }}
      .action-strip {{ grid-template-columns: 1fr; }}
      .action-buttons {{ justify-content: stretch; }}
      .action-buttons .button {{ width: 100%; }}
      .front-strip {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <a class="skip-link" href="#today">跳到今日闭环</a>
  <header>
    <div class="top">
      <div class="title-row">
        <h1>软考达人工作台</h1>
        <div class="status">{escape(status_line(snapshot))}</div>
      </div>
      <div class="metrics">
        <div class="metric"><span>目标日期</span><strong>{escape(snapshot.dashboard.campaign.exam_date.isoformat())}</strong></div>
        <div class="metric"><span>今日阶段</span><strong>{escape(snapshot.phase_name)}</strong></div>
        <div class="metric"><span>到期复习</span><strong>{len(due_cards)}</strong></div>
        <div class="metric"><span>记忆卡</span><strong>{len(cards)}</strong></div>
        <div class="metric"><span>原始材料</span><strong>{len(records)}</strong></div>
        <div class="metric"><span>风险</span><strong>{escape(snapshot.risk_text)}</strong></div>
      </div>
      <div class="action-strip risk-{escape(snapshot.risk_text)}">
        <div>
          <div class="action-kicker">今日第一动作</div>
          <div class="action-title">{escape(primary_action)}</div>
          <div class="action-reason">{escape(primary_reason)}</div>
        </div>
        <div class="action-buttons">
          <a class="button" href="#today">处理今日闭环</a>
          <a class="button secondary" href="#practice">记录练习</a>
          <a class="button secondary" href="/learning/today.html">今日三任务</a>
        </div>
      </div>
      <div class="front-strip" aria-label="三题型雷达">
        {_front_cards(front_overview)}
      </div>
    </div>
  </header>
  <main>
    <aside>
      <a href="#today">今日闭环</a>
      <a href="#cheko">学习信号</a>
      <a href="#practice">练习记录</a>
      <a href="#capture">三源录入</a>
      <a href="#cards">记忆卡</a>
      <a href="#principles">原则网络</a>
      <a href="/learning/">学习台</a>
      <a href="#vault">Obsidian</a>
      <a href="/dashboard.html">静态总图</a>
      <a href="/api/status">状态 JSON</a>
    </aside>
    <div class="content">
      {_message(message)}
      <section id="today">
        <h2>今日闭环</h2>
        <div class="split">
          <div>
            <h3>到期卡片</h3>
            {_card_list(due_cards, with_review=True, today=self.today)}
          </div>
          <div>
            <h3>最小行动</h3>
            <div class="list">
              <div class="item">复习所有到期卡片，低于 3 分立刻明天再见。</div>
              <div class="item">选择题保持概念密度，案例题保持论证手感，论文题保持素材活性。</div>
              <div class="item">每次学习至少沉淀一条 Mein / Du / Uns。</div>
            </div>
            <h3 style="margin-top:14px;">风险原因</h3>
            {_risk_reason_list(snapshot.risk_reasons)}
            <h3 style="margin-top:14px;">记忆诊断</h3>
            {_diagnostic_list(active_diagnostics)}
            <form method="post" action="/daily/receipt" style="margin-top:10px;">
              <input type="hidden" name="as_of" value="{escape(self.today.isoformat())}">
              <button type="submit">生成日结回执</button>
            </form>
            <form method="post" action="/night/evolve" style="margin-top:10px;">
              <input type="hidden" name="as_of" value="{escape(self.today.isoformat())}">
              <button type="submit">生成夜间进化草案</button>
            </form>
            <form method="post" action="/routes/map" style="margin-top:10px;">
              <input type="hidden" name="as_of" value="{escape(self.today.isoformat())}">
              <button type="submit">生成三题型覆盖图</button>
            </form>
            <form method="post" action="/state/export" style="margin-top:10px;">
              <input type="hidden" name="as_of" value="{escape(self.today.isoformat())}">
              <button type="submit">导出本地状态 JSON</button>
            </form>
            <div class="footer-actions">{receipt_link}{evolution_link}{route_link}{export_link}</div>
          </div>
        </div>
      </section>

      <section id="cheko">
        <h2>学习信号</h2>
        <div class="split">
          <div>
            <h3>Cheko 入队</h3>
            <div class="metrics">
              <div class="metric"><span>Cheko 记忆卡</span><strong>{len(cheko_cards)}</strong></div>
              <div class="metric"><span>今日到期</span><strong>{len(cheko_due_cards)}</strong></div>
            </div>
            <form method="post" action="/cheko/cards" style="margin-top:10px;">
              <input type="hidden" name="next_due" value="{escape(self.today.isoformat())}">
              <button type="submit">把 Cheko 弱点入队</button>
            </form>
            <div class="footer-actions">
              <a class="button secondary" href="/learning/cheko-sync.html">同步信号</a>
              <a class="button secondary" href="/learning/today.html">今日三任务</a>
            </div>
          </div>
          <div>
            <h3>最近 Cheko 卡片</h3>
            {_card_list(cheko_cards[-4:], with_review=False, today=self.today)}
          </div>
        </div>
      </section>

      <section id="practice">
        <h2>练习记录</h2>
        <div class="split">
          <form method="post" action="/practice">
            <div class="grid">
              <div class="field">
                <div class="field-label">题型</div>
                <div class="segmented" aria-label="练习题型">
                  <label><input type="radio" name="front" value="choice" checked>选择题</label>
                  <label><input type="radio" name="front" value="case">案例题</label>
                  <label><input type="radio" name="front" value="essay">论文题</label>
                </div>
              </div>
              <label>日期
                <input type="date" name="created_on" value="{escape(self.today.isoformat())}">
              </label>
            </div>
            <label>主题
              <input name="topic" required placeholder="系统架构设计错题 / 项目背景段">
            </label>
            <div class="grid">
              <label>得分
                <input type="number" name="score" min="0" step="0.5" inputmode="decimal">
              </label>
              <label>满分
                <input type="number" name="max_score" min="1" step="0.5" inputmode="decimal">
              </label>
              <label>耗时分钟
                <input type="number" name="duration_minutes" min="1" step="1" inputmode="numeric">
              </label>
            </div>
            <label>来源
              <input name="source" placeholder="Cheko / 真题 / 自写">
            </label>
            <label>练习摘要
              <textarea name="summary" required></textarea>
            </label>
            <label>错因 / 卡点
              <textarea name="mistakes"></textarea>
            </label>
            <button type="submit">记录练习</button>
          </form>
          <div>
            <h3>最近练习</h3>
            {_practice_list(practice_sessions[-8:])}
          </div>
        </div>
      </section>

      <section id="capture">
        <h2>三源录入</h2>
        <form method="post" action="/records">
          <div class="grid">
            <div class="field">
              <div class="field-label">来源</div>
              <div class="segmented" aria-label="三源来源">
                <label><input type="radio" name="source" value="mein" checked>Mein</label>
                <label><input type="radio" name="source" value="du">Du</label>
                <label><input type="radio" name="source" value="uns">Uns</label>
              </div>
            </div>
            <div class="field">
              <div class="field-label">状态</div>
              <div class="segmented flow" aria-label="三源状态">
                <label><input type="radio" name="promotion_status" value="raw" checked>raw</label>
                <label><input type="radio" name="promotion_status" value="extracted">extracted</label>
                <label><input type="radio" name="promotion_status" value="tested">tested</label>
                <label><input type="radio" name="promotion_status" value="promoted">promoted</label>
                <label><input type="radio" name="promotion_status" value="rejected">rejected</label>
              </div>
            </div>
          </div>
          <label>原文 / 灵感 / 对话摘录
            <textarea name="text" required></textarea>
          </label>
          <label>一句话摘要
            <textarea name="summary" required></textarea>
          </label>
          <label>主题，每行一个
            <input name="topics" placeholder="质量属性&#10;架构评估">
          </label>
          {_front_checks()}
          <button type="submit">沉淀到三源库</button>
        </form>
      </section>

      <section id="cards">
        <h2>记忆卡</h2>
        <div class="split">
          <form method="post" action="/cards">
            <div class="grid">
              <label>类型
                <select name="card_type">
                  <option value="concept">概念卡</option>
                  <option value="principle">原则卡</option>
                  <option value="comparison">对比卡</option>
                  <option value="scenario">场景卡</option>
                  <option value="expression">表达卡</option>
                </select>
              </label>
              <label>下次复习
                <input type="date" name="next_due" value="{escape(self.today.isoformat())}">
              </label>
            </div>
            <label>标题
              <input name="title" required>
            </label>
            <label>问题 / 适用场景
              <textarea name="prompt" required></textarea>
            </label>
            <label>答案 / 核心表述
              <textarea name="answer" required></textarea>
            </label>
            <label>关联原始材料 ID
              <input name="source_record_id" inputmode="numeric">
            </label>
            <label>冲突原则，每行一个。仅原则卡使用
              <input name="conflicts" placeholder="技术先行">
            </label>
            {_front_checks(default_all=True)}
            <button type="submit">创建记忆卡</button>
          </form>
          <div>
            <h3>最近卡片</h3>
            {_card_list(cards[-8:], with_review=False, today=self.today)}
          </div>
        </div>
      </section>

      <section id="principles">
        <h2>原则网络</h2>
        <div class="split">
          <form method="post" action="/relations">
            <div class="grid">
              <label>From 原则 ID
                <input name="from_card_id" inputmode="numeric" required>
              </label>
              <label>To 原则 ID
                <input name="to_card_id" inputmode="numeric" required>
              </label>
            </div>
            <label>关系
              <select name="relation">
                <option value="supports">supports 支撑</option>
                <option value="constrains">constrains 制约</option>
                <option value="conflicts_with">conflicts_with 冲突</option>
                <option value="derived_from">derived_from 派生</option>
              </select>
            </label>
            <label>为什么这样连接
              <textarea name="rationale" required></textarea>
            </label>
            <button type="submit">连接原则</button>
          </form>
          <div>
            <h3>原则卡 ID</h3>
            {_card_list(principle_cards, with_review=False, today=self.today)}
          </div>
        </div>
      </section>

      <section id="vault">
        <h2>Obsidian 与总图</h2>
        <div class="list">
          <div class="item">
            <div class="item-title">Vault 路径</div>
            <div class="meta">{escape(str(self.vault_path))}</div>
          </div>
          <div class="item">
            <div class="item-title">原则网络</div>
            <div class="meta"><a href="/vault/00-map/原则网络.md">vault/00-map/原则网络.md</a></div>
          </div>
          <div class="item">
            <div class="item-title">战役总图</div>
            <div class="meta"><a href="/vault/00-map/战役总图.md">vault/00-map/战役总图.md</a></div>
          </div>
        </div>
        <div class="footer-actions">
          <a class="button secondary" href="/learning/">打开学习台</a>
          <a class="button secondary" href="/dashboard.html">打开静态 HTML 总图</a>
          <a class="button secondary" href="/api/status">查看状态 JSON</a>
          {export_link}
        </div>
        <form method="post" action="/vault/sync" style="margin-top:10px;">
          <button type="submit">同步记忆卡到 Obsidian</button>
        </form>
        <form method="post" action="/vault/sync-raw" style="margin-top:10px;">
          <button type="submit">同步三源材料到 Obsidian</button>
        </form>
      </section>
    </div>
  </main>
</body>
</html>
"""

    def render_dashboard_page(self) -> str:
        self.initialize()
        return (self.root / "dashboard.html").read_text(encoding="utf-8")

    def render_learning_file(self, relative: str = "index.html") -> str:
        self.initialize()
        target = self._safe_learning_file(relative)
        return target.read_text(encoding="utf-8")

    def render_report_file(self, relative: str) -> str:
        target = self._safe_report_file(relative)
        return target.read_text(encoding="utf-8")

    def render_export_file(self, relative: str) -> str:
        target = self._safe_export_file(relative)
        return target.read_text(encoding="utf-8")

    def _safe_learning_file(self, relative: str) -> Path:
        learning_root = self.learning_path.resolve()
        target = (learning_root / relative).resolve()
        if learning_root not in target.parents and target != learning_root:
            raise PermissionError(relative)
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(relative)
        return target

    def _safe_report_file(self, relative: str) -> Path:
        reports_root = self.reports_path.resolve()
        target = (reports_root / relative).resolve()
        if reports_root not in target.parents and target != reports_root:
            raise PermissionError(relative)
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(relative)
        return target

    def _safe_export_file(self, relative: str) -> Path:
        exports_root = self.exports_path.resolve()
        target = (exports_root / relative).resolve()
        if exports_root not in target.parents and target != exports_root:
            raise PermissionError(relative)
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(relative)
        return target

    def render_status_json(self) -> str:
        snapshot = self.snapshot()
        payload = {
            "status": status_line(snapshot),
            "phase": snapshot.phase_name,
            "countdown": snapshot.countdown,
            "risk": snapshot.risk_text,
            "risk_reasons": list(snapshot.risk_reasons),
            "due_cards": snapshot.dashboard.due_cards,
            "review_backlog_ratio": snapshot.dashboard.review_backlog_ratio,
            "root": str(self.root),
            "vault": str(self.vault_path),
            "learning": str(self.learning_path),
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)


def serve_workbench(
    root: Path,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    as_of: date | None = None,
    open_browser: bool = False,
) -> None:
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=as_of))
    app.initialize()
    handler_cls = _handler_for(app)
    server = ThreadingHTTPServer((host, port), handler_cls)
    url = f"http://{host}:{server.server_port}/"
    print(f"Ruankao workbench: {url}", flush=True)
    if open_browser:
        webbrowser.open(url)
    server.serve_forever()


def _handler_for(app: WorkbenchApp):
    class WorkbenchHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/":
                query = parse_qs(parsed.query)
                self._send_html(app.render_home(message=_one(query, "message")))
                return
            if parsed.path == "/dashboard.html":
                self._send_html(app.render_dashboard_page())
                return
            if parsed.path == "/api/status":
                self._send_text(app.render_status_json(), "application/json; charset=utf-8")
                return
            if parsed.path in ("/learning", "/learning/"):
                self._send_html(app.render_learning_file())
                return
            if parsed.path.startswith("/learning/"):
                self._send_learning_file(_learning_relative_path(parsed.path))
                return
            if parsed.path.startswith("/reports/"):
                self._send_report_file(_report_relative_path(parsed.path))
                return
            if parsed.path.startswith("/exports/"):
                self._send_export_file(_export_relative_path(parsed.path))
                return
            if parsed.path.startswith("/vault/"):
                self._send_vault_file(_vault_relative_path(parsed.path))
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

        def do_POST(self) -> None:
            form = self._read_form()
            try:
                if self.path == "/records":
                    record_id = app.add_raw_record(form)
                    self._redirect(f"/?message=raw-record-{record_id}-saved")
                    return
                if self.path == "/cards":
                    card_id = app.add_memory_card(form)
                    self._redirect(f"/?message=memory-card-{card_id}-saved")
                    return
                if self.path == "/relations":
                    relation_id = app.add_principle_relation(form)
                    self._redirect(f"/?message=principle-relation-{relation_id}-saved")
                    return
                if self.path == "/practice":
                    session_id = app.add_practice_session(form)
                    self._redirect(f"/?message=practice-session-{session_id}-saved")
                    return
                if self.path == "/reviews":
                    app.record_review(form)
                    self._redirect("/?message=review-saved")
                    return
                if self.path == "/cheko/cards":
                    result = app.seed_cheko_cards(form)
                    self._redirect(
                        f"/?message=cheko-cards-created-{len(result.created_card_ids)}"
                        f"-skipped-{len(result.skipped_titles)}"
                    )
                    return
                if self.path == "/daily/receipt":
                    result = app.write_daily_receipt(form)
                    self._redirect(f"/?message=daily-receipt-{result.as_of.isoformat()}-written")
                    return
                if self.path == "/night/evolve":
                    result = app.write_night_evolution_plan(form)
                    self._redirect(
                        f"/?message=night-evolution-{result.as_of.isoformat()}"
                        f"-actions-{result.action_count}-staged"
                    )
                    return
                if self.path == "/routes/map":
                    result = app.write_route_map(form)
                    self._redirect(f"/?message=route-map-{result.as_of.isoformat()}-written")
                    return
                if self.path == "/state/export":
                    result = app.write_state_export(form)
                    self._redirect(f"/?message=state-export-{result.as_of.isoformat()}-written")
                    return
                if self.path == "/vault/sync":
                    result = app.sync_memory_cards_to_vault(form)
                    self._redirect(
                        f"/?message=vault-sync-written-{len(result.written_paths)}"
                        f"-skipped-{len(result.skipped_paths)}"
                    )
                    return
                if self.path == "/vault/sync-raw":
                    result = app.sync_raw_records_to_vault(form)
                    self._redirect(
                        f"/?message=raw-vault-sync-written-{len(result.written_paths)}"
                        f"-skipped-{len(result.skipped_paths)}"
                    )
                    return
            except Exception as exc:  # pragma: no cover - exercised by real browser use.
                self.send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

        def log_message(self, format: str, *args: object) -> None:
            return

        def _read_form(self) -> Mapping[str, list[str]]:
            length = int(self.headers.get("Content-Length", "0"))
            payload = self.rfile.read(length).decode("utf-8")
            return parse_qs(payload, keep_blank_values=True)

        def _send_html(self, html: str) -> None:
            self._send_text(html, "text/html; charset=utf-8")

        def _send_text(self, text: str, content_type: str) -> None:
            encoded = text.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def _send_vault_file(self, relative: str) -> None:
            vault_root = app.vault_path.resolve()
            target = (vault_root / relative).resolve()
            if vault_root not in target.parents and target != vault_root:
                self.send_error(HTTPStatus.FORBIDDEN, "Forbidden")
                return
            if not target.exists() or not target.is_file():
                self.send_error(HTTPStatus.NOT_FOUND, "Not found")
                return
            self._send_text(target.read_text(encoding="utf-8"), "text/plain; charset=utf-8")

        def _send_learning_file(self, relative: str) -> None:
            try:
                self._send_html(app.render_learning_file(relative))
            except PermissionError:
                self.send_error(HTTPStatus.FORBIDDEN, "Forbidden")
            except FileNotFoundError:
                self.send_error(HTTPStatus.NOT_FOUND, "Not found")

        def _send_report_file(self, relative: str) -> None:
            try:
                self._send_html(app.render_report_file(relative))
            except PermissionError:
                self.send_error(HTTPStatus.FORBIDDEN, "Forbidden")
            except FileNotFoundError:
                self.send_error(HTTPStatus.NOT_FOUND, "Not found")

        def _send_export_file(self, relative: str) -> None:
            try:
                self._send_text(app.render_export_file(relative), "application/json; charset=utf-8")
            except PermissionError:
                self.send_error(HTTPStatus.FORBIDDEN, "Forbidden")
            except FileNotFoundError:
                self.send_error(HTTPStatus.NOT_FOUND, "Not found")

        def _redirect(self, location: str) -> None:
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", location)
            self.end_headers()

    return WorkbenchHandler


def _one(form: Mapping[str, list[str]], key: str, default: str = "") -> str:
    values = form.get(key)
    if not values:
        return default
    return values[0].strip()


def _vault_relative_path(request_path: str) -> str:
    return unquote(request_path.removeprefix("/vault/"))


def _learning_relative_path(request_path: str) -> str:
    return unquote(request_path.removeprefix("/learning/"))


def _report_relative_path(request_path: str) -> str:
    return unquote(request_path.removeprefix("/reports/"))


def _export_relative_path(request_path: str) -> str:
    return unquote(request_path.removeprefix("/exports/"))


def _optional_int(value: str) -> int | None:
    return int(value) if value.strip() else None


def _optional_float(value: str) -> float | None:
    return float(value) if value.strip() else None


def _optional_date(value: str) -> date | None:
    return date.fromisoformat(value) if value.strip() else None


def _split_lines(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.replace(",", "\n").splitlines() if item.strip())


def _fronts(form: Mapping[str, list[str]]) -> tuple[ExamFront, ...]:
    values = form.get("fronts") or []
    return tuple(ExamFront(value) for value in values if value)


def _front_checks(default_all: bool = False) -> str:
    checked = " checked" if default_all else ""
    return f"""<div class="checks" aria-label="题型">
  <label><input type="checkbox" name="fronts" value="choice"{checked}>选择</label>
  <label><input type="checkbox" name="fronts" value="case"{checked}>案例</label>
  <label><input type="checkbox" name="fronts" value="essay"{checked}>论文</label>
</div>"""


def _message(message: str) -> str:
    if not message:
        return ""
    return f'<div class="message" role="status">{escape(message)}</div>'


def _today_primary_action(
    *,
    due_cards: list[MemoryCard],
    diagnostics: list[MemoryDiagnostic],
    practice_sessions: list[PracticeSession],
) -> str:
    if due_cards:
        return f"先复习 {len(due_cards)} 张到期卡，低于 3 分立刻明天再见。"
    if diagnostics:
        diagnostic = diagnostics[0]
        return f"先修复 {diagnostic.title}：{diagnostic.action}"
    if not practice_sessions:
        return "先记录一次选择、案例或论文练习，建立题型手感基线。"
    return "开启一轮学习模式，把新的 Mein / Du / Uns 沉淀到底层。"


def _today_primary_reason(reasons: tuple[str, ...], due_cards: list[MemoryCard]) -> str:
    if reasons:
        return reasons[0]
    if due_cards:
        return "到期复习是今天最稳定的提分动作。"
    return "当前风险信号正常，继续保持最小闭环。"


def _front_overview(
    cards: list[MemoryCard],
    due_cards: list[MemoryCard],
    practice_sessions: list[PracticeSession],
    today: date,
) -> list[dict[str, object]]:
    labels = {
        ExamFront.CHOICE: "选择题",
        ExamFront.CASE: "案例题",
        ExamFront.ESSAY: "论文题",
    }
    rows: list[dict[str, object]] = []
    for front in (ExamFront.CHOICE, ExamFront.CASE, ExamFront.ESSAY):
        front_cards = [card for card in cards if front in card.fronts]
        front_due = [card for card in due_cards if front in card.fronts]
        front_practice = [session for session in practice_sessions if session.front == front]
        practice_today = [session for session in front_practice if session.created_on == today]
        if front_due:
            state = "red"
            action = "先清到期卡"
        elif not practice_today:
            state = "yellow"
            action = "今天补一次练习"
        else:
            state = "green"
            action = "保持节奏"
        rows.append(
            {
                "front": front.value,
                "label": labels[front],
                "state": state,
                "cards": len(front_cards),
                "due": len(front_due),
                "practice_today": len(practice_today),
                "action": action,
            }
        )
    return rows


def _front_cards(rows: list[dict[str, object]]) -> str:
    cards = []
    for row in rows:
        state = escape(str(row["state"]))
        cards.append(
            f"""<div class="front-card {state}">
  <div class="front-head"><span>{escape(str(row["label"]))}</span><span class="front-state">{state}</span></div>
  <div class="front-metrics">
    <div class="front-mini"><span>卡片</span><strong>{escape(str(row["cards"]))}</strong></div>
    <div class="front-mini"><span>到期</span><strong>{escape(str(row["due"]))}</strong></div>
    <div class="front-mini"><span>今日练习</span><strong>{escape(str(row["practice_today"]))}</strong></div>
  </div>
  <div class="front-action">{escape(str(row["action"]))}</div>
</div>"""
        )
    return "".join(cards)


def _card_list(cards: list[MemoryCard], *, with_review: bool, today: date) -> str:
    if not cards:
        return '<div class="empty">还没有内容。下一步先沉淀一条材料或创建一张卡。</div>'
    items = []
    for card in reversed(cards):
        review_form = ""
        if with_review:
            review_form = f"""
            <form method="post" action="/reviews" style="margin-top:8px;">
              <input type="hidden" name="card_id" value="{card.id}">
              <input type="hidden" name="reviewed_on" value="{escape(today.isoformat())}">
              <div class="grade-row" aria-label="复习评分">
                {_review_grade_buttons()}
              </div>
            </form>
            """
        items.append(
            f"""<div class="item">
  <div class="item-title"><span>#{card.id} {escape(card.title)}</span><span>{escape(card.card_type.value)}</span></div>
  <div class="meta">fronts={escape(",".join(front.value for front in card.fronts) or "none")} | due={escape(card.next_due.isoformat() if card.next_due else "none")} | reviews={card.review_count}</div>
  <div class="meta">{escape(card.prompt[:140])}</div>
  {review_form}
</div>"""
        )
    return '<div class="list">' + "".join(items) + "</div>"


def _review_grade_buttons() -> str:
    labels = (
        (5, "很稳"),
        (4, "会"),
        (3, "勉强"),
        (2, "模糊"),
        (1, "不会"),
        (0, "空白"),
    )
    buttons = []
    for grade, label in labels:
        low = " low" if grade < 3 else ""
        buttons.append(
            f"""<button class="grade-button{low}" type="submit" name="grade" value="{grade}" title="{grade} {escape(label)}">
  <span>{grade}</span><small>{escape(label)}</small>
</button>"""
        )
    return "".join(buttons)


def _practice_list(sessions: list[PracticeSession]) -> str:
    if not sessions:
        return '<div class="empty">还没有练习记录。先记录一次选择、案例或论文练习。</div>'
    items = []
    for session in reversed(sessions):
        score = _score_text(session.score, session.max_score)
        ratio = _score_ratio_text(session.score, session.max_score)
        items.append(
            f"""<div class="item">
  <div class="item-title"><span>#{session.id} {escape(session.topic)}</span><span>{escape(_front_label(session.front))}</span></div>
  <div class="meta">score={escape(score)} | ratio={escape(ratio)} | source={escape(session.source or "none")} | duration={escape(str(session.duration_minutes or "none"))} | date={escape(session.created_on.isoformat() if session.created_on else "none")}</div>
  <div class="meta">{escape(session.summary[:140])}</div>
</div>"""
        )
    return '<div class="list">' + "".join(items) + "</div>"


def _risk_reason_list(reasons: tuple[str, ...]) -> str:
    items = [f'<div class="item">{escape(reason)}</div>' for reason in reasons]
    return '<div class="list">' + "".join(items) + "</div>"


def _score_text(score: float | None, max_score: float | None) -> str:
    if score is None:
        return "none"
    if max_score is None:
        return f"{score:g}"
    return f"{score:g}/{max_score:g}"


def _score_ratio_text(score: float | None, max_score: float | None) -> str:
    if score is None or max_score is None or max_score <= 0:
        return "none"
    return f"{score / max_score:.0%}"


def _front_label(front: ExamFront) -> str:
    return {
        ExamFront.CHOICE: "选择题",
        ExamFront.CASE: "案例题",
        ExamFront.ESSAY: "论文题",
    }[front]


def _diagnostic_list(diagnostics: list[MemoryDiagnostic]) -> str:
    if not diagnostics:
        return '<div class="empty">暂无薄弱诊断。先完成今日复习。</div>'
    items = []
    for diagnostic in diagnostics:
        items.append(
            f"""<div class="item">
  <div class="item-title"><span>#{diagnostic.card_id} {escape(diagnostic.title)}</span><span>{escape(diagnostic.status)}</span></div>
  <div class="meta">{escape(diagnostic.action)}</div>
  <div class="meta">low={diagnostic.low_grade_reviews} | last={escape(str(diagnostic.last_grade))} | avg={escape(str(diagnostic.average_grade))}</div>
</div>"""
        )
    return '<div class="list">' + "".join(items) + "</div>"
