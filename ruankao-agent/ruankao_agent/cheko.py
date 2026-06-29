from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .domain import CardType, ExamFront, SourceIdentity
from .learning import ChekoSnapshot, ensure_learning_resources, load_cheko_snapshot
from .storage import RuankaoStore


@dataclass(frozen=True, slots=True)
class ChekoSeedResult:
    raw_record_id: int
    created_card_ids: tuple[int, ...]
    skipped_titles: tuple[str, ...]


def seed_cheko_cards(root: Path | str, *, next_due: date | None = None) -> ChekoSeedResult:
    root_path = Path(root)
    ensure_learning_resources(root_path)
    snapshot = load_cheko_snapshot(root_path / "learning" / "data" / "cheko-snapshot.json")

    store = RuankaoStore(root_path / "data" / "ruankao.db")
    store.initialize()

    raw_record_id = store.add_raw_record(
        source=SourceIdentity.UNS,
        text=_snapshot_text(snapshot),
        summary=(
            f"Cheko 同步：总答题 {snapshot.answered}，错题 {snapshot.wrong}，"
            f"正确率 {snapshot.accuracy:.1f}%，预估分 {snapshot.estimated_score:.2f}。"
        ),
        topics=("cheko", "错题池", "学习信号"),
        fronts=(ExamFront.CHOICE, ExamFront.CASE, ExamFront.ESSAY),
        promotion_status="extracted",
    )

    existing_titles = {card.title for card in store.list_memory_cards()}
    created: list[int] = []
    skipped: list[str] = []
    for title, card_type, prompt, answer, fronts in _cards_from_snapshot(snapshot):
        if title in existing_titles:
            skipped.append(title)
            continue
        created.append(
            store.add_memory_card(
                card_type=card_type,
                title=title,
                prompt=prompt,
                answer=answer,
                source_record_id=raw_record_id,
                fronts=fronts,
                next_due=next_due,
            )
        )
        existing_titles.add(title)

    return ChekoSeedResult(
        raw_record_id=raw_record_id,
        created_card_ids=tuple(created),
        skipped_titles=tuple(skipped),
    )


def _snapshot_text(snapshot: ChekoSnapshot) -> str:
    weak_lines = "\n".join(
        f"- {area.title}: {area.total} 题；{area.next_action}" for area in snapshot.weak_areas
    )
    return "\n".join(
        (
            f"captured_on: {snapshot.captured_on}",
            f"answered: {snapshot.answered}",
            f"wrong: {snapshot.wrong}",
            f"accuracy: {snapshot.accuracy:.1f}%",
            f"estimated_score: {snapshot.estimated_score:.2f}",
            f"essay: {snapshot.essay_past_exam_score}",
            "weak_areas:",
            weak_lines,
        )
    )


def _cards_from_snapshot(snapshot: ChekoSnapshot):
    for area in snapshot.weak_areas[:3]:
        yield (
            f"Cheko错题池：{area.title}",
            CardType.SCENARIO,
            f"{area.title} 错题池 {area.total} 题，今天如何回炉？",
            f"{area.next_action} 完成后至少沉淀 2 张概念卡和 1 张错因卡。",
            (ExamFront.CHOICE, ExamFront.CASE),
        )
    yield (
        "Cheko论文最低触达",
        CardType.EXPRESSION,
        "论文真题最近得分为 0 / 4 时，今天最低产出是什么？",
        "写 300 字以内摘要 + 1 段项目背景，并沉淀为表达卡；不要只看范文。",
        (ExamFront.ESSAY,),
    )
