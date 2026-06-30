import subprocess
import sys

from datetime import date

from ruankao_agent.domain import CardType, ExamFront, SourceIdentity
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
    principle_note = root / "vault" / "10-memory-war-room" / "principles" / "场景先于方案.md"
    assert principle_note.exists()
    principle_text = principle_note.read_text(encoding="utf-8")
    assert "## 核心表述" in principle_text
    assert "Choice:" not in principle_text

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
    assert "记忆作战室" in (root / "dashboard.html").read_text(encoding="utf-8")


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
    assert "到期卡片：1" in html
    assert "复习积压" in html
    assert "100%" in html
    assert ">红灯<" in html


def test_cli_status_reflects_practice_front_gaps_after_practice_starts(tmp_path) -> None:
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
    store.add_practice_session(
        front=ExamFront.CHOICE,
        topic="选择题 10 道",
        summary="只做了选择题。",
        created_on=date(2026, 6, 29),
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
    assert "red" in status_result.stdout.lower()

    store.add_practice_session(
        front=ExamFront.CASE,
        topic="案例题质量属性",
        summary="补了一题案例。",
        created_on=date(2026, 6, 29),
    )
    store.add_practice_session(
        front=ExamFront.ESSAY,
        topic="论文背景段",
        summary="补了一段论文。",
        created_on=date(2026, 6, 29),
    )

    recovered_result = subprocess.run(
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

    assert recovered_result.returncode == 0, recovered_result.stderr
    assert "green" in recovered_result.stdout.lower()


def test_cli_vault_sync_exports_memory_cards(tmp_path) -> None:
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
        title="质量属性场景",
        prompt="六要素是什么？",
        answer="刺激源、刺激、环境、制品、响应、响应度量。",
        fronts=(ExamFront.CHOICE, ExamFront.CASE),
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "vault-sync",
            "--root",
            str(root),
        ],
        cwd=".",
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "written=1" in result.stdout
    assert (root / "vault" / "10-memory-war-room" / "concepts" / "质量属性场景.md").exists()


def test_cli_raw_vault_sync_exports_source_records(tmp_path) -> None:
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
    store.add_raw_record(
        source=SourceIdentity.DU,
        text="这个错因应该拆成对比卡。",
        summary="错因转对比卡",
        topics=("错因",),
        fronts=(ExamFront.CASE,),
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "raw-vault-sync",
            "--root",
            str(root),
        ],
        cwd=".",
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "written=1" in result.stdout
    assert len(list((root / "vault" / "30-du").glob("*.md"))) == 1
