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
- Tracker/docs: kept locally; optionally mirrored into `/config/docs/`
  (owner decision, backlog #014).

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