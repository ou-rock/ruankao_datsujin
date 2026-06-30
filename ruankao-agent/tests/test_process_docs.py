from pathlib import Path


DOCS_ROOT = Path(__file__).resolve().parents[1] / "docs"
REPO_ROOT = Path(__file__).resolve().parents[2]


def test_acceptance_criteria_are_learner_facing() -> None:
    text = (DOCS_ROOT / "ACCEPTANCE_CRITERIA.md").read_text(encoding="utf-8")

    assert "# 验收标准" in text
    assert "必须能运行的命令" in text
    assert "总图必须展示的内容" in text
    assert "风险灯" in text
    assert "NotebookLM 外部研究源名称" in text
    assert "必须留下的用户体验证据" in text
    assert "browser-act 打开本地页面实际体验" in text
    assert "# Acceptance Criteria" not in text


def test_tdd_plan_is_localized_but_keeps_red_green_refactor() -> None:
    text = (DOCS_ROOT / "TDD_PLAN.md").read_text(encoding="utf-8")

    assert "# TDD 计划" in text
    assert "Red：先写会失败的测试" in text
    assert "Green：实现最小闭环" in text
    assert "Refactor：通过后再收紧" in text
    assert "Agent 波次规则" in text
    assert "browser-act 用户体验实测规约" in text
    assert "不能只留在聊天里" in text
    assert "# TDD Plan" not in text


def test_ux_verification_requires_browser_act_real_browsing() -> None:
    text = (DOCS_ROOT / "UX_VERIFICATION.md").read_text(encoding="utf-8")

    assert "# 用户体验实测协议" in text
    assert "browser-act 实际体验" in text
    assert "不能只靠源码阅读" in text
    assert "--overwrite" in text
    assert "关闭 browser-act session" in text


def test_agent_orchestration_log_has_current_context_note() -> None:
    text = (DOCS_ROOT / "AGENT_ORCHESTRATION.md").read_text(encoding="utf-8")

    assert "# Agent 协作日志" in text
    assert "3 个实现 agent" in text
    assert "命令输出和风险文本保留" in text
    assert "判断当前行为时以测试" in text
    assert "工作台、日结回执和最新优化日志为准" in text


def test_readme_starts_from_workbench_and_daily_loop() -> None:
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "本地优先的 Codex 陪伴式备考系统" in text
    assert "优先打开本地工作台" in text
    assert "./start-workbench.command" in text
    assert "RUANKAO_WORKBENCH_PORT=8770 ./start-workbench.command" in text
    assert "学习回合" in text
    assert "Mein/Du/Uns 三源材料同步" in text
    assert "用户体验改动，都必须用 browser-act 打开本地页面" in text
    assert "/ruankao-ux-check <page-or-flow>" in text
    assert "Local-first Codex companion agent" not in text
