from pathlib import Path


COMMAND_ROOT = Path(__file__).resolve().parents[2] / ".codex" / "commands"


def test_architect_review_command_uses_learner_facing_terms() -> None:
    text = (COMMAND_ROOT / "ruankao-architect-review.md").read_text(encoding="utf-8")

    assert "核心七原则" in text
    assert "三源材料、记忆卡、原则卡或练习记录" in text
    assert "原则关系只标成候选冲突或候选链接" in text
    assert "Core Seven" not in text
    assert "raw record" not in text
    assert "memory card" not in text
    assert "practice session" not in text


def test_daily_command_docs_hide_internal_stage_labels() -> None:
    daily_cycle = (COMMAND_ROOT / "ruankao-daily-cycle.md").read_text(encoding="utf-8")
    night_evolve = (COMMAND_ROOT / "ruankao-night-evolve.md").read_text(encoding="utf-8")
    daily_close = (COMMAND_ROOT / "ruankao-daily-close.md").read_text(encoding="utf-8")
    learning = (COMMAND_ROOT / "ruankao-learning.md").read_text(encoding="utf-8")
    rag_query = (COMMAND_ROOT / "ruankao-rag-query.md").read_text(encoding="utf-8")

    assert "仅暂存的夜间进化草案" in daily_cycle
    assert "RAG 记忆与进步控制简报" in daily_cycle
    assert "只生成暂存计划" in night_evolve
    assert "网页回执" in daily_close
    assert "JSON 数据路径" in daily_close
    assert "RAG 控制简报" in daily_close
    assert "学习台网页资料" in learning
    assert "SQLite 仍是唯一事实源" in rag_query
    assert "召回证据、进步闸门、建议动作和回答契约" in rag_query
    assert "stage-only" not in daily_cycle
    assert "stage-only" not in night_evolve
    assert "staged plan" not in night_evolve
    assert "live skill" not in night_evolve


def test_workbench_command_documents_port_recovery() -> None:
    text = (COMMAND_ROOT / "ruankao-workbench.md").read_text(encoding="utf-8")

    assert "http://127.0.0.1:8765" in text
    assert "/ruankao-workbench --port 8770" in text
    assert "如果端口占用" in text


def test_ux_check_command_requires_browser_act_real_browsing() -> None:
    text = (COMMAND_ROOT / "ruankao-ux-check.md").read_text(encoding="utf-8")

    assert "browser-act 实际打开本地页面" in text
    assert "不能只靠源码阅读" in text
    assert "python3 -m ruankao_agent.cli learning" in text
    assert "--overwrite" in text
    assert "wait stable" in text
    assert "关闭 browser-act session" in text
