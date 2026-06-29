# Acceptance Criteria

## Required Commands

From `ruankao-agent/`:

```sh
python3 -m pytest
python3 -m ruankao_agent.cli init --root /tmp/ruankao-agent-demo
python3 -m ruankao_agent.cli status --root /tmp/ruankao-agent-demo
python3 -m ruankao_agent.cli dashboard --root /tmp/ruankao-agent-demo
```

## Required Artifacts

The init command must create:

- `data/ruankao.db`
- `dashboard.html`
- `vault/00-map/战役总图.md`
- `vault/00-map/原则网络.md`
- `vault/10-memory-war-room/principles/场景先于方案.md`

## Required Dashboard Content

The dashboard must include:

- System Architecture Designer target.
- Exam date.
- Countdown.
- Campaign phase.
- Main battle and reserve state.
- Risk state.
- Memory War Room.
- Mein, Du, Uns.
- Choice, case, and essay routes.
- NotebookLM source name.

## Required Data Behavior

- Raw records preserve source identity.
- Memory cards preserve type.
- Principle relations preserve relation type and direction.
- Risk rules are deterministic.
- Generated Obsidian links use `[[...]]`.

## Required Process Evidence

Completion requires evidence from:

- 3 implementation agents.
- 3 critical review agents.
- 3 acceptance testing agents.
- Passing tests after integration.
