from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path

from .dashboard import render_dashboard
from .domain import CardType
from .evolution import night_evolution_html_path
from .export_state import state_export_path
from .learning import ensure_learning_resources
from .loop import build_daily_loop_snapshot, status_line
from .memory import diagnose_memory
from .rag import (
    DEFAULT_RAG_QUERY,
    build_rag_brief,
    rag_brief_html_path,
    rag_brief_to_payload,
)
from .receipts import daily_receipt_html_path
from .route_map import route_map_html_path
from .storage import RuankaoStore
from .vault import (
    initialize_vault,
    write_principle_note,
)
from .web_actions import (
    WorkbenchActionContext,
    add_memory_card as add_memory_card_action,
    add_practice_session as add_practice_session_action,
    add_principle_relation as add_principle_relation_action,
    add_raw_record as add_raw_record_action,
    capture_study_turn as capture_study_turn_action,
    record_review as record_review_action,
    seed_cheko_cards as seed_cheko_cards_action,
    sync_memory_cards_to_vault_action,
    sync_raw_records_to_vault_action,
    write_daily_receipt_action,
    write_night_evolution_plan_action,
    write_rag_brief_action,
    write_route_map_action,
    write_state_export_action,
)
from .web_forms import (
    FormData,
)
from .web_render import (
    _card_list,
    _diagnostic_list,
    _front_cards,
    _front_checks,
    _front_overview,
    _message,
    _practice_list,
    _promotion_status_radios,
    _rag_panel,
    _relation_radios,
    _risk_label,
    _risk_reason_list,
    _status_summary,
    _today_primary_action,
    _today_primary_reason,
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

    def _action_context(self) -> WorkbenchActionContext:
        return WorkbenchActionContext(
            root=self.root,
            vault_path=self.vault_path,
            today=self.today,
            store=self.store,
            write_dashboard=self.write_dashboard,
        )

    def add_raw_record(self, form: FormData) -> int:
        return add_raw_record_action(self._action_context(), form)

    def add_memory_card(self, form: FormData) -> int:
        return add_memory_card_action(self._action_context(), form)

    def add_principle_relation(self, form: FormData) -> int:
        return add_principle_relation_action(self._action_context(), form)

    def add_practice_session(self, form: FormData) -> int:
        return add_practice_session_action(self._action_context(), form)

    def capture_study_turn(self, form: FormData):
        return capture_study_turn_action(self._action_context(), form)

    def record_review(self, form: FormData) -> None:
        return record_review_action(self._action_context(), form)

    def seed_cheko_cards(self, form: FormData):
        return seed_cheko_cards_action(self._action_context(), form)

    def write_daily_receipt(self, form: FormData):
        return write_daily_receipt_action(self._action_context(), form)

    def write_night_evolution_plan(self, form: FormData):
        return write_night_evolution_plan_action(self._action_context(), form)

    def write_route_map(self, form: FormData):
        return write_route_map_action(self._action_context(), form)

    def write_rag_brief(self, form: FormData):
        return write_rag_brief_action(self._action_context(), form)

    def write_state_export(self, form: FormData):
        return write_state_export_action(self._action_context(), form)

    def sync_memory_cards_to_vault(self, form: FormData):
        return sync_memory_cards_to_vault_action(self._action_context(), form)

    def sync_raw_records_to_vault(self, form: FormData):
        return sync_raw_records_to_vault_action(self._action_context(), form)

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
        rag_path = rag_brief_html_path(self.root, self.today)
        rag_link = (
            f'<a class="button secondary" href="/reports/rag/{escape(self.today.isoformat())}.html">打开 RAG 控制简报</a>'
            if rag_path.exists()
            else ""
        )
        export_path = state_export_path(self.root, self.today)
        export_link = (
            f'<a class="button secondary" href="/exports/state-{escape(self.today.isoformat())}.json">打开本地状态导出</a>'
            if export_path.exists()
            else ""
        )
        rag_brief = rag_brief_to_payload(
            build_rag_brief(store, query=DEFAULT_RAG_QUERY, as_of=self.today, limit=4)
        )
        primary_action = _today_primary_action(
            due_cards=due_cards,
            diagnostics=active_diagnostics,
            practice_sessions=practice_sessions,
        )
        primary_reason = _today_primary_reason(snapshot.risk_reasons, due_cards)
        front_overview = _front_overview(cards, due_cards, practice_sessions, self.today)
        page_title = f"软考达人工作台 · {snapshot.countdown} · {_risk_label(snapshot.risk_text)}"

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
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 2px 7px;
      font-size: 12px;
      font-weight: 750;
      white-space: nowrap;
      background: var(--band);
    }}
    .front-state.red {{
      color: #8a1f11;
      border-color: #f0b6ad;
      background: #fff1f0;
    }}
    .front-state.yellow {{
      color: #7a5600;
      border-color: #ead18a;
      background: #fff8db;
    }}
    .front-state.green {{
      color: #17623a;
      border-color: #a9d5b8;
      background: #eefaf1;
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
    .form-note {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--band);
      color: var(--muted);
      padding: 10px 12px;
      font-size: 13px;
      line-height: 1.45;
    }}
    .source-guide {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(118px, 1fr));
      gap: 6px;
      margin-top: 6px;
    }}
    .source-guide span {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--muted);
      padding: 7px 8px;
      font-size: 12px;
      line-height: 1.35;
    }}
    .source-guide strong {{
      color: var(--accent-ink);
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
    .meta-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 6px;
    }}
    .meta-row span {{
      border: 1px solid var(--line);
      border-radius: 999px;
      background: var(--band);
      color: var(--muted);
      padding: 4px 7px;
      font-size: 12px;
      line-height: 1.2;
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
    .operation-stack {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 10px;
      margin-top: 10px;
    }}
    .operation-form {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--band);
      padding: 10px;
      display: grid;
      gap: 8px;
    }}
    .operation-form button {{
      width: 100%;
    }}
    .operation-hint {{
      color: var(--muted);
      font-size: 12px;
      line-height: 1.4;
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
        <div class="status">{escape(_status_summary(snapshot))}</div>
      </div>
      <div class="metrics">
        <div class="metric"><span>目标日期</span><strong>{escape(snapshot.dashboard.campaign.exam_date.isoformat())}</strong></div>
        <div class="metric"><span>今日阶段</span><strong>{escape(snapshot.phase_name)}</strong></div>
        <div class="metric"><span>到期复习</span><strong>{len(due_cards)}</strong></div>
        <div class="metric"><span>记忆卡</span><strong>{len(cards)}</strong></div>
        <div class="metric"><span>原始材料</span><strong>{len(records)}</strong></div>
        <div class="metric"><span>风险</span><strong>{escape(_risk_label(snapshot.risk_text))}</strong></div>
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
      <a href="#rag">RAG 控制</a>
      <a href="#study-turn">学习回合</a>
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
            <div class="operation-stack" aria-label="今日产物生成">
              <form class="operation-form" method="post" action="/daily/receipt">
                <input type="hidden" name="as_of" value="{escape(self.today.isoformat())}">
                <button type="submit">生成日结回执</button>
                <div class="operation-hint">收束完成、缺口和明日最低动作。</div>
              </form>
              <form class="operation-form" method="post" action="/night/evolve">
                <input type="hidden" name="as_of" value="{escape(self.today.isoformat())}">
                <button type="submit">生成夜间进化草案</button>
                <div class="operation-hint">让系统在晚上整理卡片、风险和下一步。</div>
              </form>
              <form class="operation-form" method="post" action="/routes/map">
                <input type="hidden" name="as_of" value="{escape(self.today.isoformat())}">
                <button type="submit">生成三题型覆盖图</button>
                <div class="operation-hint">检查选择、案例、论文是否失衡。</div>
              </form>
              <form class="operation-form" method="post" action="/rag/brief">
                <input type="hidden" name="as_of" value="{escape(self.today.isoformat())}">
                <input type="hidden" name="query" value="{escape(DEFAULT_RAG_QUERY)}">
                <button type="submit">生成 RAG 控制简报</button>
                <div class="operation-hint">召回记忆证据，并指出进步闸门。</div>
              </form>
              <form class="operation-form" method="post" action="/state/export">
                <input type="hidden" name="as_of" value="{escape(self.today.isoformat())}">
                <button type="submit">导出本地状态 JSON</button>
                <div class="operation-hint">保存本地状态，方便迁移、审计和回滚。</div>
              </form>
            </div>
            <div class="footer-actions">{receipt_link}{evolution_link}{route_link}{rag_link}{export_link}</div>
          </div>
        </div>
      </section>

      <section id="rag">
        <h2>RAG 记忆控制</h2>
        {_rag_panel(rag_brief)}
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
            <div class="form-note">记录一次练习至少留下题型、得分或完成量、错因，以及下一步补救动作；这样三题型雷达和夜间进化才有材料可用。</div>
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
              <textarea name="summary" required placeholder="得分点、卡点、暴露出的知识边界"></textarea>
            </label>
            <label>错因 / 卡点
              <textarea name="mistakes" placeholder="错因、混淆项、下一次避免方式"></textarea>
            </label>
            <button type="submit">记录练习</button>
          </form>
          <div>
            <h3>最近练习</h3>
            {_practice_list(practice_sessions[-8:])}
          </div>
        </div>
      </section>

      <section id="study-turn">
        <h2>学习回合</h2>
        <form method="post" action="/study-turn">
          <div class="form-note">把一次苏格拉底式问答沉淀为一条 Mein 和一条 Du；外部证据仍走 Uns，原则链接交给夜间进化挖掘。</div>
          <label>主题
            <input name="topic" required placeholder="高可用场景 / ATAM / 缓存一致性">
          </label>
          <div class="grid">
            <label>我在哪
              <input name="learner_position" placeholder="知道概念名，但不会写可评分场景">
            </label>
            <label>你在哪
              <input name="codex_position" placeholder="ruankao-teach 追问者 / 案例教练">
            </label>
            <label>我们要去哪
              <input name="destination" placeholder="能写出刺激、响应和响应度量">
            </label>
          </div>
          <label>Mein：我的原话 / 我的答案
            <textarea name="user_text" required placeholder="先保留粗糙答案，不急着美化"></textarea>
          </label>
          <label>Du：Codex 的整理 / 纠偏 / 追问
            <textarea name="assistant_text" required placeholder="复述卡点、补结构，并只留下一个下一步追问"></textarea>
          </label>
          {_front_checks()}
          <button type="submit">记录学习回合</button>
        </form>
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
              <div class="source-guide" aria-label="三源边界">
                <span><strong>Mein：</strong>我的原话和卡点</span>
                <span><strong>Du：</strong>Codex 的整理和纠偏</span>
                <span><strong>Uns：</strong>外界资料和证据</span>
              </div>
            </div>
            <div class="field">
              <div class="field-label">状态</div>
              <div class="segmented flow" aria-label="三源状态">
                {_promotion_status_radios()}
              </div>
            </div>
          </div>
          <label>原文 / 灵感 / 对话摘录
            <textarea name="text" required placeholder="保留原话、文章摘录、对话片段或个人经验"></textarea>
          </label>
          <label>一句话摘要
            <textarea name="summary" required placeholder="一句话写清它为什么值得留下"></textarea>
          </label>
          <label>主题，每行一个
            <textarea name="topics" placeholder="质量属性&#10;架构评估"></textarea>
          </label>
          {_front_checks()}
          <button type="submit">沉淀到三源库</button>
        </form>
      </section>

      <section id="cards">
        <h2>记忆卡</h2>
        <div class="split">
          <form method="post" action="/cards">
            <div class="form-note">一张合格记忆卡要能触发回忆、能自评、能映射到选择/案例/论文；如果只是摘抄，先回三源库沉淀。</div>
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
              <textarea name="prompt" required placeholder="看到什么场景时要想起这张卡？"></textarea>
            </label>
            <label>答案 / 核心表述
              <textarea name="answer" required placeholder="可直接检索的答案、原则或表达"></textarea>
            </label>
            <label>关联原始材料 ID
              <input type="number" name="source_record_id" min="1" step="1" inputmode="numeric">
            </label>
            <label>冲突原则，每行一个。仅原则卡使用
              <textarea name="conflicts" placeholder="技术先行&#10;性能优先"></textarea>
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
            <div class="form-note">只连接有真实逻辑张力的原则：能说明支撑、制约、冲突或派生，才值得进入网络。</div>
            <div class="grid">
              <label>From 原则 ID
                <input type="number" name="from_card_id" min="1" step="1" inputmode="numeric" required>
              </label>
              <label>To 原则 ID
                <input type="number" name="to_card_id" min="1" step="1" inputmode="numeric" required>
              </label>
            </div>
            <div class="field">
              <div class="field-label">关系</div>
              <div class="segmented flow" aria-label="原则关系">
                {_relation_radios()}
              </div>
            </div>
            <label>为什么这样连接
              <textarea name="rationale" required placeholder="说明这两个原则如何支撑、制约、冲突或派生"></textarea>
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
