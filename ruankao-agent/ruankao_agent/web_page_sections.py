from __future__ import annotations

from html import escape

from .web_page_forms import (
    render_capture_section,
    render_cards_section,
    render_cheko_section,
    render_practice_section,
    render_principles_section,
    render_study_turn_section,
    render_vault_section,
)
from .web_page_operations import render_today_operations
from .web_page_style import WORKBENCH_HOME_STYLE
from .web_page_view import HomePageView
from .web_fronts import _front_cards
from .web_lists import (
    _card_list,
    _diagnostic_list,
    _risk_reason_list,
)
from .web_labels import _risk_label
from .web_rag_panel import _rag_panel
from .web_status import (
    _message,
    _status_summary,
)


def render_home_shell(view: HomePageView) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(view.page_title)}</title>
  <style>
{WORKBENCH_HOME_STYLE}
  </style>
</head>
<body>
  <a class="skip-link" href="#today">跳到今日闭环</a>
  <header>
<div class="top">
  <div class="title-row">
    <h1>软考达人工作台</h1>
    <div class="status">{escape(_status_summary(view.snapshot))}</div>
  </div>
  <div class="metrics">
    <div class="metric"><span>目标日期</span><strong>{escape(view.snapshot.dashboard.campaign.exam_date.isoformat())}</strong></div>
    <div class="metric"><span>今日阶段</span><strong>{escape(view.snapshot.phase_name)}</strong></div>
    <div class="metric"><span>到期复习</span><strong>{len(view.due_cards)}</strong></div>
    <div class="metric"><span>记忆卡</span><strong>{len(view.cards)}</strong></div>
    <div class="metric"><span>原始材料</span><strong>{len(view.records)}</strong></div>
    <div class="metric"><span>风险</span><strong>{escape(_risk_label(view.snapshot.risk_text))}</strong></div>
  </div>
  <div class="action-strip risk-{escape(view.snapshot.risk_text)}">
    <div>
      <div class="action-kicker">今日第一动作</div>
      <div class="action-title">{escape(view.primary_action)}</div>
      <div class="action-reason">{escape(view.primary_reason)}</div>
    </div>
    <div class="action-buttons">
      <a class="button" href="#today">处理今日闭环</a>
      <a class="button secondary" href="#practice">记录练习</a>
      <a class="button secondary" href="/learning/today.html">今日三任务</a>
    </div>
  </div>
  <div class="front-strip" aria-label="三题型雷达">
    {_front_cards(view.front_overview)}
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
  {_message(view.message)}
  <section id="today">
    <h2>今日闭环</h2>
    <div class="split">
      <div>
        <h3>到期卡片</h3>
        {_card_list(view.due_cards, with_review=True, today=view.today)}
      </div>
      <div>
        <h3>最小行动</h3>
        <div class="list">
          <div class="item">复习所有到期卡片，低于 3 分立刻明天再见。</div>
          <div class="item">选择题保持概念密度，案例题保持论证手感，论文题保持素材活性。</div>
          <div class="item">每次学习至少沉淀一条 Mein / Du / Uns。</div>
        </div>
        <h3 style="margin-top:14px;">风险原因</h3>
        {_risk_reason_list(view.snapshot.risk_reasons)}
        <h3 style="margin-top:14px;">记忆诊断</h3>
        {_diagnostic_list(view.active_diagnostics)}
        {render_today_operations(view)}
      </div>
    </div>
  </section>

  <section id="rag">
    <h2>RAG 记忆控制</h2>
    {_rag_panel(view.rag_brief)}
  </section>

  {render_cheko_section(view)}
  {render_practice_section(view)}
  {render_study_turn_section(view)}
  {render_capture_section()}
  {render_cards_section(view)}
  {render_principles_section(view)}
  {render_vault_section(view)}
</div>
  </main>
</body>
</html>
"""
