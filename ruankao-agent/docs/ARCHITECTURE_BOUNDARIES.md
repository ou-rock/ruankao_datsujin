# 架构边界与耦合地图

## 目标

这份文档回答三个问题：

1. 当前有哪些模块。
2. 每个模块的责任边界是什么。
3. 模块之间如何耦合，哪些耦合是合理的，哪些是后续优化重点。

本项目采用本地优先架构。SQLite 是事实源，Obsidian 是可编辑知识网络，HTML 是学习者界面，
CLI 和 Web 是外层适配器。核心规则是：外层可以依赖内层，内层不能反向依赖外层。

## 分层

```text
L5 入口适配层      cli.py, web.py, web_app.py, web_actions.py, web_bootstrap.py, web_files.py, web_handlers.py, web_forms.py, web_page.py, web_page_forms.py, web_page_sections.py, web_page_style.py, web_page_view.py, shell scripts, .codex commands
L4 报告与页面层    dashboard.py, receipts.py, route_map.py, evolution.py, learning.py, learning_content.py, learning_style.py, learning_templates.py, rag.py, rag_report.py, web_render.py
L3 学习智能层      memory.py, rag_index.py, rag_rank.py, rag_types.py, loop.py, cheko.py, principles.py, study.py
L2 持久化层        storage.py, vault.py, export_state.py
L1 领域内核        domain.py, notebooklm.py
```

`cli.py` 和 `web.py` 允许高耦合，因为它们是组合根。其他模块应保持窄依赖。

## 模块清单

| 模块 | 层级 | 当前依赖 | 边界 |
| --- | --- | --- | --- |
| `domain.py` | L1 | 无 | 枚举、日期、风险规则、战役阶段。不能依赖存储、UI 或文件系统。 |
| `notebooklm.py` | L1 | 无 | NotebookLM 外部研究源的本地元数据。不能直接访问网络。 |
| `storage.py` | L2 | `domain` | SQLite schema、仓储、数据行对象。不能渲染 HTML 或写 Obsidian。 |
| `vault.py` | L2 | 无 | Obsidian 目录与 Markdown 生成。不能读取业务状态，只接收调用方传入数据。 |
| `export_state.py` | L2 | `storage` | 导出本地 JSON 状态。不能承担业务决策。 |
| `memory.py` | L3 | `storage` | 记忆诊断、Obsidian note 渲染辅助。不能打开数据库。 |
| `rag_types.py` | L3 | `domain` | RAG 文档、切块、命中、闸门和简报数据结构。不能读取数据库、渲染 HTML 或执行排序。 |
| `rag_index.py` | L3 | `rag_types` | RAG 切块、token 化、SQLite FTS5 临时索引和 BM25 分数。不能读取业务库或渲染报告。 |
| `rag_rank.py` | L3 | `domain`, `rag_index`, `rag_types` | RAG 混合排序与题型过滤。不能写文件或生成 HTML。 |
| `loop.py` | L3 | `dashboard`, `notebooklm` | 日循环快照、风险聚合、状态文字。不能写报告文件。 |
| `cheko.py` | L3 | `domain`, `learning`, `storage` | Cheko 学习信号入队为三源和记忆卡。不能直接操作 Web。 |
| `principles.py` | L3 | `domain`, `storage` | 核心原则种子、原则卡和关系。不能渲染工作台。 |
| `study.py` | L3 | `domain`, `storage` | 学习回合沉淀 Mein/Du。不能决定夜间进化。 |
| `dashboard.py` | L4 | 无 | 静态总图渲染。只接收快照，不读取数据库。 |
| `receipts.py` | L4 | `loop`, `memory`, `rag`, `storage` | 日结 JSON/HTML，聚合每日状态。可以读库，不能处理 HTTP。 |
| `route_map.py` | L4 | `domain`, `memory`, `storage` | 三题型覆盖图。可以读库，不能写记忆卡。 |
| `evolution.py` | L4 | `receipts` | 夜间进化草案。只能生成暂存计划，不直接改 live skill。 |
| `learning_content.py` | L4 | 无 | 学习台静态课程、速查资源和 Cheko snapshot 默认数据。不能生成文件或渲染 HTML。 |
| `learning_style.py` | L4 | 无 | 学习台 CSS 常量。不能保存学习内容、Cheko 数据或生成文件。 |
| `learning_templates.py` | L4 | `domain`, `learning_content`, `learning_style` | 学习台 HTML 模板和页面片段。可以生成 HTML 字符串，不能写文件、读库或处理 HTTP。 |
| `learning.py` | L4 | `learning_content`, `learning_templates` | 学习台资源落盘与 Cheko snapshot 文件编排。不能写 ruankao.db 或承载页面模板。 |
| `rag_report.py` | L4 | `rag_types` | RAG payload、报告路径和 HTML 渲染。不能执行检索、排序或读取 SQLite。 |
| `rag.py` | L4 | `domain`, `memory`, `rag_index`, `rag_rank`, `rag_report`, `rag_types`, `storage` | RAG facade 和文件写入编排。负责从 store 装配文档、进步闸门、简报写入，并保留旧公开 API。不能处理 Web/CLI。 |
| `web_render.py` | L4 | `domain`, `memory`, `storage` | 工作台 HTML 片段、标签文案和列表渲染。不能处理 HTTP、打开数据库或写状态。 |
| `cli.py` | L5 | 多数模块 | CLI 组合根。负责参数解析和命令编排，不放业务规则。 |
| `web_forms.py` | L5 | `domain` | 工作台表单适配器。把 HTTP 表单字段转成 typed input。不能打开数据库、处理 HTTP 或渲染 HTML。 |
| `web_handlers.py` | L5 | `web_forms` | 工作台 HTTP handler 与路由分发。负责 GET/POST、响应码、重定向和文件响应。不能打开数据库或承载业务规则。 |
| `web_actions.py` | L5 | 多数模块, `web_forms` | 工作台动作适配器。负责写入、报告触发和 Vault 同步。不处理 HTTP 或页面渲染。 |
| `web_bootstrap.py` | L5 | `learning`, `storage`, `vault` | 工作台启动适配器。负责 root 初始化、Vault、默认原则和学习台资源。不处理 HTTP 或页面组装。 |
| `web_files.py` | L5 | 无 | 工作台文件读取适配器。负责 dashboard/learning/report/export 文件读取和路径越界防护。不打开数据库或处理 HTTP 状态码。 |
| `web_page_style.py` | L5 | 无 | 工作台首页样式常量。只保存 CSS 字符串，不读取状态、不拼表单、不处理 HTTP。 |
| `web_page_view.py` | L5 | 无 | 工作台首页 view model。只保存页面所需的只读数据结构，不渲染 HTML、不读取数据库。 |
| `web_page_forms.py` | L5 | `web_page_view`, `web_render` | 工作台首页表单区块适配器。负责练习、学习回合、三源、记忆卡、原则网络、Vault 等表单 HTML。不解析 HTTP 或写状态。 |
| `web_page_sections.py` | L5 | `web_page_forms`, `web_page_style`, `web_page_view`, `web_render` | 工作台首页结构适配器。负责首页 HTML shell、导航、今日闭环和只读展示区块。不读取数据库或处理 HTTP。 |
| `web_page.py` | L5 | `domain`, `evolution`, `export_state`, `memory`, `rag`, `receipts`, `route_map`, `web_page_sections`, `web_page_view`, `web_render` | 工作台首页数据适配器。负责首页只读数据装配和 view model，不处理 HTTP、写入动作或启动初始化。 |
| `web_app.py` | L5 | `dashboard`, `loop`, `storage`, `web_actions`, `web_bootstrap`, `web_files`, `web_forms`, `web_page` | 工作台应用编排层。负责快照、dashboard 写入和兼容方法委托。不处理 HTTP server 绑定。 |
| `web.py` | L5 | `web_app`, `web_handlers` | 本地 HTTP 工作台启动入口。负责服务绑定、端口回退和兼容导出，不成为事实源。 |

## 当前内部导入图

```text
cheko        -> domain, learning, storage
cli          -> cheko, dashboard, domain, evolution, export_state, learning, loop, notebooklm, principles, rag, receipts, route_map, study, vault, web
dashboard    -> -
domain       -> -
evolution    -> receipts
export_state -> storage
learning     -> learning_content, learning_templates
learning_content -> -
learning_style -> -
learning_templates -> domain, learning_content, learning_style
loop         -> dashboard, notebooklm
memory       -> storage
notebooklm   -> -
principles   -> domain, storage
rag          -> domain, memory, rag_index, rag_rank, rag_report, rag_types, storage
rag_index    -> rag_types
rag_rank     -> domain, rag_index, rag_types
rag_report   -> rag_types
rag_types    -> domain
receipts     -> loop, memory, rag, storage
route_map    -> domain, memory, storage
storage      -> domain
study        -> domain, storage
vault        -> -
web          -> web_app, web_handlers
web_actions  -> cheko, domain, evolution, export_state, rag, receipts, route_map, storage, study, vault, web_forms
web_app      -> dashboard, loop, storage, web_actions, web_bootstrap, web_files, web_forms, web_page
web_bootstrap -> learning, storage, vault
web_files    -> -
web_forms    -> domain
web_handlers -> web_forms
web_page     -> domain, evolution, export_state, memory, rag, receipts, route_map, web_page_sections, web_page_view, web_render
web_page_forms -> web_page_view, web_render
web_page_sections -> web_page_forms, web_page_style, web_page_view, web_render
web_page_style -> -
web_page_view -> -
web_render   -> domain, memory, storage
```

## 耦合分类

### 稳定核心耦合

- `storage -> domain`
- `memory -> storage`
- `rag -> domain/memory/rag_index/rag_rank/rag_report/rag_types/storage`
- `rag_index -> rag_types`
- `rag_rank -> domain/rag_index/rag_types`
- `rag_report -> rag_types`
- `receipts/route_map -> memory/storage`

这些耦合是合理的：它们围绕事实源、记忆诊断和报告聚合。

### 组合根耦合

- `cli.py` 出度 15。
- `web_app.py` 出度 8。
- `web_actions.py` 出度 11。
- `web_bootstrap.py` 出度 3。
- `web_files.py` 出度 0。
- `web_page.py` 出度 10。
- `web_page_forms.py` 出度 2。
- `web_page_sections.py` 出度 4。
- `web_page_style.py` 出度 0。
- `web_page_view.py` 出度 0。
- `web.py` 出度 2。

这是可接受但需要警惕的耦合。它们必须保持“薄”：只做编排、表单解析、路由和调用，不沉淀核心业务规则。

`web_app.py` 是工作台应用编排层。它现在主要保留快照、dashboard
写入和兼容方法委托，不再直接承载首页 HTML、启动细节或文件读取。

`web_actions.py` 是从 `web_app.py` 拆出的动作适配器。它允许依赖
`web_forms.py` 和内层服务，把写库、报告触发、Vault 同步集中在一个
可审计位置；它不能处理 HTTP、拼页面或绕过 `RuankaoStore`。

`web_bootstrap.py` 是启动适配器。它把 root 创建、SQLite 初始化、
Vault 初始化、默认原则种子和学习台静态资源收在一起，避免 `web_app.py`
直接知道启动细节。

`web_files.py` 是文件读取适配器。它只做安全路径检查和文本读取，
通过抛出 `PermissionError` / `FileNotFoundError` 让 HTTP handler
决定 403/404 响应。

`web_page.py` 是工作台首页数据适配器。它装配首页所需的只读数据，
生成 `HomePageView`，再交给 `web_page_sections.py`；它不能处理 HTTP、
写数据库、同步 Vault 或执行启动初始化。

`web_page_view.py` 是首页 view model 模块。它只定义传递给页面渲染层的
只读数据形状，不读取状态、不拼 HTML、不承载业务规则。

`web_page_sections.py` 是首页结构适配器。它接收 `HomePageView`，
调用 `web_render.py` 片段并组合首页 HTML shell、导航、今日闭环和只读展示区块；
它不能读取数据库、构造 RAG brief 或触发写入动作。

`web_page_forms.py` 是首页表单区块适配器。它接收 `HomePageView`，
渲染工作台的写入表单结构，但不解析 HTTP 表单、不调用写入动作。

`web_page_style.py` 是首页 CSS 常量模块。它不依赖任何内部模块，
也不承载页面数据、表单结构或业务文案。

`web_forms.py` 是从组合根拆出的输入适配器。它允许依赖 `domain.py`
来完成枚举转换，但不允许依赖 `storage.py`、`web.py` 或 `web_render.py`。

`web_handlers.py` 是从组合根拆出的 HTTP 适配器。它允许依赖 `web_forms.py`
读取查询参数和 POST 表单，但不能依赖 `storage.py` 或任何学习智能模块。

`rag.py` 是 RAG facade。它可以读 `RuankaoStore` 并组合文档、闸门、检索和
报告写入，但具体切块/索引在 `rag_index.py`，排序在 `rag_rank.py`，
payload/HTML 在 `rag_report.py`，数据结构在 `rag_types.py`。

### 文件生成耦合

- `receipts.py`, `route_map.py`, `evolution.py`, `learning.py`, `dashboard.py`, `rag.py`, `rag_report.py` 都生成 HTML 或 JSON。
- `learning_content.py` 只保存学习台静态内容数据，不生成文件。
- `learning_style.py` 只保存学习台页面 CSS，不生成文件。
- `learning_templates.py` 只生成学习台 HTML 字符串，不写文件。
- `rag_report.py` 只把 `RagBrief` 或 payload 转成 JSON/HTML，不做检索。
- `rag_index.py` 和 `rag_rank.py` 不写文件。
- `web_render.py` 只生成工作台 HTML 片段，不写文件。
- `web_page.py` 装配首页 view model，不写文件。
- `web_page_view.py` 只定义首页 view model，不写文件。
- `web_page_sections.py` 组合工作台首页 shell 与只读区块，不写文件。
- `web_page_forms.py` 组合工作台首页表单区块，不写文件。
- `web_page_style.py` 只保存首页 CSS 字符串。
- `web_files.py` 只读取已经生成的工作台文件，不决定 HTTP 响应码。
- 边界是：报告模块可以读库或接收快照，但不能修改学习事实，除非命令名明确是写入动作。

### 状态写入耦合

- `storage.py` 是唯一 SQLite schema 与仓储入口。
- `cheko.py`, `principles.py`, `study.py`, `web_actions.py` 可以通过 `RuankaoStore` 写入。
- 其他模块不应绕过 `RuankaoStore` 写 SQLite。

## 耦合热点

| 热点 | 证据 | 风险 | 优化方向 |
| --- | --- | --- | --- |
| `web_page_forms.py` | 约 310 行，依赖 2 个内部模块 | 表单区块已经离开页面壳，但仍承载多种写入入口 | 后续如继续增长，再按练习/记忆/同步拆小 |
| `web_page_sections.py` | 约 130 行，依赖 4 个内部模块 | 页面壳已变薄，仍聚合首页所有区块调用 | 保持只做布局编排，不回填表单细节 |
| `web_page.py` | 约 130 行，依赖 10 个内部模块 | 首页数据装配仍集中，但结构已外移 | 保持只做 view model 装配 |
| `web_page_style.py` | 约 500 行，无内部依赖 | CSS 已独立，但仍是大块内联样式 | 后续如有前端构建再外置为静态 CSS |
| `web_actions.py` | 约 200 行，依赖 11 个内部模块 | 动作层集中副作用，后续可能继续增长 | 后续按写库、报告触发、Vault 同步再拆 |
| `web_app.py` | 约 220 行，依赖 8 个内部模块 | 编排层已经变薄，仍是工作台对象入口 | 保持兼容委托，不再回填页面/动作细节 |
| `web_bootstrap.py` | 约 40 行，依赖 3 个内部模块 | 启动动作集中，未来可能吸收更多初始化 | 保持只做启动，不承载运行时业务 |
| `web_files.py` | 约 60 行，无内部依赖 | 文件读取边界清晰，风险低 | 保持只做路径防护和文本读取 |
| `cli.py` | 依赖 15 个内部模块 | 命令解析与命令执行容易变厚 | 后续拆成 `commands/*.py` 或应用服务层 |
| `learning.py` | 约 100 行，依赖 2 个内部模块 | 资源写入和 Cheko snapshot 编解码已收敛，风险低 | 保持只做学习资源落盘和 snapshot 文件编排 |
| `learning_templates.py` | 约 480 行，依赖 3 个内部模块 | HTML 模板已独立，但仍包含多页模板和片段 helper | 后续如继续增长，再按首页/课程/参考页拆分 |
| `learning_content.py` | 约 320 行，无内部依赖 | 学习台种子内容集中，适合人工审阅但会随资料增长 | 后续如继续增长，再按课程/速查/Cheko snapshot 拆分 |
| `learning_style.py` | 约 200 行，无内部依赖 | 学习台样式独立，风险低 | 保持只做 CSS 常量 |
| `rag.py` | 约 390 行，依赖 7 个内部模块 | facade 仍组合文档构造、进步闸门和文件写入 | 后续如继续增长，拆 `rag_progress.py` 或 `rag_documents.py` |
| `rag_report.py` | 约 260 行，依赖 1 个内部模块 | RAG 报告 HTML/CSS 独立但仍是大块模板 | 后续如改版，拆样式或片段 helper |
| `receipts.py` | 日结聚合、HTML、RAG 嵌入 | 报告越来越像第二个工作台 | 后续把 payload 构建和渲染拆开 |

## 允许依赖规则

1. `domain.py`, `dashboard.py`, `notebooklm.py`, `vault.py` 不依赖任何内部模块。
2. `storage.py` 只依赖 `domain.py`。
3. `memory.py` 只依赖 `storage.py`。
4. `rag_types.py` 只依赖 `domain.py`，不能读取状态、排序或渲染。
5. `rag_index.py` 只负责切块、token、FTS5/BM25 临时索引，可以依赖 `rag_types.py`，不能读取业务库或写报告。
6. `rag_rank.py` 只负责混合排序和题型过滤，可以依赖 `domain.py`, `rag_index.py`, `rag_types.py`，不能写文件或生成 HTML。
7. `rag_report.py` 只负责 RAG payload、报告路径和 HTML 渲染，可以依赖 `rag_types.py`，不能执行检索或排序。
8. `rag.py` 是 RAG facade，可以依赖 `domain.py`, `memory.py`, `rag_index.py`, `rag_rank.py`, `rag_report.py`, `rag_types.py`, `storage.py`，不能处理 HTTP 或 CLI 参数。
9. `learning_content.py` 只保存学习台静态内容、资源元数据和默认 Cheko snapshot，不能生成文件、渲染 HTML 或读取状态。
10. `learning_style.py` 只保存学习台 CSS 常量，不能保存学习内容、Cheko snapshot 或生成文件。
11. `learning_templates.py` 可以依赖 `domain.py`, `learning_content.py` 和 `learning_style.py` 生成学习台 HTML 字符串，不能写文件、读库或处理 HTTP。
12. `learning.py` 可以依赖 `learning_content.py` 和 `learning_templates.py` 生成学习台资源文件，不能写 ruankao.db 或承载页面模板。
13. `web_render.py` 只负责工作台展示片段，可以依赖只读数据对象，不能处理 HTTP 或写状态。
14. `web_forms.py` 只负责工作台表单字段到 typed input 的转换，可以依赖 `domain.py`，不能依赖存储或渲染。
15. `web_handlers.py` 只负责 HTTP handler、路由分发和响应封装，可以依赖 `web_forms.py`，不能依赖业务模块或存储。
16. `web_actions.py` 只负责工作台副作用动作，可以依赖 `web_forms.py` 和内层服务，不能处理 HTTP 或渲染页面。
17. `web_bootstrap.py` 只负责工作台启动初始化，可以依赖 `learning.py`, `storage.py`, `vault.py`，不能处理 HTTP 或运行时业务。
18. `web_files.py` 只负责工作台文件读取和路径防护，不能打开数据库、渲染页面或处理 HTTP 状态码。
19. `web_page_style.py` 只保存工作台首页 CSS 常量，不能读取状态、生成表单或依赖业务模块。
20. `web_page_view.py` 只定义首页 view model，不渲染 HTML、不读取状态。
21. `web_page_forms.py` 只负责工作台首页表单区块 HTML，可以依赖 `web_page_view.py` 和 `web_render.py`，不能解析 HTTP、读取数据库或触发写入动作。
22. `web_page_sections.py` 只负责工作台首页 shell、导航、今日闭环和只读展示区块，可以依赖 `web_page_forms.py`, `web_page_view.py`, `web_render.py` 与 `web_page_style.py`，不能读取状态或处理 HTTP。
23. `web_page.py` 只负责工作台首页 view model 装配，可以依赖只读内层服务，不能处理 HTTP、写状态或执行启动初始化。
24. `web_app.py` 是工作台应用编排层，可以依赖内层模块，但不能处理 HTTP server 绑定。
25. `cli.py` 和 `web.py` 是组合根，可以依赖内层模块。
26. 除 `cli.py` 之外，任何模块不得依赖 `web.py`。
27. 内层模块不得依赖 `cli.py`, `web.py`, `web_actions.py`, `web_app.py`, `web_bootstrap.py`, `web_files.py`, `web_forms.py`, `web_handlers.py`, `web_page.py`, `web_page_forms.py`, `web_page_sections.py`, `web_page_style.py`, `web_page_view.py`, `.codex` 命令、shell scripts 或浏览器自动化工具。

## 下一轮架构优化顺序

1. 拆 `receipts.py`：把日结 payload 构建和 HTML 渲染拆开。
2. 如果 `learning_templates.py` 继续增长，再按首页/课程/参考页拆分。
3. 如果 RAG facade 继续增长，再拆 `rag_progress.py` 或 `rag_documents.py`。
4. 如果工作台表单继续增长，再拆 `web_page_forms.py`。
5. 最后拆 `cli.py`：让命令只绑定参数到应用服务。

每次拆分必须保持外部命令、工作台 URL、生成文件路径不变。
