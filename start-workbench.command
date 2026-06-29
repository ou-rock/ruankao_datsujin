#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR/ruankao-agent"

python3 -m ruankao_agent.cli web \
  --root "$ROOT_DIR/ruankao-agent" \
  --host 127.0.0.1 \
  --port 8765 \
  --open
