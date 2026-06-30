from __future__ import annotations

from html import escape

from .receipts_format import (
    _card_type_label,
    _count_cards,
    _front_label,
    _metric,
    _ratio_text,
    _source_label,
)
from .receipts_lists import (
    _memory_diagnostics,
    _rag_brief,
    _recent_cards,
    _recent_practice,
    _recent_records,
    _recent_reviews,
)


def render_daily_receipt_sections(payload: dict[str, object]) -> str:
    metrics = payload["metrics"]
    night_focus = payload.get("night_focus", {})
    source_counts = payload["source_counts"]
    card_type_counts = payload["card_type_counts"]
    front_counts = payload["front_counts"]
    recent_records = payload["recent_records"]
    recent_cards = payload["recent_cards"]
    recent_reviews = payload["recent_reviews"]
    recent_practice = payload["recent_practice"]
    memory_diagnostics = payload["memory_diagnostics"]
    practice_front_counts = payload["practice_front_counts"]
    rag_brief = payload["rag_brief"]
    assert isinstance(metrics, dict)
    assert isinstance(night_focus, dict)
    assert isinstance(source_counts, dict)
    assert isinstance(card_type_counts, dict)
    assert isinstance(front_counts, dict)
    assert isinstance(recent_records, list)
    assert isinstance(recent_cards, list)
    assert isinstance(recent_reviews, list)
    assert isinstance(recent_practice, list)
    assert isinstance(memory_diagnostics, list)
    assert isinstance(practice_front_counts, dict)
    assert isinstance(rag_brief, dict)

    return f"""{_night_focus_band(night_focus)}
    <section>
      <h2>今日状态</h2>
      <div class="grid">
        {_metric("阶段", payload["phase"])}
        {_metric("倒计时", payload["countdown"])}
        {_metric("风险", payload["risk"])}
        {_metric("数据版本", payload["schema_version"])}
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
        {_metric("练习得分率", _ratio_text(metrics["practice_score_ratio"]))}
        {_metric("薄弱卡", metrics["weak_memory_cards"])}
        {_metric("Cheko 卡", metrics["cheko_cards"])}
        {_metric("冗余消耗", payload["reserve_days_consumed"])}
      </div>
    </section>
    <section>
      <h2>三源分布</h2>
      <div class="grid">{_count_cards(source_counts, labeler=_source_label)}</div>
    </section>
    <section>
      <h2>卡片类型</h2>
      <div class="grid">{_count_cards(card_type_counts, labeler=_card_type_label)}</div>
    </section>
    <section>
      <h2>题型覆盖</h2>
      <div class="grid">{_count_cards(front_counts, labeler=_front_label)}</div>
    </section>
    <section>
      <h2>练习题型</h2>
      <div class="grid">{_count_cards(practice_front_counts, labeler=_front_label)}</div>
    </section>
    <section>
      <h2>记忆诊断</h2>
      <div class="list">{_memory_diagnostics(memory_diagnostics)}</div>
    </section>
    <section>
      <h2>RAG 控制</h2>
      {_rag_brief(rag_brief)}
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
    </section>"""


def _night_focus_band(focus: dict[object, object]) -> str:
    return f"""<section class="focus">
  <span>今晚焦点</span>
  <strong>{escape(str(focus.get("title", "今晚沉淀今天的增量")))}</strong>
  <p>{escape(str(focus.get("reason", "暂无额外风险。")))}</p>
  <p>{escape(str(focus.get("action", "维持当前学习闭环。")))}</p>
</section>"""
