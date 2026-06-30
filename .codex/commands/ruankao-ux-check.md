---
description: 用 browser-act 实测软考达人网页用户体验。
argument-hint: [页面/流程，例如 learning today study-turn]
---

对软考达人工作台、学习台、总图或网页表单做用户体验验收。这个操作必须使用
browser-act 实际打开本地页面，不能只靠源码阅读、截图猜测或单元测试。

默认先刷新学习台静态页面：

```sh
cd /Users/pedan/Documents/ruankao/ruankao-agent
python3 -m ruankao_agent.cli learning --root /Users/pedan/Documents/ruankao/ruankao-agent --overwrite
```

然后启动本地工作台：

```sh
cd /Users/pedan/Documents/ruankao/ruankao-agent
python3 -m ruankao_agent.cli web --root /Users/pedan/Documents/ruankao/ruankao-agent --host 127.0.0.1 --port 8765
```

再用 browser-act 复用当前 Chrome 会话打开 `http://127.0.0.1:8765/`，执行 `wait stable`、
`state`、关键点击和返回路径。优先按 `$ARGUMENTS` 指定的页面或流程检查，例如学习台、
今日三任务、学习回合、记忆卡或原则网络。

必须记录：

- 访问路径。
- 点击路径。
- 发现的问题。
- 修复动作。
- 复测结果。

收尾时关闭 browser-act session，并停止本地工作台进程。
