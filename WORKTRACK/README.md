# Work Tracker — Home Assistant build

The repo's root-level tracker for this **Home Assistant instance** (HAOS VM on
Proxmox, `192.168.1.248`). This is the planner/status hub used by the owner and the
build agent between sessions. Docs about *how/what* live in `docs/` (`PLAN.md`,
`inventory.md`, `automation_requirements.md`). This tracker answers *where we
are* and *what's next*.

## Files

| File | Purpose |
|------|---------|
| `WORKTRACK/board.md`   | Status board: phase state, current focus, next actions |
| `WORKTRACK/backlog.md` | Numbered open tasks: bugs/rot found + ideas/wishes |
| `WORKTRACK/changelog.md` | Chronological log of what was done & decisions made |

## How items flow

1. A task/issue/idea gets logged in `backlog.md` (highest number = newest).
2. When picked up, move it to `board.md` under "In progress" with the phase label.
3. When done, record it in `changelog.md` and tick it off in `backlog.md` /
   `board.md` (keep the entry, just mark ✅).

## Backlog item format

```
- [ ] #N **Title** — one-line description (context: phase / priority)
      - notes: extra detail, options, acceptance criteria
```

Priorities: `p0` urgent, `p1` high, `p2` normal, `p3` later.

## Conventions

- Statuses: `⛔ blocked` · `⬜ open` · `🔨 in progress` · `✅ done` · `🗑 won't-do`
- Never store secrets or tokens here (they'd end up in git history).
- The `/config` config mirror is the *real* system; this tracker only tracks work.