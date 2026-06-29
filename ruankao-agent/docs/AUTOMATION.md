# Automation

This project keeps scheduled work explicit. The repository provides a launchd
template, but does not install it automatically.

## Daily Cycle

Manual run:

```sh
cd /Users/pedan/Documents/ruankao
./run-daily-cycle.command 2026-06-29
```

Default run uses today's date:

```sh
cd /Users/pedan/Documents/ruankao
./run-daily-cycle.command
```

The cycle runs:

- Cheko weak-area seeding.
- Daily receipt generation.
- Three-front route map generation.
- Stage-only night evolution plan generation.

## launchd Template

Template:

```text
automation/launchd/com.pedan.ruankao.daily-cycle.plist
```

Install manually:

```sh
mkdir -p /Users/pedan/Documents/ruankao/ruankao-agent/logs
cp /Users/pedan/Documents/ruankao/automation/launchd/com.pedan.ruankao.daily-cycle.plist \
  ~/Library/LaunchAgents/com.pedan.ruankao.daily-cycle.plist
launchctl load -w ~/Library/LaunchAgents/com.pedan.ruankao.daily-cycle.plist
```

Stop it:

```sh
launchctl unload -w ~/Library/LaunchAgents/com.pedan.ruankao.daily-cycle.plist
```

The template runs at 23:30 local time and writes logs under
`ruankao-agent/logs/`, which is ignored by git.
