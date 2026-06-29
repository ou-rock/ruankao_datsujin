from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from html import escape
from pathlib import Path
from typing import Any, Iterable


NOTEBOOKLM_SOURCE = "System Architecture Designer Exam Questions and Analysis"


@dataclass(frozen=True, slots=True)
class LearningColumn:
    title: str
    body: str


@dataclass(frozen=True, slots=True)
class DailyLearningPlan:
    day: int
    title: str
    goal: str
    choice: str
    case: str
    essay: str
    card: str


@dataclass(frozen=True, slots=True)
class ReferencePage:
    filename: str
    title: str
    purpose: str
    outline: tuple[str, ...]
    fronts: tuple[str, ...]
    drill: str
    cards: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ChekoWeakArea:
    title: str
    done: int
    total: int
    tier: str
    next_action: str


@dataclass(frozen=True, slots=True)
class ChekoPracticeLog:
    topic: str
    created_at: str
    state: str


@dataclass(frozen=True, slots=True)
class ChekoCourse:
    title: str
    lessons: int
    duration: str
    role: str


@dataclass(frozen=True, slots=True)
class TodayTask:
    title: str
    why: str
    action: str
    done_when: str
    output: str


@dataclass(frozen=True, slots=True)
class ChekoSnapshot:
    captured_on: str
    source: str
    answered: int
    wrong: int
    accuracy: float
    estimated_score: float
    rank: int
    rank_total: int
    percentile: float
    essay_power_remaining: int
    essay_power_total: int
    essay_past_exam_score: str
    collections_state: str
    practice_logs: tuple[ChekoPracticeLog, ...]
    weak_areas: tuple[ChekoWeakArea, ...]
    courses: tuple[ChekoCourse, ...]


LEARNING_COLUMNS = (
    LearningColumn("今日学习", "把今天要学、要练、要沉淀的动作压成一个闭环。"),
    LearningColumn("第一周路径", "先打软件架构设计与评估的基本盘，选择、案例、论文同时铺路。"),
    LearningColumn("速查资源", "把高频考点做成可打印、可复盘、可回炉的 HTML 参考页。"),
    LearningColumn("课后沉淀", "每节课必须沉淀记忆卡、原则卡或表达卡，进入工作台复习。"),
)


FIRST_WEEK_PLAN = (
    DailyLearningPlan(
        1,
        "核心破冰",
        "建立质量属性与架构战术的第一层地图。",
        "区分性能、可用性、安全性、可修改性的触发词。",
        "把题干需求先归类为质量属性，再谈方案。",
        "准备一个真实项目背景，不写技术清单，先写业务意义。",
        "概念卡：四大质量属性；原则卡：场景先于方案。",
    ),
    DailyLearningPlan(
        2,
        "场景拆解",
        "掌握质量属性场景六要素。",
        "看到刺激、环境、响应、度量时能定位组成部分。",
        "把业务句子拆成刺激源、刺激、环境、制品、响应、响应度量。",
        "练习把项目中的非功能需求写成可度量场景。",
        "场景卡：双十一支付高可用；对比卡：响应 vs 响应度量。",
    ),
    DailyLearningPlan(
        3,
        "风格辨析",
        "形成架构风格的分类、优缺点和适用场景。",
        "区分管道过滤器、分层、仓库、黑板、事件驱动、C/S。",
        "按题干业务选择风格，并说明优缺点。",
        "为论文准备一段“为何选择该架构风格”的表达。",
        "对比卡：仓库风格 vs 黑板风格；表达卡：架构风格选择句式。",
    ),
    DailyLearningPlan(
        4,
        "评估方法",
        "理解 ATAM/SAAM 的过程、产物和关键词。",
        "识别风险点、非风险点、敏感点、权衡点。",
        "用效用树组织质量属性、场景、优先级。",
        "把论文中的方案取舍写成权衡，而不是堆技术。",
        "概念卡：效用树；对比卡：敏感点 vs 权衡点。",
    ),
    DailyLearningPlan(
        5,
        "案例实战",
        "完成一轮质量属性效用树真题型训练。",
        "用触发词快速选择质量属性。",
        "按题干原句回填效用树，不脱离上下文。",
        "把同一题里的场景改写成论文论据。",
        "错因卡：误判属性；场景卡：安全审计与报警。",
    ),
    DailyLearningPlan(
        6,
        "论文寻根",
        "打磨项目背景、摘要和技术方法说明。",
        "复盘架构评估相关选择题错因。",
        "从案例题中抽取可复用的项目约束。",
        "写 300 字以内摘要和 500 字技术方法说明。",
        "表达卡：项目背景；表达卡：回应子题目。",
    ),
    DailyLearningPlan(
        7,
        "综合复盘",
        "清空第一周错题和到期卡片，生成下周补强清单。",
        "回炉全部混淆概念。",
        "复做一题效用树或架构风格案例。",
        "补一段论文结尾：效果、复盘、不足、改进。",
        "原则卡：先分类再求解；错因卡：本周最大失误。",
    ),
)


REFERENCE_PAGES = (
    ReferencePage(
        "quality-attributes-tactics.html",
        "四大质量属性与架构战术映射表",
        "把性能、可用性、安全性、可修改性的题干信号映射到常见战术。",
        (
            "性能：响应时间、吞吐量、负载、延迟、资源调度。",
            "可用性：故障、宕机、备用、重定向、恢复时间、主动冗余。",
            "安全性：授权、审计、攻击检测、报警、追踪。",
            "可修改性：变更、扩展、替换、接口稳定、信息隐藏。",
        ),
        ("选择题", "案例题", "论文题"),
        "任选 8 条需求句，先标属性，再给战术，不许直接写方案。",
        ("概念卡：四大质量属性", "对比卡：可用性 vs 可靠性", "场景卡：故障切换"),
    ),
    ReferencePage(
        "architecture-styles.html",
        "软件架构风格对比速查",
        "用“结构、优点、代价、适用场景”四格法记住常见架构风格。",
        (
            "数据流：批处理、管道过滤器，适合阶段化处理。",
            "调用返回：主程序子程序、面向对象、分层、C/S。",
            "以数据为中心：仓库、黑板，适合共享数据和状态汇聚。",
            "独立构件：进程通信、事件驱动，适合松耦合和异步扩展。",
        ),
        ("选择题", "案例题"),
        "把一个在线学习系统分别改写成分层、事件驱动、仓库风格，并比较取舍。",
        ("对比卡：分层 vs C/S", "对比卡：仓库 vs 黑板", "表达卡：风格选择理由"),
    ),
    ReferencePage(
        "quality-scenario-utility-tree.html",
        "质量属性场景六要素与效用树",
        "把模糊的非功能需求翻译为可评价、可得分、可落地的架构场景。",
        (
            "六要素：刺激源、刺激、环境、制品、响应、响应度量。",
            "效用树：质量属性 -> 细分属性 -> 场景 -> 优先级。",
            "答题顺序：先找题干原句，再判断属性，再补度量。",
            "常见坑：把响应和响应度量混写，把方案当成需求。",
        ),
        ("案例题", "论文题"),
        "将“系统要能抵挡恶意入侵并报警”拆成完整六要素。",
        ("场景卡：安全报警", "概念卡：响应度量", "错因卡：方案先行"),
    ),
    ReferencePage(
        "atam-saam.html",
        "架构评估 ATAM/SAAM 输出物清单",
        "把架构评估从名词背诵变成案例题可写的过程和产物。",
        (
            "ATAM 关注多质量属性权衡，输出风险点、非风险点、敏感点、权衡点。",
            "SAAM 更强调场景驱动的可修改性分析。",
            "效用树是质量属性优先级排序工具。",
            "案例答题要落到“为什么这是风险/权衡”，不要只写名词。",
        ),
        ("选择题", "案例题"),
        "给一个架构方案，标出 2 个敏感点和 1 个权衡点。",
        ("概念卡：敏感点", "概念卡：权衡点", "对比卡：ATAM vs SAAM"),
    ),
    ReferencePage(
        "uml-and-data-modeling.html",
        "UML 与数据建模填空指南",
        "把案例题中的图形填空训练成“按关系和上下文推理”。",
        (
            "类图看类、属性、操作、关联、聚合、组合、泛化。",
            "顺序图看参与者、生命线、消息顺序和返回。",
            "状态图看状态、事件、迁移、条件和动作。",
            "DFD/ERD 要守数据平衡和实体关系一致性。",
        ),
        ("案例题",),
        "拿一题 DFD 或 ERD，只看上下文先猜实体和数据流，再对照答案。",
        ("概念卡：数据平衡", "概念卡：组合关系", "错因卡：图形填空"),
    ),
    ReferencePage(
        "database-high-availability.html",
        "数据库高并发与高可用方案锦囊",
        "把数据库、缓存、分库分表、读写分离放进架构取舍语境。",
        (
            "读多写少：缓存、读写分离、热点数据保护。",
            "写入压力：分库分表、异步削峰、幂等与补偿。",
            "高可用：主备切换、复制、故障检测、恢复目标。",
            "一致性：强一致、最终一致、事务边界和业务补偿。",
        ),
        ("选择题", "案例题", "论文题"),
        "为一个订单系统写出读扩展、写削峰、高可用、数据一致性四段方案。",
        ("场景卡：订单高并发", "对比卡：读写分离 vs 分库分表", "表达卡：一致性取舍"),
    ),
    ReferencePage(
        "essay-background-template.html",
        "论文防翻车：项目背景与摘要模板",
        "把论文从模板腔拉回业务场景、约束、架构决策和效果。",
        (
            "背景：从组织目标、业务痛点、投入价值写起。",
            "摘要：300 字以内，覆盖项目、职责、方法、效果。",
            "正文：回应子题目，技术方法必须服务于论题。",
            "结尾：效果、复盘、不足和后续改进。",
        ),
        ("论文题",),
        "用自己的真实项目写 1 个摘要、1 个背景段、1 个回应子题目的技术段。",
        ("表达卡：300 字摘要", "表达卡：项目背景", "表达卡：回应子题目"),
    ),
    ReferencePage(
        "pitfalls.html",
        "选择、案例、论文与学习系统常见坑",
        "把会让人挂科的坑提前摆上桌面。",
        (
            "选择题：概念相似但边界不同，例如不同版本 4+1 视图。",
            "案例题：生搬模板，不回到题干原句和业务上下文。",
            "论文题：堆框架，忽略项目背景、论题回应和字数约束。",
            "学习系统：没有诊断，没有错因，没有复习，路径就会漂。",
        ),
        ("选择题", "案例题", "论文题"),
        "把最近 10 个错题按“不会、混淆、审题、表达”四类归因。",
        ("错因卡：混淆概念", "原则卡：题干优先", "原则卡：复习优先级"),
    ),
)


DEFAULT_CHEKO_SNAPSHOT = ChekoSnapshot(
    captured_on="2026-06-29",
    source="browser-act chrome-direct logged-in cheko.cc",
    answered=634,
    wrong=194,
    accuracy=69.4,
    estimated_score=43.75,
    rank=1331,
    rank_total=4923,
    percentile=73.0,
    essay_power_remaining=15,
    essay_power_total=15,
    essay_past_exam_score="2013-2026 论文真题最近得分均为 0 / 4",
    collections_state="暂无收藏",
    practice_logs=(
        ChekoPracticeLog("企业信息化", "2025-11-08 13:30:03", "继续练习"),
        ChekoPracticeLog("软件工程", "2025-11-03 23:15:12", "查看回顾"),
        ChekoPracticeLog("系统架构设计", "2025-11-03 23:14:15", "继续练习"),
    ),
    weak_areas=(
        ChekoWeakArea("系统架构设计", 164, 164, "不看必挂", "先做质量属性、架构风格、ATAM 三块错因归类。"),
        ChekoWeakArea("软件工程", 82, 82, "不看必挂", "把开发方法、测试、维护、质量管理做成对比卡。"),
        ChekoWeakArea("系统分析与设计", 65, 65, "不看必挂", "用 DFD、ERD、UML 填空题训练上下文推理。"),
        ChekoWeakArea("数据库系统", 34, 34, "不看必挂", "补读写分离、分库分表、事务一致性和恢复策略。"),
        ChekoWeakArea("企业信息化战略", 32, 32, "非重点", "只做错题回炉，沉淀术语和场景表达。"),
        ChekoWeakArea("计算机网络", 25, 25, "不看必挂", "补协议、网络安全和性能相关概念边界。"),
        ChekoWeakArea("操作系统", 25, 25, "不看必挂", "补进程、存储、调度和可靠性基础。"),
    ),
    courses=(
        ChekoCourse("系统架构设计师综合题知识", 11, "2小时20分钟5秒", "选择题基本盘"),
        ChekoCourse("系统架构设计师案例知识", 5, "1小时27分钟5秒", "案例题得分框架"),
        ChekoCourse("系统架构设计师论文知识", 6, "2小时32分钟58秒", "论文题表达训练"),
    ),
)


def ensure_learning_resources(root: Path | str, *, overwrite: bool = False) -> Path:
    base = Path(root) / "learning"
    lessons = base / "lessons"
    reference = base / "reference"
    data = base / "data"
    for directory in (base, lessons, reference, data):
        directory.mkdir(parents=True, exist_ok=True)

    cheko_snapshot = _ensure_cheko_snapshot(data / "cheko-snapshot.json", overwrite=overwrite)

    _write_resource(base / "index.html", render_learning_index(cheko_snapshot), overwrite=overwrite)
    _write_resource(
        lessons / "0001-scene-before-solution.html",
        render_scene_before_solution_lesson(),
        overwrite=overwrite,
    )
    for page in REFERENCE_PAGES:
        _write_resource(reference / page.filename, render_reference_page(page), overwrite=overwrite)
    _write_resource(base / "notebooklm-seed.html", render_notebooklm_seed(), overwrite=overwrite)
    _write_resource(base / "cheko-sync.html", render_cheko_sync(cheko_snapshot), overwrite=overwrite)
    _write_resource(base / "today.html", render_today(cheko_snapshot), overwrite=overwrite)
    return base


def render_learning_index(cheko_snapshot: ChekoSnapshot = DEFAULT_CHEKO_SNAPSHOT) -> str:
    return _page(
        title="软考达人学习台",
        body=f"""
<header class="hero">
  <p class="eyebrow">Learning Desk</p>
  <h1>软考达人学习台</h1>
  <p class="lead">学习台负责“学什么、怎么练、沉淀成什么”。工作台负责记录和复习，学习台负责把资料变成当天可执行的课。</p>
  <div class="actions">
    <a class="button" href="/learning/today.html">今日三任务</a>
    <a class="button" href="/learning/lessons/0001-scene-before-solution.html">开始第一课</a>
    <a class="button secondary" href="/learning/reference/quality-attributes-tactics.html">打开速查表</a>
    <a class="button secondary" href="/">回工作台</a>
  </div>
</header>
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
  <p class="eyebrow">Lesson 0001</p>
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
    return _page(
        title=page.title,
        body=f"""
<header class="hero">
  <p class="eyebrow">Reference</p>
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
  <div class="chips">{"".join(f'<span>{escape(front)}</span>' for front in page.fronts)}</div>
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
  <p class="eyebrow">Uns</p>
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


def render_cheko_sync(snapshot: ChekoSnapshot = DEFAULT_CHEKO_SNAPSHOT) -> str:
    return _page(
        title="芝士架构同步信号",
        body=f"""
<header class="hero">
  <p class="eyebrow">Cheko Sync</p>
  <h1>芝士架构同步信号</h1>
  <p class="lead">这页只保存学习信号，不保存账号、头像、邮箱或任何登录凭据。它把芝士架构里的练习状态翻译成学习台的下一步行动。</p>
  <div class="actions">
    <a class="button" href="/learning/today.html">今日三任务</a>
    <a class="button" href="/learning/">回学习台</a>
    <a class="button secondary" href="https://www.cheko.cc/statistic">打开芝士架构统计</a>
  </div>
</header>
{_cheko_panel(snapshot)}
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
    {_cards((course.title, f"{course.role}；{course.lessons} 节；{course.duration}") for course in snapshot.courses)}
  </div>
</section>
<section>
  <h2>练习日志</h2>
  <div class="grid">
    {_cards((log.topic, f"{log.created_at}；{log.state}") for log in snapshot.practice_logs)}
  </div>
</section>
""",
    )


def render_today(snapshot: ChekoSnapshot = DEFAULT_CHEKO_SNAPSHOT) -> str:
    tasks = today_tasks(snapshot)
    return _page(
        title="今日三任务",
        body=f"""
<header class="hero">
  <p class="eyebrow">Today</p>
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
    <li>三件事全部完成后，不继续加码，转到工作台记录复习结果。</li>
    <li>任一任务卡住超过 20 分钟，把卡住点记录到 Mein，不硬扛。</li>
    <li>如果今天只能做一件事，只做第 1 件：最大错题池回炉。</li>
  </ol>
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
            why=f"{primary.title} 是当前最大错题池，{primary.total} 题已经足够暴露结构性薄弱点。",
            action=primary.next_action,
            done_when="至少完成 10 道错题复盘，按不会/混淆/审题/表达归因。",
            output="2 张概念卡 + 1 张错因卡。",
        ),
        TodayTask(
            title=f"{secondary.title}对比卡",
            why=f"{secondary.title} 错题池为 {secondary.total}，适合用对比卡降低混淆成本。",
            action=secondary.next_action,
            done_when="挑 3 个最容易混淆的概念，各写一句边界。",
            output="1 张对比卡 + 1 条 Du 分析。",
        ),
        TodayTask(
            title="论文最低触达",
            why=snapshot.essay_past_exam_score,
            action=essay_action,
            done_when="必须产生可复用文字，不以“看了范文”作为完成。",
            output="1 张表达卡，主题为项目背景或回应子题目。",
        ),
    )


def _page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172026;
      --muted: #5e6b73;
      --line: #cfd8dc;
      --paper: #ffffff;
      --band: #f6f8f6;
      --accent: #0f766e;
      --amber: #92400e;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: #fbfcfb;
      line-height: 1.58;
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 24px 20px 48px;
    }}
    .hero {{
      border-bottom: 1px solid var(--line);
      padding: 12px 0 20px;
      margin-bottom: 18px;
    }}
    .eyebrow {{
      margin: 0 0 6px;
      font-size: 12px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0;
      font-weight: 700;
    }}
    h1 {{
      margin: 0;
      font-size: 30px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 20px;
      line-height: 1.3;
    }}
    h3 {{
      margin: 0 0 6px;
      font-size: 15px;
      line-height: 1.3;
    }}
    .lead {{
      max-width: 820px;
      color: var(--muted);
      margin: 10px 0 0;
    }}
    section {{
      border: 1px solid var(--line);
      background: var(--paper);
      border-radius: 8px;
      padding: 16px;
      margin-top: 14px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 10px;
    }}
    .panel {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--band);
      padding: 12px;
    }}
    .panel p {{ margin: 0 0 8px; }}
    .panel p:last-child {{ margin-bottom: 0; }}
    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 10px;
    }}
    .metric {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--band);
      padding: 12px;
      min-height: 78px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 4px;
    }}
    .metric strong {{
      display: block;
      font-size: 20px;
      line-height: 1.25;
    }}
    .strong {{
      font-weight: 700;
      color: #12312e;
    }}
    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 14px;
    }}
    .button {{
      border: 1px solid var(--accent);
      border-radius: 6px;
      background: var(--accent);
      color: #fff;
      padding: 9px 12px;
      text-decoration: none;
      font-weight: 700;
      display: inline-flex;
      min-height: 40px;
      align-items: center;
    }}
    .button.secondary {{
      background: #fff;
      color: #063f3b;
      border-color: var(--line);
    }}
    .timeline {{
      display: grid;
      gap: 10px;
    }}
    .day {{
      display: grid;
      grid-template-columns: 78px minmax(0, 1fr);
      gap: 12px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 12px;
      background: var(--band);
    }}
    .day-index {{
      color: var(--amber);
      font-weight: 800;
    }}
    .meta {{
      color: var(--muted);
      font-size: 13px;
    }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .chips span {{
      border: 1px solid var(--line);
      background: var(--band);
      border-radius: 999px;
      padding: 6px 9px;
      font-weight: 700;
      color: #12312e;
    }}
    a {{ color: var(--accent); }}
    li + li {{ margin-top: 6px; }}
    @media (max-width: 720px) {{
      main {{ padding: 18px 14px 40px; }}
      h1 {{ font-size: 25px; }}
      .day {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main>
    {body}
  </main>
</body>
</html>
"""


def _cards(items: Iterable[tuple[str, str]]) -> str:
    return "".join(
        f'<div class="panel"><h3>{escape(title)}</h3><p>{escape(body)}</p></div>'
        for title, body in items
    )


def _day_card(day: DailyLearningPlan) -> str:
    return f"""<div class="day">
  <div class="day-index">Day {day.day}</div>
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
    fronts = " / ".join(page.fronts)
    return f"""<div class="panel">
  <h3><a href="/learning/reference/{escape(page.filename)}">{escape(page.title)}</a></h3>
  <p>{escape(page.purpose)}</p>
  <p class="meta">{escape(fronts)}</p>
</div>"""


def _cheko_panel(snapshot: ChekoSnapshot) -> str:
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
  <div class="day-index">Task {index}</div>
  <div>
    <h3>{escape(task.title)}</h3>
    <p><strong>为什么：</strong>{escape(task.why)}</p>
    <p class="meta">动作：{escape(task.action)}</p>
    <p class="meta">完成标准：{escape(task.done_when)}</p>
    <p class="meta">产出：{escape(task.output)}</p>
  </div>
</div>"""


def _ensure_cheko_snapshot(path: Path, *, overwrite: bool) -> ChekoSnapshot:
    if path.exists() and not overwrite:
        return _load_cheko_snapshot(path)
    snapshot = DEFAULT_CHEKO_SNAPSHOT
    path.write_text(
        json.dumps(_cheko_snapshot_to_dict(snapshot), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return snapshot


def _load_cheko_snapshot(path: Path) -> ChekoSnapshot:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return _cheko_snapshot_from_dict(payload)


def _cheko_snapshot_to_dict(snapshot: ChekoSnapshot) -> dict[str, Any]:
    return asdict(snapshot)


def _cheko_snapshot_from_dict(payload: dict[str, Any]) -> ChekoSnapshot:
    return ChekoSnapshot(
        captured_on=payload["captured_on"],
        source=payload["source"],
        answered=int(payload["answered"]),
        wrong=int(payload["wrong"]),
        accuracy=float(payload["accuracy"]),
        estimated_score=float(payload["estimated_score"]),
        rank=int(payload["rank"]),
        rank_total=int(payload["rank_total"]),
        percentile=float(payload["percentile"]),
        essay_power_remaining=int(payload["essay_power_remaining"]),
        essay_power_total=int(payload["essay_power_total"]),
        essay_past_exam_score=payload["essay_past_exam_score"],
        collections_state=payload["collections_state"],
        practice_logs=tuple(ChekoPracticeLog(**item) for item in payload["practice_logs"]),
        weak_areas=tuple(ChekoWeakArea(**item) for item in payload["weak_areas"]),
        courses=tuple(ChekoCourse(**item) for item in payload["courses"]),
    )


def _write_resource(path: Path, html: str, *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        return
    path.write_text(html, encoding="utf-8")
