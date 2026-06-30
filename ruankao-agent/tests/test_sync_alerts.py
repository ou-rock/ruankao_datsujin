from __future__ import annotations

import json
import subprocess
import sys
from datetime import date

from ruankao_agent.domain import CardType, ExamFront
from ruankao_agent.storage import RuankaoStore


def test_sync_sentinel_offline_reconnect_is_silent_and_sends_no_alerts(tmp_path) -> None:
    root = tmp_path / "demo"
    discord_log = tmp_path / "discord.jsonl"
    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    for title in ("响应度量", "备用机制", "重试边界"):
        store.add_memory_card(
            card_type=CardType.CONCEPT,
            title=title,
            prompt=f"{title} 怎么落到案例题？",
            answer="先写场景，再写指标。",
            fronts=(ExamFront.CASE,),
            next_due=date(2026, 6, 29),
        )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "sync-sentinel",
            "--root",
            str(root),
            "--mode",
            "offline-reconnect",
            "--discord-log",
            str(discord_log),
            "--as-of",
            "2026-06-29",
        ],
        cwd=".",
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert not discord_log.exists() or discord_log.read_text(encoding="utf-8") == ""


def test_sync_sentinel_realtime_low_score_pushes_simulated_discord_alert(tmp_path) -> None:
    root = tmp_path / "demo"
    discord_log = tmp_path / "discord.jsonl"
    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    practice_id = store.add_practice_session(
        front=ExamFront.CASE,
        topic="灾备响应度量",
        source="manual",
        score=5.0,
        max_score=15.0,
        duration_minutes=12,
        summary="1s 查状态、2s 反馈执行结果、3s 返回明确结果。",
        mistakes="备用机制边界没有展开。",
        created_on=date(2026, 6, 29),
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "sync-sentinel",
            "--root",
            str(root),
            "--mode",
            "realtime",
            "--discord-log",
            str(discord_log),
            "--as-of",
            "2026-06-29",
        ],
        cwd=".",
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    rows = [
        json.loads(line)
        for line in discord_log.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(rows) == 1
    assert rows[0]["kind"] == "low_score"
    assert rows[0]["practice_id"] == practice_id
    assert rows[0]["topic"] == "灾备响应度量"
    assert rows[0]["score_ratio"] == 0.333
    assert "练习得分低于 60%" in rows[0]["risk_reasons"]
    assert "本周缺席 2 个以上题型" in rows[0]["risk_reasons"]
    assert "灾备响应度量" in rows[0]["message"]
    assert "练习得分低于 60%" in rows[0]["message"]

    second = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "sync-sentinel",
            "--root",
            str(root),
            "--mode",
            "realtime",
            "--discord-log",
            str(discord_log),
            "--as-of",
            "2026-06-29",
        ],
        cwd=".",
        text=True,
        capture_output=True,
        check=False,
    )

    assert second.returncode == 0, second.stderr
    assert second.stdout == ""
    assert len(discord_log.read_text(encoding="utf-8").splitlines()) == 1


def test_sync_sentinel_offline_reconnect_marks_old_low_scores_seen(tmp_path) -> None:
    root = tmp_path / "demo"
    discord_log = tmp_path / "discord.jsonl"
    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    store.add_practice_session(
        front=ExamFront.CASE,
        topic="离线期间案例低分",
        score=3.0,
        max_score=15.0,
        summary="离线积压的旧记录。",
        created_on=date(2026, 6, 29),
    )

    offline = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "sync-sentinel",
            "--root",
            str(root),
            "--mode",
            "offline-reconnect",
            "--discord-log",
            str(discord_log),
            "--as-of",
            "2026-06-29",
        ],
        cwd=".",
        text=True,
        capture_output=True,
        check=False,
    )
    realtime = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "sync-sentinel",
            "--root",
            str(root),
            "--mode",
            "realtime",
            "--discord-log",
            str(discord_log),
            "--as-of",
            "2026-06-29",
        ],
        cwd=".",
        text=True,
        capture_output=True,
        check=False,
    )

    assert offline.returncode == 0, offline.stderr
    assert realtime.returncode == 0, realtime.stderr
    assert offline.stdout == ""
    assert realtime.stdout == ""
    assert not discord_log.exists() or discord_log.read_text(encoding="utf-8") == ""
