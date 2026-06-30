from __future__ import annotations

from collections.abc import Iterable
from html import escape

from .learning_content import FRONT_LABELS
from .learning_style import LEARNING_PAGE_STYLE


def render_learning_page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
{LEARNING_PAGE_STYLE}
  </style>
</head>
<body>
  <main>
    {body}
  </main>
</body>
</html>
"""


def render_cards(items: Iterable[tuple[str, str]]) -> str:
    return "".join(
        f'<div class="panel"><h3>{escape(title)}</h3><p>{escape(body)}</p></div>'
        for title, body in items
    )


def render_front_labels(fronts: Iterable[str]) -> tuple[str, ...]:
    return tuple(FRONT_LABELS.get(front.strip().lower(), front.strip()) for front in fronts)
