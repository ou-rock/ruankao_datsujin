from pathlib import Path


DOCS_ROOT = Path(__file__).resolve().parents[1] / "docs"


def test_acceptance_criteria_are_learner_facing() -> None:
    text = (DOCS_ROOT / "ACCEPTANCE_CRITERIA.md").read_text(encoding="utf-8")

    assert "# 验收标准" in text
    assert "必须能运行的命令" in text
    assert "总图必须展示的内容" in text
    assert "风险灯" in text
    assert "NotebookLM 外部研究源名称" in text
    assert "# Acceptance Criteria" not in text


def test_tdd_plan_is_localized_but_keeps_red_green_refactor() -> None:
    text = (DOCS_ROOT / "TDD_PLAN.md").read_text(encoding="utf-8")

    assert "# TDD 计划" in text
    assert "Red：先写会失败的测试" in text
    assert "Green：实现最小闭环" in text
    assert "Refactor：通过后再收紧" in text
    assert "Agent 波次规则" in text
    assert "# TDD Plan" not in text
