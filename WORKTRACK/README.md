# Work Tracker — Home Assistant build

The repo's tracker for this **Home Assistant instance** (HAOS VM on Proxmox,
`192.168.1.248`). The build ran phases P0–P10 (all done 2026-10-23) and the
system is in normal operation. Docs about *how/what* live in `docs/`; ops how-to
in the skill (`.opencode/skills/home-assistant`). This tracker answers *where we
are* and *what's next*.

## Files

| Path | Purpose |
|------|---------|
| `WORKTRACK/NEXT.md` | **Living** tracker: open work (#020), improvement candidates (#024–#029), phase state, standing decisions |
| `WORKTRACK/archive/changelog.md` | Chronological log of changes/decisions — **still appended to**; the record of everything delivered |
| `WORKTRACK/archive/board.md` | Historical status board (superseded by NEXT.md + changelog) |
| `WORKTRACK/archive/backlog.md` | Historical issue log (superseded by NEXT.md + changelog) |

## How items flow

1. A new task/issue/idea is logged in `NEXT.md` under "Open work" (highest number = newest).
2. When picked up, promote it to the current focus at the top of NEXT.md.
3. When done, append the result to `archive/changelog.md` and tick it off in NEXT.md (keep the entry, mark ✅).

## Backlog item format

```
- [ ] #N **Title** — description (context: phase / priority)
      - notes: extra detail, options, acceptance criteria
```

Priorities: `p0` urgent, `p1` high, `p2` normal, `p3` later.

## Conventions

- Statuses: `⛔ blocked` · `⬜ open` · `🔨 in progress` · `✅ done` · `🗑 won't-do`
- Never store secrets or tokens here (they'd end up in git history).
- The `/config` config mirror is the *real* system; this tracker only tracks work.