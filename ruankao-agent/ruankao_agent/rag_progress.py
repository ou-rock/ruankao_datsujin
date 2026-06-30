from __future__ import annotations

from collections.abc import Sequence

from .rag_progress_gates import build_progress_gates
from .rag_types import ProgressGate, RagHit


def recommend_rag_action(hits: Sequence[RagHit], gates: Sequence[ProgressGate]) -> str:
    if gates:
        gate = gates[0]
        return f"先处理「{gate.title}」：{gate.action}"
    if hits:
        hit = hits[0]
        return f"围绕「{hit.document.title}」开启学习回合：先闭卷回答，再沉淀 Mein/Du。"
    return "先录入一条三源材料或创建一张基础记忆卡，让 RAG 有可召回证据。"
