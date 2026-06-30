from pathlib import Path


def test_design_document_captures_non_negotiables() -> None:
    design = Path("DESIGN.md").read_text(encoding="utf-8")

    required_phrases = [
        "14 main battle weeks and 2 reserve weeks",
        "SQLite is the training and scheduling engine",
        "Obsidian is the editable knowledge network",
        "HTML is the dashboard and total map",
        "Local RAG is the retrieval and progress-control layer",
        "NotebookLM is an external researcher",
        "Mein",
        "Du",
        "Uns",
        "Memory War Room",
        "TDD is mandatory",
        "Implementation wave, 3 agents",
        "Critical review wave, 3 agents",
        "Acceptance wave, 3 agents",
        "中文总览",
        "四个月主战和两周冗余",
        "我们在哪里",
        "我们要到哪里",
        "今天做什么",
        "HTML` 是总图和工作台",
        "NotebookLM` 只作为精选外部研究员",
        "RAG` 是记忆与进步控制层",
        "夜间进化默认只生成暂存草案",
        "browser-act` 是网页用户体验实测通道",
        "不能只靠源码阅读或单元测试",
        "BrowserAct UX verification is mandatory",
    ]

    for phrase in required_phrases:
        assert phrase in design
