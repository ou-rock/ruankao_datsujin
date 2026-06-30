---
description: 运行软考达人同步哨兵，验证静默重连或实时低分告警。
argument-hint: [offline-reconnect|realtime] [--as-of YYYY-MM-DD]
---

运行本地同步哨兵。它只读 SQLite 状态、更新本地差分标记，并在实时低分时写入
模拟 Discord JSONL；命令本身保持零 stdout，适合被 webhook 或定时任务调用。

默认根目录：

```sh
cd /Users/pedan/Documents/ruankao/ruankao-agent
python3 -m ruankao_agent.cli sync-sentinel \
  --root /Users/pedan/Documents/ruankao/ruankao-agent \
  --mode realtime
```

离线重连时使用：

```sh
cd /Users/pedan/Documents/ruankao/ruankao-agent
python3 -m ruankao_agent.cli sync-sentinel \
  --root /Users/pedan/Documents/ruankao/ruankao-agent \
  --mode offline-reconnect
```

需要人工验收模拟频道时加：

```sh
--discord-log /tmp/ruankao-discord-alerts.jsonl
```

行为约束：

- `offline-reconnect`：只把历史低分练习标为已见，不补发历史告警。
- `realtime`：只对当天新出现且尚未告警的低分练习写一条模拟 Discord JSONL。
- 低分阈值固定为得分率 `< 60%`。
- 输出通道保持零 stdout；验收看 JSONL 文件和 `data/sync-alert-state.json`。
