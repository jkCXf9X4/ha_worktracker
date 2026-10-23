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
