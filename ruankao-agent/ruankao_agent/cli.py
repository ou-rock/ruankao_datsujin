from __future__ import annotations

import argparse
import sqlite3
from datetime import date
from pathlib import Path
from typing import Sequence

from .dashboard import render_dashboard
from .loop import build_daily_loop_snapshot, status_line
from .notebooklm import DEFAULT_NOTEBOOK_SOURCE


def _load_domain() -> object | None:
    try:
        from . import domain as domain_module  # type: ignore
    except Exception:
        return None
    return domain_module


def _load_storage() -> object | None:
    try:
        from . import storage as storage_module  # type: ignore
    except Exception:
        return None
    return storage_module


def _load_vault() -> object | None:
    try:
        from . import vault as vault_module  # type: ignore
    except Exception:
        return None
    return vault_module


def _ensure_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    storage_module = _load_storage()
    if storage_module is not None and hasattr(storage_module, "RuankaoStore"):
        store = storage_module.RuankaoStore(db_path)
        if hasattr(store, "initialize"):
            store.initialize()
            return
    with sqlite3.connect(db_path):
        pass


def _open_store(root: Path):
    storage_module = _load_storage()
    if storage_module is None or not hasattr(storage_module, "RuankaoStore"):
        return None
    store = storage_module.RuankaoStore(root / "data" / "ruankao.db")
    if hasattr(store, "initialize"):
        store.initialize()
    return store


def _default_principle_content() -> str:
    return """---
type: principle
status: candidate
source: Mein
exam:
  - choice
  - case
  - essay
strength: 1
last_reviewed:
---

# 场景先于方案

## Core Statement

先确认业务目标、边界和约束，再谈技术方案。

## Applies When

任何架构设计、案例题、论文题。

## Does Not Apply When

仅做纯语言或纯格式修改时。

## Conflicts

- [[技术先行]]

## Exam Mapping

Choice:
Case:
Essay:
"""


def _ensure_vault(root: Path) -> Path:
    vault_root = root / "vault"
    vault_module = _load_vault()
    if vault_module is not None and hasattr(vault_module, "initialize_vault"):
        vault_root = vault_module.initialize_vault(vault_root)
        if hasattr(vault_module, "write_principle_note"):
            vault_module.write_principle_note(
                vault_root,
                title="场景先于方案",
                core_statement="先确认业务目标、边界和约束，再谈技术方案。",
                applies_when="任何架构设计、案例题、论文题。",
                conflicts=("技术先行",),
            )
            return vault_root

    for relative in (
        "00-map",
        "10-memory-war-room/principles",
        "10-memory-war-room/concepts",
        "10-memory-war-room/comparisons",
        "10-memory-war-room/scenarios",
        "10-memory-war-room/expressions",
        "20-mein",
        "30-du",
        "40-uns",
        "50-exam/choice",
        "50-exam/case",
        "50-exam/essay",
        "90-archive",
    ):
        (vault_root / relative).mkdir(parents=True, exist_ok=True)

    (vault_root / "00-map" / "战役总图.md").write_text("# 战役总图\n", encoding="utf-8")
    (vault_root / "00-map" / "原则网络.md").write_text("# 原则网络\n", encoding="utf-8")
    (vault_root / "00-map" / "三题型路线图.md").write_text("# 三题型路线图\n", encoding="utf-8")
    (vault_root / "10-memory-war-room" / "principles" / "场景先于方案.md").write_text(
        _default_principle_content(),
        encoding="utf-8",
    )
    return vault_root


def _parse_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _dashboard_snapshot(root: Path, *, as_of: date | None = None):
    store = _open_store(root)
    due_cards = 0
    backlog = 0.0
    if store is not None:
        effective_date = as_of or date.today()
        if hasattr(store, "count_due_cards"):
            due_cards = store.count_due_cards(effective_date)
        if hasattr(store, "review_backlog_ratio"):
            backlog = store.review_backlog_ratio(effective_date)
    return build_daily_loop_snapshot(
        as_of=as_of,
        due_cards=due_cards,
        review_backlog_ratio=backlog,
    )


def cmd_init(root: Path, as_of: date | None = None) -> int:
    root.mkdir(parents=True, exist_ok=True)
    _ensure_db(root / "data" / "ruankao.db")
    vault_root = _ensure_vault(root)
    _ = vault_root
    snapshot = _dashboard_snapshot(root, as_of=as_of)
    dashboard_path = root / "dashboard.html"
    dashboard_path.write_text(render_dashboard(snapshot.dashboard), encoding="utf-8")
    print(dashboard_path)
    return 0


def cmd_status(root: Path, as_of: date | None = None) -> int:
    snapshot = _dashboard_snapshot(root, as_of=as_of)
    print(status_line(snapshot))
    return 0


def cmd_dashboard(root: Path, as_of: date | None = None) -> int:
    root.mkdir(parents=True, exist_ok=True)
    snapshot = _dashboard_snapshot(root, as_of=as_of)
    dashboard_path = root / "dashboard.html"
    dashboard_path.write_text(render_dashboard(snapshot.dashboard), encoding="utf-8")
    print(dashboard_path)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ruankao-agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("init", "status", "dashboard"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--root", required=True, type=Path)
        subparser.add_argument("--as-of")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        return cmd_init(args.root, as_of=_parse_date(args.as_of))
    if args.command == "status":
        return cmd_status(args.root, as_of=_parse_date(args.as_of))
    if args.command == "dashboard":
        return cmd_dashboard(args.root, as_of=_parse_date(args.as_of))
    raise AssertionError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
