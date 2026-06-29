---
description: 软考达人日结：Cheko 弱点入队并生成今日回执。
argument-hint: [YYYY-MM-DD]
---

在这个仓库中完成软考达人每日收口动作。

默认日期使用今天；如果用户提供 `$ARGUMENTS`，把它当成 `YYYY-MM-DD`。

默认执行：

```sh
cd /Users/pedan/Documents/ruankao/ruankao-agent
python3 -m ruankao_agent.cli cheko-seed-cards --root /Users/pedan/Documents/ruankao/ruankao-agent --next-due <YYYY-MM-DD>
python3 -m ruankao_agent.cli daily-receipt --root /Users/pedan/Documents/ruankao/ruankao-agent --as-of <YYYY-MM-DD>
```

完成后报告生成的 HTML/JSON 路径，以及 Cheko 入队创建/跳过数量。
