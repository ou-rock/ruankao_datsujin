# ruankao datsujin

本地优先的 Codex 陪伴式备考系统，目标是通过软考系统架构设计师考试，并沉淀真正的架构判断能力。

当前实现位于 `ruankao-agent/`。

## 包含什么

- 高层设计文档和中文总览。
- TDD 测试与验收契约。
- 本地 `architect-thinking` skill 种子。
- SQLite 训练状态与排程。
- Obsidian vault 生成与同步。
- 本地网页工作台。
- 学习台与静态 HTML 总图。
- RAG 记忆与进步控制简报。
- NotebookLM 外部研究源元数据。
- 已搬入的上游 skill 参考。

## 日常使用

优先打开本地工作台：

```sh
./start-workbench.command
```

如果 8765 端口被占用，启动脚本会自动改用下一个可用端口；也可以临时指定起始端口：

```sh
RUANKAO_WORKBENCH_PORT=8770 ./start-workbench.command
```

然后在浏览器里完成今日闭环、复习评分、练习记录、学习回合、三源材料、记忆卡、
原则网络、学习台和 Obsidian vault 同步。在 Codex 里，`/ruankao-workbench`
会启动同一个工作台。

任何学习台、工作台、总图或网页表单的用户体验改动，都必须用 browser-act 打开本地页面
实际体验，不能只靠源码阅读或单元测试。

常用 Codex 命令：

```text
/ruankao-daily-cycle 2026-06-29
/ruankao-daily-close 2026-06-29
/ruankao-night-evolve 2026-06-29
/ruankao-architect-review <question-or-draft>
/ruankao-study-mode <topic-or-front>
/ruankao-ux-check <page-or-flow>
/ruankao-rag-query <query-or-front>
```

每日闭环会依次运行 Cheko 弱点入队、核心原则入队、日结回执、三题型覆盖图、
RAG 记忆与进步控制简报、仅暂存夜间进化草案、记忆卡 Obsidian 同步、
Mein/Du/Uns 三源材料同步，以及本地 JSON 状态导出。

学习模式是一问一答的苏格拉底式对话：学习者答案进入 Mein，Codex 的复述、纠偏、
结构化和追问进入 Du。夜间进化默认只生成暂存草案，不直接改 live skill 或学习规则。

定时夜间运行见 `ruankao-agent/docs/AUTOMATION.md`。

## 不提交什么

本地 `resources/` 目录用于存放考试 PDF 和生成资料。它默认被 git 忽略，除非明确审查，
否则不上传。

## 快速检查

```sh
cd ruankao-agent
python3 -m pytest
```

## 演示初始化

```sh
cd ruankao-agent
python3 -m ruankao_agent.cli init --root /tmp/ruankao-agent-demo --as-of 2026-06-29
python3 -m ruankao_agent.cli status --root /tmp/ruankao-agent-demo --as-of 2026-06-29
python3 -m ruankao_agent.cli web --root /tmp/ruankao-agent-demo --open
```
