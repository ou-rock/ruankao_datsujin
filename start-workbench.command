#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT="${RUANKAO_WORKBENCH_PORT:-8765}"

print "软考达人工作台"
print "正在从 127.0.0.1:$PORT 启动；如果端口占用，会自动改用下一个可用端口。"

cd "$ROOT_DIR/ruankao-agent"

python3 -m ruankao_agent.cli web \
  --root "$ROOT_DIR/ruankao-agent" \
  --host 127.0.0.1 \
  --port "$PORT" \
  --open
