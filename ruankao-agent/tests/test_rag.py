from __future__ import annotations

import json
from datetime import date

from ruankao_agent.domain import CardType, ExamFront, SourceIdentity
from ruankao_agent.rag import build_rag_brief, build_rag_chunks, build_rag_documents, write_rag_brief
from ruankao_agent.memory import diagnose_memory
from ruankao_agent.storage import RuankaoStore


def test_rag_brief_combines_retrieval_with_progress_gates(tmp_path) -> None:
    root = tmp_path / "demo"
    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    store.add_raw_record(
        source=SourceIdentity.MEIN,
        text="高并发订单系统里，我只写了重试机制和备用机制，没有写响应度量。",
        summary="高并发方案卡点",
        topics=("高并发", "可用性"),
        fronts=(ExamFront.CASE,),
    )
    card_id = store.add_memory_card(
        card_type=CardType.COMPARISON,
        title="可用性 vs 可靠性",
        prompt="高并发场景下备用机制、恢复时间和成功率分别指向什么？",
        answer="备用和恢复时间优先指向可用性；长期无故障更偏可靠性。",
        fronts=(ExamFront.CHOICE, ExamFront.CASE),
        next_due=date(2026, 6, 29),
    )
    store.record_review(card_id=card_id, reviewed_on=date(2026, 6, 27), grade=1)
    store.record_review(card_id=card_id, reviewed_on=date(2026, 6, 28), grade=2)
    store.add_practice_session(
        front=ExamFront.CASE,
        topic="高并发订单案例",
        source="Cheko",
        score=5,
        max_score=15,
        duration_minutes=30,
        summary="写了重试和备用，但缺少响应度量。",
        mistakes="没有把 99.9% 成功率和 3 秒明确结果写成质量属性场景。",
        created_on=date(2026, 6, 29),
    )

    brief = build_rag_brief(
        store,
        query="高并发 备用机制 响应度量",
        fronts=(ExamFront.CASE,),
        as_of=date(2026, 6, 29),
        limit=5,
    )

    assert brief.progress_gates[0].kind == "weak-memory"
    assert brief.progress_gates[0].title == "可用性 vs 可靠性"
    assert "先处理「可用性 vs 可靠性」" in brief.recommended_action
    assert brief.retrieval_strategy == "sqlite-fts5-hybrid-progress"
    assert brief.corpus_size == 3
    assert brief.chunk_count >= 3
    assert any(hit.document.title == "可用性 vs 可靠性" for hit in brief.hits)
    assert any(hit.document.title == "高并发订单案例" for hit in brief.hits)
    assert any(hit.document.source_label == "Mein" for hit in brief.hits)
    assert all(hit.chunk_ref for hit in brief.hits)
    assert all(hit.score_breakdown for hit in brief.hits)
    assert any("fts_bm25" == name for hit in brief.hits for name, _value in hit.score_breakdown)
    assert any("FTS/BM25" in reason for hit in brief.hits for reason in hit.reasons)
    assert any("回答必须引用召回证据" in item for item in brief.answer_contract)


def test_rag_brief_writes_json_and_html(tmp_path) -> None:
    root = tmp_path / "demo"
    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    store.add_memory_card(
        card_type=CardType.SCENARIO,
        title="订单高并发质量场景",
        prompt="10 万同时下单时如何写质量属性场景？",
        answer="写清刺激、环境、响应和响应度量，例如 3 秒内返回明确结果。",
        fronts=(ExamFront.CASE, ExamFront.ESSAY),
        next_due=date(2026, 6, 29),
    )

    result = write_rag_brief(
        root,
        query="10 万同时下单 3 秒 明确结果",
        fronts=(ExamFront.CASE,),
        as_of=date(2026, 6, 29),
    )

    payload = json.loads(result.json_path.read_text(encoding="utf-8"))
    html = result.html_path.read_text(encoding="utf-8")

    assert result.hit_count >= 1
    assert payload["query"] == "10 万同时下单 3 秒 明确结果"
    assert payload["retrieval_strategy"] == "sqlite-fts5-hybrid-progress"
    assert payload["corpus_size"] == 1
    assert payload["chunk_count"] >= 1
    assert payload["hits"][0]["title"] == "订单高并发质量场景"
    assert payload["hits"][0]["chunk_ref"].startswith("memory:")
    assert payload["hits"][0]["retrieval_strategy"] == "sqlite-fts5-hybrid-progress"
    assert {item["name"] for item in payload["hits"][0]["score_breakdown"]} >= {
        "progress",
        "token",
        "fts_bm25",
        "front",
    }
    assert "RAG 记忆与进步控制" in html
    assert "检索策略：sqlite-fts5-hybrid-progress" in html
    assert "fts_bm25" in html
    assert "进步闸门" in html
    assert "召回证据" in html
    assert "回答契约" in html


def test_rag_chunks_long_documents_before_retrieval(tmp_path) -> None:
    root = tmp_path / "demo"
    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    store.add_raw_record(
        source=SourceIdentity.UNS,
        text="\n".join(
            [
                "第一段：质量属性场景需要刺激源、刺激、环境、制品、响应和响应度量。",
                "第二段：高并发订单系统要把 10 万同时下单写成性能或可用性场景。",
                "第三段：如果只写缓存、重试和备用机制，没有写 3 秒明确结果，就不是可评分答案。",
            ]
            * 8
        ),
        summary="质量属性长资料",
        topics=("质量属性", "高并发"),
        fronts=(ExamFront.CASE,),
    )
    documents = build_rag_documents(
        records=store.list_raw_records(),
        cards=store.list_memory_cards(),
        practice_sessions=store.list_practice_sessions(),
        diagnostics=diagnose_memory(store.list_memory_cards(), store.list_review_logs(), as_of=date(2026, 6, 29)),
        as_of=date(2026, 6, 29),
    )

    chunks = build_rag_chunks(documents, max_chars=180, overlap=30)

    assert len(documents) == 1
    assert len(chunks) > 1
    assert chunks[0].chunk_ref == "raw:1#c1"
    assert all(len(chunk.text) <= 180 for chunk in chunks)
