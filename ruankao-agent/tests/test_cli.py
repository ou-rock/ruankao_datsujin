import subprocess
import sys

from datetime import date

from ruankao_agent.domain import CardType
from ruankao_agent.storage import RuankaoStore


def test_cli_init_status_and_dashboard(tmp_path) -> None:
    root = tmp_path / "demo"

    init_result = subprocess.run(
        [sys.executable, "-m", "ruankao_agent.cli", "init", "--root", str(root)],
        cwd=".",
        text=True,
        capture_output=True,
        check=False,
    )

    assert init_result.returncode == 0, init_result.stderr
    assert (root / "data" / "ruankao.db").exists()
    assert (root / "dashboard.html").exists()
    assert (root / "vault" / "00-map" / "战役总图.md").exists()
    assert (root / "vault" / "10-memory-war-room" / "principles" / "场景先于方案.md").exists()

    status_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "status",
            "--root",
            str(root),
            "--as-of",
            "2026-06-29",
        ],
        cwd=".",
        text=True,
        capture_output=True,
        check=False,
    )

    assert status_result.returncode == 0, status_result.stderr
    assert "D-117" in status_result.stdout
    assert "启动诊断" in status_result.stdout
    assert "green" in status_result.stdout.lower()

    dashboard_result = subprocess.run(
        [sys.executable, "-m", "ruankao_agent.cli", "dashboard", "--root", str(root)],
        cwd=".",
        text=True,
        capture_output=True,
        check=False,
    )

    assert dashboard_result.returncode == 0, dashboard_result.stderr
    assert "dashboard.html" in dashboard_result.stdout
    assert "Memory War Room" in (root / "dashboard.html").read_text(encoding="utf-8")


def test_cli_status_and_dashboard_reflect_persisted_store_state(tmp_path) -> None:
    root = tmp_path / "demo"
    subprocess.run(
        [sys.executable, "-m", "ruankao_agent.cli", "init", "--root", str(root), "--as-of", "2026-06-29"],
        cwd=".",
        text=True,
        capture_output=True,
        check=True,
    )

    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    store.add_memory_card(
        card_type=CardType.CONCEPT,
        title="可用性",
        prompt="什么是可用性？",
        answer="故障后仍能提供服务或快速恢复的能力。",
        next_due=date(2026, 6, 29),
    )

    status_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "status",
            "--root",
            str(root),
            "--as-of",
            "2026-06-29",
        ],
        cwd=".",
        text=True,
        capture_output=True,
        check=False,
    )

    assert status_result.returncode == 0, status_result.stderr
    assert "due=1" in status_result.stdout
    assert "backlog=100%" in status_result.stdout
    assert "red" in status_result.stdout.lower()

    subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "dashboard",
            "--root",
            str(root),
            "--as-of",
            "2026-06-29",
        ],
        cwd=".",
        text=True,
        capture_output=True,
        check=True,
    )

    html = (root / "dashboard.html").read_text(encoding="utf-8")
    assert "Due cards: 1" in html
    assert "Review backlog" in html
    assert "100%" in html
    assert ">red<" in html
