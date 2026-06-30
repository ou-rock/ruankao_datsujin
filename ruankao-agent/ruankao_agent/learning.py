from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .learning_content import (
    DEFAULT_CHEKO_SNAPSHOT,
    REFERENCE_PAGES,
    ChekoCourse,
    ChekoPracticeLog,
    ChekoSnapshot,
    ChekoWeakArea,
    DailyLearningPlan,
    LearningColumn,
    ReferencePage,
    TodayTask,
)
from .learning_templates import (
    render_cheko_sync,
    render_learning_index,
    render_notebooklm_seed,
    render_reference_page,
    render_scene_before_solution_lesson,
    render_today,
    today_tasks,
)


def ensure_learning_resources(root: Path | str, *, overwrite: bool = False) -> Path:
    base = Path(root) / "learning"
    lessons = base / "lessons"
    reference = base / "reference"
    data = base / "data"
    for directory in (base, lessons, reference, data):
        directory.mkdir(parents=True, exist_ok=True)

    cheko_snapshot = _ensure_cheko_snapshot(data / "cheko-snapshot.json", overwrite=overwrite)

    _write_resource(base / "index.html", render_learning_index(cheko_snapshot), overwrite=overwrite)
    _write_resource(
        lessons / "0001-scene-before-solution.html",
        render_scene_before_solution_lesson(),
        overwrite=overwrite,
    )
    for page in REFERENCE_PAGES:
        _write_resource(reference / page.filename, render_reference_page(page), overwrite=overwrite)
    _write_resource(base / "notebooklm-seed.html", render_notebooklm_seed(), overwrite=overwrite)
    _write_resource(base / "cheko-sync.html", render_cheko_sync(cheko_snapshot), overwrite=overwrite)
    _write_resource(base / "today.html", render_today(cheko_snapshot), overwrite=overwrite)
    return base


def _ensure_cheko_snapshot(path: Path, *, overwrite: bool) -> ChekoSnapshot:
    if path.exists() and not overwrite:
        return _load_cheko_snapshot(path)
    snapshot = DEFAULT_CHEKO_SNAPSHOT
    path.write_text(
        json.dumps(_cheko_snapshot_to_dict(snapshot), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return snapshot


def _load_cheko_snapshot(path: Path) -> ChekoSnapshot:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return _cheko_snapshot_from_dict(payload)


def load_cheko_snapshot(path: Path | str) -> ChekoSnapshot:
    return _load_cheko_snapshot(Path(path))


def _cheko_snapshot_to_dict(snapshot: ChekoSnapshot) -> dict[str, Any]:
    return asdict(snapshot)


def _cheko_snapshot_from_dict(payload: dict[str, Any]) -> ChekoSnapshot:
    return ChekoSnapshot(
        captured_on=payload["captured_on"],
        source=payload["source"],
        answered=int(payload["answered"]),
        wrong=int(payload["wrong"]),
        accuracy=float(payload["accuracy"]),
        estimated_score=float(payload["estimated_score"]),
        rank=int(payload["rank"]),
        rank_total=int(payload["rank_total"]),
        percentile=float(payload["percentile"]),
        essay_power_remaining=int(payload["essay_power_remaining"]),
        essay_power_total=int(payload["essay_power_total"]),
        essay_past_exam_score=payload["essay_past_exam_score"],
        collections_state=payload["collections_state"],
        practice_logs=tuple(ChekoPracticeLog(**item) for item in payload["practice_logs"]),
        weak_areas=tuple(ChekoWeakArea(**item) for item in payload["weak_areas"]),
        courses=tuple(ChekoCourse(**item) for item in payload["courses"]),
    )


def _write_resource(path: Path, html: str, *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        return
    path.write_text(html, encoding="utf-8")
