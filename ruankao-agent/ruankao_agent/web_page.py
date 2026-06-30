from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path
from typing import Any

from .domain import CardType
from .evolution import night_evolution_html_path
from .export_state import state_export_path
from .memory import diagnose_memory
from .rag import (
    DEFAULT_RAG_QUERY,
    build_rag_brief,
    rag_brief_html_path,
    rag_brief_to_payload,
)
from .receipts import daily_receipt_html_path
from .route_map import route_map_html_path
from .web_page_sections import HomePageView, render_home_shell
from .web_render import (
    _front_overview,
    _risk_label,
    _today_primary_action,
    _today_primary_reason,
)


@dataclass(frozen=True, slots=True)
class WorkbenchPageContext:
    root: Path
    vault_path: Path
    today: date
    initialize: Callable[[], None]
    store: Callable[[], Any]
    snapshot: Callable[[], Any]


def render_home_page(context: WorkbenchPageContext, message: str = "") -> str:
    context.initialize()
    store = context.store()
    records = store.list_raw_records()
    cards = store.list_memory_cards()
    practice_sessions = store.list_practice_sessions()
    review_logs = store.list_review_logs()
    snapshot = context.snapshot()
    due_cards = [card for card in cards if card.next_due is not None and card.next_due <= context.today]
    diagnostics = diagnose_memory(cards, review_logs, as_of=context.today)
    active_diagnostics = [
        diagnostic for diagnostic in diagnostics if diagnostic.status != "stable"
    ][:5]
    cheko_cards = [card for card in cards if card.title.startswith("Cheko")]
    cheko_due_cards = [
        card for card in cheko_cards if card.next_due is not None and card.next_due <= context.today
    ]
    principle_cards = [card for card in cards if card.card_type is CardType.PRINCIPLE]
    receipt_path = daily_receipt_html_path(context.root, context.today)
    receipt_link = (
        f'<a class="button secondary" href="/reports/daily/{escape(context.today.isoformat())}.html">打开今日日结</a>'
        if receipt_path.exists()
        else ""
    )
    evolution_path = night_evolution_html_path(context.root, context.today)
    evolution_link = (
        f'<a class="button secondary" href="/reports/nightly/{escape(context.today.isoformat())}.html">打开夜间草案</a>'
        if evolution_path.exists()
        else ""
    )
    route_path = route_map_html_path(context.root, context.today)
    route_link = (
        f'<a class="button secondary" href="/reports/routes/{escape(context.today.isoformat())}.html">打开三题型覆盖图</a>'
        if route_path.exists()
        else ""
    )
    rag_path = rag_brief_html_path(context.root, context.today)
    rag_link = (
        f'<a class="button secondary" href="/reports/rag/{escape(context.today.isoformat())}.html">打开 RAG 控制简报</a>'
        if rag_path.exists()
        else ""
    )
    export_path = state_export_path(context.root, context.today)
    export_link = (
        f'<a class="button secondary" href="/exports/state-{escape(context.today.isoformat())}.json">打开本地状态导出</a>'
        if export_path.exists()
        else ""
    )
    rag_brief = rag_brief_to_payload(
        build_rag_brief(store, query=DEFAULT_RAG_QUERY, as_of=context.today, limit=4)
    )
    primary_action = _today_primary_action(
        due_cards=due_cards,
        diagnostics=active_diagnostics,
        practice_sessions=practice_sessions,
    )
    primary_reason = _today_primary_reason(snapshot.risk_reasons, due_cards)
    front_overview = _front_overview(cards, due_cards, practice_sessions, context.today)
    page_title = f"软考达人工作台 · {snapshot.countdown} · {_risk_label(snapshot.risk_text)}"

    view = HomePageView(
        message=message,
        root=context.root,
        vault_path=context.vault_path,
        today=context.today,
        page_title=page_title,
        snapshot=snapshot,
        records=records,
        cards=cards,
        due_cards=due_cards,
        active_diagnostics=active_diagnostics,
        cheko_cards=cheko_cards,
        cheko_due_cards=cheko_due_cards,
        principle_cards=principle_cards,
        practice_sessions=practice_sessions,
        rag_brief=rag_brief,
        primary_action=primary_action,
        primary_reason=primary_reason,
        front_overview=front_overview,
        receipt_link=receipt_link,
        evolution_link=evolution_link,
        route_link=route_link,
        rag_link=rag_link,
        export_link=export_link,
        rag_query=DEFAULT_RAG_QUERY,
    )
    return render_home_shell(view)

