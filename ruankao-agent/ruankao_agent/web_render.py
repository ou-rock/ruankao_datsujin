from __future__ import annotations

from datetime import date
from html import escape

from .domain import ExamFront
from .memory import MemoryDiagnostic
from .storage import MemoryCard, PracticeSession
from .web_labels import (
    _card_type_label,
    _date_text,
    _duration_text,
    _front_label,
    _fronts_label,
    _gate_severity_label,
    _memory_status_label,
    _rag_status_label,
    _risk_label,
    _score_ratio_text,
    _score_text,
    _value_text,
)


def _front_checks(default_all: bool = False) -> str:
    checked = " checked" if default_all else ""
    return f"""<div class="checks" aria-label="题型">
  <label><input type="checkbox" name="fronts" value="choice"{checked}>选择</label>
  <label><input type="checkbox" name="fronts" value="case"{checked}>案例</label>
  <label><input type="checkbox" name="fronts" value="essay"{checked}>论文</label>
</div>"""


def _message(message: str) -> str:
    if not message:
        return ""
    return f'<div class="message" role="status">{escape(_message_text(message))}</div>'


def _message_text(message: str) -> str:
    if message == "review-saved":
        return "复习评分已记录。"
    if message.startswith("raw-record-") and message.endswith("-saved"):
        record_id = message.removeprefix("raw-record-").removesuffix("-saved")
        return f"三源材料 #{record_id} 已沉淀。"
    if message.startswith("memory-card-") and message.endswith("-saved"):
        card_id = message.removeprefix("memory-card-").removesuffix("-saved")
        return f"记忆卡 #{card_id} 已创建。"
    if message.startswith("principle-relation-") and message.endswith("-saved"):
        relation_id = message.removeprefix("principle-relation-").removesuffix("-saved")
        return f"原则链接 #{relation_id} 已连接。"
    if message.startswith("practice-session-") and message.endswith("-saved"):
        session_id = message.removeprefix("practice-session-").removesuffix("-saved")
        return f"练习记录 #{session_id} 已保存。"
    if message.startswith("study-turn-mein-") and message.endswith("-saved"):
        rest = message.removeprefix("study-turn-mein-").removesuffix("-saved")
        mein_id, _, du_id = rest.partition("-du-")
        return f"学习回合已沉淀：Mein #{mein_id}，Du #{du_id}。"
    if message.startswith("cheko-cards-created-"):
        rest = message.removeprefix("cheko-cards-created-")
        created, _, skipped = rest.partition("-skipped-")
        return f"Cheko 弱点已入队：新增 {created} 张，跳过 {skipped or '0'} 张。"
    if message.startswith("daily-receipt-") and message.endswith("-written"):
        day = message.removeprefix("daily-receipt-").removesuffix("-written")
        return f"{day} 日结回执已生成。"
    if message.startswith("night-evolution-"):
        rest = message.removeprefix("night-evolution-")
        day, _, tail = rest.partition("-actions-")
        actions = tail.removesuffix("-staged") if tail else "0"
        return f"{day} 夜间进化草案已生成，包含 {actions} 个动作。"
    if message.startswith("route-map-") and message.endswith("-written"):
        day = message.removeprefix("route-map-").removesuffix("-written")
        return f"{day} 三题型覆盖图已生成。"
    if message.startswith("rag-brief-") and message.endswith("-written"):
        day = message.removeprefix("rag-brief-").removesuffix("-written")
        return f"{day} RAG 控制简报已生成。"
    if message.startswith("state-export-") and message.endswith("-written"):
        day = message.removeprefix("state-export-").removesuffix("-written")
        return f"{day} 本地状态 JSON 已导出。"
    if message.startswith("vault-sync-written-"):
        rest = message.removeprefix("vault-sync-written-")
        written, _, skipped = rest.partition("-skipped-")
        return f"记忆卡已同步到 Obsidian：写入 {written} 个，跳过 {skipped or '0'} 个。"
    if message.startswith("raw-vault-sync-written-"):
        rest = message.removeprefix("raw-vault-sync-written-")
        written, _, skipped = rest.partition("-skipped-")
        return f"三源材料已同步到 Obsidian：写入 {written} 个，跳过 {skipped or '0'} 个。"
    return message


def _today_primary_action(
    *,
    due_cards: list[MemoryCard],
    diagnostics: list[MemoryDiagnostic],
    practice_sessions: list[PracticeSession],
) -> str:
    if due_cards:
        return f"先复习 {len(due_cards)} 张到期卡，低于 3 分立刻明天再见。"
    if diagnostics:
        diagnostic = diagnostics[0]
        return f"先修复 {diagnostic.title}：{diagnostic.action}"
    if not practice_sessions:
        return "先记录一次选择、案例或论文练习，建立题型手感基线。"
    return "开启一轮学习模式，把新的 Mein / Du / Uns 沉淀到底层。"


def _today_primary_reason(reasons: tuple[str, ...], due_cards: list[MemoryCard]) -> str:
    if reasons:
        return reasons[0]
    if due_cards:
        return "到期复习是今天最稳定的提分动作。"
    return "当前风险信号正常，继续保持最小闭环。"


def _rag_panel(brief: dict[str, object]) -> str:
    gates = brief.get("progress_gates", [])
    hits = brief.get("hits", [])
    assert isinstance(gates, list)
    assert isinstance(hits, list)
    gate = gates[0] if gates else None
    hit = hits[0] if hits else None
    return f"""<div class="split">
  <div>
    <h3>建议动作</h3>
    <div class="list">
      <div class="item">
        <div class="item-title">{escape(str(brief.get("recommended_action", "维持今日闭环。")))}</div>
        <div class="meta">查询：{escape(str(brief.get("query", "")))}</div>
      </div>
      {_rag_gate_item(gate)}
    </div>
  </div>
  <div>
    <h3>最高召回证据</h3>
    <div class="list">{_rag_hit_item(hit)}</div>
  </div>
</div>"""


def _rag_gate_item(gate: object) -> str:
    if not isinstance(gate, dict):
        return '<div class="item">暂无进步闸门。</div>'
    return f"""<div class="item">
  <div class="item-title"><span>{escape(str(gate.get("title", "")))}</span><span>{escape(_gate_severity_label(gate.get("severity")))}</span></div>
  <div>{escape(str(gate.get("reason", "")))}</div>
  <div class="meta">{escape(str(gate.get("action", "")))}</div>
</div>"""


def _rag_hit_item(hit: object) -> str:
    if not isinstance(hit, dict):
        return '<div class="item">暂无召回证据。</div>'
    return f"""<div class="item">
  <div class="item-title"><span>{escape(str(hit.get("title", "")))}</span><span>{escape(str(hit.get("source_label", "")))}</span></div>
  <div>{escape(str(hit.get("snippet", "")))}</div>
  <div class="meta-row">
    <span>{escape(str(hit.get("ref", "")))}</span>
    <span>{escape(str(hit.get("chunk_ref", "")))}</span>
    <span>{escape(str(hit.get("retrieval_strategy", "")))}</span>
    <span>得分：{escape(str(hit.get("score", "")))}</span>
    <span>状态：{escape(_rag_status_label(hit.get("progress_status")))}</span>
  </div>
  <div class="meta">{escape(str(hit.get("action_hint", "")))}</div>
</div>"""


def _front_overview(
    cards: list[MemoryCard],
    due_cards: list[MemoryCard],
    practice_sessions: list[PracticeSession],
    today: date,
) -> list[dict[str, object]]:
    labels = {
        ExamFront.CHOICE: "选择题",
        ExamFront.CASE: "案例题",
        ExamFront.ESSAY: "论文题",
    }
    rows: list[dict[str, object]] = []
    for front in (ExamFront.CHOICE, ExamFront.CASE, ExamFront.ESSAY):
        front_cards = [card for card in cards if front in card.fronts]
        front_due = [card for card in due_cards if front in card.fronts]
        front_practice = [session for session in practice_sessions if session.front == front]
        practice_today = [session for session in front_practice if session.created_on == today]
        if front_due:
            state = "red"
            action = "先清到期卡"
        elif not practice_today:
            state = "yellow"
            action = "今天补一次练习"
        else:
            state = "green"
            action = "保持节奏"
        rows.append(
            {
                "front": front.value,
                "label": labels[front],
                "state": state,
                "cards": len(front_cards),
                "due": len(front_due),
                "practice_today": len(practice_today),
                "action": action,
            }
        )
    return rows


def _front_cards(rows: list[dict[str, object]]) -> str:
    cards = []
    for row in rows:
        raw_state = str(row["state"])
        state = escape(raw_state)
        state_label = escape(_risk_label(raw_state))
        cards.append(
            f"""<div class="front-card {state}">
  <div class="front-head"><span>{escape(str(row["label"]))}</span><span class="front-state {state}">{state_label}</span></div>
  <div class="front-metrics">
    <div class="front-mini"><span>卡片</span><strong>{escape(str(row["cards"]))}</strong></div>
    <div class="front-mini"><span>到期</span><strong>{escape(str(row["due"]))}</strong></div>
    <div class="front-mini"><span>今日练习</span><strong>{escape(str(row["practice_today"]))}</strong></div>
  </div>
  <div class="front-action">{escape(str(row["action"]))}</div>
</div>"""
        )
    return "".join(cards)


def _status_summary(snapshot) -> str:
    backlog = snapshot.dashboard.review_backlog_ratio
    due_cards = snapshot.dashboard.due_cards
    return (
        f"{snapshot.countdown} · {snapshot.phase_name} · {_risk_label(snapshot.risk_text)} "
        f"· 到期 {due_cards} · 积压 {backlog:.0%}"
    )


def _promotion_status_radios() -> str:
    statuses = (
        ("raw", "原始", True),
        ("extracted", "已提炼", False),
        ("tested", "已检验", False),
        ("promoted", "已升格", False),
        ("rejected", "已淘汰", False),
    )
    buttons = []
    for value, label, checked in statuses:
        checked_attr = " checked" if checked else ""
        buttons.append(
            f'<label><input type="radio" name="promotion_status" value="{value}"{checked_attr}>{escape(label)}</label>'
        )
    return "\n                ".join(buttons)


def _relation_radios() -> str:
    relations = (
        ("supports", "支撑", True),
        ("constrains", "制约", False),
        ("conflicts_with", "冲突", False),
        ("derived_from", "派生", False),
    )
    buttons = []
    for value, label, checked in relations:
        checked_attr = " checked" if checked else ""
        buttons.append(
            f'<label><input type="radio" name="relation" value="{value}"{checked_attr}>{escape(label)}</label>'
        )
    return "\n                ".join(buttons)


def _card_list(cards: list[MemoryCard], *, with_review: bool, today: date) -> str:
    if not cards:
        return '<div class="empty">还没有内容。下一步先沉淀一条材料或创建一张卡。</div>'
    items = []
    for card in reversed(cards):
        review_form = ""
        if with_review:
            review_form = f"""
            <form method="post" action="/reviews" style="margin-top:8px;">
              <input type="hidden" name="card_id" value="{card.id}">
              <input type="hidden" name="reviewed_on" value="{escape(today.isoformat())}">
              <div class="grade-row" aria-label="复习评分">
                {_review_grade_buttons()}
              </div>
            </form>
            """
        items.append(
            f"""<div class="item">
  <div class="item-title"><span>#{card.id} {escape(card.title)}</span><span>{escape(_card_type_label(card.card_type))}</span></div>
  <div class="meta-row">
    <span>题型：{escape(_fronts_label(card.fronts))}</span>
    <span>到期：{escape(_date_text(card.next_due))}</span>
    <span>复习：{card.review_count}次</span>
  </div>
  <div class="meta">{escape(card.prompt[:140])}</div>
  {review_form}
</div>"""
        )
    return '<div class="list">' + "".join(items) + "</div>"


def _review_grade_buttons() -> str:
    labels = (
        (5, "很稳"),
        (4, "会"),
        (3, "勉强"),
        (2, "模糊"),
        (1, "不会"),
        (0, "空白"),
    )
    buttons = []
    for grade, label in labels:
        low = " low" if grade < 3 else ""
        buttons.append(
            f"""<button class="grade-button{low}" type="submit" name="grade" value="{grade}" title="{grade} {escape(label)}">
  <span>{grade}</span><small>{escape(label)}</small>
</button>"""
        )
    return "".join(buttons)


def _practice_list(sessions: list[PracticeSession]) -> str:
    if not sessions:
        return '<div class="empty">还没有练习记录。先记录一次选择、案例或论文练习。</div>'
    items = []
    for session in reversed(sessions):
        score = _score_text(session.score, session.max_score)
        ratio = _score_ratio_text(session.score, session.max_score)
        items.append(
            f"""<div class="item">
  <div class="item-title"><span>#{session.id} {escape(session.topic)}</span><span>{escape(_front_label(session.front))}</span></div>
  <div class="meta-row">
    <span>得分：{escape(score)}</span>
    <span>得分率：{escape(ratio)}</span>
    <span>来源：{escape(_value_text(session.source))}</span>
    <span>耗时：{escape(_duration_text(session.duration_minutes))}</span>
    <span>日期：{escape(_date_text(session.created_on))}</span>
  </div>
  <div class="meta">{escape(session.summary[:140])}</div>
</div>"""
        )
    return '<div class="list">' + "".join(items) + "</div>"


def _risk_reason_list(reasons: tuple[str, ...]) -> str:
    items = [f'<div class="item">{escape(reason)}</div>' for reason in reasons]
    return '<div class="list">' + "".join(items) + "</div>"


def _diagnostic_list(diagnostics: list[MemoryDiagnostic]) -> str:
    if not diagnostics:
        return '<div class="empty">暂无薄弱诊断。先完成今日复习。</div>'
    items = []
    for diagnostic in diagnostics:
        items.append(
            f"""<div class="item">
  <div class="item-title"><span>#{diagnostic.card_id} {escape(diagnostic.title)}</span><span>{escape(_memory_status_label(diagnostic.status))}</span></div>
  <div class="meta">{escape(diagnostic.action)}</div>
  <div class="meta-row">
    <span>低分：{diagnostic.low_grade_reviews}次</span>
    <span>最近：{escape(_value_text(diagnostic.last_grade))}</span>
    <span>平均：{escape(_value_text(diagnostic.average_grade))}</span>
  </div>
</div>"""
        )
    return '<div class="list">' + "".join(items) + "</div>"
