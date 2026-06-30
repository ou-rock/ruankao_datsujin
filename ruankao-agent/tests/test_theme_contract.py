from __future__ import annotations

from datetime import date

from ruankao_agent.dashboard import DashboardSnapshot, render_dashboard
from ruankao_agent.domain import Campaign, RiskStatus
from ruankao_agent.evolution import render_night_evolution_plan
from ruankao_agent.learning_layout import render_learning_page
from ruankao_agent.rag_report import render_rag_brief
from ruankao_agent.receipts import write_daily_receipt
from ruankao_agent.route_map_render import render_route_map
from ruankao_agent.web import WorkbenchApp, WorkbenchConfig


def test_main_frontend_surfaces_expose_dark_mode_contract(tmp_path) -> None:
    app = WorkbenchApp(WorkbenchConfig(root=tmp_path / "demo", as_of=date(2026, 6, 29)))
    campaign = Campaign.default()

    pages = [
        app.render_home(),
        render_learning_page("学习台", "<h1>学习台</h1>"),
        render_dashboard(
            DashboardSnapshot(
                campaign=campaign,
                as_of=date(2026, 6, 29),
                risk=RiskStatus.GREEN,
                notebook_name="System Architecture Designer Exam Questions and Analysis",
                due_cards=0,
                review_backlog_ratio=0,
            )
        ),
        write_daily_receipt(tmp_path / "receipt", as_of=date(2026, 6, 29)).html_path.read_text(
            encoding="utf-8"
        ),
        render_night_evolution_plan(
            {
                "as_of": "2026-06-29",
                "stage_only": True,
                "receipt_json": "data/daily-receipts/2026-06-29.json",
                "night_focus": {},
                "actions": [],
            }
        ),
        render_route_map({"as_of": "2026-06-29", "routes": []}),
        render_rag_brief(
            {
                "as_of": "2026-06-29",
                "query": "高并发 备用机制 响应度量",
                "recommended_action": "先做一次召回复盘。",
                "retrieval_strategy": "sqlite-fts5-hybrid-progress",
                "corpus_size": 0,
                "chunk_count": 0,
                "observability": {},
                "progress_gates": [],
                "hits": [],
                "answer_contract": [],
            }
        ),
    ]

    for html in pages:
        assert 'data-theme-toggle' in html
        assert 'aria-pressed="false"' in html
        assert '"ruankao-theme"' in html
        assert ':root[data-theme="dark"]' in html
        assert "color-scheme: dark" in html
