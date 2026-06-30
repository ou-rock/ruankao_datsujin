# ruankao datsujin

Local-first Codex companion agent for the System Architecture Designer exam.

The working implementation lives in `ruankao-agent/`.

## What Is Included

- high-level design document
- TDD tests
- local `architect-thinking` skill seed
- local SQLite state layer
- Obsidian vault generation
- local web workbench
- static HTML dashboard generation
- NotebookLM source metadata wrapper
- imported upstream skill references

## Daily Use

Open the local workbench:

```sh
./start-workbench.command
```

Then use the browser page for daily capture, review, memory cards, principle links,
the learning desk, and the Obsidian vault map. In Codex, `/ruankao-workbench`
starts the same workbench.

Daily close and night evolution can run from Codex:

```text
/ruankao-daily-cycle 2026-06-29
/ruankao-daily-close 2026-06-29
/ruankao-night-evolve 2026-06-29
/ruankao-architect-review <question-or-draft>
/ruankao-study-mode <topic-or-front>
```

The daily cycle command runs Cheko weak-area seeding, core principle seeding,
daily receipt generation, route map generation, a stage-only night evolution
plan, Obsidian vault sync for memory cards and raw Mein/Du/Uns material, and a
local JSON state export.
The study mode command runs a one-question-at-a-time dialogue and records each
learner answer as Mein plus each Codex refinement as Du.
The night evolution command does not directly mutate live skills or learning rules.

For scheduled nightly runs, see `ruankao-agent/docs/AUTOMATION.md`.

## What Is Not Committed

The local `resources/` folder contains exam PDFs and generated study materials. It is ignored
by git by default and should stay local unless explicitly reviewed before upload.

## Quick Check

```sh
cd ruankao-agent
python3 -m pytest
```

## Demo Init

```sh
cd ruankao-agent
python3 -m ruankao_agent.cli init --root /tmp/ruankao-agent-demo --as-of 2026-06-29
python3 -m ruankao_agent.cli status --root /tmp/ruankao-agent-demo --as-of 2026-06-29
python3 -m ruankao_agent.cli web --root /tmp/ruankao-agent-demo --open
```
