# Backlog

Issue log for the HA build. Newest at the bottom. Sources: `docs/inventory.md`,
`docs/automation_requirements.md`, family wishes.

## Cleanup (P3) — from inventory

- [X] #001 **Duplicate/ghost TV entries** — **P2b: verified, P3-1 executed.** All TV
      + media removed on owner decision: samsungtv×2, dlna_dmr, spotify, cast
      config entries + legacy `samsungtv_tizen` component. Versioned `257e19c`.
      (p1 · phase P3)
- [X] #002 **UniFi entity bloat** — **removed whole integration (owner decision).**
      Presence migrated to mobile_app companion trackers (GPS/SSID, zero MAC
      config). Live states 433 → 250. Re-addable via UI if network monitoring wanted.
      (p1 · phase P3)
- [X] #003 **535 disabled-but-never-purged entities** — registry + DB bloat.
      **DONE 2026-10-21:** registry audit — 0 orphans (no entity/device points at a
      missing config entry; UniFi removal already dropped its ~484). Remaining 227
      disabled are all legitimate default-disabled diagnostics (zha rssi/lqi,
      addon version/update sensors, phone sensors, tuya power meters, sun angles).
      Added `recorder: exclude_missing_entities: true` (core restart, applied).
      DB 182 MB, 30-day purge already live.
      (p1 · phase P3)
- [X] #004 **Legacy custom components** — **DONE 2026-10-21.** `script_engine`
      archived under `config/deprecated/script_engine_{component,scripts}` +
      `samsungtv_tizen` removed (P3-1); only stray comments reference script_engine
      now. `doorman` **kept** (owner decision, 5-yr stable, `doorman: debug`
      logger intentional). HACS-tracked: `hacs`, `scheduler` (+ scheduler-card).
      (p1 · phase P3/P4)
- [X] #005 **Deprecated `data_template`** in `scripts.yaml` — **DONE 2026-10-20**
      (commit `1a2fd5e`, needlessly unticked): both scripts rewritten to modern
      `data:`. 2026-10-21: removed 2 stale ghost script entities left in the
      registry from the old names
      (`script.light_on_with_transition_force`,
      `script.force_light_on_with_transition`).
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
- [X] #009 **Mobile app device sprawl** — the 4 mobile_app phones ARE the presence
      source now (LON-L29/Prinsen→Erik, iPhone/ApplePie→Sara). Kept as-is;
      presence independent of UniFi.
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
- [x] #013 **Host-name the devices nicely** — many Hue/ZHA entities keep raw
      names (`light.l2`, `light.p6`…). Friendly aliases for dashboards/summary.
      (p3 · phase P4/P5) — DONE 2026-10-21 during the Hue→ZHA migration
      (`light.ute_huvudentre`, `switch.p6`, `switch.laslampa_on_off` "Gästrum
      fönster", `light.isac_tak`, `light.gastrum_tak`, new `styrbar_lekstuga` +
      `hue_dimmer_isacs` remotes). Remaining raw-named entities are ZHA sub-entities
      (identify/on_level etc.), not worth hosting.

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