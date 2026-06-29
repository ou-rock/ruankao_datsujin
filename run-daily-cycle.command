#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_ROOT="$ROOT_DIR/ruankao-agent"
DAY="${1:-$(date +%F)}"

cd "$AGENT_ROOT"

python3 -m ruankao_agent.cli cheko-seed-cards \
  --root "$AGENT_ROOT" \
  --next-due "$DAY"

python3 -m ruankao_agent.cli daily-receipt \
  --root "$AGENT_ROOT" \
  --as-of "$DAY"

python3 -m ruankao_agent.cli route-map \
  --root "$AGENT_ROOT" \
  --as-of "$DAY"

python3 -m ruankao_agent.cli night-evolve \
  --root "$AGENT_ROOT" \
  --as-of "$DAY"

python3 -m ruankao_agent.cli vault-sync \
  --root "$AGENT_ROOT"

python3 -m ruankao_agent.cli raw-vault-sync \
  --root "$AGENT_ROOT"
