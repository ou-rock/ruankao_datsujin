from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .dashboard import render_dashboard
from .loop import build_daily_loop_snapshot, status_line
from .storage import RuankaoStore
from .web_actions import (
    WorkbenchActionContext,
    add_memory_card as add_memory_card_action,
    add_practice_session as add_practice_session_action,
    add_principle_relation as add_principle_relation_action,
    add_raw_record as add_raw_record_action,
    capture_study_turn as capture_study_turn_action,
    record_review as record_review_action,
    seed_cheko_cards as seed_cheko_cards_action,
    sync_memory_cards_to_vault_action,
    sync_raw_records_to_vault_action,
    write_daily_receipt_action,
    write_night_evolution_plan_action,
    write_rag_brief_action,
    write_route_map_action,
    write_state_export_action,
)
from .web_bootstrap import WorkbenchBootstrapContext, initialize_workbench
from .web_files import (
    WorkbenchFileContext,
    render_dashboard_page as render_dashboard_page_file,
    render_export_file as render_export_file_content,
    render_learning_file as render_learning_file_content,
    render_report_file as render_report_file_content,
    safe_export_file,
    safe_learning_file,
    safe_report_file,
)
from .web_forms import (
    FormData,
)
from .web_page import WorkbenchPageContext, render_home_page


@dataclass(frozen=True, slots=True)
class WorkbenchConfig:
    root: Path
    as_of: date | None = None


class WorkbenchApp:
    def __init__(self, config: WorkbenchConfig) -> None:
        self.config = config

    @property
    def root(self) -> Path:
        return self.config.root

    @property
    def db_path(self) -> Path:
        return self.root / "data" / "ruankao.db"

    @property
    def vault_path(self) -> Path:
        return self.root / "vault"

    @property
    def learning_path(self) -> Path:
        return self.root / "learning"

    @property
    def reports_path(self) -> Path:
        return self.root / "reports"

    @property
    def exports_path(self) -> Path:
        return self.root / "exports"

    @property
    def today(self) -> date:
        return self.config.as_of or date.today()

    def initialize(self) -> None:
        initialize_workbench(
            WorkbenchBootstrapContext(
                root=self.root,
                vault_path=self.vault_path,
                store=self.store,
                write_dashboard=self.write_dashboard,
            )
        )

    def store(self) -> RuankaoStore:
        return RuankaoStore(self.db_path)

    def snapshot(self):
        store = self.store()
        store.initialize()
        return build_daily_loop_snapshot(
            as_of=self.today,
            due_cards=store.count_due_cards(self.today),
            review_backlog_ratio=store.review_backlog_ratio(self.today),
            practice_sessions=store.list_practice_sessions(),
        )

    def write_dashboard(self) -> Path:
        snapshot = self.snapshot()
        dashboard_path = self.root / "dashboard.html"
        dashboard_path.write_text(render_dashboard(snapshot.dashboard), encoding="utf-8")
        return dashboard_path

    def _action_context(self) -> WorkbenchActionContext:
        return WorkbenchActionContext(
            root=self.root,
            vault_path=self.vault_path,
            today=self.today,
            store=self.store,
            write_dashboard=self.write_dashboard,
        )

    def _file_context(self) -> WorkbenchFileContext:
        return WorkbenchFileContext(
            root=self.root,
            learning_path=self.learning_path,
            reports_path=self.reports_path,
            exports_path=self.exports_path,
            initialize=self.initialize,
        )

    def _page_context(self) -> WorkbenchPageContext:
        return WorkbenchPageContext(
            root=self.root,
            vault_path=self.vault_path,
            today=self.today,
            initialize=self.initialize,
            store=self.store,
            snapshot=self.snapshot,
        )

    def add_raw_record(self, form: FormData) -> int:
        return add_raw_record_action(self._action_context(), form)

    def add_memory_card(self, form: FormData) -> int:
        return add_memory_card_action(self._action_context(), form)

    def add_principle_relation(self, form: FormData) -> int:
        return add_principle_relation_action(self._action_context(), form)

    def add_practice_session(self, form: FormData) -> int:
        return add_practice_session_action(self._action_context(), form)

    def capture_study_turn(self, form: FormData):
        return capture_study_turn_action(self._action_context(), form)

    def record_review(self, form: FormData) -> None:
        return record_review_action(self._action_context(), form)

    def seed_cheko_cards(self, form: FormData):
        return seed_cheko_cards_action(self._action_context(), form)

    def write_daily_receipt(self, form: FormData):
        return write_daily_receipt_action(self._action_context(), form)

    def write_night_evolution_plan(self, form: FormData):
        return write_night_evolution_plan_action(self._action_context(), form)

    def write_route_map(self, form: FormData):
        return write_route_map_action(self._action_context(), form)

    def write_rag_brief(self, form: FormData):
        return write_rag_brief_action(self._action_context(), form)

    def write_state_export(self, form: FormData):
        return write_state_export_action(self._action_context(), form)

    def sync_memory_cards_to_vault(self, form: FormData):
        return sync_memory_cards_to_vault_action(self._action_context(), form)

    def sync_raw_records_to_vault(self, form: FormData):
        return sync_raw_records_to_vault_action(self._action_context(), form)

    def render_home(self, message: str = "") -> str:
        return render_home_page(self._page_context(), message)

    def render_dashboard_page(self) -> str:
        return render_dashboard_page_file(self._file_context())

    def render_learning_file(self, relative: str = "index.html") -> str:
        return render_learning_file_content(self._file_context(), relative)

    def render_report_file(self, relative: str) -> str:
        return render_report_file_content(self._file_context(), relative)

    def render_export_file(self, relative: str) -> str:
        return render_export_file_content(self._file_context(), relative)

    def _safe_learning_file(self, relative: str) -> Path:
        return safe_learning_file(self._file_context(), relative)

    def _safe_report_file(self, relative: str) -> Path:
        return safe_report_file(self._file_context(), relative)

    def _safe_export_file(self, relative: str) -> Path:
        return safe_export_file(self._file_context(), relative)

    def render_status_json(self) -> str:
        snapshot = self.snapshot()
        payload = {
            "status": status_line(snapshot),
            "phase": snapshot.phase_name,
            "countdown": snapshot.countdown,
            "risk": snapshot.risk_text,
            "risk_reasons": list(snapshot.risk_reasons),
            "due_cards": snapshot.dashboard.due_cards,
            "review_backlog_ratio": snapshot.dashboard.review_backlog_ratio,
            "root": str(self.root),
            "vault": str(self.vault_path),
            "learning": str(self.learning_path),
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)
