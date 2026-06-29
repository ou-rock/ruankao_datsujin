from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .domain import CardType, ExamFront, PrincipleRelationType, SourceIdentity
from .storage import RuankaoStore


@dataclass(frozen=True, slots=True)
class CorePrinciple:
    title: str
    prompt: str
    answer: str


@dataclass(frozen=True, slots=True)
class CorePrincipleRelation:
    from_title: str
    to_title: str
    relation: PrincipleRelationType
    rationale: str


@dataclass(frozen=True, slots=True)
class PrincipleSeedResult:
    raw_record_id: int
    created_card_ids: tuple[int, ...]
    skipped_titles: tuple[str, ...]
    created_relation_ids: tuple[int, ...] = ()
    skipped_relations: tuple[str, ...] = ()


CORE_ARCHITECTURE_PRINCIPLES = (
    CorePrinciple(
        "场景先于方案",
        "做架构设计前，为什么不能先报技术方案？",
        "先确认业务目标、参与者、边界、约束和质量属性场景，再选择技术方案。",
    ),
    CorePrinciple(
        "质量属性可度量",
        "如何把非功能需求变成架构可验证目标？",
        "将模糊诉求拆为刺激、环境、响应和响应度量，例如恢复时间、吞吐量或变更成本。",
    ),
    CorePrinciple(
        "取舍必须显式",
        "为什么架构答案必须写取舍？",
        "每个决策都改善某些属性，也牺牲复杂度、成本、性能、安全或演进空间，必须说清楚。",
    ),
    CorePrinciple(
        "边界与职责先行",
        "为什么先划边界和职责？",
        "系统边界、模块职责、数据归属和接口契约决定协作方式，先于内部优化。",
    ),
    CorePrinciple(
        "简单可演进优先",
        "什么时候应该拒绝复杂方案？",
        "当风险、规模或约束不足以证明复杂度时，选择简单方案，并保留未来演进路径。",
    ),
    CorePrinciple(
        "风险驱动验证",
        "架构验证应该先验证什么？",
        "先验证最危险假设，用测试、指标、原型、评审或故障演练证明方案能工作。",
    ),
    CorePrinciple(
        "证据闭环沉淀",
        "学习和设计经验如何进入系统？",
        "把决策、错因、练习结果和外部证据沉淀为 Mein/Du/Uns、记忆卡或原则链接。",
    ),
)

CORE_ARCHITECTURE_RELATIONS = (
    CorePrincipleRelation(
        "场景先于方案",
        "质量属性可度量",
        PrincipleRelationType.SUPPORTS,
        "场景清楚后，质量属性才能被具体度量。",
    ),
    CorePrincipleRelation(
        "质量属性可度量",
        "风险驱动验证",
        PrincipleRelationType.SUPPORTS,
        "可度量目标决定验证指标和优先级。",
    ),
    CorePrincipleRelation(
        "取舍必须显式",
        "简单可演进优先",
        PrincipleRelationType.CONSTRAINS,
        "简单方案也必须说明牺牲与边界，不能以简单掩盖取舍。",
    ),
    CorePrincipleRelation(
        "边界与职责先行",
        "简单可演进优先",
        PrincipleRelationType.SUPPORTS,
        "边界清楚会降低不必要复杂度，并保留演进空间。",
    ),
    CorePrincipleRelation(
        "风险驱动验证",
        "证据闭环沉淀",
        PrincipleRelationType.SUPPORTS,
        "验证结果必须沉淀为证据、错因、卡片或原则更新。",
    ),
    CorePrincipleRelation(
        "证据闭环沉淀",
        "取舍必须显式",
        PrincipleRelationType.SUPPORTS,
        "沉淀的练习和证据会反过来校准取舍判断。",
    ),
)


def seed_core_principles(root: Path | str, *, next_due: date | None = None) -> PrincipleSeedResult:
    root_path = Path(root)
    store = RuankaoStore(root_path / "data" / "ruankao.db")
    store.initialize()
    raw_record_id = store.add_raw_record(
        source=SourceIdentity.DU,
        text=_principles_text(),
        summary="architect-thinking Core Seven 原则内核",
        topics=("architect-thinking", "原则内核", "架构能力"),
        fronts=(ExamFront.CHOICE, ExamFront.CASE, ExamFront.ESSAY),
        promotion_status="promoted",
    )

    existing_titles = {card.title for card in store.list_memory_cards()}
    created: list[int] = []
    skipped: list[str] = []
    for principle in CORE_ARCHITECTURE_PRINCIPLES:
        if principle.title in existing_titles:
            skipped.append(principle.title)
            continue
        created.append(
            store.add_memory_card(
                card_type=CardType.PRINCIPLE,
                title=principle.title,
                prompt=principle.prompt,
                answer=principle.answer,
                source_record_id=raw_record_id,
                fronts=(ExamFront.CHOICE, ExamFront.CASE, ExamFront.ESSAY),
                next_due=next_due,
            )
        )
        existing_titles.add(principle.title)

    cards_by_title = {card.title: card.id for card in store.list_memory_cards()}
    created_relations: list[int] = []
    skipped_relations: list[str] = []
    for relation in CORE_ARCHITECTURE_RELATIONS:
        from_card_id = cards_by_title.get(relation.from_title)
        to_card_id = cards_by_title.get(relation.to_title)
        if from_card_id is None or to_card_id is None:
            skipped_relations.append(f"{relation.from_title}->{relation.to_title}")
            continue
        existing = store.list_principle_relations(from_card_id)
        if any(
            item.to_card_id == to_card_id and item.relation == relation.relation
            for item in existing
        ):
            skipped_relations.append(f"{relation.from_title}->{relation.to_title}")
            continue
        created_relations.append(
            store.add_principle_relation(
                from_card_id=from_card_id,
                to_card_id=to_card_id,
                relation=relation.relation,
                rationale=relation.rationale,
            )
        )

    return PrincipleSeedResult(
        raw_record_id=raw_record_id,
        created_card_ids=tuple(created),
        skipped_titles=tuple(skipped),
        created_relation_ids=tuple(created_relations),
        skipped_relations=tuple(skipped_relations),
    )


def _principles_text() -> str:
    return "\n".join(
        f"- {principle.title}: {principle.answer}"
        for principle in CORE_ARCHITECTURE_PRINCIPLES
    )
