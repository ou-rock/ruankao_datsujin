#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_ROOT="$ROOT_DIR/ruankao-agent"
DAY="${1:-$(date +%F)}"

cd "$AGENT_ROOT"

step() {
  print ""
  print "== $1 =="
}

print "软考达人每日闭环：$DAY"

step "1/9 Cheko 弱点入队"
python3 -m ruankao_agent.cli cheko-seed-cards \
  --root "$AGENT_ROOT" \
  --next-due "$DAY"

step "2/9 核心原则入队"
python3 -m ruankao_agent.cli seed-principles \
  --root "$AGENT_ROOT" \
  --next-due "$DAY"

step "3/9 生成日结回执"
python3 -m ruankao_agent.cli daily-receipt \
  --root "$AGENT_ROOT" \
  --as-of "$DAY"

step "4/9 生成三题型覆盖图"
python3 -m ruankao_agent.cli route-map \
  --root "$AGENT_ROOT" \
  --as-of "$DAY"

step "5/9 生成 RAG 控制简报"
python3 -m ruankao_agent.cli rag-query \
  --root "$AGENT_ROOT" \
  --query "今天如何用记忆、错因和三题型进步信号安排学习？" \
  --as-of "$DAY"

step "6/9 生成夜间进化草案"
python3 -m ruankao_agent.cli night-evolve \
  --root "$AGENT_ROOT" \
  --as-of "$DAY"

step "7/9 同步记忆卡到 Obsidian"
python3 -m ruankao_agent.cli vault-sync \
  --root "$AGENT_ROOT"

step "8/9 同步三源材料到 Obsidian"
python3 -m ruankao_agent.cli raw-vault-sync \
  --root "$AGENT_ROOT"

step "9/9 导出本地状态"
python3 -m ruankao_agent.cli export-state \
  --root "$AGENT_ROOT" \
  --as-of "$DAY"

print ""
print "每日闭环完成：$DAY"
