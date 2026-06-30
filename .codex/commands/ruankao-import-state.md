---
description: 从 export-state JSON 快照重建软考达人 SQLite 状态库。
argument-hint: <exports/state-YYYY-MM-DD.json>
---

从本地纯文本状态快照恢复 SQLite。该命令用于 AC-4 双轨容灾验收：
写入动作会先生成 `data/backups/ruankao.db.bak.[1-7]` 滚动二进制备份；
当 live DB 缺失或损坏时，用 export-state JSON 在 5 秒内重建状态库。

默认执行：

```sh
cd /Users/pedan/Documents/ruankao/ruankao-agent
python3 -m ruankao_agent.cli import-state \
  --file /Users/pedan/Documents/ruankao/ruankao-agent/exports/state-YYYY-MM-DD.json
```

行为约束：

- 快照路径在 `exports/` 下时，自动推断根目录为其上一级目录。
- 只按现有表结构重建 `data/ruankao.db`，不修改 SQLite schema。
- 重建前如果 live DB 仍存在，会先尝试写入当天滚动二进制备份。
- 恢复后用 `status`、`export-state` 或 SQLite 读回校验卡片、练习、复习和三源材料。
