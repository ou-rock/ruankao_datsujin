from __future__ import annotations

from html import escape

from .learning_content import (
    DEFAULT_CHEKO_SNAPSHOT,
    ChekoSnapshot,
    ChekoWeakArea,
    TodayTask,
)
from .learning_layout import render_cards, render_learning_page


def render_cheko_sync(snapshot: ChekoSnapshot = DEFAULT_CHEKO_SNAPSHOT) -> str:
    return render_learning_page(
        title="芝士架构同步信号",
        body=f"""
<header class="hero">
  <p class="eyebrow">芝士同步</p>
  <h1>芝士架构同步信号</h1>
  <p class="lead">这页只保存学习信号，不保存账号、头像、邮箱或任何登录凭据。它把芝士架构里的练习状态翻译成学习台的下一步行动。</p>
  <div class="actions">
    <a class="button" href="/learning/today.html">今日三任务</a>
    <a class="button" href="/learning/">回学习台</a>
    <a class="button secondary" href="https://www.cheko.cc/statistic">打开芝士架构统计</a>
  </div>
</header>
{render_cheko_panel(snapshot)}
<section>
  <h2>同步规则</h2>
  <ol>
    <li>正确率低于 75% 时，今日学习优先错因回炉，而不是继续开新知识。</li>
    <li>估分低于 45 时，选择题要保护基本盘，同时每周必须触达案例和论文。</li>
    <li>错题池大于 50 的知识点，必须拆成概念卡、对比卡、场景卡三类复习。</li>
    <li>论文真题 0 / 4 时，不能只看范文，必须开始写摘要、背景段和回应子题目的技术段。</li>
    <li>芝士架构论文助手会消耗算力，自动提交前必须单独确认。</li>
  </ol>
</section>
<section>
  <h2>课程映射</h2>
  <div class="grid">
    {render_cards((course.title, f"{course.role}；{course.lessons} 节；{course.duration}") for course in snapshot.courses)}
  </div>
</section>
<section>
  <h2>练习日志</h2>
  <div class="grid">
    {render_cards((log.topic, f"{log.created_at}；{log.state}") for log in snapshot.practice_logs)}
  </div>
</section>
""",
    )


def render_today(snapshot: ChekoSnapshot = DEFAULT_CHEKO_SNAPSHOT) -> str:
    tasks = today_tasks(snapshot)
    total_minutes = sum(task.minutes for task in tasks)
    return render_learning_page(
        title="今日三任务",
        body=f"""
<header class="hero">
  <p class="eyebrow">今日</p>
  <h1>今日三任务</h1>
  <p class="lead">今天不追求打开所有资料。先把最大弱点、一个题型触达、一个记忆沉淀做完，让系统向前滚一格。</p>
  <div class="actions">
    <a class="button" href="/learning/">回学习台</a>
    <a class="button secondary" href="/learning/cheko-sync.html">查看同步信号</a>
  </div>
</header>
<section>
  <h2>今天的边界</h2>
  <div class="metric-grid">
    <div class="metric"><span>正确率</span><strong>{snapshot.accuracy:.1f}%</strong></div>
    <div class="metric"><span>预估分</span><strong>{snapshot.estimated_score:.2f}</strong></div>
    <div class="metric"><span>最大错题池</span><strong>{escape(snapshot.weak_areas[0].title)}</strong></div>
    <div class="metric"><span>论文助手算力</span><strong>{snapshot.essay_power_remaining} / {snapshot.essay_power_total}</strong></div>
    <div class="metric"><span>时间盒</span><strong>{total_minutes} 分钟</strong></div>
  </div>
</section>
<section>
  <h2>只做这三件事</h2>
  <div class="timeline">
    {"".join(_today_task_card(index, task) for index, task in enumerate(tasks, start=1))}
  </div>
</section>
<section>
  <h2>停止条件</h2>
  <ol>
    <li>三件事全部完成或 {total_minutes} 分钟用完后，不继续加码，转到工作台记录复习结果。</li>
    <li>任一任务卡住超过 20 分钟，把卡住点记录到 Mein，不硬扛。</li>
    <li>如果今天只能做一件事，只做第 1 件：最大错题池回炉。</li>
  </ol>
  <div class="actions">
    <a class="button" href="/#study-turn">记录学习回合</a>
    <a class="button secondary" href="/#cards">创建记忆卡</a>
    <a class="button secondary" href="/#practice">记录练习</a>
  </div>
</section>
""",
    )


def today_tasks(snapshot: ChekoSnapshot = DEFAULT_CHEKO_SNAPSHOT) -> tuple[TodayTask, ...]:
    primary = snapshot.weak_areas[0]
    secondary = snapshot.weak_areas[1]
    essay_needed = "0 / 4" in snapshot.essay_past_exam_score
    essay_action = (
        "写 300 字以内摘要 + 1 段项目背景，不调用论文助手。"
        if essay_needed
        else "复盘最近一篇论文生成记录，抽取 1 张表达卡。"
    )
    return (
        TodayTask(
            title=f"{primary.title}错题回炉",
            minutes=25,
            why=f"{primary.title} 是当前最大错题池，{primary.total} 题已经足够暴露结构性薄弱点。",
            action=primary.next_action,
            done_when="至少完成 10 道错题复盘，按不会/混淆/审题/表达归因。",
            output="2 张概念卡 + 1 张错因卡。",
        ),
        TodayTask(
            title=f"{secondary.title}对比卡",
            minutes=15,
            why=f"{secondary.title} 错题池为 {secondary.total}，适合用对比卡降低混淆成本。",
            action=secondary.next_action,
            done_when="挑 3 个最容易混淆的概念，各写一句边界。",
            output="1 张对比卡 + 1 条 Du 分析。",
        ),
        TodayTask(
            title="论文最低触达",
            minutes=20,
            why=snapshot.essay_past_exam_score,
            action=essay_action,
            done_when="必须产生可复用文字，不以“看了范文”作为完成。",
            output="1 张表达卡，主题为项目背景或回应子题目。",
        ),
    )


def render_cheko_panel(snapshot: ChekoSnapshot) -> str:
    top_areas = snapshot.weak_areas[:5]
    return f"""
<section>
  <h2>芝士架构同步信号</h2>
  <div class="metric-grid">
    <div class="metric"><span>总答题</span><strong>{snapshot.answered}</strong></div>
    <div class="metric"><span>错题数</span><strong>{snapshot.wrong}</strong></div>
    <div class="metric"><span>正确率</span><strong>{snapshot.accuracy:.1f}%</strong></div>
    <div class="metric"><span>预估分</span><strong>{snapshot.estimated_score:.2f}</strong></div>
    <div class="metric"><span>排名</span><strong>{snapshot.rank} / {snapshot.rank_total}</strong></div>
    <div class="metric"><span>超过学习者</span><strong>{snapshot.percentile:.1f}%</strong></div>
  </div>
  <div class="panel" style="margin-top:10px;">
    <p><strong>学习者视角诊断：</strong>当前不是缺资料，而是错题池已经足够大，需要先把系统架构设计、软件工程、系统分析与设计变成复习卡和题型训练。</p>
    <p><strong>论文信号：</strong>{escape(snapshot.essay_past_exam_score)}；论文助手算力 {snapshot.essay_power_remaining} / {snapshot.essay_power_total}。</p>
    <p><a href="/learning/cheko-sync.html">查看完整同步规则</a></p>
  </div>
  <div class="timeline" style="margin-top:10px;">
    {"".join(_weak_area_row(area) for area in top_areas)}
  </div>
</section>
"""


def _weak_area_row(area: ChekoWeakArea) -> str:
    return f"""<div class="day">
  <div class="day-index">{area.total} 题</div>
  <div>
    <h3>{escape(area.title)}</h3>
    <p><strong>{escape(area.tier)}</strong>；刷题进度 {area.done} / {area.total}</p>
    <p class="meta">{escape(area.next_action)}</p>
  </div>
</div>"""


def _today_task_card(index: int, task: TodayTask) -> str:
    return f"""<div class="day">
  <div class="day-index">第 {index} 件</div>
  <div>
    <h3>{escape(task.title)}</h3>
    <p><strong>为什么：</strong>{escape(task.why)}</p>
    <p class="meta">建议时长：{task.minutes} 分钟</p>
    <p class="meta">动作：{escape(task.action)}</p>
    <p class="meta">完成标准：{escape(task.done_when)}</p>
    <p class="meta">产出：{escape(task.output)}</p>
  </div>
</div>"""
