from __future__ import annotations

from datetime import date
from pathlib import Path


def rag_observability_payload(root: Path | str | None, as_of: date) -> dict[str, object]:
    day = as_of.isoformat()
    return {
        "trace": [
            {
                "label": "问题输入",
                "detail": "query 和题型过滤确定本轮检索意图。",
            },
            {
                "label": "语料切块",
                "detail": "三源材料、记忆卡和练习记录被拆成可追溯 chunk。",
            },
            {
                "label": "FTS5/BM25",
                "detail": "每次查询临时建立 SQLite FTS5 索引，得到词法命中分。",
            },
            {
                "label": "混合重排",
                "detail": "BM25、词项、题型、短语、状态和进步权重共同排序。",
            },
            {
                "label": "进步闸门",
                "detail": "反复低分、到期复习、题型缺口和低分练习优先进入行动建议。",
            },
        ],
        "storage": [
            {
                "label": "SQLite 事实源",
                "detail": _path_detail(root, "data/ruankao.db", "三源材料、记忆卡、复习日志和练习记录。"),
            },
            {
                "label": "HTML 简报",
                "detail": _path_detail(root, f"reports/rag/{day}.html", "给学习者看的控制报告。"),
            },
            {
                "label": "JSON 明细",
                "detail": _path_detail(root, f"data/rag/{day}.json", "给自动化、日结和后续分析读取。"),
            },
            {
                "label": "临时索引",
                "detail": "SQLite FTS5 索引按查询即时构建，不作为第二事实源长期保存。",
            },
        ],
        "backend_policy": [
            {
                "label": "为什么先用 SQLite FTS",
                "detail": "当前资料规模和考试语境更需要本地、可审计、零服务依赖和分数可解释。",
            },
            {
                "label": "为什么暂不引入向量库",
                "detail": "embedding、向量数据库和同步索引服务会增加事实源分叉、同步失败和不可解释排序成本。",
            },
            {
                "label": "后续如何升级",
                "detail": "向量召回可以作为可插拔后端加入，但 SQLite 仍保留事实源和进步控制。",
            },
        ],
    }


def _path_detail(root: Path | str | None, relative_path: str, description: str) -> str:
    if root is None:
        return f"{relative_path}：{description}"
    return f"{Path(root) / relative_path}：{description}"
