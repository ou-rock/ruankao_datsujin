from __future__ import annotations

from datetime import date
from html import escape
from typing import Any

from .domain import Campaign
from .learning_cheko_templates import (
    render_cheko_panel as _cheko_panel,
    render_cheko_sync,
    render_today,
    today_tasks,
)
from .learning_content import (
    DEFAULT_CHEKO_SNAPSHOT,
    FIRST_WEEK_PLAN,
    LEARNING_COLUMNS,
    NOTEBOOKLM_SOURCE,
    REFERENCE_PAGES,
    ChekoSnapshot,
    DailyLearningPlan,
    ReferencePage,
)
from .learning_layout import (
    render_cards as _cards,
    render_front_labels as _front_labels,
    render_learning_page as _page,
)


def render_learning_index(
    cheko_snapshot: ChekoSnapshot = DEFAULT_CHEKO_SNAPSHOT,
    *,
    as_of: date | None = None,
) -> str:
    campaign_day = as_of or date.today()
    return _page(
        title="软考达人学习台",
        body=f"""
<header class="hero">
  <p class="eyebrow">学习台</p>
  <h1>软考达人学习台</h1>
  <p class="lead">学习台负责“学什么、怎么练、沉淀成什么”。工作台负责记录和复习，学习台负责把资料变成当天可执行的课。</p>
  <div class="actions">
    <a class="button" href="/learning/today.html">今日三任务</a>
    <a class="button" href="/learning/lessons/0001-scene-before-solution.html">开始第一课</a>
    <a class="button secondary" href="/learning/reference/quality-attributes-tactics.html">打开速查表</a>
    <a class="button secondary" href="/">回工作台</a>
  </div>
</header>
{_campaign_rail(campaign_day)}
{_cheko_panel(cheko_snapshot)}
<section>
  <h2>四个栏目</h2>
  <div class="grid">
    {_cards((column.title, column.body) for column in LEARNING_COLUMNS)}
  </div>
</section>
<section>
  <h2>第一周学习路径</h2>
  <div class="timeline">
    {"".join(_day_card(day) for day in FIRST_WEEK_PLAN)}
  </div>
</section>
<section>
  <h2>速查资源</h2>
  <div class="grid">
    {"".join(_reference_card(page) for page in REFERENCE_PAGES)}
  </div>
</section>
<section>
  <h2>NotebookLM 外部研究员</h2>
  <div class="panel">
    <p>第一批学习台资料由 NotebookLM notebook “{escape(NOTEBOOKLM_SOURCE)}” 生成研究种子，再由本地 agent 改写为可维护 HTML。NotebookLM 负责外部证据和资料归纳，本地学习台负责执行、复习和沉淀。</p>
    <p><a href="/learning/notebooklm-seed.html">查看生成记录</a></p>
  </div>
</section>
""",
    )


def render_scene_before_solution_lesson() -> str:
    return _page(
        title="第一课：场景先于方案",
        body=f"""
<header class="hero">
  <p class="eyebrow">第一课</p>
  <h1>场景先于方案</h1>
  <p class="lead">架构设计不是先报技术名词，而是先把业务目标、边界、约束和质量属性场景说清楚。</p>
  <div class="actions">
    <a class="button" href="/learning/">回学习台</a>
    <a class="button secondary" href="/learning/reference/quality-scenario-utility-tree.html">质量场景速查</a>
  </div>
</header>
<section>
  <h2>导入</h2>
  <p>遇到高并发就说 Redis，遇到复杂系统就说微服务，这不是架构师思维。架构师先问：谁在什么环境下触发了什么刺激，影响哪个制品，系统应该如何响应，用什么指标验收。</p>
</section>
<section>
  <h2>核心原则</h2>
  <div class="panel strong">没有场景约束，方案只是技术清单；有了可度量场景，方案才有取舍依据。</div>
  <ol>
    <li>先写业务目标：系统为什么要建，服务谁，保护什么价值。</li>
    <li>再写质量属性：性能、可用性、安全性、可修改性等哪个是主要矛盾。</li>
    <li>再写度量：响应时间、恢复时间、吞吐量、变更成本、审计覆盖等。</li>
    <li>最后选战术：缓存、冗余、心跳、追踪审计、信息隐藏、抽象接口等。</li>
  </ol>
</section>
<section>
  <h2>选择题易错点</h2>
  <div class="grid">
    <div class="panel"><h3>可用性</h3><p>看到宕机、备用、切换、恢复时间，优先想到可用性和冗余类战术。</p></div>
    <div class="panel"><h3>性能</h3><p>看到响应时间、吞吐量、并发用户、负载，优先想到性能和资源调度。</p></div>
    <div class="panel"><h3>安全性</h3><p>看到授权、攻击、审计、报警、记录，优先想到安全性和追踪审计。</p></div>
    <div class="panel"><h3>可修改性</h3><p>看到新增接口、更换界面、扩展模块、规定工期，优先想到可修改性。</p></div>
  </div>
</section>
<section>
  <h2>案例题答题框架</h2>
  <ol>
    <li>圈出题干原句，标注质量属性触发词。</li>
    <li>拆六要素：刺激源、刺激、环境、制品、响应、响应度量。</li>
    <li>把需求放进效用树：质量属性 -> 细分属性 -> 场景 -> 优先级。</li>
    <li>说明战术选择：为什么它回应了度量，而不是只写技术名词。</li>
  </ol>
</section>
<section>
  <h2>论文题表达模板</h2>
  <div class="panel">
    <p>在本项目中，我没有直接从技术框架出发，而是先识别核心业务场景与质量约束。针对“【场景】”，系统在“【环境】”下必须满足“【响应度量】”。因此，我将“【质量属性】”作为架构设计的优先目标，并采用“【战术/方案】”实现该目标，同时通过“【监控/验证方式】”评估实际效果。</p>
  </div>
</section>
<section>
  <h2>课后卡片</h2>
  <div class="grid">
    {_cards((
      ("原则卡", "场景先于方案：先确认业务目标、边界和质量约束，再谈技术方案。"),
      ("概念卡", "质量属性场景六要素：刺激源、刺激、环境、制品、响应、响应度量。"),
      ("场景卡", "主站宕机后 20 秒内切换备用站点，属于可用性场景。"),
      ("表达卡", "本项目先识别质量约束，再选择架构战术，并用量化指标验证效果。"),
    ))}
  </div>
</section>
""",
    )


def render_reference_page(page: ReferencePage) -> str:
    fronts = _front_labels(page.fronts)
    return _page(
        title=page.title,
        body=f"""
<header class="hero">
  <p class="eyebrow">速查</p>
  <h1>{escape(page.title)}</h1>
  <p class="lead">{escape(page.purpose)}</p>
  <div class="actions">
    <a class="button" href="/learning/">回学习台</a>
    <a class="button secondary" href="/learning/lessons/0001-scene-before-solution.html">第一课</a>
  </div>
</header>
<section>
  <h2>核心提纲</h2>
  <ol>
    {"".join(f"<li>{escape(item)}</li>" for item in page.outline)}
  </ol>
</section>
<section>
  <h2>适用题型</h2>
  <div class="chips">{"".join(f'<span>{escape(front)}</span>' for front in fronts)}</div>
</section>
<section>
  <h2>训练动作</h2>
  <div class="panel strong">{escape(page.drill)}</div>
</section>
<section>
  <h2>应沉淀卡片</h2>
  <div class="grid">
    {_cards((card.split("：", 1)[0], card) for card in page.cards)}
  </div>
</section>
""",
    )


def render_notebooklm_seed() -> str:
    return _page(
        title="NotebookLM 资源生成记录",
        body=f"""
<header class="hero">
  <p class="eyebrow">Uns 外部资料</p>
  <h1>NotebookLM 资源生成记录</h1>
  <p class="lead">NotebookLM 是外部研究员，不是最终学习系统。它给出资料线索和结构，最终由本地学习台改写、执行、复习和沉淀。</p>
</header>
<section>
  <h2>本次生成</h2>
  <div class="panel">
    <p>来源 notebook：{escape(NOTEBOOKLM_SOURCE)}</p>
    <p>生成内容：学习台四栏结构、第一周路径、速查页清单、第一课《场景先于方案》、风险与坑。</p>
    <p>落地文件：学习台首页、第一课、8 份速查参考页。</p>
  </div>
</section>
<section>
  <h2>后续规则</h2>
  <ol>
    <li>外部资料必须进入 Uns。</li>
    <li>学习页面必须转化为卡片、错因或原则，才算进入系统。</li>
    <li>NotebookLM 产物只能作为候选，不能替代本地复习数据。</li>
    <li>每周夜间进化时，可以让 NotebookLM 根据本周错因补一批新资源。</li>
  </ol>
</section>
""",
    )


def _campaign_rail(as_of: date) -> str:
    campaign = Campaign.default()
    phase = campaign.phase_for(as_of)
    elapsed_days = max(0, (as_of - campaign.start_date).days)
    days_remaining = campaign.days_remaining(as_of)
    next_phase = _next_phase(campaign, phase)
    next_name = next_phase.name if next_phase is not None else "考后复盘"
    next_window = _phase_window(next_phase) if next_phase is not None else "考试后继续沉淀架构能力"
    return f"""<section>
  <h2>战役导航</h2>
  <div class="route-strip">
    <div class="route-step">
      <span>当前位置</span>
      <strong>{escape(phase.name)}</strong>
      <p>第 {elapsed_days} 天；D-{days_remaining}</p>
    </div>
    <div class="route-step">
      <span>下一站</span>
      <strong>{escape(next_name)}</strong>
      <p>{escape(next_window)}</p>
    </div>
    <div class="route-step">
      <span>终点</span>
      <strong>{escape(campaign.exam_date.isoformat())}</strong>
      <p>系统架构设计师考试，然后继续进化架构能力。</p>
    </div>
  </div>
</section>"""


def _next_phase(campaign: Campaign, phase: Any) -> Any | None:
    for index, candidate in enumerate(campaign.phases):
        if candidate.key == phase.key:
            next_index = index + 1
            if next_index < len(campaign.phases):
                return campaign.phases[next_index]
            return None
    return None


def _phase_window(phase: Any) -> str:
    end_day = int(phase.end_day)
    if end_day >= 9999:
        return f"第 {phase.start_day} 天后"
    return f"第 {phase.start_day}-{phase.end_day} 天"


def _day_card(day: DailyLearningPlan) -> str:
    return f"""<div class="day">
  <div class="day-index">第 {day.day} 天</div>
  <div>
    <h3>{escape(day.title)}</h3>
    <p><strong>目标：</strong>{escape(day.goal)}</p>
    <p class="meta">选择：{escape(day.choice)}</p>
    <p class="meta">案例：{escape(day.case)}</p>
    <p class="meta">论文：{escape(day.essay)}</p>
    <p class="meta">沉淀：{escape(day.card)}</p>
  </div>
</div>"""


def _reference_card(page: ReferencePage) -> str:
    fronts = " / ".join(_front_labels(page.fronts))
    return f"""<div class="panel">
  <h3><a href="/learning/reference/{escape(page.filename)}">{escape(page.title)}</a></h3>
  <p>{escape(page.purpose)}</p>
  <p class="meta">{escape(fronts)}</p>
</div>"""
