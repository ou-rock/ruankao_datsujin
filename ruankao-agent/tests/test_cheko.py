from __future__ import annotations

import subprocess
import sys
from datetime import date

from ruankao_agent.cheko import seed_cheko_cards
from ruankao_agent.domain import CardType, ExamFront, SourceIdentity
from ruankao_agent.storage import RuankaoStore


def test_seed_cheko_cards_creates_raw_record_and_memory_cards(tmp_path) -> None:
    root = tmp_path / "demo"

    result = seed_cheko_cards(root, next_due=date(2026, 6, 29))

    assert len(result.created_card_ids) == 4
    assert result.skipped_titles == ()

    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    records = store.list_raw_records()
    cards = store.list_memory_cards()

    assert len(records) == 1
    assert records[0].id == result.raw_record_id
    assert records[0].source == SourceIdentity.UNS
    assert records[0].promotion_status == "extracted"
    assert records[0].fronts == (ExamFront.CHOICE, ExamFront.CASE, ExamFront.ESSAY)
    assert "正确率 69.4%" in records[0].summary
    assert "系统架构设计" in records[0].text

    assert {card.id for card in cards} == set(result.created_card_ids)
    assert [card.title for card in cards] == [
        "Cheko错题池：系统架构设计",
        "Cheko错题池：软件工程",
        "Cheko错题池：系统分析与设计",
        "Cheko论文最低触达",
    ]
    assert cards[0].card_type == CardType.SCENARIO
    assert cards[0].fronts == (ExamFront.CHOICE, ExamFront.CASE)
    assert "质量属性" in cards[0].answer
    assert cards[-1].card_type == CardType.EXPRESSION
    assert cards[-1].fronts == (ExamFront.ESSAY,)
    assert "300 字以内摘要" in cards[-1].answer
    assert all(card.source_record_id == result.raw_record_id for card in cards)
    assert all(card.next_due == date(2026, 6, 29) for card in cards)


def test_seed_cheko_cards_skips_existing_card_titles(tmp_path) -> None:
    root = tmp_path / "demo"

    first = seed_cheko_cards(root)
    second = seed_cheko_cards(root)

    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()

    assert len(first.created_card_ids) == 4
    assert second.created_card_ids == ()
    assert second.skipped_titles == (
        "Cheko错题池：系统架构设计",
        "Cheko错题池：软件工程",
        "Cheko错题池：系统分析与设计",
        "Cheko论文最低触达",
    )
    assert len(store.list_raw_records()) == 2
    assert len(store.list_memory_cards()) == 4


def test_cli_cheko_seed_cards(tmp_path) -> None:
    root = tmp_path / "demo"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "cheko-seed-cards",
            "--root",
            str(root),
            "--next-due",
            "2026-06-29",
        ],
        cwd=".",
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "已导入 Cheko 信号：原始记录 1，新增卡 4，跳过 0。" in result.stdout
    assert "raw=1 created=4 skipped=0" in result.stdout

    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    assert store.count_due_cards(date(2026, 6, 29)) == 4
