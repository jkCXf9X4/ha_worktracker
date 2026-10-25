# Changelog

Chronological log of changes and decisions. Newest at the bottom.

## 2026-10-20 — P4 decision: stick with YAML (Pyscript shelved)

- **Owner decision after prototyping**: go with **YAML** for the automation
  migration. Evaluated Pyscript as an alternative hidden-logic layer:
  - Pyscript 2.1.0 installed, config entry loaded (`allow_all_imports: false`),
    but scripts in `/config/pyscript/` never evaluated (silent watchdog; no
    `sensor.pyscript_probe` / `sensor.home_status_ps` even with
    `custom_components.pyscript: debug` logging). Debugging hit diminishing
    returns.
  - Shelved the direction. **Removed** `/config/pyscript`,
    `custom_components/pyscript`, and the `pyscript:` config. System back to the
    verified YAML state: `ha core check` passes, all P4 automations + helpers +
    `sensor.home_status` (sleep at night) intact.
- Takeaway: **YAML is the path.** Simple automations follow `input_*` helpers —
  helpers are the family/chat surface (app toggles ↔ dashboard ↔ LLM). Complex
  state logic stays in centralized template/automation files.

## 2026-10-20 — P3-2: UniFi removed, presence on companion trackers

- **Owner decisions**: `doorman` **kept** (custom-made for the doors, 5 yr, no
  errors — no replacement sought); `script_engine` **confirmed as the main build
  driver** → migrate to native YAML in P4; UniFi not required for presence.
- **UniFi integration removed** (config entry delete). Presence now runs purely
  on **mobile_app companion** trackers (GPS/SSID, self-registering, zero MAC/IP/
  SSID config):
  - enabled `device_tracker.huawii` (Erik's LON-L29, was user-disabled)
  - `person.erik` → `huawii` + `prinsen`; `person.sara` → `iphone_3` + `applepie`
    (websocket `person/update`; enabled via `config/entity_registry/update`)
  - `ha core check` passes.
- **Impact**: live states **433 → 250** (−183 UniFi entities: trackers, port/LED
  switches, sensors). Verified no YAML/automation referenced UniFi entities.
- Tracker + `docs/cleanup_report.md` updated (#002/#009 → done).

## 2026-10-20 — P3-3 done: recorder live + first purge

- `ha core restart` — recorder config now live (`purge_keep_days: 30`,
  `purge_interval: 1`, `commit_interval: 5`).
- First purge verified: `events` table down to **4302 rows**, `states` capped at
  30 days. Historical long-term `statistics` (5 yr, 1.24 M rows, 58 MB) kept by
  design (energy/history charts) — bounded growth; on-disk 186 MB dominated by
  statistics + indexes now that states/events are capped.
- Tracker updated. Next: sign-offs (UniFi clients, mobile app) + HACS audit.

## 2026-10-20 — P3-3: recorder retention + **push-only exporter discovery**

- **P3-3 recorder configured** — `configuration.yaml` now has
  `recorder: purge_keep_days: 30, purge_interval: 1, commit_interval: 5`
  (was unbounded 186 MB, storing everything forever). Exported as `47e11f5`.
  **Needs `ha core restart`** to take effect + first purge. DB was 186 MB with
  leftover history from removed devices (incl. old media entities).
- **CRITICAL discovery — Git Exporter is push-only.** Tried shipping the recorder
  config by committing to the GitHub repo directly; the next export *reverted* it
  (`8478370` → exporter `19d93bc`), because `pull_before_push` only fetches to
  avoid conflicts, it never applies remote commits to `/config`. Re-applied the
  change on the VM directly (correct channel). Corrected `SKILL.md`,
  `docs/PLAN.md` (§11), and this tracker. **All config edits must go on the VM.**
- Tracker: P3-3 in progress (recorder written, restart pending).

## 2026-10-20 — P3-1: TV/media removed (clean slate)

- **Owner decision**: remove all TV + media for a clean slate.
- Deleted config entries: 2× `samsungtv`, `dlna_dmr`, `spotify`, `cast` (REST API).
- Removed entities (websocket registry): `media_player.tv_samsung_8_series_65`,
  `update.samsungtv_tizen_update`, `switch.samsungtv_tizen_pre_release`,
  `switch.wake_up_tv`, `device_tracker.tv_samsung`.
- Removed device `Samsung QE65Q8FAM`; deleted `custom_components/samsungtv_tizen/`
  (legacy, 1600+ lines); stripped `media_player: samsungtv_tizen` block from
  `configuration.yaml`; removed orphaned `samsungtv_tizen_host/mac` secrets.
- `ha core check` passes; exporter pushed `65acd1f..257e19c main`.
- Remaining: HACS device `SamsungTV Tizen` + repo id `223541049` flagged for later
  HACS cleanup (device API can't remove it).
- Tool lesson: HA websocket commands need **incrementing message `id`** per call
  (`id_reuse` error otherwise); used `uv` + `websockets` for registry removal.

## 2026-10-20 — P2b live discovery + cleanup report

- **SSH key auth** — added this machine's `id_ed25519` pubkey to the SSH & Web
  Terminal add-on `authorized_keys`; root SSH now works without a password
  (verified 192.168.1.248:2222). Multiple keys on the add-on; machine key now one.
- **P2b — long-lived token provisioned** (read-only discovery). Live API
  snapshot: **436 states**, 148 of them `device_tracker` (UniFi bloat).
- **TV duplication VERIFIED (P3-1)** — 2 `samsungtv` config entries
  (`QE65Q8FAM` `5d639020…`, `Samsung 8 Series…` `899d236f…`) are `not_loaded`
  orphans (no devices, no entities). `dlna_dmr`
  (`media_player.tv_samsung_8_series_65`) is the one live player.
  `device_tracker.tv_samsung` (UniFi, MAC `64:1c:b0:8f:59:1f`) = same TV, keep.
- **P2b — registry refresh** — 965 entities (424 enabled / 541 disabled), 212
  devices; `disabled_by`: integration 518 / user 16 / device 7.
- **UniFi bloat quantified (P3-2)** — integration options empty (defaults track
  everything); many raw-MAC `unifi_default_*` trackers.
- **`docs/cleanup_report.md` drafted** — TV plan + UniFi + recorder + open
  sign-off items. Tracker updated (P2b done, P3 in progress).

## 2026-10-20 — Bootstrap session

- **P0 access** — Installed/configured Advanced SSH & Web Terminal add-on.
  Switched add-on shell user to `root` (intended root shell) for full write
  access to `/config` and working `ha` CLI. Discovered: `ha` only works inside
  a login shell (`bash -lc`); SFTP/scp disabled (use tar-over-SSH); never pipe
  scripts via a `-t` SSH session.
- **Inventory (P2a)** — Dumped `.storage` + config over SSH; wrote
  `docs/inventory.md`. Key facts: 958 entities / 211 devices / 535 disabled;
  UniFi dominates; TV likely duplicated; Scheduler holds the "Sovrum" schedule.
- **Automation discovery** — Read the full custom `script_engine` framework +
  scripts; extracted requirements + YAML migration design in
  `docs/automation_requirements.md`.
- **P1 versioning — live** — Git Exporter add-on installed; repo
  `ha_config` on GitHub (private, branch `main`). Excludes configured
  (`.storage/`, `secrets.yaml`, `.ssh/`, DBs, logs). First push blocked by the
  exporter’s secrets check on the legacy Samsung TV IP/MAC → moved values to
  `secrets.yaml` (`!secret`). `ha core check` passes. Push confirmed
  (`f56af23..65acd1f main`).
- **secrets.yaml incident** — file had no trailing newline; an `echo >>` append
  glued lines into invalid YAML and corrupted the Yale password; an earlier
  `sed` patch inserted stray `x27` text. Repaired by atomic rewrite; validated
  with `python3 + yaml`.
- **Security flags (open #011/#012)** — the Yale password and the GitHub PAT
  were visible in tool output; both flagged for rotation.
- **Meta** — `.opencode/skills/home-assistant` knowledge base created;
  `WORKTRACK/` tracker created to carry planning across sessions.

## Decisions

- Versioning model: single GitHub repo; `/config` is the source of truth,
  mirrored by Git Exporter (`config/` subtree in repo). Build agent edits
  `/config` over SSH.
- Cleanup policy: **balanced** — report, stage, disable-not-delete, sign-off on
  ambiguous items, every step a separate commit once versioned.
- Automation target: native HA YAML + `input_*` schedule helpers (1:1 port of
  `script_engine` behaviour), replacing custom Python. Verify over a full
  day/night cycle before retiring legacy components.
- Chat agent: OpenRouter-backed Assist first (privacy-aware via exposed-entity
  scoping); local Ollama as later option.
- Family editing: HA app/dashboard over raw git; the git history + summaries
  provide the "textual definition".
- Tracker/docs: kept locally; **not** mirrored into `/config/docs/` — owner
  declined docs-sync "no for now" (2026-10-22, backlog #014). Docs/tracker live
  in this repo (`ha_worktracker`); `hue_zha_migration.md` stays the sole doc on
  the VM.

## 2026-10-21 — P4 live + Hue→ZHA migration (bulk)

- **P4 YAML go-live; script_engine retired.** 14 YAML automations +
  `input_*` schedule helpers replaced script_engine fully. The retired component
  was already dead (`ModuleNotFoundError: No module named 'script_engine'`).
  Archived → `/config/deprecated/{script_engine_component,script_engine_scripts}`,
  removed `script_engine:` block + debug logger (that edit briefly introduced
  `logger: logs: None` — fixed, `doorman: debug` kept). Restart clean, 22
  automations active.
- **HA Core upgraded 2026.9.2 → 2026.10.2.** ZHA `assert ieee in
  device_proxies` startup race is benign/upstream; dimmers poll fine.
- **ZHA patched:** 5 stale devices purged (4× `lumi.weather` 994d offline +
  `bokhylla_v` 541d offline) via `zha.remove`.
- **Hue bridge dead at 192.168.1.128 → migration.** Workbook
  `docs/hue_zha_migration.md`; logic: re-pair each device to ZHA, rename ZHA
  entity to its canonical entity_id so `groups.yaml`/automations keep working.
- **Re-paired on ZHA (renamed to canonical IDs):**
  `light.entre_hall_tak` (Signify LTW001), `light.korridor_tak` (IKEA,
  verified by flashing), `light.color_temperature_light_1` (Korridor 2, E14
  opal), `switch.p6` (innr, Isacs sänglampa), `light.l3_1` (Groventre),
  `light.l3_2` (Carport ingång), `switch.laslampa_on_off` (P7, now friendly
  "Gästrum fönster"). Hue dimmer RWL021 on ZHA (`zha_event`).
- **Outdoor main entrance was already on ZHA** as an unnamed baseline bulb —
  identified by flash-to-identify, renamed `light.ute_huvudentre` (resolves the
  long-stale `night_lamps` ref).
- **New additions** (owner): `switch.isac_lekstuga` (TRETAKT), STYRBAR dimmer
  (Isacs lekstuga), `light.gastrum_tak` + `light.isac_tak` (IKEA globes, mesh
  routers), `switch.hobby_rum_fonster` (innr). **STYRBAR + Hue dimmer bound to
  Isacs room lights** via `platform: device` automations
  (`automations/{styrbar_lekstuga,hue_dimmer_isacs}.yaml`), working off real
  `device_automation/trigger/list` subtypes.
- **Purged** (owner: physically disconnected): P8, P9, P5, L2, L5, Dimmable
  light 1, + never-existing `kontor_on_off`/`koket_on_off` + dead `bokhylla_v`
  → cleaned `groups.yaml` (domain fixes `light.p6`→`switch.p6`,
  `light.laslampa_on_off`→`switch.laslampa_on_off`). Core restarted, groups now
  resolve to live entities only.
- **Meta:** ZHA ops knowhow → skill (permit-join window gotcha, reset recipes,
  routers-first, remote trigger discovery, entity rename recipe). `#013`
  host-naming backlog item closed.
- **Isacs room morning fade** (`automations/isac_room.yaml`): daily 06:30
  slow fade-in (20 min) of `light.isac_tak` — every day incl. weekends (no
  weekday condition), brightness/time editable via
  `input_datetime.isac_on_time` + `input_number.isac_brightness`.
- **Tuya re-authed** — entry `916b4f19…` recovered from `setup_error` to
  `loaded`, 5 devices / 16 entities online. Resolves the open "outside lights
  unknown" question: the gazebo/uterum + launcher lights are **Tuya**:
  `switch.p10_socket` = "Slinga uterum" (available), `switch.p11_socket` =
  "Julslinga", `switch.p1_socket` (Hörnlampa_vardagsrum), `switch.p2_socket`,
  `switch.p4_socket` (Bilvärmare) + power sensors; `light.outroom_ballsling`/
  `light.laundry_nursingtable` are real Tuya sub-entities (unavailable while the
  plug is offline), NOT stale refs. Skill + workbook updated.
- **Backlog #003/#004/#005 closed (P3 fully done).**
  - **#003** registry audit → **0 orphan entries** (no entity/device references a
    missing config entry; UniFi removal had already shed its ~484). Remaining 227
    disabled are all legit default-disabled diagnostics. Added
    `recorder.exclude_missing_entities: true` (applies on purge) —
    `ha_config` `de00c06`, core restarted, 23 automations on.
  - **#004** verified: `script_engine` archived + `samsungtv_tizen` gone; only
    doorman kept (owner decision). HACS-tracked: `hacs`, `scheduler`.
  - **#005** was already done (commit `1a2fd5e`, never ticked); removed the 2
    ghost script entities the old names left behind in the entity registry
    (`script.light_on_with_transition_force`,
    `script.force_light_on_with_transition`).
- **Dashboard / HACS / Scheduler cleanups.**
  - **Lovelace stale-ref purge** (storage dash, via `lovelace/config/save`):
    renames `light.laslampa_on_off`→`switch.laslampa_on_off`, `light.p6`→
    `switch.p6`; `script_engine.*`→`sensor.home_status` /
    `input_boolean.light_outside`; dropped 18+ refs to removed integrations
    (samsung TV media card, UniFi device trackers, purged `lumi_weather` temps,
    purged lights `l2/l3/steamlink/hunden_on_off/other/…`). Every remaining card
    ref verified against live states (incl. string-form refs in the Debug view).
  - **Orphaned resource** `/hacsfiles/ha-floorplan/floorplan.js` removed via
    `lovelace/resources/delete` (plugin not installed, no card uses it) → 1
    resource left (`scheduler-card.js`).
  - **Scheduler #008**: add-on entry `switch.schedule_sovrum` (fbfb04) fully
    replaced by `automations/sovrum.yaml` (already existed since P4) →
    `scheduler.remove` service call removed it cleanly
    (`scheduler.storage` 0 schedules, live entity gone). Learning: hand-editing
    `scheduler.storage` gets reverted on integration exit — use the service.
  - **HACS audit**: installed = `hacs` + `scheduler` integrations + `scheduler-card`;
    `doorman` is hand-installed (not HACS). No pending updates.
- **Dashboard rebuilt** (Lovelace "Hem", storage-mode): 6 clean views in place of
  the ragged Home/Inomhus/Utomhus/Annat/Scheduler/Debug layout. **Översikt** is
  now the default view (weather, doors, family, home-status); **Belysning**
  groups indoor lights per room; **Utomhus** path fixed (`lights-indoor` →
  `utomhus`); **Energi** holds Reparatörsgatan 9 + effekt; **Historik** collects
  the status/family history graphs + lux line; **Schema** keeps the
  scheduler-card (retitled). **Debug view deleted** — it was a leftover raw
  entity dump. All 38 referenced entities verified live (0 broken).
- **Tibber integration removed** (owner decision): entry had been `setup_error`
  (unavailable) — all 27 entities (pulse + Reparatörsgatan 9 electricity) were
  `unavailable`. Deleted config entry `098aef23…` via REST; entities purged from
  registry; dashboard Energi view cleared of the 5 electricity sensors (kept
  `sensor.p4_power` effekt graph). No YAML refs. Core check clean.
- **Naming cleanup (full pass)** — all UI-facing names turned into clear Swedish:
  - **Entities**: `bokhylla_h_light`→"Bokhylla höger", dimmers→"Sovrum/Vardagsrum
    väggdimmer", `p1_socket`→"Hörnlampa vardagsrum", `p2_socket`→"Uttag p2",
    `p4_socket`→"Bilvärmaruttag", TRETAKT subs→"Lekstuga barnlås"/"Lekstuga
    LED-lampa av", `light.laundry_nursingtable`→"Tvättstuga skötbord",
    `light.outroom_ballsling`→"Uterum bollslings".
  - **Groups** (YAML): ceiling_lamps→"Taklampor", night_lamps→"Nattlampor".
  - **Devices**: 5 Tuya (P1/P2/P4/P10/P11) + 17 ZHA devices given meaningful
    room names (`name_by_user`).
  - **Automation aliases**: 10 "P4:"-prefixed english aliases → Swedish
    (e.g. "Nattlampor på när mörkt", "Lås dörrar vid sömn").
  - **Helpers**: all `input_*` friendly names Swedish (wake/bedtime, Sovrum,
    Isacs, outside-lux). Scripts → "Ljus på med mjukstart".
  - `input_boolean.vacation` → "Semester".
  Exported `0d8ced8`.
- **Carport corridor night dim**: `light.korridor_tak` now stays on at a very low
  level (default 8, `input_number.night_corridor_brightness`) when
  `sensor.home_status` → `sleep`, instead of being turned fully off with
  `group.ceiling_lamps`. Added to the existing `p4_ceiling_off_sleep`
  automation (`automations/ceiling_lights.yaml`). Exported `d8bad42`.

## 2026-10-22 — Tracker cleanup: stale items closed + recorder fact-check

- **Backlog items #006 / #007 / #010 closed** — already executed 2026-10-20/21,
  never ticked:
  - **#006 recorder**: live (`purge_keep_days: 30`, `commit_interval: 5`).
    Fact-check vs versioned config (`0d8ced8`) + HA docs: `exclude_missing_entities`
    is **not** a recorder option (the `de00c06` add is gone from current config —
    `docs/cleanup_report.md` note was right) and `purge_interval: 1` no longer in
    config either; default `auto_purge` covers the nightly purge. No action.
  - **#007 debug logger**: `script_engine: debug` removed with the P4 go-live;
    only `doorman: debug` remains (intentional).
  - **#010 Tuya**: re-auth done, used plugs confirmed + named, dead plugs purged.
- **Board phase table**: P4 marked ✅ (YAML go-live 2026-10-21); current focus =
  P5 family dashboard (#015). `docs/PLAN.md` status/progress and
  `docs/cleanup_report.md` status updated to "executed".
- **#014 docs sync**: partial — only `config/docs/hue_zha_migration.md` mirrored
  so far. Still open (owner decision).

## 2026-10-22 — #014 docs-sync declined (won't-do)

- Owner decided **"no for now"**: `docs/` + `WORKTRACK/` stay versioned in this
  repo (`ha_worktracker`) and are **not** mirrored into `/config/docs/`. No
  duplication in the config repo. `hue_zha_migration.md` remains the only doc on
  the VM under `/config/docs/`.
- Tracker updated: backlog #014 marked 🗑 won't-do; board blocked-section +
  current-focus cleaned; Decisions section corrected. No open items other than
  feature phases P5–P7 (#015–#020).

## 2026-10-22 — Exposed secrets rotated (#011/#012 closed)

- Owner rotated both secrets that leaked in tool output during P1:
  - **#011 Yale lock password** — rotated at the Yale account; `secret
    yale_password` updated on the VM (`secrets.yaml`, excluded from git).
  - **#012 GitHub fine-grained PAT** — new token generated; swapped into the Git
    Exporter add-on (config keeps working across the swap).
- Tracker updated: board blocked-section secrets bullet removed, done-highlights
  + backlog ticked. Security hygiene items now fully closed.
## 2026-10-22 — P5 (#015): Schema view rebuilt as family schedule pickers

- Rebuilt the dashboard **Schema** view (storage-mode dash "Hem", via websocket
  `lovelace/config/save`) into 4 grouped entity cards backed by the existing
  `input_*` helpers (no new helpers, no automation changes):
  - **Familj — väckning & läggdags**: wake_time_weekday/weekend,
    bedtime_weekday/weekend (drives `sensor.home_status` machine).
  - **Sovrum**: sovrum_on_time, sovrum_off_time, sovrum_brightness.
  - **Isacs rum**: isac_on_time, isac_brightness.
  - **Utomhusljus & natt**: outside_light_on/off lux-thresholds,
    night_corner_brightness.
- Removed the now-empty `custom:scheduler-card` from the view (Scheduler add-on
  has 0 schedules since #008) and dropped the orphaned `scheduler-card.js`
  Lovelace resource (`lovelace/resources/delete`; no card references it anymore).
- Exporter pushed as `ccb0e3e`; `ha core check` untouched (no config
  change). All referenced entities verified live. Users Erik+Sara already have
  accounts + apps; per-user roles deliberately left as-is pending owner input.
  Tracker updated.

## 2026-10-22 — P6 (#016): family chat agent live (OpenRouter, all-in)

- Owner chose **all-in scope**: expose everything, no carve-outs (no cameras;
  Yale locks can only be locked via HA, not opened). Privacy cost accepted.
- Added native **`open_router`** integration via config-flow (key in `.storage`,
  never versioned). Created the **conversation subentry**:
  `conversation.deepseek_deepseek_v4_flash_0731` — deepseek-v4-flash-0731,
  Swedish persona (family scheduling + light control), `llm_hass_api: [assist]`,
  web_search off.
- **KEY DISCOVERY**: the `assist` LLM API only surfaces entity-control intents
  (lights/plugs/locks) + a live-context tool — **not arbitrary services**.
  Assistant calls to `input_datetime`/`input_number` silently fail (model
  fabricates success). Fixed by adding **5 schedule-writer scripts** in
  `scripts.yaml` (`set_family_schedule`, `set_sovrum_schedule`,
  `set_isac_schedule`, `set_outside_lux`, `set_night_dim`), each with
  description + field descriptions + `stop`/`response_variable`; exposed as
  LLM tools. Scripts reloaded via `script.reload`.
- Exposed all ~275 live entities to `conversation` (incl. groups + locks);
  kept `sensor.time/date/date_time_iso`, `sun.sun`, `zone.home` hidden.
- **Verified live**: reads presence (Erik hemma, Sara unknown), toggles
  `light.ute_huvudentre` on, and actually persists `wake_time_weekday` (agent
  set 07:15 correctly). Switched default Assist pipeline to the DeepSeek agent
  (lang sv). Test values reset to defaults afterwards.
- Exporter pushed `a57db80` (scripts.yaml + lovelace_resources + transient
  `.cache/brands` icon churn from integration load). Tracker + skill updated.

## 2026-10-22 — P7 (#017/#018): summaries, ops docs, final verification

- **`tools/summarize.py`** (new): parses the `ha_config/config` mirror — all
  `input_*` helpers + `automations/` YAML → generates
  `docs/SCHEDULES.md` (helper table + time-triggered automations) and
  `docs/AUTOMATIONS.md` (full automation reference, Swedish tables). Warns on
  time triggers referencing unknown helpers. Verified: 15 helpers / 23
  automations, output matches live config.
- **`docs/ADMIN.md`** (new): operator how-to — 3 backup layers and how to
  restore from each, common ops (restart, check, presence, remotes, sensor
  battery), secrets hygiene, ongoing maintenance.
- **`proxmox/backups.md`** (new): vzdump retention crib sheet (daily×14 /
  weekly×4 / monthly×2, snapshot mode, pre-upgrade manual snapshot, restore
  steps, verify-always). Config-only, owner executes on Proxmox.
- **Final verification**: `ha core check` green; sha256 of
  scripts/configuration/groups.yaml identical between `/config` and the mirror
  submodule. PLAN.md + NEXT.md marked P0–P7 complete; build milestones done
  (remaining #019/#020 are optional enhancements).

## 2026-10-22 — P8 (#021): config_tools agent tools — built, deployed, verified

- **Custom component `config_tools`** (`/config/custom_components/config_tools/`):
  an **`llm` platform** (verified mechanism in HA 2026.10: `async_get_tools`
  hook merged into the `assist` API; open_router agent auto-forwards
  `llm_api.tools` and executes tool calls itself). 5 tools, names prefixed
  `config_tools__`: `read_file`, `glob_files` (everyone) + `write_file`,
  `check_config`, `reload` (admin-gated). **No bash** — pure pathlib, write
  allowlist = `automations/*.yaml`/`scripts.yaml`/`groups.yaml`/`template/*.yaml`,
  never `configuration.yaml`/`secrets.yaml`/`.storage`/DBs/logs.
- **write→check→reload with in-memory revert**: writes the file, runs full
  config check (`async_check_ha_config_file`), reverts on failure, then
  `automation/script/group/template.reload` on success.
- **Rollout:** copied component to VM; added `config_tools:` (empty) to
  `configuration.yaml`; `ha core check` green; **core restart** (required — llm
  platform lazy-scan only sees top-level components, i.e. at boot).
- **Verified live through the chat agent** (`conversation/process`): `glob_files`
  listed the 9 real automation files; `read_file` read scripts.yaml (2 scripts —
  post-removal state); `write_file` wrote a test automation, entity registered,
  file then removed. `bind_remote` dropped (owner: "way too specific").
- **GOTCHA:** `automation: !include_dir_merge_list automations/` **silently
  drops** single-mapping YAML files — each automations file must be a YAML
  **list** (`- id:`). `ha core check` passes on a mapping; no error anywhere;
  the automation just never registers. `write_file` cannot detect this.
  Documented in skill + AGENT_TOOLS.md; the agent persona must write automations
  as lists.
- **Removed 5 schedule-writer scripts** from `scripts.yaml` (`set_family_schedule`,
  `set_sovrum_schedule`, `set_isac_schedule`, `set_outside_lux`,
  `set_night_dim`) — owner decision, generic tools replace them. Live `input_*`
  helper values are now out of the agent's reach; family edits schedules via the
  dashboard pickers.
- Exporter pushed `3cd8d6d` then `71e48ed` (backup `*.bak_*` files I created on
  the VM accidentally got pushed, then deleted again). Live == mirror (sha
  verified for configuration.yaml, scripts.yaml, all config_tools files).
  Workspace commits follow. Stale (inert) expose_entity entries for the removed
  script entities left for a maintenance pass.

## 2026-10-22 — P8 follow-up: config_tools v0.2.0 — find_device + device_triggers

- Added 2 read-only tools to `config_tools` (component v0.2.0):
  - **`config_tools__find_device`** — substring lookup over device registry
    (name/name_by_user) → ≤10 matches with `device_id`, manufacturer, model,
    area, registered entity_ids. Everyone.
  - **`config_tools__device_triggers`** — live enum of a device's
    device-automation triggers via
    `device_automation.async_get_device_automations(hass, TRIGGER, [device_id])`
    → real `domain`/`type`/`subtype` pairs. Everyone. Agent rule: never guess
    subtypes, always read them here.
- These close the capability gap left when `bind_remote` was dropped: the chat
  agent can now resolve a friendly device name → device_id and confirm real
  trigger types, then edit/write the YAML automation with `write_file`
  (list-format rule applies), `check_config`, `reload`.
- **Verified live via `conversation/process`:** agent found STYRBAR lekstuga
  (`a9cc237d301514c8ec2f07ea87d9eaf2`), listed 16 real triggers (incl.
  `remote_button_long_press`/`dim_up`) and did a full
  find→triggers→write→check→reload edit of `automations/styrbar_lekstuga.yaml`
  (dim_up retargeted to the bedroom lamp), which was then **reverted** (sha
  re-verified live == mirror).
- Fixed during live test: `entity_registry.get_entries_for_device_id` lives on
  `registry.entities` (not the registry object) — corrected.
- Restarted core to reload the `llm` platform; exporter push to follow.

## 2026-10-22 — P8: agent knowledge layer (offline) + end-to-end self-edit verified

- The OpenRouter agent has **no internet**, so embedded its operational
  knowledge: extended the conversation-subentry system prompt (via the
  subentry reconfigure flow) with a "TEKNISK DEL" block (tool list, hard
  rules: YAML-list format, never guess device_id/type/subtype, check+reload
  after write, denylist, input_* caveat) + pointers to two reference docs.
- New versioned docs in `/config/docs/` (exported, readable by the agent):
  `AGENT_HANDBOOK.md` (rules, conventions, key entities, workflows) and
  `AGENT_EXAMPLES.md` (working YAML examples incl. the WRONG single-mapping
  shape). Prompt updated via `config_entries/subentries/flow` reconfigure
  (flat body, no step_id wrapper) → `reconfigure_successful`.
- **Verified end-to-end:** agent self-served a brand-new device automation
  (Hue dimmer Isacs short-press → ute lamp): read the handbook,
  `find_device` → `device_triggers` → wrote `automations/zz_test.yaml` as a
  proper YAML **list**, `check_config`, `reload` → entity registered
  (`automation.hue_dimmer_isacs_hoger_korttryck_ute_pa`). Test file removed.
  (Earlier same-day run had the agent write a *single mapping* under the old
  prompt — now fixed.)
- Exporter pushed `ca61c3b` (AGENT_HANDBOOK.md + AGENT_EXAMPLES.md).

## 2026-10-23 — P9 (#022): config_tools__call_service — built, deployed, hardened

- **Deployed v0.3.0, then hardened v0.3.1** — whitelisted service-action tool so
  the chat agent can call e.g. `light.turn_on` with `flash: short|long` (blink
  lamps) and real service params entity intents can't carry. Living plan →
  archived: `docs/archive/call_service_tool_P9_PLAN.md`.
- Component: `CallServiceTool` in `config_tools` (allowlist `light|switch`
  turn_on/off/toggle in `const.py`, entity-registry + exposure-only gating in
  `tools.py`, 8th tool in `llm.py`, manifest → 0.3.1 with
  `integration_type: service`). `data` = typed probatio schema (parse-time
  "did you mean" errors); atomic writes; `_LOGGER` every call.
- **v0.3.1 hardening rationale:** admin gate dropped for `call_service`
  (exposure-bound like HA's native assistant model); typed `data`; atomic
  writes; honest manifest.
- Native alternative added: `scripts.yaml::korridor_blink` (`fields:
  flash|transition`) — exposed scripts surface as `script.*` tools
  automatically → "blinka korridorlampan" works with zero component code.
- **Verified live via conversation/process:** forced `light.turn_off`/`turn_on`
  state flips with `response.data.success == []` (empty = tool path, not intent);
  bogus field returned real HA validation error verbatim. Exporter push
  `989e5a0` (v0.3.0) + v0.3.1. Found + fixed the VM's stale `find_device`
  (`registry.entities.get_entries_for_device_id`).
- Docs/skill/tracker/PLAN updated.

## 2026-10-23 — P10 (#023): critical config review patch, deployed + verified

- **Startup grace bug fixed** (`00_startup_grace.yaml`): the
  `input_boolean.ha_started` gate could be skipped by a restored `on` →
  now `initial: false` + explicit turn-off on start.
- **Family schedule edits no longer reset at boot** — removed `initial:` from
  all `input_datetime`/`input_number` schedule helpers.
- **Sleep scene fixed** — YAML scenes don't render Jinja → templated
  `scene.nattmode` replaced by `script.nattmode` (dynamic night-corner
  brightness); two static scenes remain.
- **Restart reconciliation** for outside-light flag + ceiling/night/lock
  automations (full state conditions after `ha_started -> on`).
- **Christmas helper syncs immediately** via new automation; no forced-on boot.
- Simplifications: single `lock.lock` for both doors, script field
  defaults/selectors, `time_date` removed, logger warning, `home_status`
  availability, modern `trigger:`/`action:` + `trigger: device` blueprints.
- **Registry cleanup:** 12 orphaned `unavailable` automation entities purged
  (17 active, 0 unavailable).
- Verified live (17/17 automations on); exporter `c55930a`, mirror == VM.
  Open question recorded: `switch.p4_socket` in `night_lamps` vs `switch.p6`
  in `christmas_sockets` — owner decision pending (#020/#023 follow-up).

## 2026-10-23 — Best-practice review + improvement candidates (#024–#029)

- Collected current HA best practices online (official docs: five tools,
  splitting config, triggers, organizing, securing; community: Taras
  data-driven consolidation) and audited `config/` against them →
  `docs/BEST_PRACTICES.md` (reference + build audit).
- Deep-dived the `home_status` state machine → `docs/deep_dive_home_status.md`.
  **Finding:** native `schedule` helper is the *wrong* tool here (no runtime
  `schedule.set`; blocks can't cross midnight; weekday/weekend axes don't map)
  — the template + `input_datetime` design stands. Proposed simpler equivalent
  (HH:MM:SS lexicographic compare), **not deployed**.
- Logged as improvement candidates #024–#029 in `WORKTRACK/NEXT.md` (all ⬜
  owner-decision before touch): home_status simplification, startup-grace gate
  blueprint, ceiling-lights consolidation, verification pair, seasonal labels,
  scenes/groups duplication. Schedule-helper migration marked **rejected**.

## 2026-10-23 — #019 won't-do finalized + tracker cleanup

- **#019 Ceiling morning fade — confirmed won't-do** (owner decision already
  made 2026-10-22: "remove that one, it will never be relevant"). Kept only in
  `archive/board.md`/`backlog.md` history; not reopened.
- **Tracker cleaned up for further dev** — `WORKTRACK/NEXT.md` slimmed to a
  lean forward-looking file (only #020 + improvement candidates #024–#029 open;
  P0–P10 phase table; standing decisions; ops reminders). All delivered detail
  moved to this changelog (P9/P10 backfilled above). `board.md`/`backlog.md`
  marked **SUPERSEDED** (historical, read-only). Completed plan → archived:
  `docs/archive/call_service_tool_P9_PLAN.md` (live refs updated in PLAN.md /
  AGENT_TOOLS.md). Best-practice docs added: `docs/BEST_PRACTICES.md` +
  `docs/deep_dive_home_status.md`.

## 2026-10-24 — scripts/templates/helpers simplification round + native readiness gate

Follow-up to #028/#031/#032/#034 (organized org round). Implemented, verified
live (Saturday 07:2x, `ha core check` green, exporter `66156a5`):

- **Item 1 — behavior boxes finished:** the last three automations with a
  `choose` were reduced to thin WHEN wrappers; all decision logic now lives in
  scripts. Added `script.ceiling_lights_sync` (sleep/away/awake+dark/awake+bright
  from `home_status`+`light_outside`), `script.uteljus_sync` (absorbs the old
  `sasong_sync`; resolves utelampa + sasong together), `script.outside_light_sync`
  (the lux-hysteresis choose). Automations = trigger → gate conditions → one
  `script.X`. Away branch now targets the new **`slack_borta` label** (all
  interior lamps) instead of just `taklampa`; membership assigned via WS
  (labels taklampa/natthorn preserved, merged).
- **Item 2 — room schedules blueprint:** `blueprints/automation/room_schedule.yaml`
  with inputs area / on+off `input_datetime` / brightness `input_number` /
  weekdays (empty=all) / off_enabled. Replaces `sovrum.yaml`+`isac_room.yaml` →
  two instances in `automations/room_schedules.yaml` (`p4_sovrum_schedule`
  workdays+off, `p4_isac_schedule` every day fade-in only). Fade transition
  shared via new `input_number.fade_transition_seconds` (default 1200).
  Blueprint uses `at: !input off_entity` + weekday template condition; off_branch
  gated on `off_enabled`.
- **Item 3 — derived facts on `home_status`:** attributes `is_workday`,
  `next_wake`, `next_bedtime` added to `template/home_status.yaml`
  (dashboard #033, one source instead of automations re-deriving the math).
- **Item 4+5 — knobs + label targeting:** `light_on_with_transition` gained a
  `label` field (area > label > entity branches) → fades can target labels.
  (Pause-timer feature added & then **REMOVED** — see readiness bullet.)
- **`ha_started` flag retired → native readiness gate:** after moving off
  `script_engine`, the hand-rolled `input_boolean.ha_started` + the
  `00_startup_grace` automation were the last Python-era leftover. Replaced by
  the native **`uptime` config-entry integration** (`sensor.uptime` = boot
  timestamp) + a trigger-based template binary sensor `binary_sensor.ha_ready`
  (on once up ≥2 min, time_pattern /1). All `ha_started` conditions/triggers →
  `binary_sensor.ha_ready`. Derived ⇒ can't desync, no manual toggling, no
  restore-state edge cases. Verified boot-reconcile fires via it (ceiling+lock+
  night at 05:22:48 UTC after restart, trace `p4_ceiling_lights` etc.).
- **Timer-based pause REMOVED (owner decision THIS session):** the
  `timer.automatik_paus` + `script.pausa_automatik` + resume automation I built
  this session was redundant with the family's dashboard `automatik_*` toggles
  and had a boot-ordering bug (a freshly restored timer `unknown→idle` fired the
  `to: idle` resume trigger at boot, forcing `automatik_nattlampor` ON against
  the family's choice). Reverted fully: entities purged via WS, `timer:` include
  dropped, `pausa_automatik` removed. `automatik_*` dashboard toggles are the
  single pause mechanism again.
- Orphans purged via WS entity_registry.remove: `automation.p4_sovrum_*`,
  `automation.p4_isacs_room_morning_fade_in`, `script.sasong_sync`,
  `input_boolean.ha_started`, `script.pausa_automatik`, `timer.automatik_paus`,
  `automation.p4_ha_ready`, `automation.p4_ateruppta_…`.
- Live state after all changes: 9 automation entities + 8 scripts, bedroom
  (`light.dimmer_fixed_bedroom_light_2`) verified OFF throughout (Sara asleep);
  sovrum only ever touched by the workday-gated schedule — Saturday → inert.
  `tools/summarize.py` regenerated `docs/AUTOMATIONS.md`/`SCHEDULES.md`.

## 2026-10-24 — Design-review fixes round

Source: fresh review of the post-simplification config, findings in
`/tmp/opencode/review_findings.md`. Applied on the VM, VERIFIED live, exporter
commit `7d1edf0`.

- **#1 outside_light boot re-sync gap (real bug).** The `homeassistant start`
  trigger fired before the ZHA lux sensor was up; a `numeric_state` on
  `unknown` no-ops, so the restored `light_outside` could stay wrong for hours.
  Replaced with a `binary_sensor.ha_ready -> on` state trigger — the same
  readiness signal the ceiling/night/lock automations already reconcile on.
- **#2 christmas-sockets automation not pause-gated.** `p4_christmas_sockets_sync`
  only checked `ha_ready` while its sibling `p4_night_lights` also gated on
  `automatik_nattlampor` (both call `script.uteljus_sync`). Added the
  `automatik_nattlampor` condition. Verified via WS `test_condition`: False while
  the toggle is off, ha_ready leg still True.
- **#3 isac dummy off_entity removed.** Blueprint `fade_out` trigger now a
  template `at` — `{{ [states(off_entity)] if off_enabled else [] }}` — so a
  disabled off-time renders an empty time list instead of firing a daily no-op
  trigger at 06:30. Instances unchanged (isac still passes its on-time; sovrum
  `off_enabled: true` unaffected).
- **#4 `light_on_with_transition` label foot-gun.** Documented in the field
  description that labels resolve to light-domain members only (natthorn is
  light-only; mixed labels need two calls). Kept `light.turn_on` — safer than
  `homeassistant.turn_on` with brightness/transition data on switch members.
- **#5 blueprint weekday locale-proof.** `now().strftime('%a').lower()` →
  `now().isoweekday() in weekdays` with numeric select values "1".."7" (locale
  independent, matches the numeric axes everywhere else). Instances updated
  (`sovrum` = "1".."5").
- **#6 `ha_ready` `.storage` dependency documented** in `docs/ADMIN.md` — the
  `uptime` config entry is UI/resident in `.storage` (not YAML); a full
  `.storage` rebuild silently stops every automation via `ha_ready` unless the
  integration is re-created.
- **#7 `light_on_with_transition` got `mode: restart`** (was default `single` —
  a second call during the 20-min fade would have queued 20 min).
- Verified live: `ha core check` green; all 7 automations `on`; script mode
  `restart`; isoweekday render = 6/False for saturday; bedroom lamp untouched;
  `automatik_nattlampor` left off. Exporter `7d1edf0` (5 files). Modest default
  `today is Saturday` → sovrum fade correctly inert.

## 2026-10-24 — Scripts/templates/helpers/agent-tools expansion round

Owner request: push further on scripts/templates/helpers simplification + make
it easy for the local agent to change things. Applied on the VM, VERIFIED
live, exporter commits `cd8c26a` (config round) + `f0d9ffe` (backup purge).

- **#1 Gates folded into behavior-box scripts.** The repeated `condition` blocks
  (`ha_ready` + a `automatik_*` pause toggle) were removed from 4 automation
  files — they now live at the *top of the scripts* as an `if:`/`then:` wrapper
  (NOT a script `condition:` — **YAML `script:` objects have NO top-level
  `condition` key**; HA rejected `not a valid option at 'condition'` and
  disabled the scripts; the sequence had to be wrapped in `- if:`/`then:`).
  `ceiling_lights_sync`, `uteljus_sync` (gates: pause + ha_ready) and
  `outside_light_sync` (ha_ready) self-gate; a new `script.lock_by_status`
  peers the status `sleep/away` + `automatik_las` + `ha_ready` gates while
  `script.lock_doors` stays ungated (so `goodnight` always locks). Automations
  are now trigger→script only (ceiling/night/christmas/locks). `ha_ready`
  trigger retained in each file for boot-reconcile.
- **#2 Room-schedule pause toggles.** `input_boolean.automatik_sovrum` /
  `automatik_isac` added (all pause toggles keep `initial: true` — deliberate:
  restart re-enables every behavior; comment updated to say so). `room_schedule`
  blueprint gained a `pause_entity` input (empty = always run); both instances
  wired.
- **#3 `home_status` simplification (#024) + `next_wake`/`next_bedtime` (#033).**
  State now compares zero-padded `HH:MM:SS` strings lexicographically instead
  of `as_timestamp`/date-concat math; attributes `is_workday`, `next_wake`,
  `next_bedtime` render via `as_datetime`+`timestamp_custom`. Equivalence of the
  state logic proven offline (0 mismatches across all 7 weekdays × 1440 min).
- **#4 config_tools widened + new tools (v0.4.0).** Write allowlist extended to
  `input_boolean|input_number|input_datetime/*.yaml` (these have NO reload
  service — `write_file` returns "needs restart_core"); new `set_label` tool
  (admin; entity-registry `labels` replace, label-registry validated, changed
  live via `registry.async_update_entity`); new `restart_core` tool (admin;
  schedules `homeassistant.restart`).
- **FOUND AND FIXED while verifying:** the room_schedule blueprint's `fade_out`
  trigger `at: {{ [states(off_entity)] if off_enabled else [] }}` was BROKEN in
  the current HA (limited templates get no blueprint variables →
  `off_enabled is undefined` → automation failed trigger setup; also the
  `weekdays` flow-style selector `{label,value}` failed blueprint validation
  with `value Got None`). Rewrote both: weekday options are block-form
  `label:`/`value: "1"` and `fade_out` is a plain `at: !input off_entity` (the
  choose branch gates on `off_enabled` + weekdays + pause). This was a latent
  bug from the 07:44 round — the automations were "on" but their triggers failed
  to set up.
- **HA 2026.10 registry API:** entity-registry updates are
  `EntityRegistry.async_update_entity(entity_id, **changes)` (SYNC, returns the
  entry) — `async_update` and `registry.entities.async_update` do not exist.
  `label_registry.async_get(hass)` returns the already-loaded registry;
  `async_load` asserts when it is already present.
- Verified live after 4 restarts: all 9 automations `on`, 12 scripts loaded,
  `automatik_sovrum/isac` on, `home_status` awake with new attributes,
  `light.entre_hall_tak` labels intact; `set_label` exercised end-to-end by the
  chat agent via `conversation/process` (returned `["slack_borta","taklampa"]`).
  `restart_core` deliberately not fired (destructive); the input_* write path
  shares the verified write/reload flow. Pre-change backup:
  `/root/ha_config_backup_20261024.tar` on the VM.
- **GOTCHA:** a backup tar left under `/config/.opencode_backup_20261024/` got
  picked up and committed by the exporter — backups must live OUTSIDE `/config`
  (e.g. `/root`). Purged in `f0d9ffe`.

## 2026-10-24 re: — scripts/templates/helpers simplification round 2 (#036–039, applied)

Owner "patch 1–6": templates absorb the last helper machine, single-source the
seasonal rule, centralize boot reconcile, and refresh the agent docs. Live
changes pushed over SSH → `ha core check` green → core restart → exporter
`d6d7684` (12 files, +306/−292).

- **#036 daylight flag → `binary_sensor.light_outside` template.** New
  `template/daylight.yaml` is a trigger-based template binary sensor with a
  **latched-hysteresis** `state` (`this.state`): on above
  `outside_light_on_threshold`, off below `outside_light_off_threshold` from the
  input_number helpers (dead zone, no flap). Availability mirrors the ZHA lux
  sensor. This **deleted** `automations/outside_light.yaml`,
  `input_boolean.light_outside` and `script.outside_light_sync` — "is it dark"
  is now a derived fact like `home_status`/`ha_ready`; a template self-settles
  at boot, so the `ha_ready`-gated boot re-sync is gone too. Consumers
  (ceiling/night automations + `ceiling_lights_sync`/`uteljus_sync`) retargeted
  to the binary sensor.
  - **GOTCHA (bit us on the first boot check):** a template sensor's entity_id
    comes from its NAME, not the `unique_id`/key — the sensor registered as
    `binary_sensor.light_outside_daylight_flag` from name "…(daylight flag)",
    so every `binary_sensor.light_outside` reference silently no-op'd. Fixed
    with a registry rename (`binary_sensor.light_outside_daylight_flag` →
    `binary_sensor.light_outside`), same as `binary_sensor.ha_ready` was.
  - Lovelace: live dashboard `.storage` updated via `lovelace/config/save`
    (2 cards: Hemstatus + Uteljus history-graph), mirror re-derived by exporter.
- **#037 seasonal rule single-sourced in `script.uteljus_sync`.** The
  `christmas_lights` branch was encoded twice (in `uteljus_pa/av` AND in
  `uteljus_sync`). `uteljus_pa/av` are now pure `label.utelampa` one-taps (do
  NOT touch `sasong`); `uteljus_sync` remains the single home of the seasonal
  rule for automations + voice presets. Behaviour note: "tänd uteljus" no longer
  flips the Christmas string — that's now only the daylight machine's job.
- **#038 boot reconcile centralized.** New `automations/boot_reconcile.yaml`
  (`binary_sensor.ha_ready -> on` → `script.reconcile_all`, which replays
  `uteljus_sync` → `ceiling_lights_sync` → `lock_by_status`) replaces the
  duplicated `ha_ready -> on` trigger that sat in every behavior automation
  (ceiling/night/locks). **Convention: do NOT add `ha_ready -> on` triggers to
  new automation files — extend `script.reconcile_all`.** The daylight template
  needs no boot resync.
- **#039 registry fixes discovered during verification:**
  - `script.lock_by_status` had registered under `script.las_vid_hemmastatus_gate`
    (YAML key vs alias-slug drift) — automations calling `script.lock_by_status`
    would have failed at runtime. Registry-renamed back to `script.lock_by_status`.
  - Purged orphans: `automation.p4_outside_daylight_flag`, `script.outside_light_sync`,
    `input_boolean.light_outside` (WS `config/entity_registry/remove`).
- **Agent docs refreshed (`/config/docs/`):** `AGENT_HANDBOOK.md` + `AGENT_EXAMPLES.md`
  rewritten to live state — 9 automations / 12 scripts / templates incl. the
  daylight template, the 10 config_tools (v0.4.0: write allows `input_*/*.yaml` +
  `set_label` + `restart_core`), behavior-box + blueprint copy-block recipes
  (new room / new remote), and the "scripts surface as `script.*` tools — prefer
  them over raw `call_service`" convention. (System-prompt "TEKNISK DEL" still
  needs a reconfigure-flow refresh to mention the v0.4.0 tools — optional.)
- Verified live after restart + `ha_ready` boot replay: utelampa/p11 on (dark),
  sasong off (christmas off), all 5 taklampa on (awake+dark), locks unchanged;
  `binary_sensor.light_outside` renders from lux (72 → off); no errors in
  `home-assistant.log`. Pre-change backups in `/tmp/opencode/hz_prepatch/`.

## 2026-10-24 — repo cleanup + agent prompt refresh + exposure cleanup + #027 closed

Workspace/repo: documented in the commit message of this same change set.

- **Repo cleanup/refactor** (see the session): archived the completed deep-dive
  docs (`docs/archive/`) with superseded banners; split the dated `BEST_PRACTICES`
  build-audit into `docs/archive/build_audit_2026-10-23.md`; collapsed
  `WORKTRACK/NEXT.md` to genuinely-open items only; refreshed `AGENT_TOOLS.md`
  to v0.4.0; fixed stale facts (ADMIN sensor note, PLAN status + repo handle
  `hkCX…`→`jkCX…`); removed `.ruff_cache/`.
- **#027 RESOLVED (owner 2026-10-24):** Sunday morning = weekend wake,
  Sunday evening = weekday bedtime ("morning after is early"). The deployed
  `home_status` template already matches (wake axis Mon–Fri/Sat–Sun; bed axis
  `wd in [6,0,1,2,3]` = Sun–Thu weekday bed). No config change needed.
- **Chat-agent system prompt REFRESHED to v0.4.0** via the reconfigure flow
  (entry `01M5J96GD…`, subentry `01M5J9HQ…`; the init POST returns `flow_id`,
  the step POST carries the flow_id in the URL — putting it in the body 400s
  with `not a valid option at 'flow_id'`). The "TEKNISK DEL" block now names
  all 10 tools (`set_label`, `restart_core`, `call_service`), the `script.*`-
  tool preference, and the labels/areas architecture. Persona untouched.
  Verified in `.storage` (prompt 3307 → 5323 chars).
- **Stale exposure entries REMOVED (5):** `group.ceiling_lamps`,
  `group.night_lamps`, `scene.taklampor_pa`, `scene.nattlampor_pa`,
  `scene.nattmode` — deleted entities group/scenes from 2026-10-23 left inert
  `expose_entity` entries. Found by cross-referencing
  `homeassistant/expose_entity/list` vs `/api/states`; removed with
  `should_expose: false`. (Skill §Family chat agent updated with the recipe +
  the flow_id-in-URL gotcha.)

## 2026-10-24 — Hue dimmer Isac + bedside lamp (single/double press)

- **Owner request:** also attach `switch.p6` (Isacs sänglampa) to the Hue
  dimmer in Isac's room; single ON press → both on; double ON press → only the
  bedside lamp. Implemented in the existing blueprint
  `zha_remote_lights.yaml` + `hue_dimmer_isacs.yaml` (commit `720ca7d`):
  - Blueprint gained optional `target_switch` input + a
    `remote_button_double_press` trigger. Single ON = light + switch on
    (guarded), double ON = switch on + light off, OFF = both off, dim paddles
    unchanged (light only).
  - **Verified live on-device:** single press → `light.isac_tak` + `switch.p6`
    on; double press → p6 on + ceiling off; OFF → both off. Trigger identity
    confirmed via `trace/get` (single = `remote_button_short_press`, double =
    `remote_button_double_press` — mutually exclusive, no payload matching).
  - **Debug method note:** probed with a throwaway automation (device triggers
    → `persistent_notification`) to confirm which trigger types fire; raw
    `zha_event.R` dumps show `on_press`/`on_press` for single, `on_double_press`
    for double. This is the reusable pattern — never string-match `zha_event`.
- **GOTCHA recorded in the skill:** HA `condition: template` is **falsy for any
  non-boolean render** — `{{ target_switch }}` → `"switch.p6"` evaluated false;
  fixed with `{{ target_switch != '' }}`. Same class as the numeric_state
  `above:`/`below:` gotcha (entity-id-or-float only).
- Config exported on the VM (`ha apps restart 68413af6_git-exporter`,
  "Exporter finished"). Local `ha_config` clone synced to `720ca7d`.

## 2026-10-24 — Family dashboard: dead `area` cards replaced with real room toggles

Owner report: "the dashboards now show all the areas but I can't do anything
with them".

- **Root cause (verified in frontend source + live):** in HA 2026.10 the `area`
  card (`type: area`, `display_type: compact`) no longer renders inline entity
  chips. It is a static tile (icon + room name); the tile is `interactive=false`
  unless the card has `tap_action` or card `features`. So every room "card" on
  Belysning/Utomhus rendered but was a pure dead tile.
- **Fix (owner chose "show real toggles per room"):** storage dash rebuilt via
  WS `lovelace/config` → edit → `lovelace/config/save` (`url_path: "lovelace"`,
  full config payload). All `area` cards replaced with `entities` cards
  (`show_header_toggle: true`) listing each room's live lights/switches:
  - Belysning: Entré hall, Kök korridor (l3_1/l3_2), Badrum korridor, Vardagsrum
    (dimmer livingroom + bokhylla + isac_lekstuga), Sovrum, Isacs rum, Gästrum,
    Hobbyrum, Kök (p2).
  - Utomhus: Utebelysning (ute_huvudentre + p11), Uterum (p10); Säsongsbelysning
    card unchanged.
- Excluded from room cards (kept in the seasonal/utomhus card instead):
  `p1_socket` (seasonal "Hörnlampa vardagsrum", often unavailable via Tuya),
  `p2_socket` is shown (Kök, currently unavailable), TRETAKT child-lock/LED
  toggles not useful to the family.
- Exported (`75db10e`), local `ha_config` clone synced. Skill §Dashboard views
  updated with the area-card gotcha + per-room card layout.

## 2026-10-24 — Room dim build: one dim per room + drill-in pages + plugs-follow-dim

Follow-up to the area-card fix. Owner requirements: (1) overall dashboard shows
ONE dim per room, opening a room gives detailed per-entity control; (2) when a
room is dimmed above ~75% its plugs turn on, below 75% (or room off) they turn
off, and plug presses never influence the lights.

- **Room dims = `light.group` entities** (new `/config/light.yaml`, added
  `light: !include light.yaml` to configuration.yaml; needed `ha core restart`):
  `light.vardagsrum` = dimmer_fixed_livingroom_light + bokhylla_h_light;
  `light.badrum_korridor` = korridor_tak + color_temperature_light_1;
  `light.kok_korridor` = l3_1 + l3_2. Single-light rooms and switch-only rooms
  have no group (their one light / switch is the room control). Verified in core
  source (`group/light.py`): `turn_on(brightness=X)` forwards the same level to
  every member; group reports mean brightness. Friendly names/areas set via
  entity-registry update (Kök korridor got the ö back).
- **Dashboard → overview + subviews** (`lovelace/config/save`): Belysning is now
  Automatik card + a 2-col grid of room `tile` cards — each tile is the room's
  light/group with a `light-brightness` slider (the one dim per room) and
  `tap_action: navigate /lovelace/rum-*`. **11 hidden subviews** (`subview:
  true`, `back_path: /lovelace/belysning`) hold the room's full per-entity
  `entities` card — the actual "open it up → all room functions". Subview is a
  first-class view flag (used by the Areas dashboard strategy), so no tab-bar
  clutter. Utomhus/historik/schema untouched.
- **Plugs follow room dim (75%)** — `automations/plug_dim.yaml`
  (`plug_dim_vardagsrum/isacs_rum/gastrum`, alias-slugged entity ids) →
  `script.plug_follow_room_dim` (fields `room_light` + `plugs`, `if` template
  `states == on AND brightness > 191` → switch.turn_on, else turn_off).
  Plug-ins: Vardagsrum→isac_lekstuga, Isacs→p6, Gästrum→laslampa. One-way only
  (nothing triggers on the plugs). `script.reconcile_all` extended with ×3
  plug_follow calls for boot convergence. p6 note: family had p6 on with the
  room off — the new rule (room off ⇒ plug off) turned it off after restart;
  that's the requested behavior.
- **Found + fixed a HA gotcha:** light-groups fire several `brightness` events
  per dim change (members update async); default automation `mode: single`
  dropped the up-dim run (`failed_single` in `trace/list`) so the plug missed
  turning on. Fix: `mode: restart` on the plug_dim automations + trigger =
  `state` `attribute: brightness` (+ `to: "off"`). Verified live: dim 120→plug
  off, 250→plug on, room off→plug off, on@250→plug on, manual plug press leaves
  the room light untouched. Also purged the leftover
  `automation.probe_dimmer_triggers` orphan from the morning's test automation.
- Exported `eeb1e8b` + `a8b6b6b` (also added `config/.gitignore` excluding
  `.ha_run.lock`; deleted the transient backup dir that got exported). Local
  `ha_config` clone synced. Skill §Dashboard/§Automations/§Gotchas updated.
  Post-test house state left consistent with the rule (vardagsrum 250/lekstuga
  on; gastrum/isac off + their plugs off).

## 2026-10-24 (late) — Fix: plugs flapped/blinked when the room dim hovered near 75 %

Owner report: "when I turn the livingroom dimmer on the bokhylla is blinking".
Diagnosis (live event capture + state_changed trace across the vardagsrum
group members): the plug rule acted, but turning the room dim near 75 % made
the plug flap. The Sunricher HK-SL-DIM-EU-A wall dimmer
(`light.dimmer_fixed_livingroom_light`, a `light.vardagsrum` member) **bounced
~±40–80 brightness levels around the commanded value** (e.g. 210 → 128 → 210),
so the group `brightness` kept crossing the single 191 threshold → the plug
automation re-fired on each crossing → the plugged lamp blinked. (The family's
"blinking" lamp was `switch.isac_lekstuga` following the room; bokhylla itself
was not being commanded directly.)
- **Fix**, two layers, exported `478c962`:
  1. `for: "00:00:03"` debounce on the `attribute: brightness`/`to: "off"`
     triggers — the rule only acts once the level has settled.
  2. **Hysteresis** in `script.plug_follow_room_dim` (same idea as the
     outside-light lux thresholds): plug ON at brightness > 209 (82 %), OFF at
     < 173 (68 %) or room off, HOLD between — so parking the room at ~75 %
     can't flap the plug.
- Verified live on `light.vardagsrum`: 220→on, 180→hold(on), 160→off,
  190→hold(off), 230→on. Skill §Plugs-follow updated with the dimmer-bounce +
  failed_single + hysteresis-debounce learnings. (Debug scripts in
  `/tmp/opencode/reproduce_dimmer.py`, `reproduce_group.py`.)

## 2026-10-24 (late) — Isacs rum excluded from the dim/plug rules (owner request)

- Deleted `automation.plug_dim_isacs_rum` (p6 no longer follows `light.isac_tak`
  dim) and removed its `script.reconcile_all` call; purged the orphan registry
  entity. Active rooms now: Vardagsrum (isac_lekstuga) + Gästrum (laslampa).
  Exported `76d8c47`; skill §Plugs-follow updated.

## 2026-10-24 (late) — Vardagsrum blink: Sunricher dimmer pulled out of the room dim

Owner: "when I turn the livingroom/manual dimmer on the bokhylla blinks … it's
blinking all the time now … the plug seems to work but the bokhylla has
problems." Diagnostics (event capture + live state polls): with the Sunricher
wall dimmer as a member of `light.vardagsrum`, the room dim commanded the
Sunricher (relaying phase-cut dimmer) which **bounced ±40–80 brightness levels
around the setpoint**, re-triggering the plug rule and beating on the bookshelf
circuit — bokhylla blinked, and the physical knob appeared dead. HA state was
stable during the "blinking all the time" reports, pointing to a physical/load
interaction rather than a logic loop.
- **Fix (inverted membership):** `light.vardagsrum` group now contains ONLY
  `light.bokhylla_h_light`. The Sunricher (`light.dimmer_fixed_livingroom_light`)
  is out of the room dim entirely — the physical knob remains pure manual for
  its own fixture. Room dim (dashboard tile) drives bokhylla cleanly; plug rule
  unchanged (`room_light: light.vardagsrum` still valid). Applied via
  `light.yaml` + `group.reload` (no restart). Verified: 220→isac on, 160→isac
  off, restored 254 — dimmer untouched throughout. Exported `f9b0fe5`. Skill
  §Room dimming updated with the "Sunricher stays out of room groups" rule.
- Note: if bokhylla still blinks when the physical knob is used, that is likely
  electrical (dimmer circuit feeding the driver) — physical wiring, not config.

## 2026-10-25 — Dimmer reconnected to HA; living-room plug decoupled from dim

Owner: "connect the dimmer switch back into the living room… use the dimmer
with HA… don't make the dimmer affect the plug in the living room."
- `light.vardagsrum` group = {dimmer_fixed_livingroom_light, bokhylla_h_light}
  again (room slider / HA drives the Sunricher dimmer).
- Deleted `automation.plug_dim_vardagsrum` + its `reconcile_all` call →
  `switch.isac_lekstuga` no longer follows the dim at all (fully manual; stays
  well decoupled from the wall dimmer). Purged registry orphans. Only Gästrum
  (laslampa) remains on the plug rule. Exported `fb6d33e`.
- **Hardware finding:** `light.bokhylla_h_light` (TRADFRI Driver 30W) now blinks
  AND ignores brightness commands (stuck on@254; direct `light.turn_on` to 180
  does nothing). Core log clean, ZHA device available, HA state stable during
  persistent blinking → the driver/bulb itself is failing. Not config; family
  to reseat/replace. Skill §Room dimming + §Plugs-follow updated.

## 2026-10-25 — Planned: tested-policy architecture (three-layer directions doc)

- **Owner decision**: evolve the YAML automation stack toward a modular,
  testable, LLM-maintainable Python shape. Decoupled quality infra
  (pytest/ruff/mypy + `domain/` package + fixtures) lands first, independent
  of the execution layer; a **bounded Pyscript spike** gates the rest.
- Re-opened the Pyscript evaluation (shelved 2026-10-20): verified current
  **2.1.0** supports HA 2026.5+ (we run 2026.10.2); the Oct-20 silent-failure
  was likely config-method mixing (YAML + UI flow) and/or the 2.0.0 decorator
  manager (documented `legacy_decorators: true` fallback never attempted).
  Pyscript's `modules/` package layout + native-module `sys.path` import path
  map 1:1 onto the brief's domain/adapter split and allow *tested == deployed*
  (Path E). Full design: **`docs/TESTED_POLICY_PLAN.md`**.
- **Binding invariant (owner):** never trigger any light on in `isacs_rum`
  (`light.isac_tak`, `switch.isac_lekstuga`, bedside) — Isac is asleep. Applies
  to all probes/spikes/pilot work.
- Docs + tracker updated; no live-config change. Next: Phase A quality
  skeleton, then Phase A+ Pyscript spike.

## 2026-10-25 — Phase A done: tested-policy quality skeleton

- **First delivered slice of the tested-policy architecture** (plan:
  `docs/TESTED_POLICY_PLAN.md`). All decoupled from the (as-yet undecided)
  execution layer — Path E (pyscript native) vs Path V (verify against live
  YAML) both build on this.
- **Tooling**: `pyproject.toml` via `uv` (`uv.lock`); dev deps pytest/ruff/mypy/
  pyyaml; ruff scoped to managed code (`domain`, `tests`; `tools/summarize.py`
  deliberately excluded as a legacy live script); mypy strict on `domain`.
- **Domain package** `domain/daylight/`: `models.py` (typed explicit
  input/output dataclasses + `FamilySchedule`), `home_status.py` (awake/sleep/
  away machine + `is_workday`/`next_wake`/`next_bedtime` — exact translation of
  `template/home_status.yaml`, incl. the #027 Sunday-axis decision),
  `daylight.py` (latched-lux hysteresis of `template/daylight.yaml`),
  `night.py` (`script.uteljus_sync` decision table, owner of the seasonal rule,
  NOOP on pause/`ha_ready` off). No HA imports, no entity IDs in policy.
- **Tests**: 29 unit tests (4 test files) + YAML **fixture matrix**
  `tests/fixtures/daylight/night_lights.yaml` as the policy contract. Caught a
  YAML 1.1 gotcha on the way (unquoted `on`/`off` → booleans — quoted now).
- **Gate**: `tools/qa.sh` — ruff + mypy + pytest + `summarize.py` consistency,
  all green, zero HA access. Skill dev-chain + config-method-gotcha section
  added; `docs/invariants.md` (7 invariants incl. the isacs_rum rule);
  `docs/subsystems/daylight.md` (explicit-interface record).
- No live-config change; VM untouched. Next: **Phase A+** bounded Pyscript
  spike (go/no-go gate for Path E) — the isacs_rum invariant applies.

## 2026-10-25 — Phase A+ Pyscript spike: GO (Path E chosen)

- **Spike goal:** determine, with evidence, whether pyscript can run on HA
  2026.10.2 — the Oct-20 "silent watchdog" failure made this a go/no-go for the
  execution layer. Result: **GO, Path E.**
- **Root cause (confirmed by fix):** Oct-20 mixed a `pyscript:` YAML block with
  a config-flow entry; pyscript's docs forbid mixing ("your initial choice
  determines how you update settings later"). This time: installed pyscript
  2.1.0 into `/config/custom_components/pyscript`
  (manual install, md5-baselined first), added the integration **via the config
  flow only** (`source: user`, `allow_all_imports: false`, no YAML block),
  core restart.
- **Verified live** (WS + logs): probe script module-load log; `sensor.
  pyscript_probe` = `loaded` (set *inside* `@time_trigger("startup")` → proves
  the trigger fired); watchdog auto-loaded a second probe file with no restart;
  `pyscript.reload` re-ran both; `pyscript.generate_stubs` (needs `?return_
  response`) wrote `modules/stubs/{pyscript_builtins,pyscript_generated}.py`;
  debug logging at `custom_components.pyscript.*` produced full eval/trace logs.
  Probes deleted afterwards → pyscript parked inert.
- **Exporter hiccup:** the add-on's `git-secrets` IP check flagged pyscript's
  `services.yaml` loopback default (`example/default: 127.0.0.1`). Fixed via the
  documented permalink — repo-root `.gitallowed` allow file in `ha_config`
  (pattern scoped to that file, not the rule) → exporter pushed `7d694a1`
  (pyscript component + stubs). `.gitallowed` survives because it lives outside
  `config/` and pull_before_push fetches it into the working tree pre-scan.
- Doc note (skill): `check_for_ips` is git-secrets; allow a false positive via
  `.gitallowed` at repo root (non-comment, non-blank regex lines matched against
  the scan target). Do not weaken `check.check_for_ips` globally.
- **Next:** Phase B — parity fixtures for `home_status` + `daylight` (the night
  matrix exists), then Phase C Path E adapters. Isacs_rum invariant active.

## 2026-10-25 — Phase B done: home_status + daylight fixture matrices

- Uniform fixture-matrix format `{defaults, cases}` in
  `tests/fixtures/daylight/{night_lights,home_status,daylight}.yaml`; loader
  merges defaults into inputs/schedule. `home_status.yaml` (13 cases: weekday/
  weekend axes, away, inclusive boundaries, custom schedule),
  `daylight.yaml` (12 cases: dead-zone holds, strict threshold edges,
  unavailable lux → 0).
- **Caught a real parity bug.** The fixture matrix proved the domain
  `next_wake`/`next_bedtime` disagreed with the deployed template: when
  today's boundary had already passed the template re-derives the *next day's*
  weekday axis (e.g. Sat after bed → Sun **weekday** 21:00, not weekend 21:30).
  Fixed `domain/daylight/home_status.py::_next_boundary` to mirror that exactly.
  53 tests green; qa.sh green.
