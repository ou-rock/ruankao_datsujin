from __future__ import annotations

from dataclasses import dataclass


NOTEBOOKLM_SOURCE = "System Architecture Designer Exam Questions and Analysis"
FRONT_LABELS = {
    "choice": "选择题",
    "case": "案例题",
    "essay": "论文题",
}


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
    minutes: int
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
