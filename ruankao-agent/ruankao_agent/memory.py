from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date

from .storage import MemoryCard, ReviewLog


@dataclass(frozen=True, slots=True)
class MemoryDiagnostic:
    card_id: int
    title: str
    card_type: str
    fronts: tuple[str, ...]
    status: str
    action: str
    total_reviews: int
    low_grade_reviews: int
    last_grade: int | None
    average_grade: float | None
    next_due: date | None


def diagnose_memory(
    cards: Iterable[MemoryCard],
    review_logs: Iterable[ReviewLog],
    *,
    as_of: date | None = None,
) -> tuple[MemoryDiagnostic, ...]:
    logs_by_card: dict[int, list[ReviewLog]] = {}
    for log in review_logs:
        logs_by_card.setdefault(log.card_id, []).append(log)

    diagnostics = [
        _diagnose_card(card, logs_by_card.get(card.id, ()), as_of=as_of)
        for card in cards
    ]
    return tuple(sorted(diagnostics, key=_diagnostic_sort_key))


def _diagnose_card(
    card: MemoryCard,
    logs: Iterable[ReviewLog],
    *,
    as_of: date | None,
) -> MemoryDiagnostic:
    ordered_logs = sorted(logs, key=lambda log: (log.reviewed_on, log.id))
    grades = [log.grade for log in ordered_logs]
    low_grade_reviews = sum(1 for grade in grades if grade <= 2)
    last_grade = grades[-1] if grades else None
    average_grade = round(sum(grades) / len(grades), 2) if grades else None
    today = as_of or date.today()
    is_due = card.next_due is not None and card.next_due <= today

    if low_grade_reviews >= 2 and (last_grade is None or last_grade <= 2):
        status = "leech"
        action = "拆成更小卡片，补一条错因，再明天复习。"
    elif last_grade is not None and last_grade <= 2:
        status = "unstable"
        action = "今天补提示，明天再次检索。"
    elif is_due:
        status = "due"
        action = "今天完成检索复习。"
    elif not grades:
        status = "untested"
        action = "安排首次检索，不要只读答案。"
    else:
        status = "stable"
        action = "保持当前间隔。"

    return MemoryDiagnostic(
        card_id=card.id,
        title=card.title,
        card_type=card.card_type.value,
        fronts=tuple(front.value for front in card.fronts),
        status=status,
        action=action,
        total_reviews=len(grades),
        low_grade_reviews=low_grade_reviews,
        last_grade=last_grade,
        average_grade=average_grade,
        next_due=card.next_due,
    )


def _diagnostic_sort_key(diagnostic: MemoryDiagnostic) -> tuple[int, str, int]:
    severity = {
        "leech": 0,
        "unstable": 1,
        "due": 2,
        "untested": 3,
        "stable": 4,
    }
    due_text = diagnostic.next_due.isoformat() if diagnostic.next_due else "9999-12-31"
    return (severity[diagnostic.status], due_text, diagnostic.card_id)


def obsidian_link(title: str) -> str:
    return f"[[{title}]]"


def _render_frontmatter(properties: Mapping[str, object]) -> str:
    lines: list[str] = ["---"]
    for key, value in properties.items():
        if isinstance(value, (list, tuple)):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        elif value is None:
            lines.append(f"{key}:")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines)


def render_principle_note(
    *,
    title: str,
    core_statement: str,
    applies_when: str,
    conflicts: Iterable[str] = (),
    status: str = "candidate",
    source: str = "Mein",
    exam: Iterable[str] = ("choice", "case", "essay"),
    strength: int = 1,
    last_reviewed: str = "",
) -> str:
    frontmatter = _render_frontmatter(
        {
            "type": "principle",
            "title": title,
            "status": status,
            "source": source,
            "exam": tuple(exam),
            "strength": strength,
            "last_reviewed": last_reviewed,
        }
    )

    conflict_links = [obsidian_link(conflict) for conflict in conflicts]
    conflict_block = "\n".join(f"- {link}" for link in conflict_links) if conflict_links else "- 待补充"

    body = [
        f"# {title}",
        "",
        "## Core Statement",
        "",
        core_statement,
        "",
        "## Applies When",
        "",
        applies_when,
        "",
        "## Does Not Apply When",
        "",
        "- 待补充",
        "",
        "## Conflicts",
        "",
        conflict_block,
        "",
        "## Exam Mapping",
        "",
        "Choice:",
        "Case:",
        "Essay:",
    ]
    return "\n".join([frontmatter, *body, ""])


def render_map_note(title: str, lines: Iterable[str]) -> str:
    body = [f"# {title}", "", *lines, ""]
    return "\n".join(body)
