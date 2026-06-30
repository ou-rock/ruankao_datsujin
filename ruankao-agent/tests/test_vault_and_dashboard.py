from datetime import date

from ruankao_agent.dashboard import DashboardSnapshot, render_dashboard
from ruankao_agent.domain import Campaign, CardType, ExamFront, RiskStatus, SourceIdentity
from ruankao_agent.storage import RuankaoStore
from ruankao_agent.vault import (
    initialize_vault,
    sync_memory_cards_to_vault,
    sync_raw_records_to_vault,
    write_principle_note,
)


def test_initialize_vault_creates_expected_obsidian_structure(tmp_path) -> None:
    vault = initialize_vault(tmp_path / "vault")

    assert (vault / "00-map" / "战役总图.md").exists()
    assert (vault / "00-map" / "原则网络.md").exists()
    assert (vault / "10-memory-war-room" / "principles").is_dir()
    assert (vault / "20-mein").is_dir()
    assert (vault / "30-du").is_dir()
    assert (vault / "40-uns").is_dir()


def test_initialize_vault_preserves_existing_map_notes(tmp_path) -> None:
    vault = initialize_vault(tmp_path / "vault")
    map_note = vault / "00-map" / "战役总图.md"
    map_note.write_text("# 我的战役总图\n\n- 手工整理\n", encoding="utf-8")

    initialize_vault(vault)

    assert "手工整理" in map_note.read_text(encoding="utf-8")


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


def test_sync_memory_cards_to_vault_writes_generated_obsidian_notes(tmp_path) -> None:
    root = tmp_path / "demo"
    vault = initialize_vault(root / "vault")
    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    store.add_memory_card(
        card_type=CardType.CONCEPT,
        title="质量属性场景",
        prompt="六要素是什么？",
        answer="刺激源、刺激、环境、制品、响应、响应度量。",
        fronts=(ExamFront.CHOICE, ExamFront.CASE),
        next_due=date(2026, 6, 29),
    )

    first = sync_memory_cards_to_vault(vault, store.list_memory_cards())
    second = sync_memory_cards_to_vault(vault, store.list_memory_cards())

    note = vault / "10-memory-war-room" / "concepts" / "质量属性场景.md"
    assert len(first.written_paths) == 1
    assert len(second.skipped_paths) == 1
    assert note.exists()
    text = note.read_text(encoding="utf-8")
    assert "type: memory-card" in text
    assert "card_type: concept" in text
    assert "choice" in text
    assert "- 选择题" in text
    assert "- 案例题" in text
    assert "刺激源、刺激、环境" in text


def test_sync_raw_records_to_vault_writes_mein_du_uns_notes(tmp_path) -> None:
    root = tmp_path / "demo"
    vault = initialize_vault(root / "vault")
    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    store.add_raw_record(
        source=SourceIdentity.MEIN,
        text="我把可用性和可靠性混淆了。",
        summary="可用性可靠性混淆",
        topics=("质量属性",),
        fronts=(ExamFront.CHOICE,),
    )

    first = sync_raw_records_to_vault(vault, store.list_raw_records())
    second = sync_raw_records_to_vault(vault, store.list_raw_records())

    notes = list((vault / "20-mein").glob("*.md"))
    assert len(first.written_paths) == 1
    assert len(second.skipped_paths) == 1
    assert len(notes) == 1
    text = notes[0].read_text(encoding="utf-8")
    assert "type: raw-record" in text
    assert "source: mein" in text
    assert "## Capture Context" in text
    assert "来源：Mein（我的）" in text
    assert "主题：质量属性" in text
    assert "题型：选择题" in text
    assert "可用性可靠性混淆" in text


def test_vault_sync_renders_empty_frontmatter_lists_as_yaml_arrays(tmp_path) -> None:
    root = tmp_path / "demo"
    vault = initialize_vault(root / "vault")
    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    store.add_memory_card(
        card_type=CardType.CONCEPT,
        title="无题型卡",
        prompt="临时问题",
        answer="临时答案",
    )
    store.add_raw_record(
        source=SourceIdentity.UNS,
        text="外部材料暂未分类。",
        summary="未分类外部材料",
    )

    sync_memory_cards_to_vault(vault, store.list_memory_cards())
    sync_raw_records_to_vault(vault, store.list_raw_records())

    card_text = (vault / "10-memory-war-room" / "concepts" / "无题型卡.md").read_text(
        encoding="utf-8"
    )
    raw_text = next((vault / "40-uns").glob("*.md")).read_text(encoding="utf-8")

    assert "fronts: []" in card_text
    assert "- 未标注" in card_text
    assert "- none" not in card_text
    assert "topics: []" in raw_text
    assert "fronts: []" in raw_text


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

    assert "系统架构设计师" in html
    assert "2026-10-24" in html
    assert "D-117" in html
    assert "启动诊断" in html
    assert "主战进度" in html
    assert "0 / 14 周" in html
    assert "冗余池" in html
    assert "2 周" in html
    assert "今日最小闭环" in html
    assert "到期记忆复习" in html
    assert "记忆作战室" in html
    assert "到期卡片：12" in html
    assert "风险" in html
    assert "绿灯" in html
    assert "Mein" in html
    assert "Du" in html
    assert "Uns" in html
    assert "选择题" in html
    assert "案例题" in html
    assert "论文题" in html
    assert 'id="choice"' in html
    assert 'id="case"' in html
    assert 'id="essay"' in html
    assert 'href="learning/index.html"' in html
    assert 'href="vault/00-map/原则网络.md"' in html
    assert 'href="vault/10-memory-war-room/"' in html
    assert "System Architecture Designer Exam Questions and Analysis" in html
