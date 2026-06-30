---
description: 用 Hermes 语义输入规整层解析散装打卡或降级沉淀 Mein/raw。
argument-hint: [散装输入文本]
---

把一段自然语言输入交给本地语义规整中间件。

默认执行：

```sh
cd /Users/pedan/Documents/ruankao/ruankao-agent
python3 -m ruankao_agent.cli semantic-ingest \
  --root /Users/pedan/Documents/ruankao/ruankao-agent \
  --text "$ARGUMENTS"
```

如果输入能被物理校验为练习打卡，写入 `practice_sessions` 并输出 JSON。
如果只是日常碎片或低置信输入，自动降级为 `SourceIdentity.MEIN` 的
`promotion_status="raw"` 三源材料，供 RAG 进步闸门后续处理。
如果输入带打卡意图但缺少题型或分数，返回 `rejected`，不写入 SQLite。

验收样例：

```sh
python3 -m ruankao_agent.cli semantic-ingest \
  --root /tmp/ruankao-semantic-ingest \
  --text "打卡案例题，灾备响应度理得了 12.5 分，满分 15"
```
