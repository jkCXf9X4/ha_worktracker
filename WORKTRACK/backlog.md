# Backlog

Issue log for the HA build. Newest at the bottom. Sources: `docs/inventory.md`,
`docs/automation_requirements.md`, family wishes.

## Cleanup (P3) — from inventory

- [ ] #001 **Duplicate/ghost TV entries** — `samsungtv` appears twice
      (`QE65Q8FAM`, `Samsung 8 Series (65)…`) + a `dlna_dmr` entry for the same
      TV. Verify which are live, remove stale config entries/entities.
      (p1 · phase P2b/P3)
- [ ] #002 **UniFi entity bloat** — ~484 unifi entities; old network clients
      (e.g. `pixel_6`, `iphone`, `iphone_hemma` blockers, port/LED switches).
      Prune registry for devices that no longer connect; consider
      `unifi` module settings to limit tracked clients.
      (p1 · phase P3)
- [ ] #003 **535 disabled-but-never-purged entities** — registry + DB bloat.
      Use recorder `exclude_missing_entities` + registry cleanup to drop unseen
      entities (they still exist in history; verify recorder settings first).
      (p1 · phase P3)
- [ ] #004 **Legacy custom components** — `doorman`, `script_engine`,
      `samsungtv_tizen` (hand-installed, no HACS track). After P4 migration is
      verified, uninstall + archive under `config/deprecated/`.
      (p1 · phase P3/P4)
- [ ] #005 **Deprecated `data_template`** in `scripts.yaml`
      (`light_on_with_transition`, `force_light_on_transition`) — rewrite modern
      (`data:`), keep behaviour identical.
      (p2 · phase P4)
- [ ] #006 **Recorder unconfigured** — DB 186 MB and growing with everything
      stored forever. Set `purge_keep_days` (e.g. 30) + `commit_interval`,
      `exclude_missing_entities: [30]`; purge statistics.
      (p1 · phase P3)
- [ ] #007 **Debug logging left on** — `custom_components.script_engine: debug`
      in `configuration.yaml`. Remove/quiet after migration.
      (p2 · phase P4)
- [ ] #008 **Scheduler "Sovrum" schedule** — currently UI-driven in the Scheduler
      custom integration. Migrate to YAML `input_datetime` helpers + automation
      (per automation_requirements.md) so it’s textual/versionable.
      (p1 · phase P4)
- [ ] #009 **Mobile app device sprawl** — 4 registered phones (LON-L29, iPhone,
      Prinsen, ApplePie); confirm which are active family phones, drop ghosts.
      (p2 · phase P3)
- [ ] #010 **Tuya account** — points at the owner’s Gmail; confirm sockets
      (`switch.p1…p11`) are the still-used plugs; consolidate/naming.
      (p2 · phase P3)

## Security / hygiene

- [ ] #011 **Rotate Yale lock password** — was visible in output during P1.
      Update `secret yale_password` after rotating at the Yale account.
      (p1 · ASAP)
- [ ] #012 **Rotate GitHub fine-grained PAT** — new token; replace in the Git
      Exporter add-on (config keeps working across the swap).
      (p1 · ASAP)
- [ ] #013 **Host-name the devices nicely** — many Hue/ZHA entities keep raw
      names (`light.l2`, `light.p6`…). Friendly aliases for dashboards/summary.
      (p3 · phase P4/P5)

## Features / build

- [ ] #014 **Sync `docs/` + tracker into `/config/docs/`** so the Git Exporter
      versions them on GitHub (single source of truth). *(owner decision)*
      (p2 · next)
- [ ] #015 **Family dashboard** (Lovelace) with schedule pickers/dropdowns +
      per-family-member HA accounts.
      (p1 · phase P5)
- [ ] #016 **Family chat agent** — OpenRouter conversation integration, persona,
      exposed-device scoping to schedule helpers; later optional local Ollama.
      (p1 · phase P6)
- [ ] #017 **Plain-text summaries** — `tools/summarize.py` → `SCHEDULES.md` /
      `AUTOMATIONS.md` from the YAML; surfaced to the chat agent.
      (p2 · phase P7)
- [ ] #018 **Proxmox layer** — `proxmox/backups.md`: vzdump retention crib sheet
      (config-only; owner runs on Proxmox).
      (p2 · phase P7)
- [ ] #019 **Morning fade** — restore the unused 30-min fade-in (03:00–09:00
      transition) from the old `script_ceiling_lights_group.py` if wanted.
      (p3 · phase P4)
- [ ] #020 **Seasonal night-lamp grouping** — the `p10/p11/p1` Christmas sockets
      could become a toggleable group so "night lamps" ≠ "Christmas" year-round.
      (p3 · phase P4/P5)