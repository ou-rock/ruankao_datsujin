from __future__ import annotations

from datetime import date
from urllib.parse import parse_qs

from ruankao_agent.domain import CardType, ExamFront, SourceIdentity
from ruankao_agent.storage import RuankaoStore
from ruankao_agent.web import (
    WorkbenchApp,
    WorkbenchConfig,
    _learning_relative_path,
    _vault_relative_path,
)


def test_workbench_home_is_an_actionable_control_panel(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))

    html = app.render_home()

    assert "软考达人工作台" in html
    assert "今日闭环" in html
    assert "三源录入" in html
    assert "记忆卡" in html
    assert "原则网络" in html
    assert 'href="/learning/"' in html
    assert 'action="/records"' in html
    assert 'action="/cards"' in html
    assert 'action="/relations"' in html
    assert (root / "data" / "ruankao.db").exists()
    assert (root / "dashboard.html").exists()
    assert (root / "learning" / "index.html").exists()
    assert (root / "learning" / "lessons" / "0001-scene-before-solution.html").exists()
    assert (root / "vault" / "00-map" / "原则网络.md").exists()
    assert (root / "vault" / "10-memory-war-room" / "principles" / "场景先于方案.md").exists()


def test_workbench_forms_write_store_and_principle_note(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()

    record_id = app.add_raw_record(
        parse_qs(
            "source=mein&text=先看业务约束&summary=场景先于方案&topics=架构评估&fronts=case&fronts=essay"
        )
    )
    card_id = app.add_memory_card(
        parse_qs(
            "card_type=principle&title=场景先于方案&prompt=做架构论证时"
            "&answer=先确认目标、边界、约束，再谈方案&source_record_id=1"
            "&fronts=choice&fronts=case&fronts=essay&next_due=2026-06-29"
            "&conflicts=技术先行"
        )
    )
    app.record_review(parse_qs(f"card_id={card_id}&reviewed_on=2026-06-29&grade=5"))

    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    record = store.list_raw_records()[0]
    card = store.get_memory_card(card_id)

    assert record.id == record_id
    assert record.source is SourceIdentity.MEIN
    assert record.fronts == (ExamFront.CASE, ExamFront.ESSAY)
    assert card.card_type is CardType.PRINCIPLE
    assert card.review_count == 1
    assert card.next_due is not None

    note = root / "vault" / "10-memory-war-room" / "principles" / "场景先于方案.md"
    assert note.exists()
    assert "[[技术先行]]" in note.read_text(encoding="utf-8")


def test_workbench_status_json_exposes_current_route(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()

    payload = app.render_status_json()

    assert '"countdown": "D-117"' in payload
    assert '"phase": "启动诊断"' in payload
    assert str(root / "vault") in payload
    assert str(root / "learning") in payload


def test_vault_request_paths_are_decoded_before_file_lookup() -> None:
    assert (
        _vault_relative_path("/vault/10-memory-war-room/principles/%E5%9C%BA%E6%99%AF.md")
        == "10-memory-war-room/principles/场景.md"
    )


def test_learning_request_paths_are_decoded_before_file_lookup() -> None:
    assert (
        _learning_relative_path("/learning/reference/%E5%9B%9B%E5%A4%A7.html")
        == "reference/四大.html"
    )


def test_learning_file_lookup_serves_study_pages(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()

    html = app.render_learning_file("lessons/0001-scene-before-solution.html")

    assert "场景先于方案" in html
    assert "选择题易错点" in html


def test_vault_file_lookup_serves_chinese_paths(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()
    from ruankao_agent.web import _handler_for
    handler_cls = _handler_for(app)

    captured: dict[str, str | int] = {}

    class FakeHandler(handler_cls):  # type: ignore[misc, valid-type]
        def send_error(self, code: int, message: str | None = None) -> None:
            captured["error"] = code

        def _send_text(self, text: str, content_type: str) -> None:  # type: ignore[override]
            captured["text"] = text
            captured["content_type"] = content_type

    handler = object.__new__(FakeHandler)
    handler._send_vault_file("10-memory-war-room/principles/场景先于方案.md")

    assert "场景先于方案" in str(captured["text"])
