from __future__ import annotations

from collections.abc import Iterable, Mapping


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
