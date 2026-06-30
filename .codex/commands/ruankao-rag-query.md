---
description: 生成软考达人 RAG 记忆与进步控制简报。
argument-hint: [查询文本] [--front choice|case|essay]
---

用本地 SQLite 里的三源材料、记忆卡、复习日志和练习记录生成 RAG 控制简报。
这个操作不调用外部向量库；SQLite 仍是唯一事实源。

默认执行：

```sh
cd /Users/pedan/Documents/ruankao/ruankao-agent
python3 -m ruankao_agent.cli rag-query \
  --root /Users/pedan/Documents/ruankao/ruankao-agent \
  --query "今天如何用记忆、错因和三题型进步信号安排学习？"
```

如果 `$ARGUMENTS` 指定主题或题型，追加到 `--query` 或 `--front`。
输出包括召回证据、进步闸门、建议动作和回答契约。
