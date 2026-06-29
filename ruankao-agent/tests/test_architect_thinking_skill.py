from pathlib import Path


def test_architect_thinking_skill_keeps_core_seven_principles() -> None:
    skill = Path("skills/architect-thinking/SKILL.md").read_text(encoding="utf-8")

    principles = [
        "场景先于方案",
        "质量属性可度量",
        "取舍必须显式",
        "边界与职责先行",
        "简单可演进优先",
        "风险驱动验证",
        "证据闭环沉淀",
    ]

    assert "name: architect-thinking" in skill
    assert "Core Seven" in skill
    for principle in principles:
        assert principle in skill
