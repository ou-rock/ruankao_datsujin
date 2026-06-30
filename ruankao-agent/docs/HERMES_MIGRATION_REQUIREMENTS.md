# Hermes Agent 迁移需求规格说明书 & 验收标准 (v1.0)

## 0. 变更历史与总体原则
*   **当前状态**：草案发布。
*   **总体原则**：**Hermes 为体，Codex 为魂**。Hermes 托管本地状态、文件系统、网络 Webhook 与 Discord/Telegram 网关通道；Codex 负责苏格拉底追问、架构审查、论文段落打磨、以及夜间进化规则提炼。
*   **数据底座**：本系统的数据源唯一真理（Single Source of Truth）仍为本地的 SQLite 数据库 `ruankao.db`。严禁在 Hermes 内置的 memory 模块中沉淀软考特异的备考状态以防止数据碎裂。

---

## 1. 物理拓扑与架构设计
系统应实现以下异步事件流与同步回环：

```text
[ Obsidian保存/Web练习打卡/Git提交 ] (异步输入)
              │
              ▼ (1) POST /webhooks/ruankao-sync
         [ 本地 Webhook 端点 ]
              │
              ▼ (2) 触发本地脚本 (零-Token)
    [ run-daily-cycle.command ] ──> 更新 [ SQLite / Obsidian / HTML ]
              │
              ▼ (3) 读取最新状态并发起风险计算
       [ 评估 RiskStatus ] 
              │
      ┌───────┴───────┐
      ▼ (红/黄灯或leech变化) ▼ (正常绿灯)
[触发 Discord/TG 报警推送]  [保持静默]
      │
      ▼ (4) 绑定学习线程交互
[苏格拉底追问交互 (Codex 驱动)] ──> 回应 ──> 提取 Mein / Du ──> 静默落库
```

---

## 2. 详细需求说明 (System Requirements)

### 需求一：Webhook 接收端与静默同步引擎 (Sync Pipeline)
*   **触发源**：支持通过 HTTP POST 将简要 payload 抛至本地服务端点。
*   **指令映射**：端点 `POST /webhooks/ruankao-sync` 发生请求时，Hermes 后台应无感、无阻塞地并发拉起本地脚本：
    ```bash
    /Users/pedan/Documents/ruankao/run-daily-cycle.command
    ```
*   **并发控制**：在脚本运行期间，后续的 Webhook 信号需进行防抖（Debounce），3 秒内多次触发仅执行一次，以防止 Obsidian 自动保存时造成 SQLite 写入冲突。

### 需求二：差分状态监视器与 Discord 级报警器 (Diff & Alert Gateway)
*   **状态抓取**：每次同步脚本执行完成后，系统通过读库或调用 `cli.py status` 解析出 `RiskStatus`（绿/黄/红）、`due_cards`（到期卡）、`leech` 诊断清单及缺席题型。
*   **差分判断**：设计一个“状态哨兵”服务，比对本次同步与上一次的历史指标。
*   **阈值推送规则**：
    1.  当 `RiskStatus` 发生退化（如 `green` -> `yellow` / `red`）时，必须将风险原因（如“论文超过 7 天未触达”）格式化输出为中文警报，发送给配置的 Discord 绑定 Channel。
    2.  当发现存在急需被修复的 `leech`（低分积压卡）时，于清晨或触发日结时在 Discord 进行定向提醒。
    3.  若状态仍为绿色，则保持静默，不在聊天频道灌水。

### 需求三：Obsidian 呈现面与只读契约 (Obsidian Read-Only Domain Contract)
*   **物理编辑约束**：Obsidian 在架构上定义为**纯呈现面与只读批注层**。SQLite (`ruankao.db`) 拥有绝对权威修改权。
*   **物理同步与覆盖规则**：
    1.  中端在执行 `vault-sync` 时，以 SQLite 中的卡片及提炼状态为准，强制覆盖 Obsidian 中对应的 md 文件的 YAML Frontmatter 头部及核心问题/回答正文。
    2.  当用户希望补充个人心得时，可在 md 文件底部的特定分隔线（如 `## My Notes` 或 `---` 分隔线）下方自由添加评论、手写心得或关联链接。
    3.  同步引擎 `vault.py` 在写入覆盖时，必须使用结构化解析器保护该分隔线以下的人工追加段落不被抹除。
    4.  SQLite 不对 Obsidian 写入的数据进行任何的反向读取与状态污染，完全杜绝漂移风险。

### 需求四：Obsidian / Git 提交钩子配置 (Local Trigger)
*   **物理集成**：在 `/Users/pedan/Documents/ruankao/.git/hooks/post-commit` 以及 Obsidian 软件中配置自动触发。配置需要具有极简稳定性：
    ```bash
    curl -s -X POST http://127.0.0.1:8765/webhooks/ruankao-sync > /dev/null &
    ```
    （注：端口与当前 Web 端口保持动态映射，若 8765 占用，需自适应寻址）。

### 需求五：苏格拉底式持久会话 Skill (Hermes Study-Mode Skill)
*   **命令封装**：在 Hermes 中注册 `ruankao-teach` 或 `ruankao-study-mode` 为 Pinned Local Skill。
*   **上下文路由**：当用户启动该 Skill 后，每一次对话（Study Turn）由 Hermes 打包历史上下文，路由至绑定的 Codex 推理后端：
    *   **Codex 任务**：生成“我在哪 / 你在哪 / 我们要去哪”三段短定位，并向用户抛出一个问题。
    *   **Hermes 任务**：监听用户回答。收到用户响应与 Codex 的回应后，无缝运行本地 cli，执行数据落库：
        ```bash
        python3 -m ruankao_agent.cli study-turn \
          --root /Users/pedan/Documents/ruankao/ruankao-agent \
          --topic "<主题>" \
          --user "<用户的原生回答>" \
          --assistant "<Codex的Mein/Du/追问三段反馈>" \
          --learner-position "<定位 我在哪>" \
          --codex-position "<定位 你在哪>" \
          --destination "<定位 要去哪>" \
          --front <对应的选择/案例/论文类型>
        ```
*   **零侵入规范**：入库动作对用户会话完全透明，用户无需在聊天界面感知任何命令行。

### 需求五：RAG 记忆与进步控制集成 (RAG Progress Control Engine)
*   **物理底座规约**：RAG 仅为**检索与阈值拦截计算层**，严禁引入任何第三方外部向量数据库（如 Chroma/Pinecone 等）。检索必须依赖底层已有的 SQLite 数据库数据表（三源材料 `raw_records`、卡片 `memory_cards`、复习日志 `review_logs` 和 `practice_sessions`）进行计算。
*   **计算内核逻辑**：
    1.  **文本切块 (Chunking)**：支持对三源长资料进行物理切块（支持重叠字符与自适应段落拆分），每个切块分配唯一 `chunk_ref` 标识（如 `raw:14#c1`）。
    2.  **全文检索索引 (SQLite FTS5)**：基于内存中建立的临时虚拟表 `fts5`，利用 SQLite 自带的 `bm25` 函数计算词频密度和相关性排名评分。
    3.  **分词与分段重排 (Hybrid Rerank)**：结合 FTS5 BM25 词频、词项字面匹配、完整短语命中、题型对齐（Front alignment）、状态奖励和物理进步权重（Progressive Weight，如 Leach 反复低分卡与 unstable 待回忆卡有大额提权 3.0~6.0 分）进行混合计算。
    4.  **排序透明度 (Explained Rerank)**：返回的 Brief 结果中需携带分数分解列表（fts_bm25、progress、token 等）和检索策略说明。
    5.  **进步闸门拦截 (Progress Gates)**：在每一次 RAG 命令被触发时，除了输出语义近端切块，还必须同步输出最高风险的“进步闸门”（根据 `leech` -> `unstable` -> `due-review` -> `low-practice` 优先级向下检索）。
    6.  **动作引导契约 (Answer Contract)**：返回的 brief payload 必须携带 `recommended_action`（建议动作）和交互契约（如强制引用 Mein/Du/Uns），以便在引导用户学习时直接建立回答规范。
*   **集成与管线入口**：
    1.  **闭环集成**：将 `ruankao_agent.cli rag-query` 作为每日闭环 `run-daily-cycle.command` 的第 5 步（共 9 步），每天自动生成并刷新当日的 RAG html/json 指标控制简报。
    *   **零侵入规范**：入库动作对用户会话完全透明，用户无需在聊天界面感知任何命令行。

### 需求六：意图规整过滤层 (Semantic Parser Ingest)
*   **物理职责与隔离**：为降低手写卡片的心智摩擦，中端挂载“语义解析规整层（Semantic Ingest Middleware）”。它位于前端输入动作之后，控制层 SQLite 写入之前。
*   **模型调用与数据规整（Frontend + Python -> JSON）**：
    1.  **触发阶段**：当用户在任一前端（Obsidian 保存、Webhook 事件或 Discord 回话）输入散装笔记或人话时，Harness 中的 Python 自行捕获。
    2.  **调用规整模型**：中端调用低成本、高并发的大模型（如 Gemini Flash），加载专用 Skill `ruankao-semantic-parser`。
    3.  **JSON 契约化输出**：小模型依据规范 Schema 枚举，将散装字段映射为 JSON 字符串并返回给 Python 中间件。
*   **物理层双重栅栏校验（Checklist Gate）**：
    1.  **第一层：认知校验**。如果输出非规范 JSON，硬性拦回重算。
    2.  **第二层：物理类型校验**。Python 本地强类型解析（Enum 映射匹配和 Float 等强限制），拦截不合规的脏数据，保障事实数据绝对纯净。

### 需求七：核心中脑 Payload 拼装与反馈机制 (Core Brain Payload & Response Routing)
    *   **核心中脑 Payload 生成者**：主决策大模型（Codex/推理脑）的推理 Payload **必须由中端 Harness Shell 的主编译器自包含装配（Self-contained Compilation）**。
    *   **装配装料源**：
        1.  中端的 RAG 检索引擎：提供最高相关度及需要最急迫处理的Leach/到期 `RagChunks` 证据。
        2.  本地的 `domain.py` 计算出的 countdown、`RiskStatus`、进步闸门（`ProgressGate`）和推荐动作。
        3.  语义解析规整层（RAG Parser）刚才整理好的最新输入 JSON。
    *   **单回合推理协议（Brain API Completion）**：Harness 将以上装料打包为标准的 System/User 消息报文发给 Codex。Codex 只接收自包含 Payload，输出符合回答契约（Answer Contract）的结构化文本：
        - `[Mein]`：用户卡点与原句复述。
        - `[Du]`：AI 架构原理级修正与对齐。
        - `[追问]`：下一步定向探索问题。
    *   **双向反馈流路由（Response Pathway）**：
        1.  **后端落盘**：中脑响应一经生成，Harness Shell 立即拉起 `storage.py` 将 Mein & Du 写入 SQLite 及 Obsidian 对应的 Mein/Du 本地 Vault 文件中。
        2.  **状态图更新**：重新执行 `dashboard.py` / `receipts.py`，更新 HTML 仪表盘以及当日 RAG 简报。
        3.  **前端网关投递**：如果是从 Discord 会话发起的请求，Harness 通过 Discord 适配器（Gateway Platforms）将追问和风险状态渲染为 Discord Rich Embed 卡片投递回聊天线程；如果是网页端，流式投递回网页学习控制台。

    ---

    ## 3. 验收标准与测试用例 (Acceptance Criteria & Test Plan)

    此验收测试由我（Antigravity / Hermes QA）在你的实现完成后自动或半自动运行。

    ### AC-1：Webhook 触发与同步验证 (Sync Verification)
*   **验证方法**：发送模拟 Webhook 信号，验证本地文件的生成和状态计算。
*   **测试指令**：
    ```bash
    # 模拟外部事件写入
    curl -i -X POST http://127.0.0.1:8765/webhooks/ruankao-sync
    ```
*   **检查点**：
    *   [ ] HTTP 响应状态码应为 `200 OK` 或 `202 Accepted`。
    *   [ ] 观察本地终端或日志，`run-daily-cycle.command` 应该被成功调用。
    *   [ ] 检查 `/Users/pedan/Documents/ruankao/ruankao-agent/reports/daily/` 下，最新日期的日结回执和状态导出 JSON 文件的修改时间被刷新在 30 秒以内。
    *   *防抖测试*：在 1 秒内连续发送 3 次 POST，系统日志中提示执行 `run-daily-cycle` 仅有 1 次，无并发碰撞造成的 `database is locked` 报错。

### AC-2：Discord 状态差分推送验证 (Alert Verification)
*   **验证方法**：修改 SQLite 内部的练习状态或卡片到期，人为促成状态跌落，验证 Hermes 能否在 Discord 中主动呼叫用户。
*   **测试指令**：
    1.  手动向 `ruankao.db` 注入一条假练习记录，令其“本周选择、案例、论文题型全部缺席”。
    2.  触发 `/webhooks/ruankao-sync`。
*   **检查点**：
    *   [ ] D-116 状态变为“红灯”。
    *   [ ] 绑定了 Hermes 平台的 Discord 频道在 15 秒内收到了一条来自 bot 的警告消息。
    *   [ ] 警告消息中准确指出红灯根源：“本周缺席 2 个以上题型”与“复习积压超过 40%”。

### AC-3：对话模式静默入队验证 (Socratic Process Verification)
*   **验证方法**：在 Discord 线程中模拟进行一轮 Socratic 学习交互。
*   **测试流程**：
    1.  用户发送：“我想针对'场景先于方案'原则做一轮案例分析练习。”
    2.  检查后台返回的 Mein/Du/追问 三段数据。
*   **检查点**：
    *   [ ] 后台 SQLite 数据库的 `raw_records` 表中自动生成了两条关联的新数据，`source` 字段分别标记为 `mein` 和 `du`。
    *   [ ] 对应的 Obsidian 目录下，`vault/20-mein/` and `vault/30-du/` 出现了生成的记录 md 文件。
    *   [ ] 对话正常向后翻滚，无明显卡顿，控制台无报错。

### AC-4：RAG 召回与进步闸门验收 (RAG & Progress Gates Verification)
*   **验证方法**：使用 CLI/Web 触发 RAG 检索并检查生成的控制简报是否符合排序及闸门约束。
*   **测试指令**：
    ```bash
    python3 -m ruankao_agent.cli rag-query \
      --root /Users/pedan/Documents/ruankao/ruankao-agent \
      --query "可用性 可靠性"
    ```
*   **检查点**：
    *   [ ] 对齐生成的本地 JSON 文件 `data/rag/YYYY-MM-DD.json` 及报告 HTML。
    *   [ ] 语义命中：对中文二字、三字词组做 N-Gram 切割，且**接入 SQLite FTS5 临时全文索引与 `bm25` 相关性检索**（策略类型显示为 `sqlite-fts5-hybrid-progress`）。
    *   [ ] 语义切块追溯：高相关度切块在命中时需输出明确的带索引切块 ID，如 `chunk_ref` 包含 `#c1`、`#c2` 追随。
    *   [ ] 排序权重与可解释性：混排得分中包含对 `fts_bm25` 词频的打分以及对卡片/练习进阶状态的分离与可解释 `score_breakdown` 拆分列（progress、token、fts_bm25、phrase、front、status）。
    *   [ ] 进步闸门拦截：当有任务处于高危状态（如某卡复习到期、某战线题型缺席）时，自动生成 `ProgressGate` 元素并给出强退回的 `recommended_action` 警醒。
    *   [ ] 每天闭环运行完，新生成的日结报表中应正常显示 `RAG 控制` 面板与契约指令。


