from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class HomePageView:
    message: str
    root: Path
    vault_path: Path
    today: date
    page_title: str
    snapshot: Any
    records: Sequence[Any]
    cards: Sequence[Any]
    due_cards: Sequence[Any]
    active_diagnostics: Sequence[Any]
    cheko_cards: Sequence[Any]
    cheko_due_cards: Sequence[Any]
    principle_cards: Sequence[Any]
    practice_sessions: Sequence[Any]
    rag_brief: dict[str, object]
    primary_action: str
    primary_reason: str
    front_overview: Sequence[Any]
    receipt_link: str
    evolution_link: str
    route_link: str
    rag_link: str
    export_link: str
    rag_query: str
