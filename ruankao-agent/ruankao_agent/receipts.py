from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path
from typing import Iterable

from .loop import build_daily_loop_snapshot, status_line
from .memory import MemoryDiagnostic, diagnose_memory
from .storage import MemoryCard, PracticeSession, RawRecord, ReviewLog, RuankaoStore


@dataclass(frozen=True, slots=True)
class DailyReceiptResult:
    as_of: date
    json_path: Path
    html_path: Path
    status: str


def daily_receipt_json_path(root: Path | str, as_of: date) -> Path:
    return Path(root) / "data" / "daily-receipts" / f"{as_of.isoformat()}.json"


def daily_receipt_html_path(root: Path | str, as_of: date) -> Path:
    return Path(root) / "reports" / "daily" / f"{as_of.isoformat()}.html"


def write_daily_receipt(root: Path | str, *, as_of: date | None = None) -> DailyReceiptResult:
    root_path = Path(root)
    day = as_of or date.today()
    store = RuankaoStore(root_path / "data" / "ruankao.db")
    store.initialize()
    schema_version = store.schema_version()

    records = store.list_raw_records()
    cards = store.list_memory_cards()
    review_logs = store.list_review_logs()
    practice_sessions = store.list_practice_sessions()
    reviews_today = [log for log in review_logs if log.reviewed_on == day]
    practice_today = [session for session in practice_sessions if session.created_on == day]
    due_cards = [card for card in cards if card.next_due is not None and card.next_due <= day]
    cheko_cards = [card for card in cards if card.title.startswith("Cheko")]
    cheko_due_cards = [card for card in cheko_cards if card.next_due is not None and card.next_due <= day]
    diagnostics = diagnose_memory(cards, review_logs, as_of=day)

    snapshot = build_daily_loop_snapshot(
        as_of=day,
        due_cards=len(due_cards),
        review_backlog_ratio=store.review_backlog_ratio(day),
    )
    payload = _receipt_payload(
        day=day,
        status=status_line(snapshot),
        phase=snapshot.phase_name,
        countdown=snapshot.countdown,
        risk=snapshot.risk_text,
        schema_version=schema_version,
        reserve_days_consumed=snapshot.reserve_days_consumed,
        review_backlog_ratio=snapshot.dashboard.review_backlog_ratio,
        records=records,
        cards=cards,
        review_logs=review_logs,
        reviews_today=reviews_today,
        practice_sessions=practice_sessions,
        practice_today=practice_today,
        diagnostics=list(diagnostics),
        due_cards=due_cards,
        cheko_cards=cheko_cards,
        cheko_due_cards=cheko_due_cards,
    )

    json_path = daily_receipt_json_path(root_path, day)
    html_path = daily_receipt_html_path(root_path, day)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(render_daily_receipt(payload), encoding="utf-8")

    return DailyReceiptResult(
        as_of=day,
        json_path=json_path,
        html_path=html_path,
        status=str(payload["status"]),
    )


def render_daily_receipt(payload: dict[str, object]) -> str:
    metrics = payload["metrics"]
    assert isinstance(metrics, dict)
    source_counts = payload["source_counts"]
    card_type_counts = payload["card_type_counts"]
    front_counts = payload["front_counts"]
    recent_records = payload["recent_records"]
    recent_cards = payload["recent_cards"]
    recent_reviews = payload["recent_reviews"]
    recent_practice = payload["recent_practice"]
    memory_diagnostics = payload["memory_diagnostics"]
    practice_front_counts = payload["practice_front_counts"]
    assert isinstance(source_counts, dict)
    assert isinstance(card_type_counts, dict)
    assert isinstance(front_counts, dict)
    assert isinstance(recent_records, list)
    assert isinstance(recent_cards, list)
    assert isinstance(recent_reviews, list)
    assert isinstance(recent_practice, list)
    assert isinstance(memory_diagnostics, list)
    assert isinstance(practice_front_counts, dict)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>日结回执 {escape(str(payload["as_of"]))}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172026;
      --muted: #5e6b73;
      --line: #cfd8dc;
      --paper: #ffffff;
      --band: #f5f7f5;
      --accent: #0f766e;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: #fbfcfb;
      line-height: 1.55;
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 24px 20px 48px;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      padding-bottom: 18px;
      margin-bottom: 16px;
    }}
    h1 {{
      margin: 0;
      font-size: 28px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 19px;
      line-height: 1.3;
    }}
    .status {{
      color: var(--muted);
      margin: 8px 0 0;
    }}
    section {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      padding: 16px;
      margin-top: 14px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px;
    }}
    .metric, .item {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--band);
      padding: 11px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 4px;
    }}
    .metric strong {{
      display: block;
      font-size: 19px;
      line-height: 1.25;
    }}
    .list {{
      display: grid;
      gap: 10px;
    }}
    .meta {{
      color: var(--muted);
      font-size: 12px;
      margin-top: 4px;
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>日结回执 {escape(str(payload["as_of"]))}</h1>
      <p class="status">{escape(str(payload["status"]))}</p>
    </header>
    <section>
      <h2>今日状态</h2>
      <div class="grid">
        {_metric("阶段", payload["phase"])}
        {_metric("倒计时", payload["countdown"])}
        {_metric("风险", payload["risk"])}
        {_metric("Schema", payload["schema_version"])}
        {_metric("复习积压", f'{float(payload["review_backlog_ratio"]):.0%}')}
        {_metric("到期卡片", metrics["due_cards"])}
        {_metric("Cheko 到期", metrics["cheko_due_cards"])}
      </div>
    </section>
    <section>
      <h2>库存</h2>
      <div class="grid">
        {_metric("原始材料", metrics["raw_records"])}
        {_metric("记忆卡", metrics["memory_cards"])}
        {_metric("今日复习", metrics["reviews_today"])}
        {_metric("今日练习", metrics["practice_today"])}
        {_metric("薄弱卡", metrics["weak_memory_cards"])}
        {_metric("Cheko 卡", metrics["cheko_cards"])}
        {_metric("冗余消耗", payload["reserve_days_consumed"])}
      </div>
    </section>
    <section>
      <h2>三源分布</h2>
      <div class="grid">{_count_cards(source_counts)}</div>
    </section>
    <section>
      <h2>卡片类型</h2>
      <div class="grid">{_count_cards(card_type_counts)}</div>
    </section>
    <section>
      <h2>题型覆盖</h2>
      <div class="grid">{_count_cards(front_counts)}</div>
    </section>
    <section>
      <h2>练习题型</h2>
      <div class="grid">{_count_cards(practice_front_counts)}</div>
    </section>
    <section>
      <h2>记忆诊断</h2>
      <div class="list">{_memory_diagnostics(memory_diagnostics)}</div>
    </section>
    <section>
      <h2>最近材料</h2>
      <div class="list">{_recent_records(recent_records)}</div>
    </section>
    <section>
      <h2>最近卡片</h2>
      <div class="list">{_recent_cards(recent_cards)}</div>
    </section>
    <section>
      <h2>最近复习</h2>
      <div class="list">{_recent_reviews(recent_reviews)}</div>
    </section>
    <section>
      <h2>最近练习</h2>
      <div class="list">{_recent_practice(recent_practice)}</div>
    </section>
  </main>
</body>
</html>
"""


def _receipt_payload(
    *,
    day: date,
    status: str,
    phase: str,
    countdown: str,
    risk: str,
    schema_version: str,
    reserve_days_consumed: int,
    review_backlog_ratio: float,
    records: list[RawRecord],
    cards: list[MemoryCard],
    review_logs: list[ReviewLog],
    reviews_today: list[ReviewLog],
    practice_sessions: list[PracticeSession],
    practice_today: list[PracticeSession],
    diagnostics: list[MemoryDiagnostic],
    due_cards: list[MemoryCard],
    cheko_cards: list[MemoryCard],
    cheko_due_cards: list[MemoryCard],
) -> dict[str, object]:
    return {
        "version": 1,
        "as_of": day.isoformat(),
        "status": status,
        "phase": phase,
        "countdown": countdown,
        "risk": risk,
        "schema_version": schema_version,
        "reserve_days_consumed": reserve_days_consumed,
        "review_backlog_ratio": review_backlog_ratio,
        "metrics": {
            "raw_records": len(records),
            "memory_cards": len(cards),
            "review_logs": len(review_logs),
            "reviews_today": len(reviews_today),
            "practice_sessions": len(practice_sessions),
            "practice_today": len(practice_today),
            "weak_memory_cards": sum(
                1 for diagnostic in diagnostics if diagnostic.status in {"leech", "unstable"}
            ),
            "due_cards": len(due_cards),
            "cheko_cards": len(cheko_cards),
            "cheko_due_cards": len(cheko_due_cards),
        },
        "source_counts": _count(record.source.value for record in records),
        "card_type_counts": _count(card.card_type.value for card in cards),
        "front_counts": _count(front.value for card in cards for front in card.fronts),
        "practice_front_counts": _count(session.front.value for session in practice_sessions),
        "memory_diagnostics": [
            {
                "card_id": diagnostic.card_id,
                "title": diagnostic.title,
                "card_type": diagnostic.card_type,
                "fronts": list(diagnostic.fronts),
                "status": diagnostic.status,
                "action": diagnostic.action,
                "total_reviews": diagnostic.total_reviews,
                "low_grade_reviews": diagnostic.low_grade_reviews,
                "last_grade": diagnostic.last_grade,
                "average_grade": diagnostic.average_grade,
                "next_due": diagnostic.next_due.isoformat() if diagnostic.next_due else None,
            }
            for diagnostic in diagnostics
            if diagnostic.status != "stable"
        ][:8],
        "recent_records": [
            {
                "id": record.id,
                "source": record.source.value,
                "summary": record.summary,
                "topics": list(record.topics),
                "promotion_status": record.promotion_status,
            }
            for record in records[-5:]
        ],
        "recent_cards": [
            {
                "id": card.id,
                "title": card.title,
                "card_type": card.card_type.value,
                "fronts": [front.value for front in card.fronts],
                "next_due": card.next_due.isoformat() if card.next_due else None,
                "review_count": card.review_count,
            }
            for card in cards[-8:]
        ],
        "recent_reviews": [
            {
                "id": log.id,
                "card_id": log.card_id,
                "reviewed_on": log.reviewed_on.isoformat(),
                "grade": log.grade,
                "retrieval_strength": log.retrieval_strength,
                "next_due": log.next_due.isoformat(),
            }
            for log in review_logs[-8:]
        ],
        "recent_practice": [
            {
                "id": session.id,
                "front": session.front.value,
                "topic": session.topic,
                "source": session.source,
                "score": session.score,
                "max_score": session.max_score,
                "duration_minutes": session.duration_minutes,
                "summary": session.summary,
                "mistakes": session.mistakes,
                "created_on": session.created_on.isoformat() if session.created_on else None,
            }
            for session in practice_sessions[-8:]
        ],
    }


def _count(values: Iterable[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def _metric(label: str, value: object) -> str:
    return (
        f'<div class="metric"><span>{escape(label)}</span>'
        f"<strong>{escape(str(value))}</strong></div>"
    )


def _count_cards(counts: dict[object, object]) -> str:
    if not counts:
        return '<div class="item">暂无数据</div>'
    return "".join(_metric(str(key), value) for key, value in counts.items())


def _recent_records(records: list[object]) -> str:
    if not records:
        return '<div class="item">暂无材料</div>'
    items = []
    for item in records:
        assert isinstance(item, dict)
        items.append(
            f"""<div class="item">
  <strong>#{escape(str(item["id"]))} {escape(str(item["source"]))}</strong>
  <div>{escape(str(item["summary"]))}</div>
  <div class="meta">status={escape(str(item["promotion_status"]))} | topics={escape(", ".join(str(topic) for topic in item["topics"]))}</div>
</div>"""
        )
    return "".join(items)


def _memory_diagnostics(diagnostics: list[object]) -> str:
    if not diagnostics:
        return '<div class="item">暂无薄弱诊断。继续保持复习节奏。</div>'
    items = []
    for item in diagnostics:
        assert isinstance(item, dict)
        items.append(
            f"""<div class="item">
  <strong>#{escape(str(item["card_id"]))} {escape(str(item["title"]))}</strong>
  <div>{escape(str(item["action"]))}</div>
  <div class="meta">status={escape(str(item["status"]))} | type={escape(str(item["card_type"]))} | low={escape(str(item["low_grade_reviews"]))} | last={escape(str(item["last_grade"]))} | avg={escape(str(item["average_grade"]))}</div>
</div>"""
        )
    return "".join(items)


def _recent_cards(cards: list[object]) -> str:
    if not cards:
        return '<div class="item">暂无卡片</div>'
    items = []
    for item in cards:
        assert isinstance(item, dict)
        items.append(
            f"""<div class="item">
  <strong>#{escape(str(item["id"]))} {escape(str(item["title"]))}</strong>
  <div class="meta">type={escape(str(item["card_type"]))} | fronts={escape(", ".join(str(front) for front in item["fronts"]))} | due={escape(str(item["next_due"]))} | reviews={escape(str(item["review_count"]))}</div>
</div>"""
        )
    return "".join(items)


def _recent_reviews(reviews: list[object]) -> str:
    if not reviews:
        return '<div class="item">暂无复习记录</div>'
    items = []
    for item in reviews:
        assert isinstance(item, dict)
        items.append(
            f"""<div class="item">
  <strong>review #{escape(str(item["id"]))} card #{escape(str(item["card_id"]))}</strong>
  <div class="meta">date={escape(str(item["reviewed_on"]))} | grade={escape(str(item["grade"]))} | strength={escape(str(item["retrieval_strength"]))} | next={escape(str(item["next_due"]))}</div>
</div>"""
        )
    return "".join(items)


def _recent_practice(sessions: list[object]) -> str:
    if not sessions:
        return '<div class="item">暂无练习记录</div>'
    items = []
    for item in sessions:
        assert isinstance(item, dict)
        score = _score_text(item["score"], item["max_score"])
        items.append(
            f"""<div class="item">
  <strong>#{escape(str(item["id"]))} {escape(str(item["front"]))} {escape(str(item["topic"]))}</strong>
  <div>{escape(str(item["summary"]))}</div>
  <div class="meta">score={escape(score)} | source={escape(str(item["source"]))} | duration={escape(str(item["duration_minutes"]))} | date={escape(str(item["created_on"]))}</div>
  <div class="meta">mistakes={escape(str(item["mistakes"]))}</div>
</div>"""
        )
    return "".join(items)


def _score_text(score: object, max_score: object) -> str:
    if score is None:
        return "none"
    if max_score is None:
        return str(score)
    return f"{score}/{max_score}"
