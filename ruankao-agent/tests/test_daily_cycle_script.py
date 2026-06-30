from pathlib import Path


def test_daily_cycle_script_includes_closure_exports() -> None:
    script = Path(__file__).resolve().parents[2] / "run-daily-cycle.command"
    text = script.read_text(encoding="utf-8")

    assert "cheko-seed-cards" in text
    assert "seed-principles" in text
    assert "daily-receipt" in text
    assert "route-map" in text
    assert "rag-query" in text
    assert "night-evolve" in text
    assert "vault-sync" in text
    assert "raw-vault-sync" in text
    assert "export-state" in text
    assert text.index("route-map") < text.index("rag-query") < text.index("night-evolve")
    assert text.index("raw-vault-sync") < text.index("export-state")
    assert "软考达人每日闭环：$DAY" in text
    assert "1/9 Cheko 弱点入队" in text
    assert "5/9 生成 RAG 控制简报" in text
    assert "6/9 生成夜间进化草案" in text
    assert "9/9 导出本地状态" in text
    assert "每日闭环完成：$DAY" in text
    assert text.index("1/9 Cheko 弱点入队") < text.index("9/9 导出本地状态")


def test_automation_doc_is_learner_facing() -> None:
    doc = Path(__file__).resolve().parents[1] / "docs" / "AUTOMATION.md"
    text = doc.read_text(encoding="utf-8")

    assert "# 自动化闭环" in text
    assert "每日闭环" in text
    assert "导入 Cheko 弱区信号" in text
    assert "生成 RAG 记忆与进步控制简报" in text
    assert "同步 Mein / Du / Uns 三源材料到 Obsidian" in text
    assert "This project keeps scheduled work explicit" not in text


def test_start_workbench_script_announces_local_url() -> None:
    script = Path(__file__).resolve().parents[2] / "start-workbench.command"
    text = script.read_text(encoding="utf-8")

    assert "软考达人工作台" in text
    assert "地址：http://127.0.0.1:$PORT" in text
    assert "按 Ctrl-C 停止。" in text
    assert 'PORT="${RUANKAO_WORKBENCH_PORT:-8765}"' in text
    assert '--port "$PORT"' in text
