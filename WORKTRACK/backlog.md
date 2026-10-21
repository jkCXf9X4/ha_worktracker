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
- [X] #008 **Scheduler "Sovrum" schedule** — **DONE 2026-10-21.** The Scheduler
      add-on entry `fbfb04` (=`switch.schedule_sovrum`) was fully replaced by the
      YAML automation (`automations/sovrum.yaml`: `p4_sovrum_morning_fade_in` +
      `p4_sovrum_off`, workdays 06:22 fade-in brightness 200 / 1200 s, 09:36 off,
      helpers `input_datetime.sovrum_{on,off}_time` + `input_number.sovrum_brightness`).
      Entry removed via `scheduler.remove` (`storage/scheduler.storage` now 0
      schedules; live entity gone). Retry note: editing `scheduler.storage` by hand
      is reverted by the running integration on exit — always use the service.
      (p1 · phase P4)
- [X] #009 **Mobile app device sprawl** — the 4 mobile_app phones ARE the presence
      source now (LON-L29/Prinsen→Erik, iPhone/ApplePie→Sara). Kept as-is;
      presence independent of UniFi.
      (p2 · phase P3)
- [ ] #010 **Tuya account** — points at the owner’s Gmail; confirm sockets
      (`switch.p1…p11`) are the still-used plugs; consolidate/naming.
      (p2 · phase P3)

## Security / hygiene

- [X] **Tibber removed** (2026-10-21, owner decision): integration was dead
      (`setup_error`, on Layout OK no re-auth planned). Config entry
      `098aef23…` deleted via REST, 27 entities purged from registry
      (`notify.tibber`, `sensor.electricity_price_reparatorsgatan_9`,
      `sensor.monthly_*_reparatorsgatan_9`, `sensor.tibber_pulse_lilla_huset_*`).
      Dashboard **Energi** view cleared of the 5 electricity sensors (kept the
      Tuya `sensor.p4_power` effekt graph). No YAML references existed. Core
      check passes. Tracked as part of #010's "what drives this house" sweep.

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

## Dashboard / UI (2026-10-21 cleanup)

- [X] **Lovelace stale-ref purge** — storage-mode dashboard cleaned via
      `lovelace/config/save`: fixed renames (`light.laslampa_on_off`→`switch.`,
      `light.p6`→`switch.p6`), `script_engine.*`→`sensor.home_status` /
      `input_boolean.light_outside`, dropped 18+ refs to removed integrations
      (TV `media_player.samsung_tv_remote`, UniFi `device_tracker.unifi_*`,
      purged `sensor.lumi_lumi_weather_*`, purged lights `light.l2/l3/steamlink/
      hunden_on_off/…`). All remaining card refs verified against live states.
- [X] **Dashboard rebuilt 2026-10-21** (single storage dash "Hem", 6 views):
      **Översikt** (default — weather/doors/family/home-status), **Belysning**
      (indoor lights by room), **Utomhus** (path fixed from copy-pasta
      `lights-indoor` → `utomhus`), **Energi** (Reparatörsgatan 9 + effekt
      graph), **Historik** (status history graphs), **Schema** (scheduler-card).
      **Debug view deleted** (was raw entity-dump leftover). 38 card refs, all
      verified live.
- [X] **Orphaned Lovelace resources** — removed `/hacsfiles/ha-floorplan/floorplan.js`
      (no plugin installed, no card uses it). Only `scheduler-card.js` remains.
- [X] **HACS state audit** — installed: `hacs`, `scheduler` integrations +
      `scheduler-card` frontend (v1 = HACS-tracked). No pending updates
      (`update.scheduler_*`/`update.hacs_update` = off). `doorman` is
      hand-installed, not HACS.
- [ ] #015 **Family dashboard** (Lovelace) with schedule pickers/dropdowns +
      per-family-member HA accounts — still open (P5).

## Features / build

- [ ] #014 **Sync `docs/` + tracker into `/config/docs/`** so the Git Exporter
      versions them on GitHub (single source of truth). *(owner decision)*
      (p2 · next)
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