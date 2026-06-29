---
description: 生成或刷新软考达人学习台 HTML 资料。
argument-hint: [--overwrite]
---

在这个仓库中生成软考达人学习台资料。

默认执行：

```sh
cd /Users/pedan/Documents/ruankao/ruankao-agent
python3 -m ruankao_agent.cli learning --root /Users/pedan/Documents/ruankao/ruankao-agent
```

如果用户提供 `$ARGUMENTS`，按参数决定是否追加 `--overwrite`。
