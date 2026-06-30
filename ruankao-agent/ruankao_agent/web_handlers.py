from __future__ import annotations

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Mapping
from urllib.parse import parse_qs, unquote, urlparse

from .web_forms import one


def _handler_for(app):
    class WorkbenchHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/":
                query = parse_qs(parsed.query)
                self._send_html(app.render_home(message=one(query, "message")))
                return
            if parsed.path == "/dashboard.html":
                self._send_html(app.render_dashboard_page())
                return
            if parsed.path == "/api/status":
                self._send_text(app.render_status_json(), "application/json; charset=utf-8")
                return
            if parsed.path in ("/learning", "/learning/"):
                self._send_html(app.render_learning_file())
                return
            if parsed.path.startswith("/learning/"):
                self._send_learning_file(_learning_relative_path(parsed.path))
                return
            if parsed.path.startswith("/reports/"):
                self._send_report_file(_report_relative_path(parsed.path))
                return
            if parsed.path.startswith("/exports/"):
                self._send_export_file(_export_relative_path(parsed.path))
                return
            if parsed.path.startswith("/vault/"):
                self._send_vault_file(_vault_relative_path(parsed.path))
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

        def do_POST(self) -> None:
            form = self._read_form()
            try:
                if self.path == "/records":
                    record_id = app.add_raw_record(form)
                    self._redirect(f"/?message=raw-record-{record_id}-saved")
                    return
                if self.path == "/cards":
                    card_id = app.add_memory_card(form)
                    self._redirect(f"/?message=memory-card-{card_id}-saved")
                    return
                if self.path == "/relations":
                    relation_id = app.add_principle_relation(form)
                    self._redirect(f"/?message=principle-relation-{relation_id}-saved")
                    return
                if self.path == "/practice":
                    session_id = app.add_practice_session(form)
                    self._redirect(f"/?message=practice-session-{session_id}-saved")
                    return
                if self.path == "/study-turn":
                    result = app.capture_study_turn(form)
                    self._redirect(
                        f"/?message=study-turn-mein-{result.mein_record_id}"
                        f"-du-{result.du_record_id}-saved"
                    )
                    return
                if self.path == "/reviews":
                    app.record_review(form)
                    self._redirect("/?message=review-saved")
                    return
                if self.path == "/cheko/cards":
                    result = app.seed_cheko_cards(form)
                    self._redirect(
                        f"/?message=cheko-cards-created-{len(result.created_card_ids)}"
                        f"-skipped-{len(result.skipped_titles)}"
                    )
                    return
                if self.path == "/daily/receipt":
                    result = app.write_daily_receipt(form)
                    self._redirect(f"/?message=daily-receipt-{result.as_of.isoformat()}-written")
                    return
                if self.path == "/night/evolve":
                    result = app.write_night_evolution_plan(form)
                    self._redirect(
                        f"/?message=night-evolution-{result.as_of.isoformat()}"
                        f"-actions-{result.action_count}-staged"
                    )
                    return
                if self.path == "/routes/map":
                    result = app.write_route_map(form)
                    self._redirect(f"/?message=route-map-{result.as_of.isoformat()}-written")
                    return
                if self.path == "/rag/brief":
                    result = app.write_rag_brief(form)
                    self._redirect(f"/?message=rag-brief-{result.as_of.isoformat()}-written")
                    return
                if self.path == "/state/export":
                    result = app.write_state_export(form)
                    self._redirect(f"/?message=state-export-{result.as_of.isoformat()}-written")
                    return
                if self.path == "/vault/sync":
                    result = app.sync_memory_cards_to_vault(form)
                    self._redirect(
                        f"/?message=vault-sync-written-{len(result.written_paths)}"
                        f"-skipped-{len(result.skipped_paths)}"
                    )
                    return
                if self.path == "/vault/sync-raw":
                    result = app.sync_raw_records_to_vault(form)
                    self._redirect(
                        f"/?message=raw-vault-sync-written-{len(result.written_paths)}"
                        f"-skipped-{len(result.skipped_paths)}"
                    )
                    return
            except Exception as exc:  # pragma: no cover - exercised by real browser use.
                self.send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

        def log_message(self, format: str, *args: object) -> None:
            return

        def _read_form(self) -> Mapping[str, list[str]]:
            length = int(self.headers.get("Content-Length", "0"))
            payload = self.rfile.read(length).decode("utf-8")
            return parse_qs(payload, keep_blank_values=True)

        def _send_html(self, html: str) -> None:
            self._send_text(html, "text/html; charset=utf-8")

        def _send_text(self, text: str, content_type: str) -> None:
            encoded = text.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def _send_vault_file(self, relative: str) -> None:
            vault_root = app.vault_path.resolve()
            target = (vault_root / relative).resolve()
            if vault_root not in target.parents and target != vault_root:
                self.send_error(HTTPStatus.FORBIDDEN, "Forbidden")
                return
            if not target.exists() or not target.is_file():
                self.send_error(HTTPStatus.NOT_FOUND, "Not found")
                return
            self._send_text(target.read_text(encoding="utf-8"), "text/plain; charset=utf-8")

        def _send_learning_file(self, relative: str) -> None:
            try:
                self._send_html(app.render_learning_file(relative))
            except PermissionError:
                self.send_error(HTTPStatus.FORBIDDEN, "Forbidden")
            except FileNotFoundError:
                self.send_error(HTTPStatus.NOT_FOUND, "Not found")

        def _send_report_file(self, relative: str) -> None:
            try:
                self._send_html(app.render_report_file(relative))
            except PermissionError:
                self.send_error(HTTPStatus.FORBIDDEN, "Forbidden")
            except FileNotFoundError:
                self.send_error(HTTPStatus.NOT_FOUND, "Not found")

        def _send_export_file(self, relative: str) -> None:
            try:
                self._send_text(app.render_export_file(relative), "application/json; charset=utf-8")
            except PermissionError:
                self.send_error(HTTPStatus.FORBIDDEN, "Forbidden")
            except FileNotFoundError:
                self.send_error(HTTPStatus.NOT_FOUND, "Not found")

        def _redirect(self, location: str) -> None:
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", location)
            self.end_headers()

    return WorkbenchHandler


def _vault_relative_path(request_path: str) -> str:
    return unquote(request_path.removeprefix("/vault/"))


def _learning_relative_path(request_path: str) -> str:
    return unquote(request_path.removeprefix("/learning/"))


def _report_relative_path(request_path: str) -> str:
    return unquote(request_path.removeprefix("/reports/"))


def _export_relative_path(request_path: str) -> str:
    return unquote(request_path.removeprefix("/exports/"))
