# Ruankao Agent Design

## 0. 中文总览

软考达人是一个本地优先的陪伴式备考系统。它的目标不是只把题讲会，而是在
四个月主战和两周冗余里，让学习者真正长出系统架构师的判断力。

系统每天必须回答三个问题：

- 我们在哪里：倒计时、战役阶段、风险灯、记忆积压、三题型覆盖。
- 我们要到哪里：通过系统架构设计师考试，并沉淀可复用的架构判断能力。
- 今天做什么：先处理最高风险动作，再把结果沉淀成可复习、可追踪的资产。

核心分工：

- `SQLite` 保存训练状态、排程、复习、练习和三源材料。
- `RAG` 是记忆与进步控制层，只从 SQLite、Obsidian 同步产物和本地资料召回证据。
- `Obsidian` 保存可编辑的知识网络，尤其是原则卡和 Mein / Du / Uns。
- `HTML` 是总图和工作台，必须让人一眼看到位置、目标和下一步。
- `NotebookLM` 只作为精选外部研究员，输出进入 Uns，不能直接替代判断。
- `browser-act` 是网页用户体验实测通道。学习台、工作台和总图的 UX 改动必须
  用真实浏览路径验证，不能只靠源码阅读或单元测试。

成长底座：

- `Mein`：我的原话、答案、卡点和经验。
- `Du`：Codex 的追问、纠偏、结构化和自我修正。
- `Uns`：外部资料、NotebookLM、Cheko、真题、标准答案和文章证据。

夜间进化默认只生成暂存草案。原则链接、skill 改造和核心规则调整必须先留下
证据，再进入人工确认或后续迭代。

## 1. Mission

Build a local Codex companion agent for the Software Exam System Architecture Designer track.
Its job is not only to help pass the exam, but to grow with the learner until both exam skill
and real architecture judgement improve.

The first campaign targets the 2026 H2 System Architecture Designer exam. As of 2026-06-29,
the earliest known exam window starts on 2026-10-24, leaving about 117 days. The strategy is a
4-month campaign with 14 main battle weeks and 2 reserve weeks.

## 2. Product Thesis

The agent is a local, durable learning system with a daily heartbeat.

It combines:

- Exam readiness: choice questions, case analysis, essay writing.
- Real architecture ability: scenarios, quality attributes, trade-offs, risks, validation.
- Strategic memory: spaced review and retrieval practice across a large knowledge body.
- Mutual growth: the learner, the agent, and selected external sources all leave traces.

The agent must feel like a companion, but behave like an accountable training system.

## 3. Non-Negotiables

- Local-first: all durable state lives under `ruankao-agent/`.
- No chat-context dependence: conversation memory must be written to durable files or SQLite.
- NotebookLM is an external researcher, not the source of truth.
- SQLite is the training and scheduling engine.
- Local RAG is the retrieval and progress-control layer, not a second memory store.
- Obsidian is the editable knowledge network.
- HTML is the dashboard and total map.
- BrowserAct UX verification is mandatory for learner-facing web changes.
- Night evolution is stage-only by default; it cannot silently modify live core skills.
- TDD is mandatory for implementation.
- Parallel agent work is capped in waves of 3 and must use disjoint ownership.

## 4. Success Definition

The first high-level success state is:

1. The learner can see where they are, where they are going, and what to do next.
2. Daily loop state is recorded in durable storage.
3. Memory War Room can schedule and classify cards.
4. Mein/Du/Uns raw materials can be recorded and later promoted.
5. Principle cards can conflict, support, constrain, and link to Obsidian notes.
6. The dashboard renders countdown, risk state, campaign phase, memory state, and routes.
7. NotebookLM can be represented as a registered external research source.
8. Tests prove the above behavior without relying on live NotebookLM network calls.

Passing the exam is the campaign outcome; this project builds the local system that makes the
campaign executable.

## 5. Total Map

The dashboard first screen must answer three questions:

- Where are we?
- Where are we going?
- What is the next move?

The first screen shows:

- Target: 2026 H2 System Architecture Designer pass.
- Countdown from the configured current date to exam date.
- Current campaign phase.
- Main battle progress.
- Reserve pool and reserve days consumed.
- Risk status: green, yellow, or red.
- Today's minimum loop.
- Links to Memory War Room, three exam fronts, Obsidian vault, and NotebookLM source map.

The second layer shows the knowledge and growth pyramid:

```text
L5 Core principles       7 hard architecture principles in architect-thinking
L4 Stable methods        reusable frameworks, scoring methods, essay structures
L3 Verified patterns     patterns repeatedly validated by practice
L2 Candidate insights    extracted ideas from raw material
L1 Raw material          Mein / Du / Uns
```

## 6. Campaign Plan

The initial campaign has six phases:

| Phase | Window | Purpose | Output |
| --- | --- | --- | --- |
| Stage 0 | 3 days | launch diagnosis | exam date, baseline, data store, dashboard |
| Stage 1 | weeks 1-2 | diagnostic modeling | baseline scores, weakness map, memory queue |
| Stage 2 | weeks 3-7 | system breakthrough | core knowledge, case frameworks, essay skeletons |
| Stage 3 | weeks 8-11 | past paper strengthening | timed practice, mistakes recycle, full essays |
| Stage 4 | weeks 12-14 | score protection | templates, high-frequency review, simulation |
| Stage 5 | weeks 15-16 | reserve and firefighting | biggest weakness only, no large new domains |

Reserve is a risk budget, not vacation. It is consumed when planned critical work slips.

## 7. Risk Rules v0.1

Risk is intentionally rule-based at first.

Green:

- Daily minimum loop completed.
- This week touches all three exam fronts.
- Memory review backlog is not materially growing.
- Essay and case training have not been skipped for too long.

Yellow:

- 2 consecutive days miss the minimum loop.
- 1 exam front is absent this week.
- Review backlog exceeds 20%.
- Essay is untouched for more than 7 days.
- Case is untouched for more than 5 days.
- Reserve consumed is at least 3 days.

Red:

- 4 consecutive days miss the minimum loop.
- 2 or more exam fronts are absent this week.
- Review backlog exceeds 40%.
- Essay is untouched for more than 14 days.
- Case is untouched for more than 10 days.
- Reserve consumed is at least 7 days.
- Within 30 days of the exam, fewer than 2 complete essays have been written.

## 8. Daily Loop

The standard minimum loop:

1. Memory review: all due cards or due knowledge units.
2. Choice practice: at least 10 questions with error cause.
3. Case/essay alternating touch:
   - Odd day: one case sub-question or scoring-point decomposition.
   - Even day: one essay paragraph, outline, or material rewrite.
4. Grading and follow-up question.
5. Mein/Du/Uns deposition.
6. Tomorrow's plan.

Busy-day minimum:

1. Due memory review.
2. 5 choice questions.
3. One case or essay touch.
4. One Mein reflection sentence.

## 9. Memory War Room

Memory is a strategic subsystem because the knowledge body is large.

Card types:

- Principle card: architecture, design, and exam-answering principles.
- Concept card: definitions, composition, features, applicability.
- Comparison card: confusing concepts, technologies, styles, quality attributes.
- Scenario card: context, constraints, quality attributes, architecture decisions.
- Expression card: case scoring phrases, essay sentences, project narratives.

Memory must track both:

- Storage strength: how likely the learner is to retain it.
- Retrieval strength: whether the learner can use it in choice, case, or essay contexts.

Principle cards are a network, not a list. They may support, constrain, conflict with, or
derive from one another.

## 10. Mein / Du / Uns

All raw material starts in L1 under one of three source identities:

- Mein: the learner's understanding, experience, answers, doubts, reflections.
- Du: the agent's analysis, questions, grading, summaries, corrections, mistakes.
- Uns: external material entering the shared learning field, including NotebookLM, PDFs,
  articles, official material, past papers, and standard answers.

Each L1 record keeps:

- raw text
- source identity
- timestamp
- short summary
- topic tags
- related exam fronts
- promotion status

The system must preserve agent mistakes and corrections in Du. Growth requires recording
what the agent got wrong, not only polished conclusions.

## 11. Data Architecture

```text
SQLite
  Training state, loop records, risk state, memory scheduling, mastery, source index.

Obsidian vault
  Editable knowledge network: principles, concepts, comparisons, scenarios, expressions,
  selected Mein/Du/Uns notes, and cross-links.

HTML dashboard
  Generated total map: countdown, risk, campaign phase, memory war room, routes, and links.

NotebookLM
  External researcher for selected notebooks. Its outputs enter Uns as candidate evidence.
```

SQLite is the fact source for scheduling and state. Obsidian is the human-editable knowledge
surface. HTML is a generated map. NotebookLM is evidence, not memory.

## 12. Obsidian Vault

Initial structure:

```text
vault/
  00-map/
    战役总图.md
    原则网络.md
    三题型路线图.md
  10-memory-war-room/
    principles/
    concepts/
    comparisons/
    scenarios/
    expressions/
  20-mein/
  30-du/
  40-uns/
  50-exam/
    choice/
    case/
    essay/
  90-archive/
```

Principle card minimal template:

```markdown
---
type: principle
status: candidate
source: Mein
exam:
  - choice
  - case
  - essay
strength: 1
last_reviewed:
---

# Principle Name

## Core Statement

## Applies When

## Does Not Apply When

## Conflicts

- [[Other Principle]]

## Exam Mapping

Choice:
Case:
Essay:
```

## 13. Skills Architecture

Two skill layers:

```text
upstream-skills/   original third-party references, kept unchanged
skills/            local ruankao adaptations, allowed to evolve
```

Initial local skills:

- `architect-thinking`: architecture thinking kernel and 7 core principles.
- `ruankao-loop`: daily, weekly, and night orchestration.
- `ruankao-teach`: teaching, retrieval, spaced review, short lessons.
- `ruankao-grill`: one-question-at-a-time pressure testing.
- `night-evolution`: SkillOpt sleep style staged improvement.

`ruankao-loop` is the coordinator. The other skills are capabilities it invokes.

## 14. NotebookLM Role

Registered primary notebook:

- Title: `System Architecture Designer Exam Questions and Analysis`
- URL: `https://notebooklm.google.com/notebook/5d1ffc0c-2fef-47e2-ac3c-3b29a0ab8c0a`
- Local library id: `system-architecture-designer-e`
- Role: selected external researcher for System Architecture Designer exam sources.

NotebookLM output flow:

```text
query -> cited answer -> Uns raw record -> candidate insight -> validated pattern -> stable method
```

It must not directly overwrite core principles or live skills.

## 15. Module Boundaries

Python package: `ruankao_agent`.

Expected modules:

- `domain.py`: dates, phases, risk status, card types, source identities, core models.
- `storage.py`: SQLite schema and repository functions.
- `memory.py`: card creation, review scheduling, principle relation handling.
- `vault.py`: Obsidian directory and note generation.
- `dashboard.py`: static HTML dashboard generation.
- `notebooklm.py`: local representation and CLI wrapper for NotebookLM queries.
- `rag.py`: local retrieval and progress-control briefs from SQLite evidence.
- `loop.py`: daily loop status, risk evaluation, next-action generation.
- `cli.py`: command line entry points.

## 16. TDD Contract

Tests are written before implementation and must cover:

- Campaign countdown and phase computation.
- Risk color rules.
- Mein/Du/Uns record persistence.
- Memory card classification and scheduling.
- Principle conflict/support relation persistence.
- Obsidian vault initialization and principle note generation.
- Dashboard rendering of campaign, risk, memory, and navigation.
- RAG brief generation from raw records, memory cards, review logs, and practice sessions.
- NotebookLM source metadata without live network dependency.
- CLI smoke behavior.

The first implementation wave must make the tests pass without reaching out to live
NotebookLM. Live integrations are wrapped behind explicit commands and mocks.

## 17. Parallel Agent Plan

Implementation wave, 3 agents:

1. Core State Agent
   - Owns `domain.py`, `storage.py`, and related tests.
   - Implements campaign, risk, triad records, SQLite schema.

2. Memory/Vault Agent
   - Owns `memory.py`, `vault.py`, templates, and related tests.
   - Implements card scheduling, principle graph relations, Obsidian notes.

3. Dashboard/CLI Agent
   - Owns `dashboard.py`, `loop.py`, `notebooklm.py`, `cli.py`, and related tests.
   - Implements generated map, daily loop summary, NotebookLM metadata wrapper.

Critical review wave, 3 agents:

1. Design Critic: checks whether implementation still satisfies this design.
2. Code Critic: checks module boundaries, persistence correctness, and maintainability.
3. Test Critic: checks whether tests prove the explicit requirements.

Acceptance wave, 3 agents:

1. Scenario Tester: runs a realistic first-day setup and daily loop.
2. Data Tester: validates SQLite and Obsidian artifacts.
3. Dashboard Tester: validates generated HTML content and navigation.

All agents must return evidence: changed files, commands run, failures, residual risks.

## 18. First Release Acceptance

Release v0.1 is acceptable when:

- `python3 -m pytest` passes from `ruankao-agent/`.
- `python3 -m ruankao_agent.cli init --root <tmpdir>` creates SQLite, vault, and dashboard.
- `python3 -m ruankao_agent.cli status --root <tmpdir>` prints countdown, phase, and risk.
- The generated dashboard contains target, countdown, phase, reserve, risk, Memory War Room,
  Mein/Du/Uns, and links to Obsidian notes.
- Principle notes contain Obsidian-style `[[...]]` links.
- NotebookLM metadata is recorded without requiring a live query.

## 19. Known Risks

- Too much automation can hide learning. The system must force retrieval and reflection.
- Too many skills can fragment the agent. `ruankao-loop` remains the coordinator.
- NotebookLM can become a crutch. Its output must be validated before promotion.
- Principle networks can become visually impressive but useless. Every principle needs
  exam mapping and evidence.
- Night evolution can corrupt identity if it edits core files silently. Stage-only is mandatory.

## 20. Open Future Work

- Add launchd or Codex heartbeat automation for morning and evening loops.
- Add SkillOpt-style replay harness for night evolution.
- Add richer HTML graph rendering for principle networks.
- Add importers for local PDFs and NotebookLM source lists.
- Add scoring rubrics for choice, case, and essay practice.
