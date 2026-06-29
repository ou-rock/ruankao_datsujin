from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from collections.abc import Iterable

from ruankao_agent.memory import render_map_note, render_principle_note
from ruankao_agent.storage import MemoryCard


@dataclass(frozen=True, slots=True)
class VaultSyncResult:
    written_paths: tuple[Path, ...]
    skipped_paths: tuple[Path, ...]


CARD_TYPE_DIRECTORIES = {
    "principle": "principles",
    "concept": "concepts",
    "comparison": "comparisons",
    "scenario": "scenarios",
    "expression": "expressions",
}


def initialize_vault(root: Path | str) -> Path:
    vault = Path(root)

    directories = (
        vault / "00-map",
        vault / "10-memory-war-room" / "principles",
        vault / "10-memory-war-room" / "concepts",
        vault / "10-memory-war-room" / "comparisons",
        vault / "10-memory-war-room" / "scenarios",
        vault / "10-memory-war-room" / "expressions",
        vault / "20-mein",
        vault / "30-du",
        vault / "40-uns",
        vault / "50-exam" / "choice",
        vault / "50-exam" / "case",
        vault / "50-exam" / "essay",
        vault / "90-archive",
    )
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    _write_map_notes(vault)
    return vault


def write_principle_note(
    vault: Path | str,
    title: str,
    core_statement: str,
    applies_when: str,
    conflicts: Iterable[str] = (),
) -> Path:
    vault_path = Path(vault)
    note_path = vault_path / "10-memory-war-room" / "principles" / f"{title}.md"
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(
        render_principle_note(
            title=title,
            core_statement=core_statement,
            applies_when=applies_when,
            conflicts=tuple(conflicts),
        ),
        encoding="utf-8",
    )
    return note_path


def sync_memory_cards_to_vault(
    vault: Path | str,
    cards: Iterable[MemoryCard],
    *,
    overwrite: bool = False,
) -> VaultSyncResult:
    vault_path = initialize_vault(vault)
    written: list[Path] = []
    skipped: list[Path] = []
    for card in cards:
        note_path = _memory_card_note_path(vault_path, card)
        if note_path.exists() and not overwrite:
            skipped.append(note_path)
            continue
        note_path.parent.mkdir(parents=True, exist_ok=True)
        note_path.write_text(_render_memory_card_note(card), encoding="utf-8")
        written.append(note_path)
    return VaultSyncResult(written_paths=tuple(written), skipped_paths=tuple(skipped))


def _write_map_notes(vault: Path) -> None:
    map_dir = vault / "00-map"

    total_map = render_map_note(
        "战役总图",
        [
            "- Target: System Architecture Designer 2026 H2",
            "- Links: [[原则网络]]",
            "- Fronts: [[三题型路线图]]",
            "- Memory: [[../10-memory-war-room/principles/场景先于方案|场景先于方案]]",
        ],
    )
    principle_network = render_map_note(
        "原则网络",
        [
            "- [[场景先于方案]]",
            "- [[技术先行]]",
            "- [[简单可演进优先]]",
        ],
    )
    route_map = render_map_note(
        "三题型路线图",
        [
            "- Choice",
            "- Case",
            "- Essay",
        ],
    )

    _write_if_missing(map_dir / "战役总图.md", total_map)
    _write_if_missing(map_dir / "原则网络.md", principle_network)
    _write_if_missing(map_dir / "三题型路线图.md", route_map)


def _write_if_missing(path: Path, text: str) -> None:
    if path.exists():
        return
    path.write_text(text, encoding="utf-8")


def _memory_card_note_path(vault: Path, card: MemoryCard) -> Path:
    directory = CARD_TYPE_DIRECTORIES.get(card.card_type.value, "concepts")
    filename = _safe_note_name(card.title)
    return vault / "10-memory-war-room" / directory / f"{filename}.md"


def _safe_note_name(title: str) -> str:
    return (
        title.replace("/", "-")
        .replace("\\", "-")
        .replace(":", "：")
        .strip()
        or "untitled"
    )


def _render_memory_card_note(card: MemoryCard) -> str:
    fronts = "\n".join(f"  - {front.value}" for front in card.fronts) or "  []"
    source_record = card.source_record_id if card.source_record_id is not None else ""
    next_due = card.next_due.isoformat() if card.next_due else ""
    last_reviewed = card.last_reviewed_on.isoformat() if card.last_reviewed_on else ""
    return f"""---
type: memory-card
card_id: {card.id}
card_type: {card.card_type.value}
fronts:
{fronts}
source_record_id: {source_record}
review_count: {card.review_count}
retrieval_strength: {card.retrieval_strength}
storage_strength: {card.storage_strength}
next_due: {next_due}
last_reviewed: {last_reviewed}
---

# {card.title}

## Prompt

{card.prompt}

## Answer

{card.answer}

## Exam Fronts

{chr(10).join(f"- {front.value}" for front in card.fronts) or "- none"}
"""
