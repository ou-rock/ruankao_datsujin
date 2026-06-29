# TDD Plan

## Red

Write tests for the design contract before implementation:

- campaign countdown and phase
- risk rules
- Mein/Du/Uns persistence
- memory card types and scheduling
- principle graph relations
- Obsidian vault generation
- dashboard generation
- NotebookLM metadata representation
- CLI smoke flow

## Green

Implement the smallest coherent local system:

- standard-library Python
- SQLite through `sqlite3`
- static HTML generation
- Markdown files for Obsidian
- no live NotebookLM dependency in unit tests

## Refactor

After tests pass:

- remove duplication in storage repositories
- tighten module boundaries
- add docstrings only where behavior is not obvious
- keep generated files deterministic

## Agent Wave Rules

- Maximum 3 implementation agents in the first wave.
- Each agent owns a disjoint write set.
- No agent may revert another agent's work.
- Every agent returns changed files and verification commands.
- Central integration reruns the full test suite.
