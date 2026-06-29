from pathlib import Path


def test_design_document_captures_non_negotiables() -> None:
    design = Path("DESIGN.md").read_text(encoding="utf-8")

    required_phrases = [
        "14 main battle weeks and 2 reserve weeks",
        "SQLite is the training and scheduling engine",
        "Obsidian is the editable knowledge network",
        "HTML is the dashboard and total map",
        "NotebookLM is an external researcher",
        "Mein",
        "Du",
        "Uns",
        "Memory War Room",
        "TDD is mandatory",
        "Implementation wave, 3 agents",
        "Critical review wave, 3 agents",
        "Acceptance wave, 3 agents",
    ]

    for phrase in required_phrases:
        assert phrase in design
