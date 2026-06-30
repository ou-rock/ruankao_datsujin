# 用户体验实测协议

## 硬规则

涉及学习台、工作台、总图或网页表单的改动，必须用 browser-act 实际体验。不能只靠源码阅读、
截图猜测或单元测试判断用户体验。

## 默认流程

1. 刷新被跟踪的学习台页面：

```sh
cd /Users/pedan/Documents/ruankao/ruankao-agent
python3 -m ruankao_agent.cli learning --root /Users/pedan/Documents/ruankao/ruankao-agent --overwrite
```

2. 启动本地工作台：

```sh
python3 -m ruankao_agent.cli web --root /Users/pedan/Documents/ruankao/ruankao-agent --host 127.0.0.1 --port 8765
```

3. 用 browser-act 复用当前 Chrome 会话打开页面，至少执行 `state`、关键点击和一次返回路径。

4. 记录访问路径、点击路径、发现的问题、修复动作和复测结果。

5. 关闭 browser-act session，并停止本地工作台进程。

## 禁止事项

- 不在未确认的情况下提交真实表单或消耗外部服务算力。
- 不把 browser-act 输出里的私人页面内容直接提交到仓库。
- 不用单元测试通过替代真实浏览体验。
