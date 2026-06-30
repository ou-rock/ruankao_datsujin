from __future__ import annotations

from html import escape

from .receipts_sections import render_daily_receipt_sections
from .receipts_style import RECEIPT_PAGE_STYLE


def render_daily_receipt(payload: dict[str, object]) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>日结回执 {escape(str(payload["as_of"]))}</title>
  <style>
{RECEIPT_PAGE_STYLE}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>日结回执 {escape(str(payload["as_of"]))}</h1>
      <p class="status">{escape(str(payload["status"]))}</p>
    </header>
    {render_daily_receipt_sections(payload)}
  </main>
</body>
</html>
"""
