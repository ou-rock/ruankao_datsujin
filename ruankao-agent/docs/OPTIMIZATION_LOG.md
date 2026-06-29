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
