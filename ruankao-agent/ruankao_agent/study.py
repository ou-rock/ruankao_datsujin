from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .domain import ExamFront, SourceIdentity
from .storage import RuankaoStore


@dataclass(frozen=True, slots=True)
class StudyTurnResult:
    mein_record_id: int
    du_record_id: int
    topic: str
    fronts: tuple[ExamFront, ...]


def capture_study_turn(
    root: Path | str,
    *,
    topic: str,
    user_text: str,
    assistant_text: str,
    fronts: Sequence[ExamFront] = (),
) -> StudyTurnResult:
    clean_topic = topic.strip() or "未命名学习回合"
    clean_user = user_text.strip()
    clean_assistant = assistant_text.strip()
    if not clean_user:
        raise ValueError("user_text is required")
    if not clean_assistant:
        raise ValueError("assistant_text is required")

    root_path = Path(root)
    store = RuankaoStore(root_path / "data" / "ruankao.db")
    store.initialize()
    front_tuple = tuple(fronts)
    topics = ("学习模式", clean_topic)

    mein_record_id = store.add_raw_record(
        source=SourceIdentity.MEIN,
        text=clean_user,
        summary=f"学习模式 Mein：{clean_topic}",
        topics=topics,
        fronts=front_tuple,
        promotion_status="raw",
    )
    du_record_id = store.add_raw_record(
        source=SourceIdentity.DU,
        text=clean_assistant,
        summary=f"学习模式 Du：{clean_topic}",
        topics=topics,
        fronts=front_tuple,
        promotion_status="extracted",
    )
    return StudyTurnResult(
        mein_record_id=mein_record_id,
        du_record_id=du_record_id,
        topic=clean_topic,
        fronts=front_tuple,
    )
