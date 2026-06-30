from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .receipts_payload import build_daily_receipt_payload
from .receipts_render import render_daily_receipt


@dataclass(frozen=True, slots=True)
class DailyReceiptResult:
    as_of: date
    json_path: Path
    html_path: Path
    status: str


def daily_receipt_json_path(root: Path | str, as_of: date) -> Path:
    return Path(root) / "data" / "daily-receipts" / f"{as_of.isoformat()}.json"


def daily_receipt_html_path(root: Path | str, as_of: date) -> Path:
    return Path(root) / "reports" / "daily" / f"{as_of.isoformat()}.html"


def write_daily_receipt(root: Path | str, *, as_of: date | None = None) -> DailyReceiptResult:
    root_path = Path(root)
    day = as_of or date.today()
    payload = build_daily_receipt_payload(root_path, day)

    json_path = daily_receipt_json_path(root_path, day)
    html_path = daily_receipt_html_path(root_path, day)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(render_daily_receipt(payload), encoding="utf-8")

    return DailyReceiptResult(
        as_of=day,
        json_path=json_path,
        html_path=html_path,
        status=str(payload["status"]),
    )
