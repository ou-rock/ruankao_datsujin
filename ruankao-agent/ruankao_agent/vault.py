from __future__ import annotations

from pathlib import Path
from collections.abc import Iterable

from ruankao_agent.memory import render_map_note, render_principle_note


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
