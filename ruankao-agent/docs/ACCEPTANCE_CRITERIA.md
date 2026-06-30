# 验收标准

## 必须能运行的命令

在 `ruankao-agent/` 目录下必须能运行：

```sh
python3 -m pytest
python3 -m ruankao_agent.cli init --root /tmp/ruankao-agent-demo
python3 -m ruankao_agent.cli status --root /tmp/ruankao-agent-demo
python3 -m ruankao_agent.cli dashboard --root /tmp/ruankao-agent-demo
```

## 必须生成的产物

`init` 命令必须创建：

- `data/ruankao.db`
- `dashboard.html`
- `vault/00-map/战役总图.md`
- `vault/00-map/原则网络.md`
- `vault/10-memory-war-room/principles/场景先于方案.md`

## 总图必须展示的内容

`dashboard.html` 必须包含：

- 系统架构设计师考试目标。
- 考试日期。
- 倒计时。
- 当前战役阶段。
- 主战与冗余状态。
- 风险灯。
- 记忆作战室。
- Mein、Du、Uns。
- 选择题、案例题、论文题路线。
- NotebookLM 外部研究源名称。

## 必须保持的数据行为

- 原始材料必须保留来源身份。
- 记忆卡必须保留卡片类型。
- 原则关系必须保留关系类型和方向。
- 风险规则必须是确定性的。
- 生成的 Obsidian 链接必须使用 `[[...]]`。

## 必须留下的过程证据

完成时必须留下：

- 3 个实现 agent 的证据。
- 3 个关键审查 agent 的证据。
- 3 个验收测试 agent 的证据。
- 集成后的通过测试记录。
