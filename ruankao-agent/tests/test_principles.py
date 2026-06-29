from __future__ import annotations

import subprocess
import sys
from datetime import date

from ruankao_agent.domain import CardType, ExamFront, SourceIdentity
from ruankao_agent.principles import (
    CORE_ARCHITECTURE_PRINCIPLES,
    CORE_ARCHITECTURE_RELATIONS,
    seed_core_principles,
)
from ruankao_agent.storage import RuankaoStore


def test_seed_core_principles_creates_seven_principle_cards(tmp_path) -> None:
    root = tmp_path / "demo"

    result = seed_core_principles(root, next_due=date(2026, 6, 29))

    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    records = store.list_raw_records()
    cards = store.list_memory_cards()

    assert len(result.created_card_ids) == 7
    assert len(result.created_relation_ids) == len(CORE_ARCHITECTURE_RELATIONS)
    assert result.skipped_titles == ()
    assert len(records) == 1
    assert records[0].source == SourceIdentity.DU
    assert records[0].promotion_status == "promoted"
    assert len(cards) == len(CORE_ARCHITECTURE_PRINCIPLES)
    assert all(card.card_type == CardType.PRINCIPLE for card in cards)
    assert all(card.fronts == (ExamFront.CHOICE, ExamFront.CASE, ExamFront.ESSAY) for card in cards)
    assert all(card.next_due == date(2026, 6, 29) for card in cards)
    assert {card.title for card in cards} == {
        principle.title for principle in CORE_ARCHITECTURE_PRINCIPLES
    }
    first_card = next(card for card in cards if card.title == "场景先于方案")
    relations = store.list_principle_relations(first_card.id)
    assert relations[0].relation.value == "supports"


def test_seed_core_principles_skips_existing_titles(tmp_path) -> None:
    root = tmp_path / "demo"

    first = seed_core_principles(root)
    second = seed_core_principles(root)

    assert len(first.created_card_ids) == 7
    assert len(first.created_relation_ids) == len(CORE_ARCHITECTURE_RELATIONS)
    assert second.created_card_ids == ()
    assert second.skipped_titles == tuple(
        principle.title for principle in CORE_ARCHITECTURE_PRINCIPLES
    )
    assert second.created_relation_ids == ()
    assert len(second.skipped_relations) == len(CORE_ARCHITECTURE_RELATIONS)


def test_cli_seed_principles(tmp_path) -> None:
    root = tmp_path / "demo"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "seed-principles",
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
    assert "created=7" in result.stdout
    assert "relations=6" in result.stdout
