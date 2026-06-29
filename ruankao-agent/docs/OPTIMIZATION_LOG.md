# Optimization Log

## 2026-06-29 Round 001 - Cheko Signals Into Learning Desk

### Learner Friction

The learning desk had static resources, but a learner opening it could not see
where their real practice pain was. The Cheko account already had enough signal
to guide the next action, yet the local system ignored it.

### Evidence Read From Cheko

- Logged-in state was confirmed through browser-act `chrome-direct`.
- Cheko statistic page showed:
  - total answered: 634
  - wrong answers: 194
  - accuracy: 69.4%
  - estimated score: 43.75
  - rank: 1,331 / 4,923
  - percentile: 73.0%
- Error book showed the largest weak areas:
  - 系统架构设计: 164
  - 软件工程: 82
  - 系统分析与设计: 65
  - 数据库系统: 34
  - 企业信息化战略: 32
- Essay practice signal:
  - 2013-2026 essay past exams all showed recent score 0 / 4.
  - Little Cain essay assistant showed compute 15 / 15 and no generation history.

### Change

- Added a local Cheko learning-signal snapshot at `learning/data/cheko-snapshot.json`.
- Added `learning/cheko-sync.html`.
- Added a Cheko signal panel to `learning/index.html`.
- Kept the snapshot privacy-scoped: no account, avatar, email, cookie, or credential data.
- Translated weak areas into concrete next actions for the learning desk.

### Validation

- Unit tests assert:
  - the Cheko snapshot is generated;
  - the learning desk renders Cheko signals;
  - Cheko sync shows learning metrics and omits account identity artifacts;
  - generated learning resources still preserve manual edits unless `--overwrite` is explicit.

### Next Random Directions

- Add a Cheko sync command that reads browser-act output into snapshot JSON.
- Convert weak areas into actual memory cards and due review queues.
- Add a daily "one screen" learner view: score risk, today's 3 tasks, and one essay action.
- Add BrowserAct extraction receipts under `docs/` without storing private page content.

## 2026-06-29 Round 002 - Today Three Tasks

### Learner Friction

After Round 001, the learning desk could show real Cheko practice signals, but
the learner still had to decide what to do. A tired learner does not need another
dashboard; they need one narrow next action list.

### Change

- Added `learning/today.html`.
- Added `today_tasks()` derived from the Cheko snapshot.
- Added a "今日三任务" entry point to the learning desk and Cheko sync page.
- Converted the largest weak areas into:
  - Task 1: 系统架构设计错题回炉
  - Task 2: 软件工程对比卡
  - Task 3: 论文最低触达

### Learning Rule Captured

If the learner can only do one thing, do the largest wrong-answer pool first.
If essay practice is still 0 / 4, produce reusable text instead of only reading
examples.

### Validation

- Unit tests assert:
  - `today.html` is generated;
  - the learning desk links to 今日三任务;
  - the three tasks derive from Cheko weak areas;
  - the essay task is triggered by the 0 / 4 essay signal.

## 2026-06-29 Round 003 - Cheko Signals Into Memory Cards

### Learner Friction

Round 002 made the next actions visible, but visibility still depended on the
learner manually carrying the signal into the memory system. Because memory is a
strategic layer for this exam, the largest wrong-answer pools should enter the
review queue automatically.

### Change

- Added `ruankao_agent.cheko.seed_cheko_cards()`.
- Added CLI command:
  - `python3 -m ruankao_agent.cli cheko-seed-cards --root <root> --next-due <YYYY-MM-DD>`
- Stored the Cheko snapshot as an `Uns` raw record with `promotion_status=extracted`.
- Seeded four memory cards:
  - top three Cheko weak areas as scenario cards for choice/case review;
  - essay 0 / 4 signal as an expression card for essay practice.
- Added duplicate protection by memory-card title, so repeated syncs keep a new
  raw snapshot record without creating duplicate review cards.

### Learning Rule Captured

External practice data is not just a report. Once a weak area is large enough,
it must become a scheduled retrieval object with a due date.

### Validation

- `python3 -m pytest tests/test_cheko.py -q`
- `python3 -m pytest -q`
- `python3 -m ruankao_agent.cli cheko-seed-cards --root /tmp/ruankao-cheko-seed --next-due 2026-06-29`
- Tests assert:
  - Cheko snapshot becomes an `Uns` raw record;
  - four memory cards are created with the expected fronts and due date;
  - repeated seeding skips existing card titles;
  - the CLI prints a compact hook-friendly result line.

## 2026-06-29 Round 004 - Cheko One-Click Workbench Entry

### Learner Friction

Round 003 created the right command for hooks and scheduled jobs, but the daily
learner still had to remember a CLI command. That keeps the system feeling like
an implementation detail instead of a companion workbench.

### Change

- Added a workbench "学习信号" section.
- Added a one-click form that posts to `/cheko/cards`.
- Reused `seed_cheko_cards()` so CLI, hooks, and browser actions share the same
  Cheko-to-memory-card path.
- Displayed Cheko card count, due Cheko card count, and recent Cheko cards in
  the workbench.
- Added navigation from the workbench to Cheko sync and 今日三任务 pages.

### Learning Rule Captured

When an action is strategically important and recurring, it should exist in the
main daily surface, not only as a remembered command.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- `python3 -m pytest -q`
- Tests assert:
  - the workbench renders the Cheko learning-signal entry;
  - the workbench action creates four due Cheko cards;
  - the home page shows Cheko card state after seeding.

## 2026-06-29 Round 005 - Daily Receipt For Night Evolution

### Learner Friction

The system could show status and create cards, but it still lacked a durable
daily receipt. Without a receipt, nightly evolution has to infer what happened
from scattered state instead of reading one bounded artifact.

### Change

- Added `ruankao_agent.receipts.write_daily_receipt()`.
- Wrote machine-readable JSON to `data/daily-receipts/<date>.json`.
- Wrote human-readable HTML to `reports/daily/<date>.html`.
- Added CLI command:
  - `python3 -m ruankao_agent.cli daily-receipt --root <root> --as-of <YYYY-MM-DD>`
- Added a workbench button that posts to `/daily/receipt`.
- Added safe `/reports/` serving so the generated receipt can be opened in the
  browser workbench.

### Learning Rule Captured

Daily learning must leave a receipt. Night evolution should consume an explicit
summary of status, inventory, Cheko queue state, recent raw material, and recent
cards instead of guessing from scattered files.

### Validation

- `python3 -m pytest tests/test_daily_receipt.py -q`
- `python3 -m pytest tests/test_web_workbench.py -q`
- `python3 -m pytest -q`
- `python3 -m ruankao_agent.cli daily-receipt --root /tmp/ruankao-daily-receipt-<id> --as-of 2026-06-29`
- Tests assert:
  - daily receipt JSON and HTML are written;
  - counts cover raw records, memory cards, due cards, Cheko cards, sources, and fronts;
  - the CLI prints hook-friendly paths and status;
  - the workbench can write and serve the daily HTML receipt.

## 2026-06-29 Round 006 - Immutable Review History

### Learner Friction

The memory system updated a card after review, but it did not preserve each
review attempt. That makes it impossible to later detect patterns such as
"always failing the same concept", "improves after two exposures", or "essay
expression cards decay faster than choice concepts".

### Change

- Added a `review_logs` SQLite table.
- Added `ReviewLog` and `RuankaoStore.list_review_logs()`.
- Updated `record_review()` to keep the current card scheduling behavior while
  appending an immutable review log.
- Extended daily receipts with:
  - total review logs;
  - today's review count;
  - recent review attempts.

### Learning Rule Captured

A spaced-repetition system needs review history, not only current state. The
current card state answers "what is next"; review history answers "how memory is
actually changing".

### Validation

- `python3 -m pytest tests/test_storage_and_memory.py -q`
- `python3 -m pytest tests/test_daily_receipt.py -q`
- `python3 -m pytest -q`
- `python3 -m ruankao_agent.cli init --root /tmp/ruankao-review-log-<id> --as-of 2026-06-29`
- Tests assert:
  - each review writes a durable log row;
  - multiple attempts survive reopening the SQLite database;
  - daily receipts include review log metrics and recent review grades.

## 2026-06-29 Round 007 - Memory Diagnostics From Review History

### Learner Friction

Review history is useful only if it turns into action. After Round 006, the
system could store attempts, but it still could not tell the learner which cards
were stable, untested, due, unstable, or repeatedly failing.

### Change

- Added `MemoryDiagnostic` and `diagnose_memory()` to `memory.py`.
- Classified cards as:
  - `leech`: repeated low-grade reviews;
  - `unstable`: latest review is low-grade;
  - `due`: scheduled for review now;
  - `untested`: no retrieval attempt yet;
  - `stable`: reviewed and not urgent.
- Extended daily receipts with weak-memory counts and top memory diagnostics.
- Added the same active diagnostics to the workbench home page.

### Learning Rule Captured

Memory supervision must not stop at logging grades. The system should transform
review history into the next repair action: split the card, add a mistake cause,
review today, or schedule first retrieval.

### Validation

- `python3 -m pytest tests/test_memory_diagnostics.py -q`
- `python3 -m pytest tests/test_daily_receipt.py -q`
- `python3 -m pytest tests/test_web_workbench.py -q`
- `python3 -m pytest -q`
- Tests assert:
  - diagnostics rank leech, unstable, due, untested, and stable cards in action order;
  - daily receipts mark repeated low-grade cards as `leech`;
  - the workbench surfaces weak-card diagnostics and repair actions.

## 2026-06-29 Round 008 - Stage-Only Night Evolution Plan

### Learner Friction

The system had daily receipts and memory diagnostics, but no bounded nighttime
evolution artifact. Without a staged plan, "night evolution" would either do
nothing or risk silently changing live behavior.

### Change

- Added `ruankao_agent.evolution.write_night_evolution_plan()`.
- Generated machine-readable staged plans under `evolution/staged/<date>.json`.
- Generated readable HTML under `reports/nightly/<date>.html`.
- Added CLI command:
  - `python3 -m ruankao_agent.cli night-evolve --root <root> --as-of <YYYY-MM-DD>`
- Added a workbench button that posts to `/night/evolve`.
- Kept the plan `stage_only=true`; it proposes actions but does not mutate core
  skills or live learning rules.

### Learning Rule Captured

Autonomous improvement needs a staging layer. Night work should transform daily
evidence into a bounded action plan before any live system behavior changes.

### Validation

- `python3 -m pytest tests/test_evolution.py -q`
- `python3 -m pytest tests/test_web_workbench.py -q`
- `python3 -m pytest -q`
- `python3 -m ruankao_agent.cli night-evolve --root /tmp/ruankao-night-evolve-<id> --as-of 2026-06-29`
- Tests assert:
  - night evolution creates a staged JSON plan and HTML report;
  - weak memory diagnostics become high-priority repair actions;
  - the CLI prints hook-friendly staged plan paths;
  - the workbench can generate and serve the nightly HTML plan.

## 2026-06-29 Round 009 - Codex Operations For Daily Close And Night Evolution

### Learner Friction

The system had the right CLI commands, but daily use should not require
remembering Python module invocations. The learner should be able to ask Codex
for a named operation.

### Change

- Added `.codex/commands/ruankao-daily-close.md`.
- Added `.codex/commands/ruankao-night-evolve.md`.
- Updated `README.md` daily-use instructions.
- Daily close now has a named Codex operation for:
  - Cheko weak-area seeding;
  - daily receipt generation.
- Night evolution now has a named Codex operation for stage-only plan generation.

### Learning Rule Captured

Recurring learning-system actions should have stable names. A companion system
should reduce command memory load, especially for the actions that must happen
every day.

### Validation

- Command docs point at the local `ruankao-agent` root.
- README exposes both daily operations.
- `python3 -m pytest -q`
- `rg -n "ruankao-daily-close|ruankao-night-evolve|night-evolve|daily-receipt|cheko-seed-cards" .codex/commands README.md ruankao-agent/docs/OPTIMIZATION_LOG.md`

## 2026-06-29 Round 010 - Three-Front Route Coverage Map

### Learner Friction

The workbench tracked cards and diagnostics, but it still did not answer a
campaign-level question: are choice, case, and essay all being covered, or is one
front silently starving?

### Change

- Added `ruankao_agent.route_map.write_route_map()`.
- Generated JSON and HTML under `reports/routes/<date>.*`.
- Added CLI command:
  - `python3 -m ruankao_agent.cli route-map --root <root> --as-of <YYYY-MM-DD>`
- Added a workbench action that posts to `/routes/map`.
- Each front now reports:
  - total cards;
  - due cards;
  - weak cards;
  - untested cards;
  - a route status and next action.

### Learning Rule Captured

The exam has three fronts. The system should keep all three visible, because a
learner can feel busy while still starving case practice or essay expression.

### Validation

- `python3 -m pytest tests/test_route_map.py -q`
- `python3 -m pytest tests/test_web_workbench.py -q`
- `python3 -m pytest -q`
- `python3 -m ruankao_agent.cli route-map --root /tmp/ruankao-route-map-<id> --as-of 2026-06-29`
- Tests assert:
  - route maps summarize choice, case, and essay coverage;
  - weak cards turn the affected route red;
  - the CLI prints report paths;
  - the workbench can generate and serve the route coverage HTML.

## 2026-06-29 Round 011 - Practice Session Ledger

### Learner Friction

The system could manage memory and route coverage, but it did not preserve
actual practice sessions. Passing the exam requires remembering what was
practiced, scored, timed, and missed across choice, case, and essay fronts.

### Change

- Added `practice_sessions` SQLite table.
- Added `PracticeSession`, `add_practice_session()`, and `list_practice_sessions()`.
- Added workbench "练习记录" form and recent practice list.
- Extended daily receipts with:
  - total practice sessions;
  - today's practice count;
  - practice front counts;
  - recent practice sessions.
- Extended night evolution with `protect-exam-practice` when no practice was
  recorded for the day.

### Learning Rule Captured

Memory review is necessary but not sufficient. The system must also track real
exam practice: score, duration, topic, source, and mistakes.

### Validation

- `python3 -m pytest tests/test_storage_and_memory.py -q`
- `python3 -m pytest tests/test_daily_receipt.py -q`
- `python3 -m pytest tests/test_web_workbench.py -q`
- `python3 -m pytest tests/test_evolution.py -q`
- `python3 -m pytest -q`
- Tests assert:
  - practice sessions survive SQLite reopen and front filtering;
  - daily receipts include practice metrics and recent practice;
  - the workbench writes and renders practice sessions;
  - night evolution warns when no practice session was recorded.

## 2026-06-29 Round 012 - Route Map Reads Practice Ledger

### Learner Friction

Round 010 made the three-front route map visible, and Round 011 added practice
sessions. Those two facts were still disconnected: the route map could say a
front had cards, but not whether it had real practice.

### Change

- Extended route maps with per-front:
  - practice session count;
  - today's practice count;
  - latest practice date.
- Updated route status rules so a front with cards but no practice is yellow.
- Kept weak memory cards as red because repair still takes priority over adding
  more raw practice.

### Learning Rule Captured

Coverage means both memory and use. A route with cards but no real exercises is
not healthy yet.

### Validation

- `python3 -m pytest tests/test_route_map.py -q`
- `python3 -m pytest -q`
- Tests assert:
  - route maps include practice counts and latest practice date;
  - weak-card routes remain red;
  - rendered HTML shows practice metrics.

## 2026-06-29 Round 013 - Risk Reads Practice Coverage

### Learner Friction

Practice sessions were stored, but the main status line still treated case and
essay gaps as healthy because loop signals used placeholder values. That could
make the dashboard green while the learner only practiced choice questions.

### Change

- Extended `build_daily_loop_snapshot()` with `practice_sessions`.
- Computed:
  - fronts absent in the last 7 days;
  - days since latest case practice;
  - days since latest essay practice;
  - completed essay practice count.
- Passed practice sessions from CLI/dashboard and workbench snapshots.
- Preserved old empty-database behavior: if no practice sessions exist yet, the
  system does not punish the learner for unknown history.

### Learning Rule Captured

Risk should be evidence-based. Once practice tracking begins, the system should
use real practice coverage instead of optimistic defaults.

### Validation

- `python3 -m pytest tests/test_cli.py -q`
- `python3 -m pytest tests/test_campaign_and_risk.py -q`
- `python3 -m pytest tests/test_web_workbench.py -q`
- `python3 -m pytest -q`
- Tests assert:
  - fresh init can still start green;
  - once practice tracking starts, choice-only practice makes missing case/essay red;
  - touching all three fronts can recover the status to green.

## 2026-06-29 Round 014 - Explainable Risk Reasons

### Learner Friction

The dashboard could turn red, yellow, or green, but it did not explain why.
Without reasons, risk becomes a warning light instead of a coachable signal.

### Change

- Added `risk_reasons` to `DailyLoopSnapshot`.
- Derived reasons from the same signals used by risk evaluation:
  - missed minimum loop;
  - absent exam fronts;
  - review backlog;
  - case/essay staleness;
  - reserve consumption;
  - late essay-count risk.
- Added risk reasons to workbench home.
- Added risk reasons to `/api/status`.

### Learning Rule Captured

Supervision should be explainable. The system should tell the learner which
constraint was violated, not only that risk is red.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- `python3 -m pytest tests/test_cli.py -q`
- `python3 -m pytest -q`
- Tests assert:
  - normal status includes a normal reason;
  - practice gaps produce a concrete risk reason;
  - CLI status behavior remains stable.

## 2026-06-29 Round 015 - Daily Cycle Script For Scheduled Runs

### Learner Friction

The system had separate commands for Cheko seeding, daily receipts, route maps,
and night evolution. A human can run them one by one, but a scheduled job needs
one stable entry point.

### Change

- Added `run-daily-cycle.command`.
- Added `/ruankao-daily-cycle` Codex command.
- Updated README daily-use instructions.
- Updated `.gitignore` so local `reports/` and staged evolution outputs are not
  accidentally committed.
- The cycle runs:
  - Cheko weak-area seeding;
  - daily receipt generation;
  - three-front route map generation;
  - stage-only night evolution plan generation.

### Learning Rule Captured

Daily closure should be one callable operation. The learner can still inspect
each artifact, but the loop itself needs a single scheduled-task entry point.

### Validation

- `chmod +x run-daily-cycle.command`
- `./run-daily-cycle.command 2026-06-29`
- `python3 -m pytest -q`
- Script follows the same root layout as `start-workbench.command`.

## 2026-06-29 Round 016 - launchd Template For Nightly Automation

### Learner Friction

Round 015 created one daily-cycle script, but there was still no concrete local
scheduled-task template. The learner would have to remember how to wire macOS
automation by hand.

### Change

- Added `automation/launchd/com.pedan.ruankao.daily-cycle.plist`.
- Added `docs/AUTOMATION.md` with manual install and unload commands.
- Added `ruankao-agent/logs/` to `.gitignore`.
- Linked automation docs from README.
- Did not install or load the LaunchAgent automatically.

### Learning Rule Captured

Automation should be inspectable before it is active. Nightly evolution is
powerful enough that the schedule must be explicit and reversible.

### Validation

- launchd template is stored in version control.
- Automation docs include manual install and unload commands.
- `plutil -lint automation/launchd/com.pedan.ruankao.daily-cycle.plist`
- `python3 -m pytest -q`

## 2026-06-29 Round 017 - SQLite Schema Version Stamp

### Learner Friction

The SQLite store has evolved quickly: review logs, practice sessions, receipts,
route maps, and risk signals all depend on schema shape. Without a version stamp,
future migrations and nightly evolution cannot know what structure they are
reading.

### Change

- Added `SCHEMA_VERSION`.
- Added `schema_meta` SQLite table.
- Added `RuankaoStore.schema_version()`.
- Wrote the current schema version during `initialize()`.
- Added `schema_version` to daily receipt JSON and HTML.

### Learning Rule Captured

A system that evolves with the learner needs to know its own structural version.
Memory should include not only study data, but also the shape of the store that
holds it.

### Validation

- `python3 -m pytest tests/test_storage_and_memory.py -q`
- `python3 -m pytest tests/test_daily_receipt.py -q`
- `python3 -m pytest -q`
- Tests assert:
  - schema version is written and survives reopen;
  - daily receipts include a non-unknown schema version.

## 2026-06-29 Round 018 - Memory Cards To Obsidian Vault

### Learner Friction

The Memory War Room existed in SQLite and the vault had directories, but ordinary
memory cards were not yet visible as Obsidian notes. That made the knowledge
network harder to browse and manually refine.

### Change

- Added `sync_memory_cards_to_vault()`.
- Added generated markdown notes under the existing `10-memory-war-room` card
  type directories.
- Added CLI command:
  - `python3 -m ruankao_agent.cli vault-sync --root <root>`
- Added workbench action that posts to `/vault/sync`.
- Default behavior is non-destructive: existing notes are skipped unless
  overwrite is explicitly requested.

### Learning Rule Captured

SQLite remains the scheduling fact source, but Obsidian should expose the memory
network for browsing, linking, and manual improvement.

### Validation

- `python3 -m pytest tests/test_vault_and_dashboard.py -q`
- `python3 -m pytest tests/test_cli.py -q`
- `python3 -m pytest tests/test_web_workbench.py -q`
- `python3 -m pytest -q`
- Tests assert:
  - memory cards become markdown notes in the right type directory;
  - repeated sync skips existing notes by default;
  - CLI and workbench sync paths work.

## 2026-06-29 Round 019 - Raw Records To Mein Du Uns Vault

### Learner Friction

Memory cards could sync to Obsidian, but the pyramid bottom layer still stayed
inside SQLite. The learner's notes, agent analysis, and external evidence should
also be visible in the vault under Mein, Du, and Uns.

### Change

- Added `sync_raw_records_to_vault()`.
- Wrote raw records into:
  - `20-mein`
  - `30-du`
  - `40-uns`
- Added CLI command:
  - `python3 -m ruankao_agent.cli raw-vault-sync --root <root>`
- Added workbench action that posts to `/vault/sync-raw`.
- Kept default behavior non-destructive: existing raw notes are skipped.

### Learning Rule Captured

The bottom layer of the knowledge pyramid must be inspectable. Raw material is
not noise; it is where future cards, principles, and architecture judgement grow.

### Validation

- `python3 -m pytest tests/test_vault_and_dashboard.py -q`
- `python3 -m pytest tests/test_cli.py -q`
- `python3 -m pytest tests/test_web_workbench.py -q`
- `python3 -m pytest -q`
- Tests assert:
  - Mein/Du/Uns raw records land in the correct vault directories;
  - repeated sync skips existing notes;
  - CLI and workbench raw sync paths work.

## 2026-06-29 Round 020 - Daily Cycle Includes Vault Sync

### Learner Friction

Vault sync existed as separate actions, but the daily-cycle script did not call
them. A scheduled daily loop should move both SQLite state and Obsidian-visible
knowledge forward.

### Change

- Updated `run-daily-cycle.command` to run:
  - `vault-sync`
  - `raw-vault-sync`
- Updated `/ruankao-daily-cycle` command docs.
- Updated README daily-cycle description.
- Kept sync non-destructive by default.

### Learning Rule Captured

The daily loop should end with a readable knowledge network. Obsidian is not an
occasional export; it is part of the daily closure surface.

### Validation

- `./run-daily-cycle.command 2026-06-29`
- `python3 -m pytest -q`
- Script output includes memory-card vault sync and raw-record vault sync.

## 2026-06-29 Round 021 - Robust Empty YAML Lists In Vault Sync

### Learner Friction

Vault sync could produce awkward frontmatter when a card or raw record had no
fronts or topics. That is easy to miss early, but brittle once Obsidian,
scripts, or future agents parse the notes.

### Change

- Added a shared `_yaml_list()` helper in `vault.py`.
- Rendered empty lists as `key: []`.
- Applied it to memory-card fronts and raw-record topics/fronts.

### Learning Rule Captured

Generated knowledge files should be boringly parseable. Durable notes are part
of the learning system, not a pretty export.

### Validation

- `python3 -m pytest tests/test_vault_and_dashboard.py -q`
- `python3 -m pytest -q`
- Tests assert:
  - memory cards without fronts render `fronts: []`;
  - raw records without topics/fronts render `topics: []` and `fronts: []`.

## 2026-06-29 Round 022 - Architect Thinking Skill Seed

### Learner Friction

The system stored cards, practice, routes, and vault notes, but the requested
"architect thinking" skill was still implicit. The seven most central
architecture principles needed a concrete local skill seed that can evolve.

### Change

- Added `skills/architect-thinking/SKILL.md`.
- Captured seven core principles:
  - 场景先于方案
  - 质量属性可度量
  - 取舍必须显式
  - 边界与职责先行
  - 简单可演进优先
  - 风险驱动验证
  - 证据闭环沉淀
- Added a compact workflow for architecture analysis, ruankao case/essay answers,
  and local-system deposits.
- Updated README to mention the local skill seed.

### Learning Rule Captured

Architectural ability should have a stable kernel. The kernel should be small
enough to remember, but strong enough to guide case analysis, essay writing, and
real design judgement.

### Validation

- `python3 -m pytest tests/test_architect_thinking_skill.py -q`
- `python3 -m pytest -q`
- Tests assert the skill exists and keeps all seven core principles.

## 2026-06-29 Round 023 - Seed Core Principles Into Memory

### Learner Friction

Round 022 created the architect-thinking skill seed, but the seven principles
were still only text. To actually train them, they need to become principle
cards in the Memory War Room.

### Change

- Added `ruankao_agent.principles`.
- Added `CORE_ARCHITECTURE_PRINCIPLES`.
- Added `seed_core_principles()`.
- Added CLI command:
  - `python3 -m ruankao_agent.cli seed-principles --root <root> --next-due <YYYY-MM-DD>`
- Added principle seeding to `run-daily-cycle.command`.
- Updated README and `/ruankao-daily-cycle` docs.

### Learning Rule Captured

Principles are not just prose. They must become retrievable memory objects so
they can be practiced, challenged, linked, and eventually replaced if evidence
demands it.

### Validation

- `python3 -m pytest tests/test_principles.py -q`
- `python3 -m pytest tests/test_architect_thinking_skill.py -q`
- `./run-daily-cycle.command 2026-06-29`
- `python3 -m pytest -q`
- Tests assert:
  - seven core principles become principle cards;
  - repeated seeding skips existing titles;
  - CLI seeding creates all seven cards.
