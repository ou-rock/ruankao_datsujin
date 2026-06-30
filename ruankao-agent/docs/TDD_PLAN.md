# TDD 计划

## Red：先写会失败的测试

实现前先为设计契约写测试：

- 战役倒计时与阶段。
- 风险规则。
- Mein/Du/Uns 持久化。
- 记忆卡类型与排程。
- 原则图谱关系。
- Obsidian vault 生成。
- dashboard 生成。
- NotebookLM 元数据表达。
- CLI 冒烟流程。

## Green：实现最小闭环

实现一个最小但自洽的本地系统：

- 标准库 Python。
- 通过 `sqlite3` 使用 SQLite。
- 生成静态 HTML。
- 为 Obsidian 生成 Markdown 文件。
- 单元测试不依赖实时 NotebookLM 网络。

## Refactor：通过后再收紧

测试通过后：

- 移除存储仓储里的重复。
- 收紧模块边界。
- 只在行为不明显处添加 docstring。
- 保持生成文件可预测、可重复。

## Agent 波次规则

- 第一轮最多 3 个实现 agent。
- 每个 agent 拥有互不重叠的写入范围。
- 任何 agent 不得回滚其他 agent 的工作。
- 每个 agent 都要返回变更文件和验证命令。
- 中央集成必须重新运行完整测试套件。
