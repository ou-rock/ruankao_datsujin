from datetime import date

from ruankao_agent.dashboard import DashboardSnapshot, render_dashboard
from ruankao_agent.domain import Campaign, RiskStatus
from ruankao_agent.vault import initialize_vault, write_principle_note


def test_initialize_vault_creates_expected_obsidian_structure(tmp_path) -> None:
    vault = initialize_vault(tmp_path / "vault")

    assert (vault / "00-map" / "战役总图.md").exists()
    assert (vault / "00-map" / "原则网络.md").exists()
    assert (vault / "10-memory-war-room" / "principles").is_dir()
    assert (vault / "20-mein").is_dir()
    assert (vault / "30-du").is_dir()
    assert (vault / "40-uns").is_dir()


def test_principle_note_uses_obsidian_links(tmp_path) -> None:
    vault = initialize_vault(tmp_path / "vault")

    note = write_principle_note(
        vault,
        title="场景先于方案",
        core_statement="先确认业务目标、边界和约束，再谈技术方案。",
        applies_when="任何架构设计、案例题、论文题。",
        conflicts=("技术先行",),
    )

    text = note.read_text(encoding="utf-8")
    assert "[[技术先行]]" in text
    assert "type: principle" in text
    assert "场景先于方案" in text


def test_dashboard_renders_total_map() -> None:
    campaign = Campaign.default()
    snapshot = DashboardSnapshot(
        campaign=campaign,
        as_of=date(2026, 6, 29),
        risk=RiskStatus.GREEN,
        notebook_name="System Architecture Designer Exam Questions and Analysis",
        due_cards=12,
        review_backlog_ratio=0.1,
    )

    html = render_dashboard(snapshot)

    assert "System Architecture Designer" in html
    assert "2026-10-24" in html
    assert "D-117" in html
    assert "启动诊断" in html
    assert "Main battle progress" in html
    assert "0 / 14 weeks" in html
    assert "Reserve pool" in html
    assert "2 weeks" in html
    assert "Today&#x27;s minimum loop" in html
    assert "到期记忆复习" in html
    assert "Memory War Room" in html
    assert "Mein" in html
    assert "Du" in html
    assert "Uns" in html
    assert "选择题" in html
    assert "案例题" in html
    assert "论文题" in html
    assert 'id="choice"' in html
    assert 'id="case"' in html
    assert 'id="essay"' in html
    assert 'href="vault/00-map/原则网络.md"' in html
    assert 'href="vault/10-memory-war-room/"' in html
    assert "System Architecture Designer Exam Questions and Analysis" in html
