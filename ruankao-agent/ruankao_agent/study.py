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
    learner_position: str
    codex_position: str
    destination: str


def capture_study_turn(
    root: Path | str,
    *,
    topic: str,
    user_text: str,
    assistant_text: str,
    fronts: Sequence[ExamFront] = (),
    learner_position: str = "",
    codex_position: str = "",
    destination: str = "",
) -> StudyTurnResult:
    clean_topic = topic.strip() or "未命名学习回合"
    clean_user = user_text.strip()
    clean_assistant = assistant_text.strip()
    clean_learner_position = learner_position.strip()
    clean_codex_position = codex_position.strip()
    clean_destination = destination.strip()
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
        text=_with_position_header(
            clean_user,
            learner_position=clean_learner_position,
            codex_position=clean_codex_position,
            destination=clean_destination,
        ),
        summary=f"学习模式 Mein：{clean_topic}",
        topics=topics,
        fronts=front_tuple,
        promotion_status="raw",
    )
    du_record_id = store.add_raw_record(
        source=SourceIdentity.DU,
        text=_with_position_header(
            clean_assistant,
            learner_position=clean_learner_position,
            codex_position=clean_codex_position,
            destination=clean_destination,
        ),
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
        learner_position=clean_learner_position,
        codex_position=clean_codex_position,
        destination=clean_destination,
    )


def _with_position_header(
    text: str,
    *,
    learner_position: str,
    codex_position: str,
    destination: str,
) -> str:
    if not any((learner_position, codex_position, destination)):
        return text
    return "\n".join(
        (
            "学习定位:",
            f"- 我在哪: {learner_position or '未记录'}",
            f"- 你在哪: {codex_position or '未记录'}",
            f"- 我们要去哪: {destination or '未记录'}",
            "",
            text,
        )
    )
