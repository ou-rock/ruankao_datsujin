---
description: 打开软考达人工作台本地网页。
argument-hint: [--port 8765] [--as-of YYYY-MM-DD]
---

在这个仓库中启动软考达人工作台本地网页。

默认执行：

```sh
cd /Users/pedan/Documents/ruankao/ruankao-agent
python3 -m ruankao_agent.cli web --root /Users/pedan/Documents/ruankao/ruankao-agent --host 127.0.0.1 --port 8765 --open
```

默认本地地址是 `http://127.0.0.1:8765`。如果端口占用，工作台会自动改用下一个可用端口。
也可以显式换端口，例如 `/ruankao-workbench --port 8770`；如果用户提供了日期参数，
用 `$ARGUMENTS` 覆盖端口或日期。
