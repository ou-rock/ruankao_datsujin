---
description: 软考达人夜间进化：基于日结生成仅暂存草案。
argument-hint: [YYYY-MM-DD]
---

在这个仓库中生成软考达人夜间进化草案。

默认日期使用今天；如果用户提供 `$ARGUMENTS`，把它当成 `YYYY-MM-DD`。

默认执行：

```sh
cd /Users/pedan/Documents/ruankao/ruankao-agent
python3 -m ruankao_agent.cli night-evolve --root /Users/pedan/Documents/ruankao/ruankao-agent --as-of <YYYY-MM-DD>
```

该命令只生成暂存计划，不直接修改正在使用的 skill、核心原则或学习规则。
