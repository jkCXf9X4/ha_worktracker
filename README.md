# ha_config

Home Assistant configuration for the home HAOS VM on Proxmox.

This folder serves two roles:

- **Work tracker / planner** for this HA instance — see `WORKTRACK/` (board,
  backlog, changelog).
- **Docs & config workspace** — `docs/` hold the plan, inventory and automation
  migration spec.

The live HA `/config` is the source of truth and is mirrored to a private
GitHub repo via the **Git Exporter** add-on (files land under `config/`).

## Pointers

- Plan: `docs/PLAN.md`
- Status board: `WORKTRACK/board.md`
- Backlog / issues: `WORKTRACK/backlog.md`
- Changelog & decisions: `WORKTRACK/changelog.md`
- Inventory snapshot: `docs/inventory.md`
- Automation requirements & migration design: `docs/automation_requirements.md`
- HA operational knowledge (agent skill): `.opencode/skills/home-assistant/SKILL.md`