from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .route_map_payload import build_route_map_payload
from .route_map_render import render_route_map


@dataclass(frozen=True, slots=True)
class RouteMapResult:
    as_of: date
    json_path: Path
    html_path: Path


def route_map_json_path(root: Path | str, as_of: date) -> Path:
    return Path(root) / "reports" / "routes" / f"{as_of.isoformat()}.json"


def route_map_html_path(root: Path | str, as_of: date) -> Path:
    return Path(root) / "reports" / "routes" / f"{as_of.isoformat()}.html"


def write_route_map(root: Path | str, *, as_of: date | None = None) -> RouteMapResult:
    root_path = Path(root)
    day = as_of or date.today()
    payload = build_route_map_payload(root_path, day)

    json_path = route_map_json_path(root_path, day)
    html_path = route_map_html_path(root_path, day)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(render_route_map(payload), encoding="utf-8")
    return RouteMapResult(as_of=day, json_path=json_path, html_path=html_path)
