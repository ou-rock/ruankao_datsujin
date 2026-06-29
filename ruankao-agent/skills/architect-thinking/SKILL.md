---
name: architect-thinking
description: Use when analyzing system architecture design decisions, ruankao system architect choice/case/essay questions, quality attributes, trade-offs, architecture principles, scenario decomposition, solution critique, or when turning practice mistakes into reusable architecture judgement.
---

# Architect Thinking

Use this skill to reason like a system architect, not like a technology list
generator. It supports ruankao System Architecture Designer preparation and real
architecture judgement.

## Core Seven

Apply these seven principles as the stable kernel. Principles may be revised
only when practice evidence shows a better formulation.

1. **场景先于方案**: identify business goal, actors, constraints, and scenario before naming technologies.
2. **质量属性可度量**: translate vague non-functional needs into stimulus, response, and measurable response.
3. **取舍必须显式**: every architecture decision should say what it improves and what it sacrifices.
4. **边界与职责先行**: define system boundary, module responsibility, data ownership, and interface contract before optimizing internals.
5. **简单可演进优先**: prefer the simplest design that preserves future change paths; add complexity only when risk or scale justifies it.
6. **风险驱动验证**: validate the riskiest assumption first with tests, metrics, prototypes, reviews, or failure drills.
7. **证据闭环沉淀**: convert decisions, mistakes, and external evidence into Mein/Du/Uns records, memory cards, or principle links.

## Workflow

When answering an architecture question:

1. Restate the scenario and boundary.
2. Identify the dominant quality attributes and measurable targets.
3. Name candidate tactics or styles only after the scenario is clear.
4. Compare trade-offs, including complexity, reliability, performance, security, maintainability, and operational cost.
5. State risks, validation method, and rollback or mitigation path.
6. Map the answer to choice, case, or essay scoring needs.
7. Propose what should be deposited into the local system: raw record, memory card, principle, practice session, or vault note.

## Output Shape

Prefer this compact structure unless the user asks otherwise:

- **Scenario**: business context, boundary, constraints.
- **Quality Attributes**: measurable targets and priority.
- **Decision**: style, tactics, components, interfaces.
- **Trade-offs**: gains, costs, conflicts.
- **Validation**: how to prove it works.
- **Exam Deposit**: choice/case/essay memory or expression output.

## Guardrails

- Do not start with framework names.
- Do not treat memorized definitions as architecture judgement.
- Do not write essay prose without project context and explicit trade-offs.
- Do not let external evidence enter as truth until it is deposited as Uns and checked against practice.
