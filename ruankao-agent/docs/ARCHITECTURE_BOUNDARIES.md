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
L5 入口适配层      cli.py, web.py, web_app.py, web_handlers.py, web_forms.py, shell scripts, .codex commands
L4 报告与页面层    dashboard.py, receipts.py, route_map.py, evolution.py, learning.py, web_render.py
L3 学习智能层      memory.py, rag.py, loop.py, cheko.py, principles.py, study.py
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
| `rag.py` | L3 | `domain`, `memory`, `storage` | 本地 RAG：切块、FTS/BM25、混合排序、进步闸门。不能依赖 Web/CLI。 |
| `loop.py` | L3 | `dashboard`, `notebooklm` | 日循环快照、风险聚合、状态文字。不能写报告文件。 |
| `cheko.py` | L3 | `domain`, `learning`, `storage` | Cheko 学习信号入队为三源和记忆卡。不能直接操作 Web。 |
| `principles.py` | L3 | `domain`, `storage` | 核心原则种子、原则卡和关系。不能渲染工作台。 |
| `study.py` | L3 | `domain`, `storage` | 学习回合沉淀 Mein/Du。不能决定夜间进化。 |
| `dashboard.py` | L4 | 无 | 静态总图渲染。只接收快照，不读取数据库。 |
| `receipts.py` | L4 | `loop`, `memory`, `rag`, `storage` | 日结 JSON/HTML，聚合每日状态。可以读库，不能处理 HTTP。 |
| `route_map.py` | L4 | `domain`, `memory`, `storage` | 三题型覆盖图。可以读库，不能写记忆卡。 |
| `evolution.py` | L4 | `receipts` | 夜间进化草案。只能生成暂存计划，不直接改 live skill。 |
| `learning.py` | L4 | `domain` | 学习台静态 HTML 和 Cheko snapshot。不能写 ruankao.db。 |
| `web_render.py` | L4 | `domain`, `memory`, `storage` | 工作台 HTML 片段、标签文案和列表渲染。不能处理 HTTP、打开数据库或写状态。 |
| `cli.py` | L5 | 多数模块 | CLI 组合根。负责参数解析和命令编排，不放业务规则。 |
| `web_forms.py` | L5 | `domain` | 工作台表单适配器。把 HTTP 表单字段转成 typed input。不能打开数据库、处理 HTTP 或渲染 HTML。 |
| `web_handlers.py` | L5 | `web_forms` | 工作台 HTTP handler 与路由分发。负责 GET/POST、响应码、重定向和文件响应。不能打开数据库或承载业务规则。 |
| `web_app.py` | L5 | 多数模块, `web_forms`, `web_render` | 工作台应用编排层。负责初始化、写入动作、报告触发和页面组合。不处理 HTTP server 绑定。 |
| `web.py` | L5 | `web_app`, `web_handlers` | 本地 HTTP 工作台启动入口。负责服务绑定、端口回退和兼容导出，不成为事实源。 |

## 当前内部导入图

```text
cheko        -> domain, learning, storage
cli          -> cheko, dashboard, domain, evolution, export_state, learning, loop, notebooklm, principles, rag, receipts, route_map, study, vault, web
dashboard    -> -
domain       -> -
evolution    -> receipts
export_state -> storage
learning     -> domain
loop         -> dashboard, notebooklm
memory       -> storage
notebooklm   -> -
principles   -> domain, storage
rag          -> domain, memory, storage
receipts     -> loop, memory, rag, storage
route_map    -> domain, memory, storage
storage      -> domain
study        -> domain, storage
vault        -> -
web          -> web_app, web_handlers
web_app      -> cheko, dashboard, domain, evolution, export_state, learning, loop, memory, rag, receipts, route_map, storage, study, vault, web_forms, web_render
web_forms    -> domain
web_handlers -> web_forms
web_render   -> domain, memory, storage
```

## 耦合分类

### 稳定核心耦合

- `storage -> domain`
- `memory -> storage`
- `rag -> domain/memory/storage`
- `receipts/route_map -> memory/storage`

这些耦合是合理的：它们围绕事实源、记忆诊断和报告聚合。

### 组合根耦合

- `cli.py` 出度 15。
- `web_app.py` 出度 16。
- `web.py` 出度 2。

这是可接受但需要警惕的耦合。它们必须保持“薄”：只做编排、表单解析、路由和调用，不沉淀核心业务规则。

`web_app.py` 是工作台应用编排层，暂时保留高耦合以保护外部 URL、
HTML 和 CLI 行为。它是后续继续拆工作台应用服务的主要热点。

`web_forms.py` 是从组合根拆出的输入适配器。它允许依赖 `domain.py`
来完成枚举转换，但不允许依赖 `storage.py`、`web.py` 或 `web_render.py`。

`web_handlers.py` 是从组合根拆出的 HTTP 适配器。它允许依赖 `web_forms.py`
读取查询参数和 POST 表单，但不能依赖 `storage.py` 或任何学习智能模块。

### 文件生成耦合

- `receipts.py`, `route_map.py`, `evolution.py`, `learning.py`, `dashboard.py` 都生成 HTML 或 JSON。
- `web_render.py` 只生成工作台 HTML 片段，不写文件。
- 边界是：报告模块可以读库或接收快照，但不能修改学习事实，除非命令名明确是写入动作。

### 状态写入耦合

- `storage.py` 是唯一 SQLite schema 与仓储入口。
- `cheko.py`, `principles.py`, `study.py`, `web_app.py` 可以通过 `RuankaoStore` 写入。
- 其他模块不应绕过 `RuankaoStore` 写 SQLite。

## 耦合热点

| 热点 | 证据 | 风险 | 优化方向 |
| --- | --- | --- | --- |
| `web_app.py` | 约 1260 行，依赖 16 个内部模块 | 页面组合、写入动作、报告触发仍在一起 | 后续拆 `web_actions.py`, `web_files.py`, `web_page.py` |
| `cli.py` | 依赖 15 个内部模块 | 命令解析与命令执行容易变厚 | 后续拆成 `commands/*.py` 或应用服务层 |
| `learning.py` | 超过 1000 行 | 静态内容、CSS、Cheko snapshot、页面渲染混合 | 后续拆模板、数据、CSS 常量 |
| `rag.py` | RAG 切块、FTS、HTML 渲染同模块 | 检索算法和报告渲染可能互相拖累 | 后续拆 `rag_index.py`, `rag_rank.py`, `rag_report.py` |
| `receipts.py` | 日结聚合、HTML、RAG 嵌入 | 报告越来越像第二个工作台 | 后续把 payload 构建和渲染拆开 |

## 允许依赖规则

1. `domain.py`, `dashboard.py`, `notebooklm.py`, `vault.py` 不依赖任何内部模块。
2. `storage.py` 只依赖 `domain.py`。
3. `memory.py` 只依赖 `storage.py`。
4. `rag.py` 只依赖 `domain.py`, `memory.py`, `storage.py`。
5. `web_render.py` 只负责工作台展示片段，可以依赖只读数据对象，不能处理 HTTP 或写状态。
6. `web_forms.py` 只负责工作台表单字段到 typed input 的转换，可以依赖 `domain.py`，不能依赖存储或渲染。
7. `web_handlers.py` 只负责 HTTP handler、路由分发和响应封装，可以依赖 `web_forms.py`，不能依赖业务模块或存储。
8. `web_app.py` 是工作台应用编排层，可以依赖内层模块，但不能处理 HTTP server 绑定。
9. `cli.py` 和 `web.py` 是组合根，可以依赖内层模块。
10. 除 `cli.py` 之外，任何模块不得依赖 `web.py`。
11. 内层模块不得依赖 `cli.py`, `web.py`, `web_app.py`, `web_forms.py`, `web_handlers.py`, `.codex` 命令、shell scripts 或浏览器自动化工具。

## 下一轮架构优化顺序

1. 继续拆 `web_app.py`：`web.py` 已降为启动入口，下一步拆写入动作、文件服务和页面组装。
2. 再拆 `rag.py`：让索引、排序、报告各自独立。
3. 再拆 `learning.py`：把静态数据、模板和样式分开。
4. 最后拆 `cli.py`：让命令只绑定参数到应用服务。

每次拆分必须保持外部命令、工作台 URL、生成文件路径不变。
