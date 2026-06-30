from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import date
from pathlib import Path
from typing import Sequence

from .cheko import seed_cheko_cards
from .dashboard import render_dashboard
from .domain import ExamFront
from .evolution import write_night_evolution_plan
from .export_state import write_state_export
from .import_state import import_state_snapshot
from .learning import ensure_learning_resources
from .loop import build_daily_loop_snapshot, status_line
from .notebooklm import DEFAULT_NOTEBOOK_SOURCE
from .principles import seed_core_principles
from .rag import write_rag_brief
from .receipts import write_daily_receipt
from .route_map import write_route_map
from .semantic_ingest import ingest_semantic_input
from .study import capture_study_turn
from .sync_alerts import SyncSentinelMode, run_sync_sentinel
from .vault import sync_memory_cards_to_vault, sync_raw_records_to_vault
from .web import serve_workbench


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

## 核心表述

先确认业务目标、边界和约束，再谈技术方案。

## 适用场景

任何架构设计、案例题、论文题。

## 不适用场景

仅做纯语言或纯格式修改时。

## 冲突原则

- [[技术先行]]

## 考试映射

选择题：
案例题：
论文题：
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


def _parse_fronts(values: Sequence[str] | None) -> tuple[ExamFront, ...]:
    return tuple(ExamFront(value) for value in values or ())


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
        practice_sessions = (
            store.list_practice_sessions()
            if hasattr(store, "list_practice_sessions")
            else ()
        )
    else:
        practice_sessions = ()
    return build_daily_loop_snapshot(
        as_of=as_of,
        due_cards=due_cards,
        review_backlog_ratio=backlog,
        practice_sessions=practice_sessions,
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


def cmd_web(
    root: Path,
    *,
    host: str,
    port: int,
    as_of: date | None = None,
    open_browser: bool = False,
) -> int:
    serve_workbench(
        root,
        host=host,
        port=port,
        as_of=as_of,
        open_browser=open_browser,
    )
    return 0


def cmd_learning(root: Path, *, overwrite: bool = False) -> int:
    learning_path = ensure_learning_resources(root, overwrite=overwrite)
    print(learning_path / "index.html")
    return 0


def cmd_cheko_seed_cards(root: Path, *, next_due: date | None = None) -> int:
    result = seed_cheko_cards(root, next_due=next_due)
    print(
        "已导入 Cheko 信号："
        f"原始记录 {result.raw_record_id}，"
        f"新增卡 {len(result.created_card_ids)}，"
        f"跳过 {len(result.skipped_titles)}。"
    )
    print(
        f"raw={result.raw_record_id} "
        f"created={len(result.created_card_ids)} "
        f"skipped={len(result.skipped_titles)}"
    )
    return 0


def cmd_daily_receipt(root: Path, *, as_of: date | None = None) -> int:
    result = write_daily_receipt(root, as_of=as_of)
    print(f"日结回执已生成：{result.html_path}（状态 {result.status}）。")
    print(f"html={result.html_path} json={result.json_path} status={result.status}")
    return 0


def cmd_night_evolve(root: Path, *, as_of: date | None = None) -> int:
    result = write_night_evolution_plan(root, as_of=as_of)
    stage_text = "是" if result.stage_only else "否"
    print(
        f"夜间进化计划已生成：{result.html_path}"
        f"（动作 {result.action_count}，仅暂存 {stage_text}）。"
    )
    print(
        f"html={result.html_path} json={result.json_path} "
        f"actions={result.action_count} stage_only={str(result.stage_only).lower()}"
    )
    return 0


def cmd_route_map(root: Path, *, as_of: date | None = None) -> int:
    result = write_route_map(root, as_of=as_of)
    print(f"三题型路线图已生成：{result.html_path}。")
    print(f"html={result.html_path} json={result.json_path}")
    return 0


def cmd_rag_query(
    root: Path,
    *,
    query: str,
    fronts: Sequence[str] = (),
    as_of: date | None = None,
    limit: int = 6,
) -> int:
    result = write_rag_brief(
        root,
        query=query,
        fronts=_parse_fronts(fronts),
        as_of=as_of,
        limit=limit,
    )
    print(f"RAG 记忆与进步控制已生成：{result.html_path}。")
    print(f"建议动作：{result.recommended_action}")
    print(
        f"html={result.html_path} json={result.json_path} "
        f"hits={result.hit_count} gates={result.gate_count}"
    )
    return 0


def cmd_semantic_ingest(
    root: Path,
    *,
    text: str,
    as_of: date | None = None,
) -> int:
    result = ingest_semantic_input(root, text, as_of=as_of)
    print(json.dumps(result.to_dict(), ensure_ascii=False))
    return 0


def cmd_sync_sentinel(
    root: Path,
    *,
    mode: SyncSentinelMode,
    discord_log: Path | None = None,
    as_of: date | None = None,
) -> int:
    run_sync_sentinel(
        root,
        mode=mode,
        discord_log=discord_log,
        as_of=as_of,
    )
    return 0


def cmd_vault_sync(root: Path, *, overwrite: bool = False) -> int:
    store = _open_store(root)
    cards = store.list_memory_cards() if store is not None else []
    result = sync_memory_cards_to_vault(root / "vault", cards, overwrite=overwrite)
    print(
        "记忆卡已同步到 Obsidian："
        f"写入 {len(result.written_paths)} 个，"
        f"跳过 {len(result.skipped_paths)} 个。"
    )
    print(
        f"written={len(result.written_paths)} "
        f"skipped={len(result.skipped_paths)} "
        f"vault={root / 'vault'}"
    )
    return 0


def cmd_raw_vault_sync(root: Path, *, overwrite: bool = False) -> int:
    store = _open_store(root)
    records = store.list_raw_records() if store is not None else []
    result = sync_raw_records_to_vault(root / "vault", records, overwrite=overwrite)
    print(
        "三源材料已同步到 Obsidian："
        f"写入 {len(result.written_paths)} 个，"
        f"跳过 {len(result.skipped_paths)} 个。"
    )
    print(
        f"written={len(result.written_paths)} "
        f"skipped={len(result.skipped_paths)} "
        f"vault={root / 'vault'}"
    )
    return 0


def cmd_seed_principles(root: Path, *, next_due: date | None = None) -> int:
    result = seed_core_principles(root, next_due=next_due)
    print(
        "核心原则已种入记忆系统："
        f"原始记录 {result.raw_record_id}，"
        f"新增卡 {len(result.created_card_ids)}，"
        f"跳过 {len(result.skipped_titles)}，"
        f"关系 {len(result.created_relation_ids)}。"
    )
    print(
        f"raw={result.raw_record_id} "
        f"created={len(result.created_card_ids)} "
        f"skipped={len(result.skipped_titles)} "
        f"relations={len(result.created_relation_ids)} "
        f"relation_skipped={len(result.skipped_relations)}"
    )
    return 0


def cmd_export_state(root: Path, *, as_of: date | None = None) -> int:
    result = write_state_export(root, as_of=as_of)
    print(
        f"状态快照已导出：{result.json_path}"
        f"（材料 {result.raw_records}，卡片 {result.memory_cards}，练习 {result.practice_sessions}）。"
    )
    print(
        f"json={result.json_path} "
        f"raw={result.raw_records} "
        f"cards={result.memory_cards} "
        f"practice={result.practice_sessions}"
    )
    return 0


def cmd_import_state(snapshot_path: Path, *, root: Path | None = None) -> int:
    result = import_state_snapshot(snapshot_path, root=root)
    print(
        f"状态快照已导入：{result.db_path}"
        f"（材料 {result.raw_records}，卡片 {result.memory_cards}，"
        f"复习 {result.review_logs}，练习 {result.practice_sessions}，"
        f"关系 {result.principle_relations}）。"
    )
    print(
        f"db={result.db_path} "
        f"json={result.json_path} "
        f"raw={result.raw_records} "
        f"cards={result.memory_cards} "
        f"reviews={result.review_logs} "
        f"practice={result.practice_sessions} "
        f"relations={result.principle_relations}"
    )
    return 0


def cmd_study_turn(
    root: Path,
    *,
    topic: str,
    user_text: str,
    assistant_text: str,
    fronts: Sequence[str] = (),
    learner_position: str = "",
    codex_position: str = "",
    destination: str = "",
) -> int:
    result = capture_study_turn(
        root,
        topic=topic,
        user_text=user_text,
        assistant_text=assistant_text,
        fronts=_parse_fronts(fronts),
        learner_position=learner_position,
        codex_position=codex_position,
        destination=destination,
    )
    front_text = "、".join(_front_display(front) for front in result.fronts) or "未标注"
    print(
        "学习回合已记录："
        f"Mein {result.mein_record_id}，"
        f"Du {result.du_record_id}，"
        f"题型 {front_text}。"
    )
    print(
        f"mein={result.mein_record_id} "
        f"du={result.du_record_id} "
        f"topic={result.topic} "
        f"fronts={front_text}"
    )
    return 0


def _front_display(front: ExamFront) -> str:
    return {
        ExamFront.CHOICE: "选择题",
        ExamFront.CASE: "案例题",
        ExamFront.ESSAY: "论文题",
    }[front]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ruankao-agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("init", "status", "dashboard"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--root", required=True, type=Path)
        subparser.add_argument("--as-of")

    web_parser = subparsers.add_parser("web")
    web_parser.add_argument("--root", required=True, type=Path)
    web_parser.add_argument("--as-of")
    web_parser.add_argument("--host", default="127.0.0.1")
    web_parser.add_argument("--port", default=8765, type=int)
    web_parser.add_argument("--open", action="store_true", dest="open_browser")

    learning_parser = subparsers.add_parser("learning")
    learning_parser.add_argument("--root", required=True, type=Path)
    learning_parser.add_argument("--overwrite", action="store_true")

    cheko_parser = subparsers.add_parser("cheko-seed-cards")
    cheko_parser.add_argument("--root", required=True, type=Path)
    cheko_parser.add_argument("--next-due")

    receipt_parser = subparsers.add_parser("daily-receipt")
    receipt_parser.add_argument("--root", required=True, type=Path)
    receipt_parser.add_argument("--as-of")

    evolve_parser = subparsers.add_parser("night-evolve")
    evolve_parser.add_argument("--root", required=True, type=Path)
    evolve_parser.add_argument("--as-of")

    route_parser = subparsers.add_parser("route-map")
    route_parser.add_argument("--root", required=True, type=Path)
    route_parser.add_argument("--as-of")

    rag_parser = subparsers.add_parser("rag-query")
    rag_parser.add_argument("--root", required=True, type=Path)
    rag_parser.add_argument("--query", required=True)
    rag_parser.add_argument("--as-of")
    rag_parser.add_argument("--limit", default=6, type=int)
    rag_parser.add_argument(
        "--front",
        choices=("choice", "case", "essay"),
        action="append",
        default=[],
        dest="fronts",
    )

    semantic_parser = subparsers.add_parser("semantic-ingest")
    semantic_parser.add_argument("--root", required=True, type=Path)
    semantic_parser.add_argument("--text", required=True)
    semantic_parser.add_argument("--as-of")

    sync_parser = subparsers.add_parser("sync-sentinel")
    sync_parser.add_argument("--root", required=True, type=Path)
    sync_parser.add_argument("--as-of")
    sync_parser.add_argument(
        "--mode",
        required=True,
        choices=("offline-reconnect", "realtime"),
    )
    sync_parser.add_argument("--discord-log", type=Path)

    vault_parser = subparsers.add_parser("vault-sync")
    vault_parser.add_argument("--root", required=True, type=Path)
    vault_parser.add_argument("--overwrite", action="store_true")

    raw_vault_parser = subparsers.add_parser("raw-vault-sync")
    raw_vault_parser.add_argument("--root", required=True, type=Path)
    raw_vault_parser.add_argument("--overwrite", action="store_true")

    principles_parser = subparsers.add_parser("seed-principles")
    principles_parser.add_argument("--root", required=True, type=Path)
    principles_parser.add_argument("--next-due")

    export_parser = subparsers.add_parser("export-state")
    export_parser.add_argument("--root", required=True, type=Path)
    export_parser.add_argument("--as-of")

    import_parser = subparsers.add_parser("import-state")
    import_parser.add_argument("--file", required=True, type=Path, dest="snapshot_path")
    import_parser.add_argument("--root", type=Path)

    study_parser = subparsers.add_parser("study-turn")
    study_parser.add_argument("--root", required=True, type=Path)
    study_parser.add_argument("--topic", required=True)
    study_parser.add_argument("--user", required=True, dest="user_text")
    study_parser.add_argument("--assistant", required=True, dest="assistant_text")
    study_parser.add_argument("--learner-position", default="")
    study_parser.add_argument("--codex-position", default="")
    study_parser.add_argument("--destination", default="")
    study_parser.add_argument(
        "--front",
        choices=("choice", "case", "essay"),
        action="append",
        default=[],
        dest="fronts",
    )

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
    if args.command == "web":
        return cmd_web(
            args.root,
            host=args.host,
            port=args.port,
            as_of=_parse_date(args.as_of),
            open_browser=args.open_browser,
        )
    if args.command == "learning":
        return cmd_learning(args.root, overwrite=args.overwrite)
    if args.command == "cheko-seed-cards":
        return cmd_cheko_seed_cards(args.root, next_due=_parse_date(args.next_due))
    if args.command == "daily-receipt":
        return cmd_daily_receipt(args.root, as_of=_parse_date(args.as_of))
    if args.command == "night-evolve":
        return cmd_night_evolve(args.root, as_of=_parse_date(args.as_of))
    if args.command == "route-map":
        return cmd_route_map(args.root, as_of=_parse_date(args.as_of))
    if args.command == "rag-query":
        return cmd_rag_query(
            args.root,
            query=args.query,
            fronts=args.fronts,
            as_of=_parse_date(args.as_of),
            limit=args.limit,
        )
    if args.command == "semantic-ingest":
        return cmd_semantic_ingest(args.root, text=args.text, as_of=_parse_date(args.as_of))
    if args.command == "sync-sentinel":
        return cmd_sync_sentinel(
            args.root,
            mode=args.mode,
            discord_log=args.discord_log,
            as_of=_parse_date(args.as_of),
        )
    if args.command == "vault-sync":
        return cmd_vault_sync(args.root, overwrite=args.overwrite)
    if args.command == "raw-vault-sync":
        return cmd_raw_vault_sync(args.root, overwrite=args.overwrite)
    if args.command == "seed-principles":
        return cmd_seed_principles(args.root, next_due=_parse_date(args.next_due))
    if args.command == "export-state":
        return cmd_export_state(args.root, as_of=_parse_date(args.as_of))
    if args.command == "import-state":
        return cmd_import_state(args.snapshot_path, root=args.root)
    if args.command == "study-turn":
        return cmd_study_turn(
            args.root,
            topic=args.topic,
            user_text=args.user_text,
            assistant_text=args.assistant_text,
            fronts=args.fronts,
            learner_position=args.learner_position,
            codex_position=args.codex_position,
            destination=args.destination,
        )
    raise AssertionError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
