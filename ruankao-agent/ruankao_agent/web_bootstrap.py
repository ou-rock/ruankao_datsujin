from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .learning import ensure_learning_resources
from .storage import RuankaoStore
from .vault import initialize_vault, write_principle_note


@dataclass(frozen=True, slots=True)
class WorkbenchBootstrapContext:
    root: Path
    vault_path: Path
    store: Callable[[], RuankaoStore]
    write_dashboard: Callable[[], Path]


def initialize_workbench(context: WorkbenchBootstrapContext) -> None:
    context.root.mkdir(parents=True, exist_ok=True)
    store = context.store()
    store.initialize()
    initialize_vault(context.vault_path)
    ensure_seed_principle(context.vault_path)
    ensure_learning_resources(context.root)
    context.write_dashboard()


def ensure_seed_principle(vault_path: Path) -> None:
    note = vault_path / "10-memory-war-room" / "principles" / "场景先于方案.md"
    if note.exists():
        return
    write_principle_note(
        vault_path,
        title="场景先于方案",
        core_statement="先确认业务目标、边界和约束，再谈技术方案。",
        applies_when="任何架构设计、案例题、论文题。",
        conflicts=("技术先行",),
    )
