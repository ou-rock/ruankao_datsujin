# 自动化闭环

这个项目把定时任务保持为显式操作：仓库提供 `launchd` 模板，但不会自动安装。
这样可以先确认本地路径、日志目录和执行时间，再决定是否交给系统每天运行。

## 每日闭环

手动指定日期运行：

```sh
cd /Users/pedan/Documents/ruankao
./run-daily-cycle.command 2026-06-29
```

不传日期时，默认使用今天：

```sh
cd /Users/pedan/Documents/ruankao
./run-daily-cycle.command
```

闭环会依次完成这些动作：

- 导入 Cheko 弱区信号，生成可复习的记忆卡。
- 种入七条核心原则，补齐原则记忆底座。
- 生成当天日结回执。
- 生成选择题、案例题、论文题三题型路线图。
- 生成 RAG 记忆与进步控制简报。
- 生成仅暂存的夜间进化计划。
- 同步记忆卡到 Obsidian。
- 同步 Mein / Du / Uns 三源材料到 Obsidian。
- 导出本地状态快照到 `ruankao-agent/exports/`。

## launchd 模板

模板位置：

```text
automation/launchd/com.pedan.ruankao.daily-cycle.plist
```

手动安装：

```sh
mkdir -p /Users/pedan/Documents/ruankao/ruankao-agent/logs
cp /Users/pedan/Documents/ruankao/automation/launchd/com.pedan.ruankao.daily-cycle.plist \
  ~/Library/LaunchAgents/com.pedan.ruankao.daily-cycle.plist
launchctl load -w ~/Library/LaunchAgents/com.pedan.ruankao.daily-cycle.plist
```

停止定时任务：

```sh
launchctl unload -w ~/Library/LaunchAgents/com.pedan.ruankao.daily-cycle.plist
```

模板会在本地时间 23:30 运行，并把日志写入 `ruankao-agent/logs/`。这个目录已被
git 忽略，可以长期保留本地运行记录。
