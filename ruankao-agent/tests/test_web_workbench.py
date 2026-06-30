from __future__ import annotations

from datetime import date
from urllib.parse import parse_qs

from ruankao_agent.domain import CardType, ExamFront, SourceIdentity
from ruankao_agent.storage import RuankaoStore
from ruankao_agent.web import (
    WorkbenchApp,
    WorkbenchConfig,
    _export_relative_path,
    _learning_relative_path,
    _report_relative_path,
    _vault_relative_path,
)


def test_workbench_home_is_an_actionable_control_panel(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))

    html = app.render_home()

    assert "<title>软考达人工作台 · D-117 · 绿灯</title>" in html
    assert "软考达人工作台" in html
    assert "D-117 | 启动诊断 | 绿灯 | 到期=0 | 积压=0%" in html
    assert '<div class="metric"><span>风险</span><strong>绿灯</strong></div>' in html
    assert 'class="skip-link" href="#today"' in html
    assert "今日闭环" in html
    assert "今日第一动作" in html
    assert "处理今日闭环" in html
    assert "三题型雷达" in html
    assert "选择题" in html
    assert "案例题" in html
    assert "论文题" in html
    assert "学习信号" in html
    assert "把 Cheko 弱点入队" in html
    assert "记忆诊断" in html
    assert "今日产物生成" in html
    assert "风险原因" in html
    assert "生成日结回执" in html
    assert "生成夜间进化草案" in html
    assert "生成三题型覆盖图" in html
    assert "导出本地状态 JSON" in html
    assert "收束完成、缺口和明日最低动作" in html
    assert "检查选择、案例、论文是否失衡" in html
    assert "练习记录" in html
    assert "记录一次练习至少留下题型、得分或完成量、错因，以及下一步补救动作" in html
    assert "三源录入" in html
    assert "记忆卡" in html
    assert "一张合格记忆卡要能触发回忆、能自评、能映射到选择/案例/论文" in html
    assert "原则网络" in html
    assert 'href="/learning/"' in html
    assert 'action="/daily/receipt"' in html
    assert 'action="/night/evolve"' in html
    assert 'action="/routes/map"' in html
    assert 'action="/state/export"' in html
    assert 'action="/cheko/cards"' in html
    assert 'action="/practice"' in html
    assert 'action="/vault/sync"' in html
    assert 'action="/vault/sync-raw"' in html
    assert 'action="/records"' in html
    assert 'action="/cards"' in html
    assert 'action="/relations"' in html
    assert (root / "data" / "ruankao.db").exists()
    assert (root / "dashboard.html").exists()
    assert (root / "learning" / "index.html").exists()
    assert (root / "learning" / "lessons" / "0001-scene-before-solution.html").exists()
    assert (root / "vault" / "00-map" / "原则网络.md").exists()
    assert (root / "vault" / "10-memory-war-room" / "principles" / "场景先于方案.md").exists()


def test_workbench_message_is_announced_as_status(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))

    html = app.render_home(message="review-saved")

    assert '<div class="message" role="status">复习评分已记录。</div>' in html
    assert "review-saved" not in html


def test_workbench_messages_translate_common_action_slugs(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))

    messages = {
        "raw-record-3-saved": "三源材料 #3 已沉淀。",
        "memory-card-5-saved": "记忆卡 #5 已创建。",
        "practice-session-7-saved": "练习记录 #7 已保存。",
        "cheko-cards-created-4-skipped-1": "Cheko 弱点已入队：新增 4 张，跳过 1 张。",
        "daily-receipt-2026-06-29-written": "2026-06-29 日结回执已生成。",
        "night-evolution-2026-06-29-actions-3-staged": "2026-06-29 夜间进化草案已生成，包含 3 个动作。",
        "route-map-2026-06-29-written": "2026-06-29 三题型覆盖图已生成。",
        "state-export-2026-06-29-written": "2026-06-29 本地状态 JSON 已导出。",
        "vault-sync-written-2-skipped-1": "记忆卡已同步到 Obsidian：写入 2 个，跳过 1 个。",
        "raw-vault-sync-written-1-skipped-0": "三源材料已同步到 Obsidian：写入 1 个，跳过 0 个。",
    }

    for slug, text in messages.items():
        html = app.render_home(message=slug)
        assert f'<div class="message" role="status">{text}</div>' in html
        assert slug not in html


def test_workbench_home_shows_three_front_radar_with_due_state(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()
    app.add_memory_card(
        parse_qs(
            "card_type=concept&title=质量属性场景&prompt=六要素是什么"
            "&answer=刺激源、刺激、环境、制品、响应、响应度量"
            "&fronts=case&next_due=2026-06-29"
        )
    )
    app.add_practice_session(
        parse_qs("front=choice&topic=选择题 10 道&summary=概念复盘&created_on=2026-06-29")
    )

    html = app.render_home()

    assert 'aria-label="三题型雷达"' in html
    assert '<div class="front-head"><span>案例题</span><span class="front-state red">红灯</span></div>' in html
    assert '<div class="front-head"><span>选择题</span><span class="front-state green">绿灯</span></div>' in html
    assert "今天补一次练习" in html


def test_workbench_home_prioritizes_due_review_in_first_action(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()
    app.add_memory_card(
        parse_qs(
            "card_type=concept&title=质量属性场景&prompt=六要素是什么"
            "&answer=刺激源、刺激、环境、制品、响应、响应度量"
            "&fronts=case&next_due=2026-06-29"
        )
    )

    html = app.render_home()

    assert "今日第一动作" in html
    assert "先复习 1 张到期卡" in html
    assert "risk-red" in html


def test_due_card_review_uses_one_tap_grade_buttons(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()
    app.add_memory_card(
        parse_qs(
            "card_type=concept&title=权衡点&prompt=什么是权衡点"
            "&answer=影响多个质量属性的取舍点&fronts=case&next_due=2026-06-29"
        )
    )

    html = app.render_home()

    assert 'class="grade-row"' in html
    assert "<span>#1 权衡点</span><span>概念卡</span>" in html
    assert "题型=案例题" in html
    assert "到期=2026-06-29" in html
    assert "复习=0次" in html
    assert 'name="grade" value="5"' in html
    assert 'name="grade" value="0"' in html
    assert 'class="grade-button low"' in html
    assert "<select name=\"grade\">" not in html


def test_practice_front_uses_segmented_radio_control(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))

    html = app.render_home()

    assert 'class="segmented" aria-label="练习题型"' in html
    assert 'type="radio" name="front" value="choice" checked' in html
    assert 'type="radio" name="front" value="case"' in html
    assert 'type="radio" name="front" value="essay"' in html
    assert '<select name="front">' not in html


def test_practice_numeric_fields_have_browser_constraints(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))

    html = app.render_home()

    assert 'type="number" name="score" min="0" step="0.5"' in html
    assert 'type="number" name="max_score" min="1" step="0.5"' in html
    assert 'type="number" name="duration_minutes" min="1" step="1"' in html
    assert 'type="number" name="source_record_id" min="1" step="1"' in html
    assert 'type="number" name="from_card_id" min="1" step="1"' in html
    assert 'type="number" name="to_card_id" min="1" step="1"' in html


def test_workbench_textareas_have_learning_placeholders(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))

    html = app.render_home()

    assert 'placeholder="得分点、卡点、暴露出的知识边界"' in html
    assert 'placeholder="错因、混淆项、下一次避免方式"' in html
    assert 'placeholder="保留原话、文章摘录、对话片段或个人经验"' in html
    assert 'placeholder="一句话写清它为什么值得留下"' in html
    assert 'placeholder="看到什么场景时要想起这张卡？"' in html
    assert 'placeholder="可直接检索的答案、原则或表达"' in html
    assert 'placeholder="说明这两个原则如何支撑、制约、冲突或派生"' in html


def test_raw_record_source_uses_segmented_radio_control(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))

    html = app.render_home()

    assert 'class="segmented" aria-label="三源来源"' in html
    assert 'type="radio" name="source" value="mein" checked' in html
    assert 'type="radio" name="source" value="du"' in html
    assert 'type="radio" name="source" value="uns"' in html
    assert 'class="source-guide" aria-label="三源边界"' in html
    assert "Mein：</strong>我的原话和卡点" in html
    assert "Du：</strong>Codex 的整理和纠偏" in html
    assert "Uns：</strong>外界资料和证据" in html
    assert '<select name="source">' not in html


def test_raw_record_status_uses_segmented_radio_control(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))

    html = app.render_home()

    assert 'class="segmented flow" aria-label="三源状态"' in html
    assert 'type="radio" name="promotion_status" value="raw" checked>原始' in html
    assert 'type="radio" name="promotion_status" value="extracted">已提炼' in html
    assert 'type="radio" name="promotion_status" value="tested">已检验' in html
    assert 'type="radio" name="promotion_status" value="promoted">已升格' in html
    assert 'type="radio" name="promotion_status" value="rejected">已淘汰' in html
    assert '<select name="promotion_status">' not in html


def test_principle_relation_uses_segmented_radio_control(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))

    html = app.render_home()

    assert 'class="segmented flow" aria-label="原则关系"' in html
    assert 'type="radio" name="relation" value="supports" checked>支撑' in html
    assert 'type="radio" name="relation" value="constrains">制约' in html
    assert 'type="radio" name="relation" value="conflicts_with">冲突' in html
    assert 'type="radio" name="relation" value="derived_from">派生' in html
    assert "只连接有真实逻辑张力的原则" in html
    assert '<select name="relation">' not in html


def test_workbench_forms_write_store_and_principle_note(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()

    record_id = app.add_raw_record(
        parse_qs(
            "source=mein&text=先看业务约束&summary=场景先于方案&topics=架构评估&fronts=case&fronts=essay"
        )
    )
    card_id = app.add_memory_card(
        parse_qs(
            "card_type=principle&title=场景先于方案&prompt=做架构论证时"
            "&answer=先确认目标、边界、约束，再谈方案&source_record_id=1"
            "&fronts=choice&fronts=case&fronts=essay&next_due=2026-06-29"
            "&conflicts=技术先行"
        )
    )
    app.record_review(parse_qs(f"card_id={card_id}&reviewed_on=2026-06-29&grade=5"))

    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    record = store.list_raw_records()[0]
    card = store.get_memory_card(card_id)

    assert record.id == record_id
    assert record.source is SourceIdentity.MEIN
    assert record.fronts == (ExamFront.CASE, ExamFront.ESSAY)
    assert card.card_type is CardType.PRINCIPLE
    assert card.review_count == 1
    assert card.next_due is not None

    note = root / "vault" / "10-memory-war-room" / "principles" / "场景先于方案.md"
    assert note.exists()
    assert "[[技术先行]]" in note.read_text(encoding="utf-8")


def test_workbench_forms_write_practice_session(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()

    session_id = app.add_practice_session(
        parse_qs(
            "front=case&topic=质量属性效用树&source=真题&score=8&max_score=15"
            "&duration_minutes=35&summary=能列出场景但度量不够具体"
            "&mistakes=响应和响应度量混写&created_on=2026-06-29"
        )
    )

    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    sessions = store.list_practice_sessions()
    html = app.render_home()

    assert sessions[0].id == session_id
    assert sessions[0].front == ExamFront.CASE
    assert sessions[0].score == 8
    assert sessions[0].max_score == 15
    assert sessions[0].duration_minutes == 35
    assert "质量属性效用树" in html
    assert "<span>#1 质量属性效用树</span><span>案例题</span>" in html
    assert "8/15" in html
    assert "得分率=53%" in html
    assert "耗时=35分钟" in html


def test_workbench_lists_render_missing_values_as_unrecorded(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()
    app.add_memory_card(
        parse_qs(
            "card_type=concept&title=未归类概念&prompt=先占位"
            "&answer=稍后补充"
        )
    )
    app.add_practice_session(
        parse_qs("front=choice&topic=选择题速记&summary=只记录了结论")
    )

    html = app.render_home()

    assert "题型=未记录 | 到期=未记录 | 复习=0次" in html
    assert "得分=未记录 | 得分率=未记录 | 来源=未记录 | 耗时=未记录 | 日期=2026-06-29" in html
    assert "到期=none" not in html
    assert "得分=none" not in html
    assert "来源=none" not in html


def test_workbench_can_seed_cheko_cards_from_learning_signal_action(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()

    result = app.seed_cheko_cards(parse_qs("next_due=2026-06-29"))

    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    cards = store.list_memory_cards()

    assert len(result.created_card_ids) == 4
    assert store.count_due_cards(date(2026, 6, 29)) == 4
    assert {card.title for card in cards} >= {
        "Cheko错题池：系统架构设计",
        "Cheko错题池：软件工程",
        "Cheko错题池：系统分析与设计",
        "Cheko论文最低触达",
    }
    assert "Cheko 记忆卡" in app.render_home()


def test_workbench_home_surfaces_memory_diagnostics(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()
    card_id = app.add_memory_card(
        parse_qs(
            "card_type=comparison&title=敏感点 vs 权衡点&prompt=二者边界"
            "&answer=敏感点影响一个属性，权衡点影响多个属性"
            "&fronts=choice&fronts=case&next_due=2026-06-29"
        )
    )
    app.record_review(parse_qs(f"card_id={card_id}&reviewed_on=2026-06-27&grade=1"))
    app.record_review(parse_qs(f"card_id={card_id}&reviewed_on=2026-06-28&grade=2"))

    html = app.render_home()

    assert "敏感点 vs 权衡点" in html
    assert "leech" in html
    assert "拆成更小卡片" in html


def test_workbench_can_write_and_serve_daily_receipt(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()
    app.seed_cheko_cards(parse_qs("next_due=2026-06-29"))

    result = app.write_daily_receipt(parse_qs("as_of=2026-06-29"))
    html = app.render_report_file("daily/2026-06-29.html")
    home = app.render_home()

    assert result.as_of == date(2026, 6, 29)
    assert "日结回执 2026-06-29" in html
    assert "Cheko 到期" in html
    assert 'href="/reports/daily/2026-06-29.html"' in home


def test_workbench_can_write_and_serve_night_evolution_plan(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()
    app.seed_cheko_cards(parse_qs("next_due=2026-06-29"))

    result = app.write_night_evolution_plan(parse_qs("as_of=2026-06-29"))
    html = app.render_report_file("nightly/2026-06-29.html")
    home = app.render_home()

    assert result.as_of == date(2026, 6, 29)
    assert result.stage_only is True
    assert "夜间进化草案 2026-06-29" in html
    assert "写明日三动作" in html
    assert "write-tomorrow-plan" not in html
    assert 'href="/reports/nightly/2026-06-29.html"' in home


def test_workbench_can_write_and_serve_route_map(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()
    app.seed_cheko_cards(parse_qs("next_due=2026-06-29"))

    result = app.write_route_map(parse_qs("as_of=2026-06-29"))
    html = app.render_report_file("routes/2026-06-29.html")
    home = app.render_home()

    assert result.as_of == date(2026, 6, 29)
    assert "三题型覆盖图 2026-06-29" in html
    assert "选择题" in html
    assert "论文题" in html
    assert 'href="/reports/routes/2026-06-29.html"' in home


def test_workbench_can_export_and_serve_local_state(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()
    app.add_memory_card(
        parse_qs(
            "card_type=concept&title=质量属性场景&prompt=六要素是什么"
            "&answer=刺激源、刺激、环境、制品、响应、响应度量"
            "&fronts=case"
        )
    )

    result = app.write_state_export(parse_qs("as_of=2026-06-29"))
    payload = app.render_export_file("state-2026-06-29.json")
    home = app.render_home()

    assert result.as_of == date(2026, 6, 29)
    assert '"memory_cards": 1' in payload
    assert "质量属性场景" in payload
    assert 'href="/exports/state-2026-06-29.json"' in home


def test_workbench_can_sync_memory_cards_to_vault(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()
    app.add_memory_card(
        parse_qs(
            "card_type=concept&title=质量属性场景&prompt=六要素是什么"
            "&answer=刺激源、刺激、环境、制品、响应、响应度量"
            "&fronts=choice&fronts=case"
        )
    )

    result = app.sync_memory_cards_to_vault(parse_qs(""))

    note = root / "vault" / "10-memory-war-room" / "concepts" / "质量属性场景.md"
    assert len(result.written_paths) == 1
    assert note.exists()
    assert "type: memory-card" in note.read_text(encoding="utf-8")


def test_workbench_can_sync_raw_records_to_vault(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()
    app.add_raw_record(
        parse_qs(
            "source=mein&text=我把可用性和可靠性混淆了"
            "&summary=可用性可靠性混淆&topics=质量属性&fronts=choice"
        )
    )

    result = app.sync_raw_records_to_vault(parse_qs(""))

    notes = list((root / "vault" / "20-mein").glob("*.md"))
    assert len(result.written_paths) == 1
    assert len(notes) == 1
    assert "type: raw-record" in notes[0].read_text(encoding="utf-8")


def test_workbench_status_json_exposes_current_route(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()

    payload = app.render_status_json()

    assert '"countdown": "D-117"' in payload
    assert '"phase": "启动诊断"' in payload
    assert '"risk_reasons": [' in payload
    assert "当前风险信号正常" in payload
    assert str(root / "vault") in payload
    assert str(root / "learning") in payload


def test_workbench_status_json_explains_practice_gap_risk(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()
    app.add_practice_session(
        parse_qs(
            "front=choice&topic=选择题 10 道&summary=只做选择题"
            "&created_on=2026-06-29"
        )
    )

    payload = app.render_status_json()

    assert '"risk": "red"' in payload
    assert "本周缺席 2 个以上题型" in payload


def test_vault_request_paths_are_decoded_before_file_lookup() -> None:
    assert (
        _vault_relative_path("/vault/10-memory-war-room/principles/%E5%9C%BA%E6%99%AF.md")
        == "10-memory-war-room/principles/场景.md"
    )


def test_learning_request_paths_are_decoded_before_file_lookup() -> None:
    assert (
        _learning_relative_path("/learning/reference/%E5%9B%9B%E5%A4%A7.html")
        == "reference/四大.html"
    )


def test_report_request_paths_are_decoded_before_file_lookup() -> None:
    assert (
        _report_relative_path("/reports/daily/%E6%97%A5%E7%BB%93.html")
        == "daily/日结.html"
    )


def test_export_request_paths_are_decoded_before_file_lookup() -> None:
    assert (
        _export_relative_path("/exports/state-%E6%97%A5%E7%BB%93.json")
        == "state-日结.json"
    )


def test_learning_file_lookup_serves_study_pages(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()

    html = app.render_learning_file("lessons/0001-scene-before-solution.html")

    assert "场景先于方案" in html
    assert "选择题易错点" in html


def test_vault_file_lookup_serves_chinese_paths(tmp_path) -> None:
    root = tmp_path / "demo"
    app = WorkbenchApp(WorkbenchConfig(root=root, as_of=date(2026, 6, 29)))
    app.initialize()
    from ruankao_agent.web import _handler_for
    handler_cls = _handler_for(app)

    captured: dict[str, str | int] = {}

    class FakeHandler(handler_cls):  # type: ignore[misc, valid-type]
        def send_error(self, code: int, message: str | None = None) -> None:
            captured["error"] = code

        def _send_text(self, text: str, content_type: str) -> None:  # type: ignore[override]
            captured["text"] = text
            captured["content_type"] = content_type

    handler = object.__new__(FakeHandler)
    handler._send_vault_file("10-memory-war-room/principles/场景先于方案.md")

    assert "场景先于方案" in str(captured["text"])
