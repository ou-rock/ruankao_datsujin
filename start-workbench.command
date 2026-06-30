#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT="${RUANKAO_WORKBENCH_PORT:-8765}"

print "软考达人工作台"
print "地址：http://127.0.0.1:$PORT"
print "按 Ctrl-C 停止。"

cd "$ROOT_DIR/ruankao-agent"

python3 -m ruankao_agent.cli web \
  --root "$ROOT_DIR/ruankao-agent" \
  --host 127.0.0.1 \
  --port "$PORT" \
  --open
