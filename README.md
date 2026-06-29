# ruankao datsujin

Local-first Codex companion agent for the System Architecture Designer exam.

The working implementation lives in `ruankao-agent/`.

## What Is Included

- high-level design document
- TDD tests
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
