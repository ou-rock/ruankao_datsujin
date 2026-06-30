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

## 2026-06-29 Round 024 - Core Principle Relation Seed

### Learner Friction

The seven architecture principles were seeded as cards, but still behaved like a
list. The learner explicitly wanted principles to support, constrain, conflict,
and link as a logic network.

### Change

- Added `CORE_ARCHITECTURE_RELATIONS`.
- Seeded initial principle links such as:
  - 场景先于方案 supports 质量属性可度量
  - 质量属性可度量 supports 风险驱动验证
  - 取舍必须显式 constrains 简单可演进优先
  - 风险驱动验证 supports 证据闭环沉淀
- Updated `seed_core_principles()` to create missing relations after cards exist.
- Added relation duplicate protection.
- Updated CLI output with relation counts.

### Learning Rule Captured

Architecture principles are not a checklist. They form a graph of support,
constraint, and feedback; learning improves when the graph becomes explicit.

### Validation

- `python3 -m pytest tests/test_principles.py -q`
- `python3 -m pytest tests/test_cheko.py -q`
- `./run-daily-cycle.command 2026-06-29`
- `python3 -m pytest -q`
- Tests assert:
  - first seeding creates all principle relations;
  - repeated seeding skips existing relations;
  - Cheko seed output remains unchanged.

## 2026-06-29 Round 025 - Architect Review Command

### Learner Friction

The architect-thinking skill seed existed, but the learner still needed an easy
Codex entry point to apply it to an answer, design, or essay paragraph.

### Change

- Added `.codex/commands/ruankao-architect-review.md`.
- Linked the command from README.
- The command points Codex to the local `architect-thinking/SKILL.md` and asks it
  to apply the Core Seven review shape.

### Learning Rule Captured

A principle kernel becomes useful when it is applied repeatedly to real answers.
The review command makes that application path explicit.

### Validation

- Command doc points at the local skill file.
- README lists the command with the other daily operations.

## 2026-06-29 Round 026 - Practice Score Ratios In Reports

### Learner Friction

Practice sessions stored score and max score, but daily receipts and route maps
did not summarize score quality. The learner could see that practice happened,
but not how well it went.

### Change

- Added per-front `average_score_ratio` to route maps.
- Added overall `practice_score_ratio` to daily receipts.
- Ratios only use sessions with both `score` and positive `max_score`.
- HTML renders ratios as percentages and shows `none` when no valid score exists.

### Learning Rule Captured

Practice volume and practice quality are different signals. The system should
track both.

### Validation

- `python3 -m pytest tests/test_daily_receipt.py -q`
- `python3 -m pytest tests/test_route_map.py -q`
- `python3 -m pytest -q`
- Tests assert:
  - daily receipt shows a 70% practice score ratio for 7/10;
  - route map shows a 75% front score ratio for 3/4.

## 2026-06-29 Round 027 - Local State JSON Export

### Learner Friction

The SQLite store now carries raw notes, memory cards, reviews, practice logs,
and principle relations. That is enough local state that the learner needs a
single backup and audit artifact outside the live database.

### Change

- Added `export_state.py` to write `exports/state-YYYY-MM-DD.json`.
- Export includes schema version, metrics, raw records, memory cards, review
  logs, practice sessions, and principle relations.
- Added `ruankao-agent export-state --root ... --as-of ...`.
- Added a workbench button plus `/exports/...` JSON serving.
- Ignored `ruankao-agent/exports/` so personal backups are not committed.

### Learning Rule Captured

Memory is strategic only if it is portable. A local-first learner agent needs a
recoverable state snapshot, not just a live database.

### Validation

- `python3 -m pytest tests/test_export_state.py -q`
- `python3 -m pytest tests/test_web_workbench.py -q`
- `python3 -m pytest -q`
- Tests assert:
  - the export captures all current store tables;
  - the CLI prints a hook-friendly export path;
  - the workbench can create and serve the JSON snapshot.

## 2026-06-29 Round 028 - Daily Cycle Includes State Export

### Learner Friction

The state export existed, but it was still a manual action. A learner who relies
on nightly evolution should not need to remember one more backup command at the
end of the day.

### Change

- Added `export-state` to `run-daily-cycle.command`.
- Updated README, `/ruankao-daily-cycle`, and automation docs.
- Added a script-level test that guards the daily closure command list and keeps
  export after raw vault sync.

### Learning Rule Captured

Backups should ride the loop. The best memory snapshot is the one created
automatically after the day's capture, review, route map, vault sync, and
night-evolution staging.

### Validation

- `python3 -m pytest tests/test_daily_cycle_script.py -q`
- `./run-daily-cycle.command 2026-06-29`
- `python3 -m pytest -q`
- Tests assert `export-state` is part of the daily cycle and runs after raw
  vault sync.

## 2026-06-30 Round 029 - Interactive Study Mode For Mein And Du

### Learner Friction

Uns can grow from Cheko, NotebookLM, and other external sources, but Mein and Du
need live dialogue. The system needed a mode where the learner speaks first,
Codex refines second, and both sides are recorded instead of lost in chat.

### Change

- Added `study.py` with `capture_study_turn()`.
- Added CLI command:
  - `python3 -m ruankao_agent.cli study-turn --root <root> --topic <topic> --user <text> --assistant <text> --front case`
- Added `/ruankao-study-mode` Codex command with a one-question-at-a-time
  protocol.
- Updated README daily-use commands.

### Learning Rule Captured

Mein is not polished knowledge; it is the learner's current model. Du is not a
lecture; it is the agent's refinement that pushes the learner one step further.
Both must be recorded turn by turn.

### Validation

- `python3 -m pytest tests/test_study_mode.py -q`
- Tests assert:
  - each learning turn creates one Mein raw record and one Du raw record;
  - topic, fronts, and promotion status are preserved;
  - the CLI prints hook-friendly record IDs;
  - the Codex command documents the one-question-at-a-time protocol.

## 2026-06-30 Round 030 - Socratic Study Positioning

### Learner Friction

The first study-mode draft recorded Mein and Du, but it did not yet behave like
entering a dedicated learning perspective. It also blurred daytime study actions
with principle-link mining, which belongs to night evolution.

### Change

- Updated `/ruankao-study-mode` to start with:
  - `我在哪`
  - `你在哪`
  - `我们要去哪`
- Added ruankao-teach and Uns as question-seeding inputs.
- Clarified that Uns creates questions or candidates, not direct conclusions.
- Removed daytime principle-link creation from study-mode behavior.
- Added optional `study-turn` position fields:
  - `--learner-position`
  - `--codex-position`
  - `--destination`

### Learning Rule Captured

Socratic learning needs position awareness. The agent should know the learner's
current model, its own role, and the next reachable target before asking.

### Validation

- `python3 -m pytest tests/test_study_mode.py -q`
- Tests assert:
  - study turns persist the three position fields in Mein and Du records;
  - the command mentions ruankao-teach and Uns question seeding;
  - principle links are deferred to night mining.

## 2026-06-30 Round 031 - Workbench First Action Strip

### Learner Friction

The workbench header showed counts and risk, but a learner opening it still had
to translate those signals into a first action. Red risk should become a visible
next step, not just a status label.

### Change

- Added a `今日第一动作` strip below the top metrics.
- Prioritized the action by:
  - due reviews;
  - active memory diagnostics;
  - missing practice;
  - study-mode continuation.
- Added three stable shortcuts:
  - `处理今日闭环`
  - `记录练习`
  - `今日三任务`
- Styled the strip with risk-colored left border and responsive stacking.

### UX Rule Captured

The first viewport should answer "what should I do next?" before asking the
learner to interpret dashboards, reports, or raw counts.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert:
  - the workbench home shows the first-action strip;
  - due reviews become the primary action;
  - red risk is reflected in the strip class.

## 2026-06-30 Round 032 - One-Tap Review Grades

### Learner Friction

The due-card review form required opening a select field and then submitting.
That is small friction, but spaced repetition depends on fast, repeated
micro-decisions.

### Change

- Replaced the review select with six one-tap grade buttons.
- Kept the same `/reviews` endpoint and `grade` field.
- Added compact grade labels:
  - 5 很稳
  - 4 会
  - 3 勉强
  - 2 模糊
  - 1 不会
  - 0 空白
- Marked low grades with a danger color.

### UX Rule Captured

Review grading should feel like a fast flashcard action, not a form-filling
task.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert:
  - due cards render a grade-button row;
  - grades 5 and 0 submit through the same `grade` field;
  - the old grade select is gone.

## 2026-06-30 Round 033 - Three-Front Radar In Header

### Learner Friction

The workbench already had a full route map, but it lived behind a generated
report. The first screen still did not make the three exam fronts comparable at
a glance.

### Change

- Added a `三题型雷达` strip to the workbench header.
- Rendered one compact card each for:
  - 选择题
  - 案例题
  - 论文题
- Each card shows:
  - total cards;
  - due cards;
  - today's practice count;
  - a small next action.
- Used red/yellow/green top borders to make front status scannable.

### UX Rule Captured

Route awareness should be visible before the learner opens a report. The
dashboard should make imbalance between choice, case, and essay hard to miss.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert:
  - all three fronts appear in the header radar;
  - a front with due cards is red;
  - a front practiced today is green.

## 2026-06-30 Round 034 - Segmented Practice Front Control

### Learner Friction

The practice form treated the exam front as a dropdown. Choice, case, and essay
are not a long option list; they are the three core modes of the campaign and
should be visible at the point of logging practice.

### Change

- Replaced the practice `front` select with a segmented radio control.
- Kept the same submitted `front` field and values:
  - `choice`
  - `case`
  - `essay`
- Added reusable `.segmented`, `.field`, and `.field-label` styles.

### UX Rule Captured

Primary modes should be visible and one-tap. Hiding choice/case/essay in a
dropdown makes the learner do unnecessary work before recording evidence.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert:
  - the practice form renders a segmented control;
  - all three front radio values are present;
  - the old front select is gone.

## 2026-06-30 Round 035 - Practice Numeric Input Constraints

### Learner Friction

Practice score, max score, and duration were rendered as unconstrained text
inputs. The backend could parse them, but the browser did not help prevent
obvious input mistakes.

### Change

- Changed score to `type="number" min="0" step="0.5"`.
- Changed max score to `type="number" min="1" step="0.5"`.
- Changed duration to `type="number" min="1" step="1"`.
- Kept existing field names and backend parsing unchanged.

### UX Rule Captured

The interface should make valid evidence easier to enter than invalid evidence.
Practice logs are later used for risk and route decisions, so small data quality
guards matter.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert all three practice numeric fields expose browser-level
  constraints.

## 2026-06-30 Round 036 - Workbench Skip Link

### Learner Friction

The workbench now has a richer header and side navigation. Keyboard users would
otherwise have to tab through that chrome before reaching today's actual study
loop.

### Change

- Added a focus-visible skip link at the top of the workbench.
- The link jumps directly to `#today`.
- Styled it to stay hidden until focused.

### UX Rule Captured

Useful dashboards still need a fast path to the task. Keyboard navigation should
not make the learner pay for every navigation affordance on every visit.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert the skip link points to the today section.

## 2026-06-30 Round 037 - Status Role For Workbench Messages

### Learner Friction

Workbench messages confirm actions such as saved reviews, generated reports, and
sync results. They were visible on screen, but did not carry an explicit status
role for assistive technology.

### Change

- Added `role="status"` to the workbench message element.
- Kept existing message rendering and redirect behavior unchanged.

### UX Rule Captured

Feedback after an action should be announced as feedback, not merely drawn as
text. Small semantic improvements make repeated operations less ambiguous.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert message markup includes `role="status"`.

## 2026-06-30 Round 038 - Dynamic Workbench Page Title

### Learner Friction

The browser tab title stayed generic even though the workbench knows the current
countdown and risk state. With Cheko, NotebookLM, local reports, and the
workbench open together, the tab should identify the current campaign status.

### Change

- Changed the workbench `<title>` to include:
  - page name;
  - countdown;
  - risk status.

### UX Rule Captured

Context should survive tab switching. A useful app title names the work surface
and the state that matters when the user returns.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert the title includes `D-117` and `green` in the empty demo state.

## 2026-06-30 Round 039 - Segmented Mein Du Uns Source Control

### Learner Friction

The raw-record capture form hid Mein, Du, and Uns inside a dropdown. These are
not incidental options; they are the bottom-layer identity model of the whole
learning system.

### Change

- Replaced the raw-record `source` select with a segmented radio control.
- Kept the same submitted `source` field and values:
  - `mein`
  - `du`
  - `uns`
- Defaulted the capture path to Mein, matching learner-first entry.

### UX Rule Captured

Core mental models should be visible where the learner makes the decision.
Mein, Du, and Uns are learning identities, not a hidden metadata field.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert:
  - the raw-record form renders a segmented source control;
  - all three source values are present;
  - the old source select is gone.

## 2026-06-30 Round 040 - Segmented Raw Record Status Control

### Learner Friction

The raw-record source became visible, but promotion status still lived in a
dropdown. The bottom layer needs quick status judgement: raw, extracted, tested,
promoted, or rejected.

### Change

- Replaced the raw-record `promotion_status` select with segmented radio
  controls.
- Added `.segmented.flow` so five statuses wrap cleanly.
- Kept the same submitted `promotion_status` field and values.

### UX Rule Captured

Workflow state should be scannable. A learner reviewing raw material should see
whether a note is still raw, already extracted, tested, promoted, or rejected
without opening a control.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert:
  - all five status values are visible radio options;
  - raw remains the default;
  - the old status select is gone.

## 2026-06-30 Round 041 - Practice List Score Ratio

### Learner Friction

The recent practice list showed raw scores such as `8/15`, but did not surface
the score ratio. Learners should not have to mentally calculate whether a
practice attempt was roughly half, passing, or strong.

### Change

- Added `ratio=<percent>` to recent practice rows.
- Preserved the original `score/max_score` text.
- Rendered `ratio=none` when score or max score is missing.

### UX Rule Captured

Practice evidence should be scannable. Raw marks are useful, but ratio makes
quality easier to compare across fronts and exercises.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert an 8/15 practice session renders `ratio=53%`.

## 2026-06-30 Round 042 - Localized Practice Front Labels

### Learner Friction

Recent practice rows displayed internal front values such as `case`. The rest of
the workbench speaks in choice, case, and essay as exam fronts, so the practice
list should not require translating enum values.

### Change

- Added a small front-label helper for workbench display.
- Changed recent practice rows to show:
  - 选择题
  - 案例题
  - 论文题
- Kept stored values and submitted form values unchanged.

### UX Rule Captured

Internal enums are for code. Learners should see the exam language they use
while deciding what to practice next.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert a case practice row renders `案例题`.

## 2026-06-30 Round 043 - Localized Memory Card Type Labels

### Learner Friction

Card lists displayed internal card type values such as `concept`. The learner
works with concept cards, principle cards, comparison cards, scenario cards, and
expression cards, not enum names.

### Change

- Added a card type label helper for workbench display.
- Changed card list badges to show:
  - 原则卡
  - 概念卡
  - 对比卡
  - 场景卡
  - 表达卡
- Kept stored values and form values unchanged.

### UX Rule Captured

Visible labels should match the learner's study vocabulary. Internal enum names
belong in data and code, not in the card scanning surface.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert a concept due card renders `概念卡`.

## 2026-06-30 Round 044 - Localized Card Front Metadata

### Learner Friction

Card rows still displayed front metadata as internal values such as `fronts=case`.
That made the row partly learner-facing and partly implementation-facing.

### Change

- Changed card row metadata from `fronts=case` style to `题型=案例题`.
- Reused the front label helper already used by practice rows.
- Kept CLI, storage, and JSON enum values unchanged.

### UX Rule Captured

Metadata in a learner-facing list should use the same vocabulary as the visible
controls. The card list should read like study material, not debug output.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert a case due card renders `题型=案例题`.

## 2026-06-30 Round 045 - Localized Card Review Metadata

### Learner Friction

After localizing card type and fronts, card rows still showed `due` and
`reviews`. These English debug-style labels stood out in an otherwise Chinese
learning surface.

### Change

- Changed card row metadata:
  - `due=` to `到期=`
  - `reviews=` to `复习=...次`
- Kept dates and counts unchanged.

### UX Rule Captured

Microcopy consistency matters in repeated scanning surfaces. A review queue
should not alternate between learner language and implementation labels.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert due cards render localized due date and review count labels.

## 2026-06-30 Round 046 - Localized Practice Metadata

### Learner Friction

Recent practice rows had Chinese titles but English metadata labels such as
`score`, `ratio`, `source`, `duration`, and `date`. That made the row feel like a
debug readout instead of a learning record.

### Change

- Changed recent practice metadata labels:
  - `score` to `得分`
  - `ratio` to `得分率`
  - `source` to `来源`
  - `duration` to `耗时`
  - `date` to `日期`
- Rendered duration as `N分钟` when present.

### UX Rule Captured

Practice evidence should read like the learner's own logbook. English field
names are useful internally, but repeated review surfaces should use study
language.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert a practice row renders `得分率=53%` and `耗时=35分钟`.

## 2026-06-30 Round 047 - Localized Capture Status Choices

### Learner Friction

The three-source capture form used a segmented control for material status, but
the visible labels were still raw enum values: `raw`, `extracted`, `tested`,
`promoted`, and `rejected`. That made the bottom layer feel like a database
field rather than a material-evolution workflow.

### Change

- Kept the stored `promotion_status` values unchanged for compatibility.
- Localized visible status choices:
  - `raw` to `原始`
  - `extracted` to `已提炼`
  - `tested` to `已检验`
  - `promoted` to `已升格`
  - `rejected` to `已淘汰`
- Extracted status radio rendering into a small helper so the vocabulary can be
  iterated later without editing the main HTML block.

### UX Rule Captured

Capture controls should speak in the learner's workflow language. Internal
state names can remain stable underneath, but the surface should describe how a
note moves through the learning pyramid.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert status radio values remain stable while labels render in Chinese.

## 2026-06-30 Round 048 - Localized Daily Receipt Metadata

### Learner Friction

Daily receipts are meant to be read during review and nightly evolution, but the
recent-material sections still used machine-style labels such as `status`,
`type`, `grade`, `score`, and `duration`. The workbench had become more
learner-facing, while receipts still exposed internal field names.

### Change

- Localized HTML-only receipt metadata for recent records, diagnostics, cards,
  reviews, and practice sessions.
- Localized count labels for source, card type, and exam front distributions.
- Kept the JSON receipt payload unchanged so hooks, scripts, and exports can
  keep reading stable enum values.
- Rendered missing values as `未记录` and practice duration as `N分钟`.

### UX Rule Captured

Human receipts should read like study evidence, not raw telemetry. Preserve
machine contracts in JSON, but make HTML receipts suitable for a learner's daily
review loop.

### Validation

- `python3 -m pytest tests/test_daily_receipt.py -q`
- Tests assert receipt HTML renders `评分=4`, `得分=7/10`, `耗时=18分钟`,
  localized card/front labels, and no longer renders old `grade=` or `score=`
  metadata.

## 2026-06-30 Round 049 - Localized Route Map Status

### Learner Friction

The three-front route map exists to answer "where am I, and where should I go
next?", but each route card still showed `status=red` and
`last_practice=... | focus=...`. That made a strategic map feel like a raw
debug panel.

### Change

- Changed route status display from `status=red/yellow/green` to visible
  `状态：红灯/黄灯/绿灯` badges.
- Changed route footer metadata:
  - `last_practice` to `最近练习`
  - `focus` to `焦点`
- Rendered missing route ratios and dates as `未记录` instead of `none`.
- Kept JSON route payload values unchanged for scripts and automation.

### UX Rule Captured

A route map should be instantly scannable. Machine states can remain stable in
JSON, but the learner-facing map should show traffic-light judgement and next
focus in study language.

### Validation

- `python3 -m pytest tests/test_route_map.py -q`
- Tests assert the route map renders localized state badges, localized footer
  metadata, and no longer renders `status=red` or `last_practice=`.

## 2026-06-30 Round 050 - Workbench Missing Value Language

### Learner Friction

The workbench still rendered missing card and practice fields as `none`. This
could appear on normal in-progress material: cards without a due date, cards
without chosen exam fronts, or quick practice logs without scores and timing.

### Change

- Replaced visible workbench missing values with `未记录`.
- Applied the change to:
  - card fronts;
  - card due dates;
  - practice score;
  - practice score ratio;
  - practice source;
  - practice duration.
- Changed multi-front labels from comma-separated values to Chinese顿号
  separation.

### UX Rule Captured

An incomplete learning artifact should feel like something to refine, not a
programming null. Use learner-facing missing-value language in visible lists.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert missing card and practice fields render as `未记录` and no longer
  render old visible `none` metadata.

## 2026-06-30 Round 051 - Daily Receipt Missing Ratio Language

### Learner Friction

Daily receipts could still show `none` for the overall practice score ratio when
there were no scored practice sessions. That one field contradicted the newer
`未记录` convention used in workbench and receipt metadata.

### Change

- Changed the daily receipt HTML ratio formatter from `none` to `未记录` when no
  scored practice exists.
- Kept the JSON metric as `null` so automation can still distinguish missing
  data from a real 0% score.

### UX Rule Captured

Missing study evidence should be visible as missing evidence, not as a
programming sentinel. Preserve machine semantics in JSON and learner semantics
in HTML.

### Validation

- `python3 -m pytest tests/test_daily_receipt.py -q`
- Tests assert empty practice history keeps JSON `practice_score_ratio` as
  `null` while HTML renders `练习得分率` as `未记录`.

## 2026-06-30 Round 052 - Learner-Facing Action Feedback

### Learner Friction

Workbench action feedback was technically announced with `role="status"`, but
the message itself still exposed internal URL slugs such as `review-saved` and
`daily-receipt-2026-06-29-written`. After a learner clicks a button, the system
should acknowledge the action in human language.

### Change

- Added a message translation helper for common workbench action slugs.
- Localized feedback for:
  - reviews;
  - three-source records;
  - memory cards;
  - practice sessions;
  - Cheko card seeding;
  - daily receipts;
  - night evolution drafts;
  - route maps;
  - state exports;
  - memory-card and raw-material Obsidian sync.
- Kept unknown messages as escaped raw text for future diagnostics.

### UX Rule Captured

A successful action should close the loop in the learner's language. Technical
event names can remain in URLs, but visible feedback should describe the result
and quantity created or skipped.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert common action slugs render as localized status messages and the
  raw slugs are not visible.

## 2026-06-30 Round 053 - Localized Workbench Risk Signals

### Learner Friction

The workbench had localized reports and action messages, but the main title,
risk metric, header status, and three-front radar still exposed raw risk values:
`green`, `yellow`, and `red`. These values are useful as CSS and JSON states, but
they are not the language a learner scans under time pressure.

### Change

- Changed the workbench title risk suffix to `红灯/黄灯/绿灯`.
- Changed the visible risk metric to the same traffic-light wording.
- Replaced the header status line with localized labels for risk, due cards, and
  backlog.
- Changed three-front radar badges from raw `red/green` text to localized
  traffic-light labels while keeping the raw state classes.

### UX Rule Captured

Risk signals should be immediately legible. Keep raw states in machine-facing
classes and JSON, but use traffic-light labels wherever the learner reads the
status.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert the workbench title, header status, risk metric, and front radar
  render localized traffic-light labels.

## 2026-06-30 Round 054 - Segmented Principle Relation Control

### Learner Friction

The principle network form still used a dropdown for relation type and exposed
enum-like labels such as `supports 支撑` and `conflicts_with 冲突`. Principle
relations are a core architecture-thinking move, so the four choices should be
immediately visible.

### Change

- Replaced the principle relation select with a segmented radio control.
- Kept stored relation values unchanged:
  - `supports`
  - `constrains`
  - `conflicts_with`
  - `derived_from`
- Localized visible labels to `支撑`, `制约`, `冲突`, and `派生`.
- Kept `supports` as the default relation.

### UX Rule Captured

Core thinking moves should be visible, not hidden in menus. Keep the graph
contract stable underneath, but let the learner choose relationships in domain
language.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert the principle relation field renders as segmented radios with
  stable values and no longer renders the relation select.

## 2026-06-30 Round 055 - Numeric Constraints For ID Inputs

### Learner Friction

Several ID fields used `inputmode="numeric"` but not `type="number"` or browser
range constraints. That meant source-record IDs and principle relation IDs could
accept text, zero, or fractional values until the backend rejected them.

### Change

- Added `type="number" min="1" step="1"` to:
  - memory-card source record ID;
  - principle relation From ID;
  - principle relation To ID.
- Kept backend parsing and stored values unchanged.

### UX Rule Captured

Forms should reject impossible values as early as the browser can. Small input
constraints reduce failed submissions and make advanced graph operations feel
less brittle.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert ID inputs now expose browser numeric constraints.

## 2026-06-30 Round 056 - Contextual Learning Placeholders

### Learner Friction

Several high-effort textareas were blank: practice summaries, mistakes,
three-source raw text, card prompts, card answers, and principle relation
rationales. Blank boxes make capture slower because the learner must remember
what kind of evidence is worth preserving.

### Change

- Added contextual placeholders for:
  - practice summary;
  - mistake/cause notes;
  - three-source raw text;
  - three-source summary;
  - memory-card prompt;
  - memory-card answer;
  - principle relation rationale.
- Kept field names, storage, and validation unchanged.

### UX Rule Captured

Free-text fields should pull better thinking from the learner. A placeholder can
act as a small Socratic cue without adding another instructional block to the
page.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert the workbench renders all contextual learning placeholders.

## 2026-06-30 Round 057 - Localized Static Total Map

### Learner Friction

The static dashboard was meant to be the system's total map, but it still looked
like an English template: `Ruankao Agent Dashboard`, `Today's minimum loop`,
`Memory War Room`, `Routes`, `Knowledge Flow`, and raw risk values such as
`green` or `red`.

### Change

- Localized the static dashboard title, hero, metric labels, section headings,
  and navigation labels.
- Rendered risk as `红灯/黄灯/绿灯` in the HTML total map.
- Localized dashboard evidence labels such as due cards, NotebookLM source, main
  battle progress, reserve pool, and review backlog.
- Kept filesystem paths and CLI status output unchanged.

### UX Rule Captured

The total map should be readable as a study artifact, not a project scaffold.
Paths and machine outputs can remain stable, while the learner-facing HTML
speaks the campaign's language.

### Validation

- `python3 -m pytest tests/test_vault_and_dashboard.py -q`
- `python3 -m pytest tests/test_cli.py -q`
- Tests assert the dashboard renders localized map headings, risk labels, due
  card evidence, and navigation links.

## 2026-06-30 Round 058 - Localized Night Evolution Metadata

### Learner Friction

Night evolution reports still exposed raw staging and action metadata:
`stage_only=true` and `id=... | priority=...`. The JSON plan needs those fields,
but the HTML report should read like tomorrow's operating instructions.

### Change

- Changed the visible staging marker to `仅暂存：是/否`.
- Changed action priority metadata to `优先级=高/中/低`.
- Removed visible action IDs from the HTML report while keeping them in JSON.
- Kept CLI output and staged JSON unchanged.

### UX Rule Captured

Night reports should show decisions, not implementation identifiers. Keep action
IDs in machine-readable plans; make the HTML useful for a tired learner scanning
tomorrow's moves.

### Validation

- `python3 -m pytest tests/test_evolution.py -q`
- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert night reports render localized staging and priority labels and no
  longer expose raw action IDs or `priority=`.

## 2026-06-30 Round 059 - Localized Learning Desk Chrome

### Learner Friction

Learning desk pages still had small English UI labels: `Learning Desk`,
`Lesson 0001`, `Reference`, `Cheko Sync`, `Today`, plus `Day` and `Task`
sequence labels. They were not technical contracts; they were visible page
chrome.

### Change

- Localized learning page eyebrows:
  - `Learning Desk` to `学习台`
  - `Lesson 0001` to `第一课`
  - `Reference` to `速查`
  - `Uns` to `Uns 外部资料`
  - `Cheko Sync` to `芝士同步`
  - `Today` to `今日`
- Changed first-week path labels from `Day N` to `第 N 天`.
- Changed today-task labels from `Task N` to `第 N 件`.

### UX Rule Captured

Small labels set the tone of a learning surface. Keep product and source names
when they are meaningful, but localize generic page chrome so the study desk
feels coherent.

### Validation

- `python3 -m pytest tests/test_learning.py -q`
- Tests assert learning pages render localized chrome and no longer expose the
  old generic English labels.

## 2026-06-30 Round 060 - Guard Learning Front Labels

### Learner Friction

The learning desk stores and exchanges exam fronts as compact internal codes in
other parts of the system, such as `choice`, `case`, and `essay`. Reference pages
were already authored with Chinese labels, but the renderer had no guardrail: a
future resource generated from structured data could leak storage codes into the
visible learning surface.

### Change

- Added a single learning-page display map from front codes to Chinese exam
  labels:
  - `choice` to `选择题`
  - `case` to `案例题`
  - `essay` to `论文题`
- Routed reference-page chips through the display map.
- Routed learning-index reference cards through the same display map.

### UX Rule Captured

Storage codes are not learner language. Keep compact codes for commands,
records, and imports; translate them at the last visible boundary before HTML.

### Validation

- `python3 -m pytest tests/test_learning.py -q`
- Added a regression test that renders a reference page with raw front codes and
  asserts the page shows `选择题 / 案例题 / 论文题` instead.

## 2026-06-30 Round 061 - Add Learning Campaign Rail

### Learner Friction

The learning desk explained what to do today and what to read, but its first
screen did not answer the strategic orientation question: where am I, what is
the next stage, and what is the fixed exam endpoint? The workbench had campaign
state, while the learning entrance still felt like a pile of resources.

### Change

- Added a learning-index campaign rail with three stable anchors:
  - `当前位置`
  - `下一站`
  - `终点`
- Reused the existing `Campaign.default()` model instead of hard-coding a second
  timeline.
- Added responsive CSS so the rail is three columns on desktop and one column on
  mobile.

### UX Rule Captured

Learning pages should show local action and global campaign context together.
The learner should never have to mentally reconnect today's task to the
four-month exam strategy.

### Validation

- `python3 -m pytest tests/test_learning.py -q`
- Added a deterministic 2026-06-30 test that checks the learning index shows
  `启动诊断`, next stage `诊断建模`, `D-116`, and endpoint `2026-10-24`.

## 2026-06-30 Round 062 - Timebox Today Tasks

### Learner Friction

The today page told the learner what three actions to do, but it did not bound
how much time to spend. Without a timebox, "今日三任务" can quietly become an
unbounded study session, which increases avoidance and makes completion harder
to judge.

### Change

- Added a `minutes` field to today tasks.
- Assigned a 60-minute study budget:
  - 25 minutes for the largest wrong-answer pool.
  - 15 minutes for the comparison card.
  - 20 minutes for the minimum essay touch.
- Added a visible `时间盒` metric to the today page.
- Added each task's suggested duration to the task card.
- Updated the stop condition to stop after completion or after the timebox is
  used up.

### UX Rule Captured

Daily execution should be finishable. For a companion study agent, a bounded
minimum loop beats a heroic, vague study plan.

### Validation

- `python3 -m pytest tests/test_learning.py -q`
- Tests assert the three tasks carry `25 / 15 / 20` minute budgets and the today
  page shows a 60-minute timebox.

## 2026-06-30 Round 063 - Clarify Workbench Output Actions

### Learner Friction

The workbench had four important generation buttons under the daily loop, but
they appeared as a plain vertical stack. The actions were technically available,
yet a tired learner still had to remember why each artifact mattered.

### Change

- Grouped the daily output actions into a `今日产物生成` operation stack.
- Kept the existing POST routes unchanged:
  - daily receipt
  - night evolution draft
  - three-front route map
  - local state export
- Added one short purpose hint under each button.
- Added responsive grid styling so the actions scan as a compact tool group.

### UX Rule Captured

Command surfaces should explain their learning consequence at the point of use.
A button that changes study state deserves a one-line reason, not a memory test.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert the workbench exposes `今日产物生成` and the new purpose hints while
  preserving all original form actions.

## 2026-06-30 Round 064 - Add Practice Capture Rule

### Learner Friction

The practice form had good fields, but it did not state the minimum standard for
a useful record. A learner could submit a thin entry and later wonder why the
three-front radar, review loop, or night evolution had weak evidence.

### Change

- Added a compact note at the top of the practice form.
- The note says each practice record should preserve:
  - exam front
  - score or completion amount
  - mistake cause
  - next repair action
- Reused the existing workbench visual language with a small `.form-note` style.

### UX Rule Captured

Input forms should teach the shape of good data. The system should improve
record quality before storage, not merely complain after analysis.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert the practice form includes the new capture rule.

## 2026-06-30 Round 065 - Explain Mein Du Uns Boundaries

### Learner Friction

The three-source capture form used the right vocabulary, but the boundary
between `Mein`, `Du`, and `Uns` was only implicit. That is risky because this
bottom layer is where raw experience, Codex synthesis, and external evidence
must stay distinct enough to evolve together.

### Change

- Added a compact source guide under the three-source segmented control.
- The guide defines:
  - `Mein`: learner's original words and stuck points.
  - `Du`: Codex organization, correction, and synthesis.
  - `Uns`: outside material and evidence.
- Styled the guide as lightweight inline chips so it teaches without becoming a
  second manual.

### UX Rule Captured

Core vocabulary should be explained exactly where the learner has to choose it.
The system should protect source identity at capture time, not during cleanup.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert the `三源边界` guide and all three source definitions render in
  the workbench.

## 2026-06-30 Round 066 - Add Memory Card Quality Rule

### Learner Friction

The memory-card form collected title, prompt, answer, fronts, and due date, but
it did not remind the learner what separates a reviewable card from a passive
note. This matters because memory is a strategic layer of the exam system, not a
side archive.

### Change

- Added a compact quality rule at the top of the memory-card form.
- The rule requires a good card to:
  - trigger recall
  - support self-rating
  - map to choice, case, or essay fronts
- It also nudges pure excerpts back into the three-source capture layer first.

### UX Rule Captured

Memory entry should be biased toward retrievability. A card that cannot be
recalled and graded is not yet a useful study asset.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert the memory-card form includes the new quality rule.

## 2026-06-30 Round 067 - Add Principle Link Quality Rule

### Learner Friction

The principle relation form supported support, constraint, conflict, and
derivation, but it did not warn against casual linking. A principle network only
helps architecture thinking if every edge carries real reasoning pressure.

### Change

- Added a compact note at the top of the principle relation form.
- The note says to connect principles only when there is true logical tension:
  support, constraint, conflict, or derivation.
- Kept the segmented relation control and storage behavior unchanged.

### UX Rule Captured

Principle links are claims, not decoration. The UI should bias the learner
toward fewer, stronger edges.

### Validation

- `python3 -m pytest tests/test_web_workbench.py -q`
- Tests assert the principle relation form includes the new link-quality rule.

## 2026-06-30 Round 068 - Localize Vault Exam Fronts

### Learner Friction

Generated Obsidian memory-card notes kept stable `choice / case / essay` values
in YAML, which is good for tools, but the visible `Exam Fronts` section also
showed those machine labels. Obsidian notes are read by the learner, so the body
should speak study language.

### Change

- Kept YAML frontmatter unchanged for structured tooling.
- Added a Markdown display mapper for exam fronts.
- Changed memory-card note bodies to show:
  - `选择题`
  - `案例题`
  - `论文题`
- Changed empty front lists in the visible body from `none` to `未标注`.

### UX Rule Captured

Obsidian frontmatter is for machines; Markdown body is for learning. Preserve
stable codes in YAML, but localize the visible note body.

### Validation

- `python3 -m pytest tests/test_vault_and_dashboard.py -q`
- Tests assert frontmatter still contains `choice`, the body shows Chinese exam
  fronts, and empty visible front lists render as `未标注`.

## 2026-06-30 Round 069 - Add Vault Raw Capture Context

### Learner Friction

Generated raw-record notes preserved source, topics, fronts, and status in YAML,
but the readable Markdown body jumped directly to raw text. In Obsidian, that
forces the learner to inspect frontmatter to understand whether a note came from
Mein, Du, or Uns and which exam front it supports.

### Change

- Added a visible `Capture Context` section to raw-record notes.
- The section renders:
  - source identity with learner-facing labels
  - promotion status
  - topics
  - exam fronts with localized labels
- Kept the YAML frontmatter unchanged for tooling.

### UX Rule Captured

Raw material needs provenance in the reading surface. The learner should be able
to understand a note's role without opening YAML.

### Validation

- `python3 -m pytest tests/test_vault_and_dashboard.py -q`
- Tests assert raw-record notes include readable source, topic, and exam-front
  context in the Markdown body.

## 2026-06-30 Round 070 - Humanize Route Map Footer

### Learner Friction

The three-front route map still rendered route metadata as
`最近练习=... | 焦点=...`. It was technically understandable, but it read like a
debug string inside a learner-facing report.

### Change

- Replaced the pipe-delimited route metadata line with two footer chips:
  - `最近练习：...`
  - `焦点：...`
- Added `.route-foot` styling for compact, scannable metadata.
- Kept the JSON payload and route analysis unchanged.

### UX Rule Captured

Reports should not expose debug-string punctuation in their visible layer. Use
small structured UI elements when the learner is scanning status metadata.

### Validation

- `python3 -m pytest tests/test_route_map.py -q`
- Tests assert the new localized footer labels render and the old `=` metadata
  format no longer appears.

## 2026-06-30 Round 071 - Localize Daily Receipt Version Label

### Learner Friction

The daily receipt showed a metric labeled `Schema`. The value is useful for
tooling, but the visible report is read by the learner at the end of the day,
where `Schema` feels like implementation vocabulary.

### Change

- Kept the JSON `schema_version` field unchanged.
- Changed the HTML metric label from `Schema` to `数据版本`.

### UX Rule Captured

Machine contract names belong in JSON. Report labels should explain the same
fact in learner language.

### Validation

- `python3 -m pytest tests/test_daily_receipt.py -q`
- Tests assert the daily receipt shows `数据版本` and no longer shows `Schema` in
  the HTML report.

## 2026-06-30 Round 072 - Humanize Receipt Practice Metadata

### Learner Friction

The daily receipt's recent-practice entries still displayed practice metadata as
`得分=... | 来源=... | 耗时=... | 日期=...`. That reads like a serialized string,
even though it is one of the most important end-of-day review surfaces.

### Change

- Added a compact `meta-row` chip style to daily receipt HTML.
- Changed recent-practice metadata into separate chips:
  - score
  - source
  - duration
  - date
- Changed the mistake label from `错因=` to `错因：`.

### UX Rule Captured

End-of-day reports should optimize for tired scanning. Practice metadata should
be chunked into visual units, not packed into a pipe-delimited line.

### Validation

- `python3 -m pytest tests/test_daily_receipt.py -q`
- Tests assert the receipt shows `得分：7/10` and no longer renders the old
  `得分=7/10` practice metadata format.
