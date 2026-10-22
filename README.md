# ha_config

Home Assistant configuration for the home HAOS VM on Proxmox.

This folder serves two roles:

- **Work tracker / planner** for this HA instance — see `WORKTRACK/` (NEXT.md =
  live tracker; `archive/` = history).
- **Docs & config workspace** — `docs/` hold the plan; `docs/archive/` holds the
  completed baseline/spec/history docs.

The live HA `/config` is the source of truth and is mirrored to a private
GitHub repo via the **Git Exporter** add-on (files land under `config/`).

## Pointers

- Plan: `docs/PLAN.md`
- Live tracker / next work: `WORKTRACK/NEXT.md`
- Historical logs (frozen): `WORKTRACK/archive/` (board, backlog, changelog)
- Completed/archived docs: `docs/archive/` (inventory snapshot, automation spec, cleanup report)
- ZHA device map (canonical IDs ↔ IEEE) + pairing recipes: `.opencode/skills/home-assistant/SKILL.md`; full migration workbook: `docs/archive/hue_zha_migration.md`
- Floor plan / room map: `docs/house_map.png`
- HA operational knowledge (agent skill): `.opencode/skills/home-assistant/SKILL.md`