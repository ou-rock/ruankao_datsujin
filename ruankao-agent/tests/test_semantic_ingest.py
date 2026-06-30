from __future__ import annotations

import json
import subprocess
import sys

from ruankao_agent.domain import ExamFront, SourceIdentity
from ruankao_agent.semantic_ingest import parse_semantic_input
from ruankao_agent.storage import RuankaoStore


def test_semantic_ingest_parses_practice_checkin_with_physical_validator() -> None:
    result = parse_semantic_input("打卡案例题，灾备响应度理得了 12.5 分，满分 15")

    assert result.status == "parsed"
    assert result.intent == "practice_session"
    assert result.payload is not None
    assert result.payload.model_dump(mode="json") == {
        "intent": "practice_session",
        "front": "case",
        "topic": "案例题打卡",
        "score": 12.5,
        "max_score": 15.0,
        "summary": "打卡案例题，灾备响应度理得了 12.5 分，满分 15",
        "source": "semantic-ingest",
    }


def test_cli_semantic_ingest_falls_back_to_mein_raw_record(tmp_path) -> None:
    root = tmp_path / "demo"
    text = "今天随便看了看性能，感觉有点累，明天再说吧。"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "semantic-ingest",
            "--root",
            str(root),
            "--text",
            text,
        ],
        cwd=".",
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "fallback_raw"
    assert payload["source"] == "mein"
    assert payload["promotion_status"] == "raw"
    assert "low_confidence" in payload["warnings"]

    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    records = store.list_raw_records()

    assert len(records) == 1
    assert records[0].source == SourceIdentity.MEIN
    assert records[0].text == text
    assert records[0].summary == "语义解析降级：日常碎片"
    assert records[0].promotion_status == "raw"
    assert records[0].fronts == ()


def test_cli_semantic_ingest_records_parsed_practice_session(tmp_path) -> None:
    root = tmp_path / "demo"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "semantic-ingest",
            "--root",
            str(root),
            "--text",
            "打卡案例题，灾备响应度理得了 12.5 分，满分 15",
        ],
        cwd=".",
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "parsed"
    assert payload["intent"] == "practice_session"
    assert payload["payload"]["front"] == "case"
    assert payload["payload"]["score"] == 12.5
    assert payload["payload"]["max_score"] == 15.0

    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    sessions = store.list_practice_sessions()

    assert len(sessions) == 1
    assert sessions[0].front == ExamFront.CASE
    assert sessions[0].topic == "案例题打卡"
    assert sessions[0].score == 12.5
    assert sessions[0].max_score == 15.0
    assert sessions[0].source == "semantic-ingest"


def test_cli_semantic_ingest_rejects_incomplete_practice_checkin(tmp_path) -> None:
    root = tmp_path / "demo"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "semantic-ingest",
            "--root",
            str(root),
            "--text",
            "打卡案例题，灾备响应度理没有写好",
        ],
        cwd=".",
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "rejected"
    assert payload["intent"] == "practice_session"
    assert "score_missing" in payload["warnings"]

    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    assert store.list_practice_sessions() == []
    assert store.list_raw_records() == []
