---
description: 软考达人完整日循环：入队、日结、路线图、夜间草案。
argument-hint: [YYYY-MM-DD]
---

在这个仓库中运行完整软考达人日循环。

默认日期使用今天；如果用户提供 `$ARGUMENTS`，把它当成 `YYYY-MM-DD`。

默认执行：

```sh
cd /Users/pedan/Documents/ruankao
./run-daily-cycle.command <YYYY-MM-DD>
```

该操作会依次运行 Cheko 入队、核心原则入队、日结回执、三题型覆盖图、
stage-only 夜间进化草案、记忆卡 Obsidian 同步、三源材料 Obsidian 同步，
以及本地状态 JSON 导出。
