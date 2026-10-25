---
name: home-assistant
description: Living operational knowledge base for the rosenlund home Home Assistant setup (HAOS VM at 192.168.1.248, /config, YAML automations, Git Exporter versioning, ZHA/Tuya). Use whenever connecting to this HA instance, reading or editing its config/entities/automations/schedules, or working on the versioning + cleanup + migration build. Append new learnings here as they are discovered.
---

# Home Assistant — operational knowledge

This is a living reference, maintained while working on the build. Good places
for deeper context: `docs/PLAN.md` (the plan), `docs/archive/` (historical
baseline/spec/workbooks — incl. `hue_zha_migration.md`), and `WORKTRACK/NEXT.md`
(the live work tracker). Only `hue_zha_migration.md` is mirrored to the HA
config at `/config/docs/`.

## Accessing the instance

- **SSH & Web Terminal add-on** at `192.168.1.248:2222`, user **`root`**
  (add-on maps `/config` read-write and provides a root shell).
- Password is supplied by the owner during a session — do **not** persist it in
  this repo or in any committed file. Local publickey auth also works
  (`~/.ssh/id_ed25519` is allowed) — use it to avoid needing the password:
  `ssh -p 2222 -o PreferredAuthentications=publickey root@192.168.1.248 '<cmd>'`.
- Working connect command (password auth):

  ```bash
  sshpass -p "$HA_PASS" ssh -p 2222 -o StrictHostKeyChecking=accept-new \
    -o PreferredAuthentications=password -o PubkeyAuthentication=no root@192.168.1.248 '<cmd>'
  ```

### Critical shell quirks
- The **`ha` CLI (supervisor)** only works inside a **login shell**: wrap with
  `bash -lc "ha ..."`. A plain non-login command fails with
  `unauthorized: missing or invalid API token`.
- **Never pass `-t`/`-tt` when piping a script via stdin** (`ssh ... 'python3 -' < f.py`) —
  a TTY turns it into an interactive REPL and hangs. Use *plain* ssh (no `-t`);
  reserve `-tt` + `bash -lc "..."` for `ha` commands.
- **SFTP/scp is disabled** (`subsystem request failed`). Transfer files with
  tar-over-ssh:
  ```bash
  # pull:  ssh ... 'tar -C /config -cf - .storage' > dump.tar
  # push:  tar -C src -cf - . | ssh ... 'tar -C /config -xf -'
  ```

### Standalone commands
- `ha apps info 68413af6_git-exporter` — exporter options (includes plaintext PAT; don't print).
- `ha core check` — validate config (watch for secrets/IP/MAC complaints).
- `ha core restart`, `ha apps restart 68413af6_git-exporter`, `ha apps logs 68413af6_git-exporter`.
- `ha addons` is deprecated → use `ha apps`.

## Environment facts

- VM: **HAOS 18.3** on Proxmox. **HA Core 2026.10.2** (upgraded from 2026.9.2 on
  2026-10-21). `/config` → symlink to `/homeassistant`.
- SSH container: **Alpine 3.24** (has `python3` + `yaml`, git, etc.).
- Install add-ons present: Advanced SSH & Web Terminal (`a0d7b954_ssh`), Samba
  share (`core_samba`), File editor (`core_configurator`), Home Assistant Git
  Exporter (`68413af6_git-exporter`).
- `/config/custom_components/`: `doorman`, `hacs`, `scheduler`
  (scheduler + scheduler-card are HACS-tracked; `doorman` is legacy
  hand-installed). `samsungtv_tizen` removed 2026-10-20 and `script_engine`
  retired 2026-10-21 — component + scripts archived under
  `/config/deprecated/`, all logic now YAML automations.

## Versioning / Git Exporter

- **Git Exporter** mirrors `/config` → private GitHub repo `ha_config`
  (branch `main`, `pull_before_push: true`, interval-based).
- Exporter places exported config under **`config/`** in the repo.
- **Keep excluded** (set in add-on, matches `.gitignore`): `.storage/`,
  `secrets.yaml`, `.ssh/`, `.cloud/`, `*.db*`, `*.log*`, `__pycache__`, `tts/`, `deps/`.
- The exporter's **secrets check blocks commits** on IP/MAC/`password:`-type
  lines (patterns shown in logs). Move such values into `secrets.yaml` (excluded
  → not pushed) and reference with `!secret key`.
- **Git Exporter is PUSH-ONLY from `/config`** — verified 2026-10-20. Even with
  `pull_before_push: true`, remote commits are only fetched to avoid merge
  conflicts; they are **NOT** applied to `/config`. A commit pushed straight to
  the GitHub repo was silently reverted on the next export. **All config edits
  must go on the VM** (`/config/...` over SSH), then the exporter versions them.
  - **False-positive IP/MAC allow-list (verified 2026-10-25):** the exporter's
    secret check is `git-secrets` (awslabs, v1.3.0); `check.check_for_ips`
    blocks any IPv4/MAC. A **repo-root `.gitallowed`** (in `ha_config`) is the
    documented escape — it is read from `$(git rev-parse --show-toplevel)/`
    and each non-blank, non-`#` line is an allowed regex (comment with `#`).
    It survives because it lives outside `config/` and is fetched by
    `pull_before_push` before the scan. Scope the regex to the file, not the
    rule (e.g. `custom_components/pyscript/services\.yaml` for a loopback
    default). Do NOT set `check_for_ips: false` globally.
- Config change loop:
  1. edit files under `/config` over SSH,
  2. `ha core check`,
  3. `ha apps restart 68413af6_git-exporter`,
  4. inspect `ha apps logs 68413af6_git-exporter` for "Exporter finished".
- Because `pull_before_push` is on, commits made directly to the GitHub repo
  also land in `/config` on the next export run.

## Home topology (key entities)

- Groups (YAML): only `group.family` = person.sara + person.erik remains
  (2026-10-23). Ceiling/night/christmas roles moved to **labels** (see Labels
  section): `taklampa`, `natthorn`, `sasong`, `utelampa`. Seasonal sockets are
  gated by `input_boolean.christmas_lights` in `night_lights.yaml`. Scenes in
  `/config/scenes/scenes.yaml`: `scene.taklampor_pa`, `scene.nattlampor_pa`
  (static presets only — **scenes do not render Jinja templates**). The dynamic
  "Nattmode" (ceiling off + night-corner dim at the helper brightness) is
  `script.nattmode` in `scripts.yaml`. Cleaned 2026-10-21: only
  live entities remain (kontor_on_off/koket_on_off never existed; bokhylla_v +
  others purged).
- Locks (Yale via `doorman`): `lock.back`, `lock.main`, `lock.carport`.
- Outside-light sensor (ZHA/Aqara): `sensor.lumi_lumi_sen_ill_mgl01_8b21773c_illuminance` —
  live again 2026-10-23 (~58 lux at dusk); it is battery-powered, so watch for
  `unavailable` if the night/day automations stop reacting.
- **Open grouping question (owner input needed):** `switch.p4_socket` is a
  "Bilvärmaruttag" (car-heater outlet) yet sits in `group.night_lamps`
  year-round, while `switch.p6` ("Isacs rum sänglampa") sits in
  `group.christmas_sockets`. Suggest p4 be seasonal and p6 a night lamp, but
  that changes live behaviour — confirm with the owner before changing.
  **RESOLVED 2026-10-23:** P4 plug broke and was physically replaced by P11.
  `switch.p4_socket` no longer exists. Labels now own these roles (see below).
  **RESOLVED 2026-10-23 (late):** `switch.p6` removed from `label.sasong` — it is
  a bedside lamp, not a seasonal socket, and was turning on every night while
  `christmas_lights` was on (dusk→dawn via `script.uteljus_pa`). p6 is now a
  purely manual lamp. `sasong` = p10_socket + p1_socket only.
- **ZHA migration of the dead Hue bridge COMPLETE (2026-10-21).** All lights and
  plugs are on ZHA (ConBee II) with canonical entity IDs; canonical ID ↔ IEEE
  table in the ZHA section below. Full workbook:
  `docs/archive/hue_zha_migration.md`.
- Integrations: **zha (ConBee II)**, tuya, met, mobile_app ×4 phones, **uptime**
  (added 2026-10-24 as the readiness-gate source: `sensor.uptime` = boot
  timestamp, drives `binary_sensor.ha_ready`). Removed
  2026-10-20/21 (do not expect their entities): hue, samsungtv, dlna_dmr,
  spotify, cast, tibber, unifi.
- **Tuya re-authed 2026-10-21** — entry `916b4f19…` (title
  erik.rosenlund.private@gmail.com) back to `loaded` (was `setup_error`/token
  expired). 5 Tuya devices, **16 entities**. The outsides/gazebo lights ARE
  Tuya smart plugs:
  - `switch.p10_socket` "Slinga uterum" (gazebo light string, dev P10)
  - `switch.p11_socket` "Julslinga" (Christmas string, P11) — **since 2026-10-23
    it is the fixture that replaced the broken P4** = the front outdoor light
    following the daylight machine (utelampa label); nominally `unavailable`
    while the Tuya cloud is down
  - `switch.p1_socket` "Hörnlampa_vardagsrum" (P1)
  - `switch.p2_socket` (P2)
  - `light.laundry_nursingtable` (P1 sub-entity "Laundry.NursingTable") and
    `light.outroom_ballsling` — real Tuya light entities, **not** stale refs;
    show `unavailable` when the plug is physically off/absent (seasonal).

### Labels / areas (built 2026-10-23)

Areas (11) own "where"; **labels** own "role". Groups deleted except `family`.

- Areas: `korridor`=Badrum korridor, `carport_korridor`=Kök korridor, `hall`,
  `vardagsrum` (incl. lekstuga), `sovrum`, `isacs_rum`, `gastrum`, `hobbyrum`,
  `kitchen`=Kök, `outsideroom`=Uterum, `utebelysning`. Uteljussensor = house-wide.
- Labels (slug → membership):
  - `taklampa` — entre_hall_tak, korridor_tak, color_temperature_light_1,
    laslampa_on_off, bokhylla_h_light (ceiling lamps; was `group.ceiling_lamps`)
  - `natthorn` — l3_1, l3_2 (night-corner; was hard-coded in script.nattmode)
  - `sasong` — p10_socket, p1_socket (seasonal sockets; was `christmas_sockets`;
    **p6 removed 2026-10-23 — bedside lamp, not seasonal**)
  - `utelampa` — ute_huvudentre, p11_socket (front outdoor, follows daylight;
    was `group.night_lamps`)
- **CRITICAL label-targeting gotcha (verified 2026-10-23):** `entity_id: label.X`
  silently no-ops (success:true, nothing happens). Labels only resolve through
  `target.label_id: <slug>` (WS/automation channel). `light.turn_*`/`switch.turn_*`
  also accept `label_id`; `homeassistant.turn_*` accept it too. `area_id` targeting
  works normally (`light.turn_on` touches only light-domain entities in the area,
  so `switch.p6` in isacs_rum is NOT lit by the morning fade).
- Add a lamp to a role = edit the entity's label in the registry, no YAML.
  - Power meters: `sensor.p{4,10,11}_{current,power,voltage,total_energy}`.
- Registry: UniFi/Tibber/TV entities removed; remaining disabled entities are
  legit default-disabled diagnostics (~227).

## Automations (YAML — script_engine retired)

All legacy automation logic ran in custom Python
`custom_components/script_engine` + `/config/script_engine/*.py`; that
component **failed to load (ModuleNotFoundError) and was retired 2026-10-21**
(archived under `/config/deprecated/`). The build is now pure YAML
automations + schedule helpers. Migration design + P4 requirements: see
`docs/archive/automation_requirements.md`. Summary of what the stack does:

- Home-status machine `sensor.home_status` (`awake/sleep/away`) — input helpers
  + template in `/config/template/home_status.yaml`, schedules in
  `/config/input_*/schedules.yaml` (wake 06:45, bedtime 21:00 Sun–Thu /
  21:30 Fri–Sat). Template is **trigger-based via `time_pattern` every minute**
  (added 2026-10-23 — a state-based template never re-ran on the clock, so the
  awake/sleep transitions were stuck until someone arrived/left). Derived
  attributes on it (2026-10-24): `is_workday`, `next_wake`, `next_bedtime`.
  State/attribute logic uses **lexicographic compare of zero-padded `HH:MM:SS`
  strings** (clock order == string order), not timestamp math (#024, verified
  equivalent offline).
- Locks on sleep/away (`automations/locks.yaml`); the outside daylight fact is
  **`binary_sensor.light_outside` — a trigger-based template binary sensor**
  (`template/daylight.yaml`, since 2026-10-24) with a **latched-hysteresis**
  `state` via `this.state` (on above `outside_light_on_threshold`, off below
  `outside_light_off_threshold`; dead zone 150–400 lux by default, no flap).
  This **replaced** `automations/outside_light.yaml` + `input_boolean.light_outside`
  + `script.outside_light_sync` — a template self-settles at boot from the
  current lux, so no boot re-sync exists and there is no mutable state to
  restore. Availability mirrors the ZHA lux sensor (unavailable ⇒ consumers
  no-op). Threshold/on/off edges still fire the night/ceiling automations via
  state triggers on the binary sensor. Ceiling + night lamps — **since
  2026-10-23 the four
  ceiling automations are ONE data-driven automation**
  (`p4_ceiling_lights_follow_home_status_daylight`: state trigger on
  `home_status`+`binary_sensor.light_outside`; the 4-way `choose` now lives in
  `script.ceiling_lights_sync`, action targets `label.taklampa` /
  `label.slack_borta`, sleep branch runs `script.nattmode`) plus
  `night_lights.yaml` (both automations call `script.uteljus_sync`);
  Sovrum + Isac morning fades — **since 2026-10-24 two instances of the
  `room_schedule` blueprint** in `automations/room_schedules.yaml`, targeting the
  `sovrum`/`isacs_rum` **areas** through `script.light_on_with_transition`;
  readiness gate **`binary_sensor.ha_ready`** (`template/ha_ready.yaml`, derived
  from `sensor.uptime` ≥2 min; replaced the hand-rolled `input_boolean.ha_started`
  + `00_startup_grace.yaml`, retired 2026-10-24).
- **12 automation entities from 8 YAML files** across `/config/automations/`
  (include_dir_merge_list): boot_reconcile, ceiling_lights, night_lights
  (incl. the christmas-sockets sync), locks, room_schedules, hue_dimmer_isacs,
  styrbar_lekstuga, **plug_dim** (2026-10-24). **Boot reconciliation is ONE automation**
  (`automations/boot_reconcile.yaml`): `binary_sensor.ha_ready -> on` →
  `script.reconcile_all` (replays uteljus_sync → ceiling_lights_sync →
  lock_by_status **→ plug_follow_room_dim ×3**; each child is self-gated so
  paused behaviours are skipped).
  **Do NOT add `ha_ready -> on` triggers to new automation files** — extend
  `script.reconcile_all` instead. The daylight flag is a template and needs no
  boot re-sync.
- **12 automation entities + 13 scripts, 0 unavailable** (2026-10-24 late):
  registry renames `binary_sensor.light_outside_daylight_flag` →
  `binary_sensor.light_outside` and `script.las_vid_hemmastatus_gate` →
  `script.lock_by_status`; purged the `input_boolean.light_outside`,
  `automation.p4_outside_daylight_flag` and `script.outside_light_sync` orphans.
  **GOTCHA:** a template sensor's entity_id follows its NAME (not the
  key/`unique_id`) — rename in the entity registry, exactly as was done for
  `binary_sensor.ha_ready`.
- **Plugs follow room dim (75%) — `automations/plug_dim.yaml` + `script.plug_follow_room_dim`**
  (2026-10-24): **active room = Gästrum (laslampa_only).** Vardagsrum
  (isac_lekstuga) EXCLUDED 2026-10-24/25 (owner: "don't make the dimmer affect
  the plug in the living room") and Isacs (p6) excluded earlier — both plugs
  are fully manual. One-way rule with **hysteresis**: room dim `on` + brightness
  > 209 (82 %) → plugs ON; < 173 (68 %) or room off → OFF; between → plug keeps
  its state. Plug presses never touch the room lights (no trigger watches the
  plugs). Boot reconcile extends `script.reconcile_all`.
  **GOTCHAS (verified 2026-10-24):** (1) light-groups emit several `brightness`
  events per dim change (members respond async) — default automation
  `mode: single` DROPS the later run (`failed_single` in `trace/list`) → the
  plug can miss turning on; use `mode: restart`. (2) The Sunricher HK-SL-DIM-EU-A
  wall dimmer (`light.dimmer_fixed_livingroom_light`) **bounces ~±40–80
  brightness levels around the setpoint** when commanded, so a single 75 %
  threshold alone makes the plug flap/blink near the boundary → keep the
  hysteresis band AND add a `for: 3s` debounce on the `attribute: brightness`
  triggers so the plug only acts after the level has settled. Trigger =
  `state` `attribute: brightness` + `to: "off"`, both with `for`.
- **Scenes removed 2026-10-23** — `scenes.yaml` deleted: the 2 static scenes
  duplicated the taklampa/utelampa labels 1:1 and scenes can't target labels.
  Replaced by label-driven scripts (`script.taklampa_pa` = taklampa on,
  `script.uteljus_pa` = utelampa on). Scenes cannot render Jinja — keep dynamic
  presets in scripts (`script.nattmode`).
- **Automations are thin "when" wrappers** (2026-10-23 → finished 2026-10-24):
  the actual light/lock behavior lives in **scripts** (behavior boxes). As of
  2026-10-24 automations are **trigger→`script.X` only** — the pause/ha_ready
  gates were folded INTO the behavior-box scripts as a leading `if:`/`then:`
  wrapper (see the gotcha below — scripts have *no* top-level `condition` key).
  `ceiling_lights_sync`/`uteljus_sync` gate on their `automatik_*` toggle +
  `ha_ready`; `lock_by_status` gates `automatik_las` + `ha_ready` +
  `home_status sleep/away` and calls the ungated `lock_doors` (so `goodnight`
  always locks). Boot reconcile is centralized (see above).
  Decision logic (`choose`) lives in scripts — none left in automations:
  - `script.ceiling_lights_sync` — the 4-branch ceiling role (sleep→`nattmode`;
    away→`label slack_borta` off; awake+dark→`taklampa` on; awake+bright→off).
  - `script.uteljus_sync` — resolves `utelampa` from
    `binary_sensor.light_outside` (via `uteljus_pa/av`) **and** `sasong` from
    `christmas_lights`+`light_outside` in one call; **the single owner of the
    seasonal rule** (absorbed the old `script.sasong_sync`). Called by the
    night-lamps + christmas-toggle automations and `reconcile_all`.
  - `script.uteljus_pa/av` — front outdoor (`label.utelampa`) one-taps ONLY
    (since 2026-10-24 they do NOT touch `sasong`; the seasonal rule moved
    entirely into `uteljus_sync`). Named actions also used by `uteljus_sync`.
  - `script.reconcile_all` — boot replay of uteljus_sync → ceiling_lights_sync →
    lock_by_status (called by the single boot_reconcile automation).
  - `script.taklampa_pa` — ceiling lamps (`label.taklampa`) on.
  - `script.lock_doors` — locks back+main; UNGATED (used by goodnight).
  - `script.lock_by_status` — gated wrapper (automatik_las + ha_ready +
    home_status sleep/away) → `lock_doors`; the locks automation and
    `reconcile_all` call THIS. Entity is `script.lock_by_status`.
  - `script.goodnight` — composes `nattmode` + `lock_doors` (voice "god natt").
  - `script.nattmode` — ceiling off (`taklampa`) + night-corner dim (`natthorn`).
  - `script.light_on_with_transition` — fade a light, an area, **or a label**
    (choose order: area > label > entity). Label targeting added 2026-10-24.
- **Readiness gate = native `binary_sensor.ha_ready` (2026-10-24)** — the
  Python-era `input_boolean.ha_started` flag and `00_startup_grace.yaml` are
  **gone**. Instead: the **`uptime`** config-entry integration (created via
  config-flow; `sensor.uptime` = boot timestamp) + a trigger-based template
  binary sensor `binary_sensor.ha_ready` in `template/ha_ready.yaml` (on after
  ≥2 min, `time_pattern` /1). All automations trigger on `ha_ready -> on` and
  gate on `ha_ready == on`. Derived ⇒ can't desync / no manual toggling /
  no restore-state edges. (Fun fact: the pause-timer resume also fired at boot
  because a fresh timer went `unknown→idle` — a mutable-entity class bug; the
  derived sensor has zero such surface.)
- **`slack_borta` away label (2026-10-24)** — new cross-cutting label on all
  interior lamps/dimmers (incl. bedroom `dimmer_fixed_bedroom_light_2`,
  taklampa/natthorn are merged, NOT outdoor `utelampa`/seasonal `sasong`).
  The away branch of `ceiling_lights_sync` targets it → away = all indoor
  lighting off, outdoor stays on the daylight machine.
- **`room_schedule` blueprint (2026-10-24)** — `blueprints/automation/room_schedule.yaml`
  replaces `sovrum.yaml` + `isac_room.yaml`. Instances in
  `automations/room_schedules.yaml`: `p4_sovrum_schedule` (Mon–Fri + off) and
  `p4_isac_schedule` (daily, fade-in only). Inputs: area + on/off `input_datetime`
  entities + `input_number` brightness + weekday list (empty=all) +
  optional `pause_entity` (an `input_boolean`; when OFF the whole schedule is
  inert — empty = no pause). Fade transition shared via
  `input_number.fade_transition_seconds` (default 1200). Weekday check uses
  locale-proof `now().isoweekday() in weekdays` (select values are QUOTED
  numeric strings "1".."7", Monday=1). Both `on_entity` and `off_entity` are
  plain `at: !input X` time triggers; `off_enabled`/weekdays/pause gate the
  fade_out **action branch** (a no-op daily fire when off_enabled=false is
  harmless). **GOTCHA:** trigger `at:` limited templates get NO blueprint
  variables — a template `at` referencing `variables:` fails with
  `'x' is undefined` and the automation's triggers fail to set up. Keep `at:`
  values to `!input` substitutions only.
- **Blueprint select `value:` gotcha (2026-10-24):** the ORIGINAL flow-style
  selector options `- { label: X, value: "1" }` failed blueprint validation
  (`expected str at ...options[0].value'. Got None` → instances silently
  `unavailable`, only visible as setup errors in `ha core logs`). Block-form
  `- label: X\n  value: "1"` parses reliably — use that. (Note: the skill's
  older "quoted ints" wording is superseded by block-form.)
- **Pause toggles** (2026-10-23, extended 2026-10-24):
  `input_boolean.automatik_taklampor` / `automatik_nattlampor` / `automatik_las`
  + `automatik_sovrum` / `automatik_isac` (per room-schedule) gate the
  behaviors — family can pause from the dashboard (Automatik card, Belysning
  view). **This is the ONLY pause mechanism.** (A timer-based "pause for 1 h" +
  resume automation was built and then *removed* same day 2026-10-24 — redundant
  with the toggles and caused a boot-ordering bug; do not re-introduce.)
  All toggles use `initial: true` (deliberate: every restart re-enables the
  behaviors — unlike the schedule/seasonal helpers which restore). Gates live
  as `if:`/`then:` wrappers at the top of the dispatcher scripts, NOT in the
  automation files. **Gotchas:** `automation.trigger` bypasses conditions; and
  YAML `script:` objects have NO top-level `condition` key (HA rejects it:
  `not a valid option at 'condition'` and disables the script) — use a leading
  `- if:` `/` `then:` sequence item, or a `choose` with `default: []`.
- Dashboard views (2026-10-24): overview, **belysning** (Automatik card + a
  2-col grid of room **tiles** — one per room, each a `tile` card on the room's
  light/light-group with a `light-brightness` slider = "one dim per room", and
  `tap_action: navigate` into that room's hidden **subview**), utomhus
  (Utebelysning/Uterum entity cards + Säsongsbelysning = p10/p1), historik,
  schema. Energi view removed (had only the dead `sensor.p4_power`).
  **Room dimming = `light.group` entities** (YAML `light: - platform: group`
  in `/config/light.yaml`, needs core restart to load): `light.vardagsrum`
  (dimmer_fixed_livingroom_light + bokhylla_h_light — the Sunricher wall dimmer
  is IN the group again since 2026-10-24/25, used via HA; **isac_lekstuga is
  NOT coupled to the dim**, owner decision), `light.badrum_korridor`
  (korridor_tak + color_temperature_light_1), `light.kok_korridor` (l3_1 +
  l3_2). Group `turn_on(brightness=X)` sends the SAME brightness to every
  member; reported brightness = mean of members. **GOTCHA: the Sunricher
  HK-SL-DIM-EU-A bounces ±40–80 around a commanded level when driven quickly —
  keep it OUT of plug-follow triggers or debounce them (`for: 3s`).** Single-light
  rooms (hall/sovrum/isacs/gästrum/utebelysning) have no group — their single
  light is the room dim. Switch-only rooms (kök/hobbyrum/uterum) get plain
  toggles (nothing to dim). **NOTE: `light.bokhylla_h_light` (TRADFRI Driver
  30W) as of 2026-10-25 blinks and IGNORES brightness commands (stuck @254) —
  hardware failure of the driver/bulb, not config; family to replace/reseat.**
  **Room detail = hidden subviews** (`subview: true` + `back_path:
  /lovelace/belysning`, paths `rum-*`) — one per room with the room's full
  `entities` card, reached only via the overview tile (hidden from the tab bar).
  **GOTCHA (2026-10-24):** in HA 2026.10 the `area` card (`type: area`,
  `display_type: compact`) NO LONGER lists entities inline — it renders a static
  tile (icon + room name) with `interactive=false` unless it has `tap_action` or
  `card features`. It looks like a control but tapping does nothing. The family
  dashboard was rebuilt with `entities` cards per room instead (storage dash,
  `lovelace/config` + `lovelace/config/save`, full config payload, `url_path:
  "lovelace"`; WS ids must strictly increase).
- ZHA remote bindings are **blueprint instances** (added 2026-10-23):
  `automations/hue_dimmer_isacs.yaml` + `styrbar_lekstuga.yaml` use
  `blueprints/automation/zha_remote_lights.yaml` / `zha_remote_switch.yaml`
  (`use_blueprint: path: <filename>.yaml`, **no `local/` prefix**).

### Testing automations & pause gates live (2026-10-23)

Verified the hard way while testing the collapsed automations:

- **Do NOT use the `automation.trigger` service to test a gate/condition.** It
  runs the action **regardless** of conditions (trace showed `action/0` executed
  with no condition step while the gate was OFF) and updates `last_triggered`
  every time — a gate test via `automation/trigger` produces a false "it ran"
  result. Honest tests:
  1. **Real state change** — `binary_sensor.light_outside` is a template, so
     you can't set it by hand; force a flip instead by moving the
     `outside_light_on_threshold`/`outside_light_off_threshold` helpers across
     the current lux (or toggle `input_boolean.christmas_lights` to exercise the
     sasong path). These exercise the night automation's real trigger +
     `choose`; or
  2. **WS `test_condition`** — pass the exact `condition` list, get a boolean
     (`{"result": true|false}`); proves the gate flips the outcome without
     firing anything; or
3. **`binary_sensor.ha_ready` off→on** — every state automation triggers on
      `ha_ready -> on` (and gates on its state). `ha_ready` is on once HA has been
      up ≥2 min (template, derived from `sensor.uptime`). Since it can't be set
      manually (it's derived, not writable), synthesize a boot replay by
      reloading the template (`template.reload` resets its state) or by a real
      core restart — re-runs the whole reconcile path (night lamps, ceiling,
      locks) through real services.
- **`homeassistant.set_state` is NOT a service** (`Service homeassistant.set_state
  not found`) — you cannot fake entity states via the API. And **setting a
  `person.*` state does NOT cascade to `group.family`** (groups track
  device_trackers), so presence-based triggers can't be driven that way either.
- **Don't trust `last_triggered` (or logbook "ran") as proof a gate worked** —
  it updates even when a condition was bypassed by `automation.trigger`. Read the
  automation **trace** (`trace/list`, `trace/get`) for the actual step sequence.
- Real-world latency: Tuya plugs (p10/p11) and ZHA fixtures take **~3–6 s** to
  actually change state after a service call — wait/sleep before asserting states.

## ZHA (ConBee II) operations

- **Wiring/access**: ZHA integration runs on a ConBee II, config entry
  `61e34fbe326a93dbb8365024da665070`. Use the WebSocket API from
  `/tmp/opencode/zha_reload/` via `uv run --with websockets python3 -` for:
  `zha/devices` (device list incl. ieee/manufacturer/model),
  `config/entity_registry/list` (find an entity by unique_id prefix = the IEEE),
  `config/entity_registry/update` (rename entity_id + friendly name),
  `config/device_registry/list` / `update` (rename a device by identifiers).
  The trigger-list command is `device_automation/trigger/list` — the legacy
  `config/device_automation/trigger/list` form returns `unknown_command`.

### Device map (canonical entity_id ↔ IEEE)

All migrated onto ZHA 2026-10-21 (Hue bridge retired). Re-paired devices were
renamed to these canonical IDs so `groups.yaml`/automations kept working.

| Entity | Physical device | IEEE |
|--------|-----------------|------|
| `light.entre_hall_tak` | Hue ambiance — Entré hall tak | `00:17:88:01:02:5d:20:78` |
| `light.korridor_tak` | IKEA Dimmable — Korridor tak | (verified by flashing) |
| `light.color_temperature_light_1` | IKEA Color temp — Korridor 2 (E14 opal) | `68:0a:e2:ff:fe:97:37:28` |
| `light.l3_1` | Hue ambiance — "Groventre tak" (night corner) | `00:17:88:01:02:5f:a1:d1` |
| `light.l3_2` | IKEA Color temp — "Carport ingång" (night corner) | `8c:6f:b9:ff:fe:1e:fb:59` |
| `light.gastrum_tak` | IKEA E27 WS globe — guest room, mesh **router** | `8c:6f:b9:ff:fe:1e:f9:36` |
| `light.isac_tak` | IKEA E27 WS globe — Isacs room, mesh **router** | `8c:6f:b9:ff:fe:1e:fb:40` |
| `light.ute_huvudentre` | IKEA E27 WW — outdoor main entrance (was unnamed baseline bulb) | `58:8e:81:ff:fe:07:1b:b6` |
| `switch.laslampa_on_off` | innr plug P7 — "Gästrum fönster" | `00:15:8d:00:01:fd:e8:60` |
| `switch.p6` | innr plug — Isacs sänglampa | `00:15:8d:00:01:fd:ec:ab` |
| `switch.hobby_rum_fonster` | innr SP 120 — hobby room window | `00:15:8d:00:01:fe:98:f0` |
| `switch.isac_lekstuga` | IKEA TRETAKT plug — Isacs play house | `14:2d:41:ff:fe:e7:3f:0b` |
| (STYRBAR) | IKEA STYRBAR E2002 dimmer — Isacs lekstuga, `zha_event` buttons | `34:10:f4:ff:fe:fd:43:2b` |
| (Hue dimmer) | Hue dimmer RWL021 — Isacs, `zha_event` buttons | `00:17:88:01:02:d4:f7:ba` |
| `light.dimmer_fixed_bedroom_light_2` / `light.dimmer_fixed_livingroom_light` | ZHA dimmers (baseline, not from Hue bridge) | — |

**Purged 2026-10-21 — physically disconnected, do not hunt for these:** `light.p8`
(hunden), `light.steamlink` (P9), `light.on_off_plug_1` (P5), `light.l2`
(Christmas), `light.color_temperature_light_1_3` (L5), `light.dimmable_light_1`,
`light.bokhylla_v`. Hue virtual room entities (`light.vardagsrum`, `light.hall`,
`light.korridor`, `light.traningsrum`, `light.kvallsbelysning`,
`light.carport_korridor`, `light.gastrum`, `light.other`) died with the bridge —
recreate as HA groups if ever needed.

### Pairing routine
- Open/refresh permit-join via REST `POST /api/services/zha/permit
  {"duration":254}`. The window closes after ~4 min **and after EACH successful
  join** — re-call it between devices. A `nohup` loop re-calling it every ~8s
  during physical resets is the reliable pattern; earlier "pulsating but never
  joining" failures were the permit window lapsing while the device was mid-reset.
- Physical resets: IKEA/Hue bulbs — power-cycle ~6x ending ON (IKEA TRADFRI needs
  exactly 6 cycles to leave the old network); innr SP 120 plugs — hold the button
  ~10s until it blinks fast; IKEA TRETAKT — hold ~10s; IKEA STYRBAR dimmer
  (E2002) — paperclip the hole on the back ~5s until the LED blinks; Hue dimmer
  RWL021 — hold the setup button ~10s.
- A slowly "pulsing" lamp means it IS in pairing mode but the permit has often
  lapsed — re-open the permit and leave the device alone.
- Mains-powered devices (IKEA E27 globes, plugs) are Zigbee **routers** and add
  mesh coverage — pair them first so far/poorly-reached devices can join.
  Confirmed 2026-10-21: guest-room and Isacs ceiling globes enabled
  previously-stuck devices.

### Remote → light binding
- Do **not** string-match `zha_event` payloads. Poll
  `device_automation/trigger/list` (device_id from `config/device_registry/list`,
  domain `zha`) for the device's REAL trigger subtypes, then write YAML
  automations in `/config/automations/` with `platform: device` triggers —
  e.g. `remote_button_short_press`/`remote_button_long_press` with subtypes
  `turn_on`, `turn_off`, `dim_up`, `dim_down`. Dim via `light.turn_on` +
  `brightness_step_pct` (positive up, negative down), `mode: restart`.
- Validate with `ha core check` (wrap `ha` in `bash -lc`), then
  `POST /api/services/automation/reload`. Automation files load via
  `automation: include_dir_merge_list`.
- **The chat agent can now do this itself** (v0.2.0): `find_device` by friendly
  name → `device_id`, `device_triggers` for real type/subtype, `write_file` a
  YAML-**list** automation, `check_config`, `reload`. Same rule: never guess
  subtypes — always read them from `device_triggers`.
- Live examples: `/config/automations/styrbar_lekstuga.yaml` (STYRBAR →
  `switch.isac_lekstuga`), `/config/automations/hue_dimmer_isacs.yaml`
  (RWL021 → `light.isac_tak` + bedside `switch.p6`).
- **Single vs double press (RWL021, verified 2026-10-24):** ZHA device
  automation distinguishes them as **separate trigger types** —
  `remote_button_short_press` / `remote_button_double_press` (same subtype
  `turn_on`). No payload string-matching needed; the triggers are mutually
  exclusive (a double press fires only `double_press`).
  `blueprint zha_remote_lights.yaml` implements: single ON = light+optional
  switch on, double ON = switch on + light off, OFF/dim as usual.
- **GOTCHA (hit 2026-10-24):** HA's `condition: template` is **falsy for any
  non-boolean render** — `{{ target_switch }}` renders `"switch.p6"` and
  evaluates false. Use an explicit boolean, e.g. `{{ target_switch != '' }}`.
  Same class as numeric_state thresholds: never rely on a string render.

### Entity rename recipe
- Find the new ZHA entity via entity_registry unique_id prefix (= the IEEE),
  then `config/entity_registry/update` with `new_entity_id` + `name`.
- innr smart plugs register as `switch.*`, **not** `light.*` (SP 120) — canonical
  IDs must use the switch domain (e.g. `switch.p6`, `switch.laslampa_on_off`);
  groups referencing the old `light.*` IDs then need a ref update.

## Family chat agent (P6 — 2026-10-22, all-in)

- Native **`open_router`** integration (HA 2026.10, built-in), config-flow entry
  only (API key lives in `.storage` = never versioned). Conversation agent:
  `conversation.deepseek_deepseek_v4_flash_0731`, model
  `deepseek/deepseek-v4-flash-0731`, persona in Swedish (schedule + light
  control), web_search off. Default Assist pipeline switched to it (lang `sv`).
- **The `assist` LLM API does NOT expose arbitrary services.** It gives the
  model entity-control intents (lights/plugs/locks) + a live-context tool only.
  `input_datetime`/`input_number` helper writes are **not** reachable as
  services — the model fabricates success and nothing changes.
- Therefore helper writes went through **exposed scripts** (became LLM tools):
  5 schedule-writer scripts in `/config/scripts.yaml` — `set_family_schedule`,
  `set_sovrum_schedule`, `set_isac_schedule`, `set_outside_lux`,
  `set_night_dim`. Each: `description` (what/when), per-field `description`s,
  ends with a `stop` action + `response_variable` so the tool returns a real
  confirmation string. Script entity IDs take the slugified **alias**, e.g.
  `script.set_family_wake_bedtime_schedule`.
  - **Removed 2026-10-22 (owner decision, #021/P8):** those 5 scripts deleted
    from `scripts.yaml` in favour of the generic `config_tools` component
    (LLM `llm` platform → read_file/glob_files/write_file/check_config/reload
    tools). `bind_remote` was dropped as "too specific". **Live `input_*`
    helper values are now NOT changeable by the agent** (writes target
    reloadable YAML only); the family changes schedules via the dashboard
    pickers. The build flow for exposing a *new* script-as-tool still works:
    script + `description` + `stop`/`response_variable`, then
    `homeassistant/expose_entity`.
- **Exposure**: all live entities exposed to `conversation` (all-in) except
  `sun.sun`, `zone.home` (the unused `time_date` platform was removed
  2026-10-23, so `sensor.time/date*` no longer exist). WebSocket
  `homeassistant/expose_entity {assistants,entity_ids,should_expose}`;
  `homeassistant/expose_entity/list` to verify. Note: only entities where
  `async_should_expose` is true become LLM tools/index entries.
- Flow plumbing (all live, no YAML config): config-entry via
  `POST /api/config/config_entries/flow`; conversation **subentry** via
  `POST /api/config/config_entries/subentries/flow` with handler
  `[entry_id, "conversation"]` + `{model, prompt, llm_hass_api:["assist"], web_search}`;
  subentry/options flow handlers take the **entry_id**, not the domain.
- Pipeline routing on the VM: `assist_pipeline/pipeline/update` — full payload
  required (all TTS/STT/wake fields), each with values, or it 400s on
  "required key not provided".
- Test: `POST /api/conversation/process {text, agent_id, language}`; verify the
  side effect via `/api/states/<entity>` — the model often *reports* success it
  never performed when no tool matches; trust the state, not the reply.
- `.cache/brands/` icon churn shows up in exporter commits around integration
  loads (model catalogs, brand icons) — benign transient noise.

## config_tools component (P8 — 2026-10-22, deployed + extended to v0.4.0)

- Adds tools to the **same `assist` API** the OpenRouter agent uses, via a
  custom-component **`llm` platform**: `custom_components/config_tools/` with
  `manifest.json` (`"platforms": ["llm"]`), `llm.py` defining
  `async_get_tools(hass, llm_context, api_id) -> LLMTools | None`
  (`api_id == llm.LLM_API_ASSIST`). The `llm` integration merges platforms of
  all loaded integrations; the open_router agent auto-sends `llm_api.tools` to
  the model and executes tool calls itself (chat_log loop) — no agent code
  changes needed.
- Tools (names prefixed `config_tools__`): `read_file`, `glob_files`,
  `write_file`, `check_config`, `reload` (`automation|script|group|template`)
  — plus (v0.2.0) **`find_device`** (device-registry lookup by name →
  `device_id`) and **`device_triggers`** (live `device_automation` trigger
  type/subtype enum), (v0.3.0) **`call_service`** (see below), and (v0.4.0)
  **`set_label`** (reassign an entity's role labels in the entity registry;
  label-registry validated, applies instantly, no reload) + **`restart_core`**
  (admin; schedules `homeassistant.restart` — the only way new `input_*`
  helpers or component code take effect).
  `write_file`/`check_config`/`reload`/`set_label`/`restart_core` require an
  **admin** caller (checked via `llm_context.context.user_id` →
  `hass.auth.async_get_user().is_admin`); `call_service` is **exposure-bound
  only** (no admin gate — matches HA's native assistant-access model).
- Security: pure `pathlib`; path canonicalized under `config_dir`; write only
  `automations/*.yaml`, `scripts.yaml`, `groups.yaml`, `template/*.yaml`,
  **and `input_boolean|input_number|input_datetime/*.yaml`** (v0.4.0); never
  `configuration.yaml`/`secrets.yaml`/`.storage`/DBs/logs/config_tools itself.
  write→`async_check_ha_config_file`→reload (input_* have NO reload service —
  the tool returns "call restart_core"), reverting in memory on check
  failure. **No shell** (shell_command/command_line/py_script all live in
  `configuration.yaml`, never writable).
- Load: needs `config_tools:` (empty) in `configuration.yaml` + **core restart**
  — the `llm` platform lazy-scan only sees top-level components at boot.
- **Deployed + verified 2026-10-22 (v0.2.0):** all 7 tools exercised through
  the chat agent via `conversation/process` — incl. `find_device`→
  `device_triggers`→`write_file` round-trip on `styrbar_lekstuga.yaml`
  (dim_up retargeted then reverted).
- **Agent knowledge layer (offline, no internet):** the OpenRouter agent prompt
  (conversation subentry, `.storage`) carries a "TEKNISK DEL" block of hard
  rules + two reference docs it reads via `read_file`:
  `/config/docs/AGENT_HANDBOOK.md` and `/config/docs/AGENT_EXAMPLES.md`
  (both exported/versioned). **Refresh to v0.4.0 done 2026-10-24** — prompt now
  names all 10 tools (incl. `set_label`/`restart_core`), the `script.*`-tool
  preference, and the labels/areas architecture. To change the prompt again,
  use the **reconfigure flow**:
  1. `POST /api/config/config_entries/subentries/flow`
     body `{"handler": ["<entry_id>", "conversation"], "subentry_id": "<subentry_id>"}`
     → returns `flow_id` (the init form; WS command is `unknown_command`).
  2. `POST /api/config/config_entries/subentries/flow/{flow_id}` with the flat
     form fields `{"model","prompt","llm_hass_api":["assist"],"web_search":"off"}`
     (the URL carries the flow_id — **not** the body) →
     returns `"reason": "reconfigure_successful"`. Do NOT send `step_id`.
  (subentries/update websocket only changes `title`, not `data`.)
- **Stale exposure cleanup (2026-10-24):** exposure is all-in (above); when an
  entity/group/scene is deleted its `expose_entity` entry PERSISTS in
  `homeassistant/expose_entity/list` though the entity is gone (inert, but
  clutter). Cross-reference the list against `/api/states`, then un-expose
  stale entries (`should_expose: false`). 5 removed 2026-10-24
  (`group.ceiling_lamps`, `group.night_lamps`, the 3 deleted scenes).
- **Verified end-to-end 2026-10-22:** agent self-served a *new* device
  automation (ZZ test, Hue dimmer short-press right → ute lamp): read handbook,
  `find_device`, `device_triggers`, wrote a YAML **list** file, `check_config`,
  `reload` → entity registered; file then removed.
- **GOTCHA (verified 2026-10-22):** `automation: !include_dir_merge_list
  automations/` silently **drops** a file that is a single YAML mapping — each
  `automations/*.yaml` must be a **list** (start `- id: ...`). `ha core check`
  passes on the mapping (valid YAML), reload runs, but the automation never
  registers — no error anywhere. The chat agent's `write_file` cannot catch
  this; instruct it to always write automations as YAML lists.
- Rollout checklist: `docs/AGENT_TOOLS.md` §5.

### config_tools__call_service (P9 — v0.3.1, hardened + deployed 2026-10-23)

- **Purpose:** let the chat agent physically blink/act on lamps via real
  service params the entity intents can't carry (`flash`, `effect`,
  `transition`). The `assist` LLM API exposes no generic "any service" toggle;
  HA's `ActionTool` is script-only for schemas → custom tool in `config_tools`.
- **Native alternative (prefer for named actions):** an exposed **script** becomes
  a `script.*` tool automatically (schema = its `fields`; `ActionTool`). See
  `scripts.yaml::korridor_blink` (`fields: flash|transition`) — "blinka
  korridorlampan" works as a native script call, zero component code.
- **Allowlist** (`const.py::ALLOWED_SERVICE_ACTIONS`, single source of truth):
  `light|switch` `turn_on`/`turn_off`/`toggle` only. `group.*` targets work via
  core group expansion.
- **Blink = `light.turn_on` + `data={"flash": "short"|"long"}`.** Feature-bit
  background: ZHA lights report `supported_features` 40 = FLASH(8)+
  TRANSITION(32); the intents can't express flash, so use the service tool (or
  the script) when a param is needed.
- **Gating (v0.3.1): EXPOSURE-ONLY, no admin gate** — target must be in the
  entity registry AND
  `homeassistant.exposed_entities.async_should_expose(hass,
  llm_context.assistant, entity_id)` (assistant == `"conversation"` for the
  OpenRouter pipeline). Matches HA's native model (intents aren't admin-gated;
  the exposure registry IS the per-assistant permission). Admin gate remains on
  `write_file`/`check_config`/`reload` only.
- **`data` is a TYPED probatio schema** (`flash` In short/long, `brightness_pct`
  0-100, `brightness` 0-255, `transition` ≥0, `effect`, `color_temp_kelvin`,
  `color_temp`, `color_name`, `white`, `profile`, `xy_color`/`rgb_color`/
  `rgbw_color`/`rgbww_color`/`hs_color` as arrays). Unknown keys → parse-time
  `did you mean '...'` error. Service schema in
  `hass.services.async_call(blocking=True)` backstops. Returns re-read `state`
  + `attributes`; every call logged (`_LOGGER.info/warning`).
- **Writes in config_tools are atomic** (tempfile + `os.replace`, chmod 0644) —
  a crash can't leave a truncated YAML.
- **Verify recipe:** `conversation/process` prompting the exact tool + entity.
  Discriminator tool-vs-intent: `response.data.success`
  stays `[]` for the tool (an entity intent populates `success`). Trust state,
  not the reply — force `light.turn_off` and watch the state flip, then back on.
  Typo'd field in typed `data` (e.g. `data={"brightnes":123}`) → parse error.
- **GOTCHA found during deploy:** the VM's old v0.2.0 `_device_entity_ids` used
  `registry.get_entries_for_device_id` (EntityRegistry) → AttributeError —
  repo version uses `registry.entities.get_entries_for_device_id` (HA 2026.10);
  ensure pushed files md5-match (mirror == VM == repo). Exporter push `989e5a0`.
- **HA 2026.10 entity-registry API (v0.4.0 finding):** updates go through
  `EntityRegistry.async_update_entity(entity_id, **changes)` — a **sync**
  method that RETURNS the entry (do NOT `await` it; both `registry.async_update`
  and `registry.entities.async_update` are gone). Entity existence check is
  `registry.async_get(entity_id)`. Labels set via `labels=[...]` (replaces the
  whole set; validated against `label_registry.async_get(hass).labels`, which is
  already loaded — `async_load` asserts if present).
- **Component-code + `input_*` changes need a CORE RESTART** (config_tools
  module cache / no reload service). The agent's `config_tools__restart_core`
  is the sanctioned path (admin). `config_tools__set_label` applies instantly —
  no reload or restart.
- **GOTCHA (2026-10-24):** the Git Exporter versions EVERYTHING under
  `/config`, including stray backups — keep rollback tars OUTSIDE `/config`
  (e.g. `/root/...tar`). A `/config/.opencode_backup_*/files.tar` was
  committed and had to be pruned in a follow-up push.
- Plan + findings (archived): `docs/archive/call_service_tool_P9_PLAN.md`; live
  reference + security model: `docs/AGENT_TOOLS.md` §3.6.

## Gotchas / lessons learned

- **`secrets.yaml` hygiene**: the file had no trailing newline, so appending with
  `echo >> ` glued lines together into invalid YAML and corrupted the Yale
  password. Always validate with `python3 -c "import yaml; yaml.safe_load(open(...))"`.
  Prefer rewriting the file atomically over `sed` on it.
- **Never output `secrets.yaml`, the add-on PAT, or `ha apps info ... options`**
  (it prints the PAT verbatim). Redact anything sensitive from tool output.
- Watch for stray duplicate is in config: legacy `samsungtv_tizen` platform vs
  the built-in `samsungtv` config entries produce duplicated TV entities; the
  legacy platform keeps an IP+MAC in `configuration.yaml` (already moved to
  secrets).
- `configuration.yaml` is ancient style (deprecated `data_template`, bare
  `sensor:`/`script:` platform includes). Normalization is part of the build.
- Editing a file that a running instance depends on (configuration.yaml,
  secrets.yaml) — changes apply on next restart/core reload only; existing
  in-memory config keeps working meanwhile.
- **Jinja inside YAML + heredoc** = easy to lose quotes. A `cat <<'EOF'` heredoc
  with embedded single-quoted strings (e.g. `['weekday wake ' ~ var]`) mangled
  the quotes and HA disabled the script with `invalid template`. Fix: build the
  YAML locally (Write tool) → `yaml.safe_load`+`safe_dump` round-trip to verify
  → push via tar-over-ssh. Templates with embedded string literals are fragile
  through shell; prefer `~`-concatenation or separate `variables`.
- **Dynamic numeric_state thresholds** (`above:`/`below:`): use an **entity id**
  (`above: input_number.xxx`), NOT a Jinja string — the schema only accepts a
  float or an entity id in domains input_number/number/sensor/zone. A template
  string fails with `expected float at 'above'. Got None` and disables the
  automation.
- **Local automation blueprints**: file in `blueprints/automation/<name>.yaml`,
  reference as `use_blueprint: path: <name>.yaml` (**no `local/` prefix** — that
  only applies to UI-imported blueprints; wrong path → `Unable to find
  local/<name>.yaml` and the automation is silently `unavailable`). Device
  selectors take `integration:` (not `domain:`). YAML 1.1 footgun: unquoted
  `on`/`off` become booleans — quote trigger/conditions `id:`/`state:` values.
- **Scenes are NOT templated**: scene `entities` attributes are stored as
  literal values (`_convert_states` in `components/homeassistant/scene.py`), so
  a Jinja string for `brightness:` silently fails the light call. Use a script
  (or `scene.apply` inside one) for dynamic values — hence `script.nattmode`.
- **`initial:` on `input_datetime`/`input_number` resets family edits**: the
  value is re-applied on **every** HA start, overriding the restored state.
  Removed from all schedule helpers 2026-10-23; they now restore. Keep documented
  standard values in `tools/summarize.py::DEFAULTS` instead.
- **Friendly-name registry override**: a UI-set name wins over YAML `name:`
  (e.g. a YAML template's `name:` isn't applied if a registry override exists —
  `binary_sensor.ha_ready` shows "HA redo" from the registry, not the YAML name).
  Fix with WebSocket `config/entity_registry/update` (`entity_id` + `name`), or
  the UI — not by editing YAML.
- **Purging stale entities**: when automations are replaced/renamed, the old
  registry entities stay `unavailable` (e.g. after the 2026-10-24 round: old
  `p4_sovrum_*`/`p4_isacs_room_morning_fade_in`, `script.sasong_sync`,
  `pausa_automatik`, `timer.automatik_paus`, `automation.p4_ha_ready`,
  `input_boolean.ha_started`). Safe automated removal:
  WebSocket `config/entity_registry/remove` per `entity_id` (done 2026-10-23;
  avoids hand-editing `.storage/core.entity_registry`).
  - **WS message `id` must increase every request** — reusing the same `id`
    fails with `id_reuse ... Identifier values have to increase`. Use a counter.
  - Registry `remove` is one-shot per entity; batch = loop with incremented ids.
- **Lovelace dashboard is storage-backed**: live dashboard lives in
  `.storage/lovelace.lovelace` (not `/config/lovelace/...yaml`). The exporter's
  `lovelace/lovelace.lovelace.yaml` is a *derived mirror*. To change the live
  dashboard: **read it back via WS `lovelace/config` → edit JSON → `lovelace/config/save`**
  (full config in the save payload), then restart the exporter so the mirror
  updates. Editing the YAML mirror locally does NOT touch the live dashboard.
- **Adding helpers via YAML needs a core restart**: `input_boolean`/
  `input_number`/`input_datetime` added in YAML have **no reload service** —
  `ha core restart` is required for new helper entities to appear (2026-10-23:
  `automatik_las` only loaded after restart). The chat agent can do the whole
  loop itself with `config_tools__write_file` (input_* is now writable) +
  `config_tools__restart_core`.

## Tested-policy architecture (Phase A+ — active from 2026-10-25)

Plan: `docs/TESTED_POLICY_PLAN.md`; per-subsystem contract:
`docs/subsystems/daylight.md`; binding decisions: `docs/invariants.md`.

- **Quality gate (run before ANY deploy of managed logic):** `tools/qa.sh`
  (from repo root) — ruff + mypy + pytest + `summarize.py` consistency. Zero HA
  access needed; must exit 0. Fast form: `tools/qa.sh fast` (skips summarize).
- **Domain package** `domain/daylight/` = pure Python policy (no HA imports,
  no entity IDs), typed via `models.py`. Unit tests + YAML fixture matrices in
  `tests/`. The fixture matrix (`tests/fixtures/daylight/night_lights.yaml`) is
  the contract the deployed YAML/pyscript adapter must satisfy.
- **Repo = source of truth for managed logic; VM `/config` = source of truth
  for config state.** This preserves the push-only exporter. `mirror == build`
  and `mirror == VM` md5 checks fail on drift.
- **Binding invariant (owner):** never trigger any light on in `isacs_rum`
  (`light.isac_tak`, `switch.isac_lekstuga`, bedside) — Isac is asleep. All
  probes/spikes/deploys respect this; the sovrum/isac fades stay pure YAML.
- **Config-method gotcha (Pyscript, verified 2026-10-20 + docs 2026-10-25):**
  do NOT mix a `pyscript:` YAML block with a UI config-flow entry — Pyscript
  ignores the three settings from YAML when added via the UI flow; pick one
  method. If the 2.0+ decorator subsystem misbehaves, `legacy_decorators: true`
  is the documented fallback (needs a restart). Debug logger path is
  `custom_components.pyscript.apps.*: debug` (2.x), not just the parent.
  Pyscript 2.1.0 supports HA 2026.5+ (we run 2026.10.2).
- **Pyscript native-module import idiom (verified 2026-10-25):** to import a
  NATIVE Python package (not pyscript-interpreted) you must use
  `importlib` + a sys.path insert + **`importlib.invalidate_caches()`** and put
  the package OUTSIDE `/config/pyscript/modules/`. The `modules/` dir is
  re-parsed by pyscript's AST interpreter (NOT native — cannot run dataclasses/
  StrEnum/generators) so it is unsuitable for the pytest-tested domain package.
  Working idiom at top of a script:
  ```python
  import sys, importlib
  _NATIVE_DOMAIN = "/config/pyscript/native_domain"
  if _NATIVE_DOMAIN not in sys.path:
      sys.path.insert(0, _NATIVE_DOMAIN)
  importlib.invalidate_caches()
  from domain.daylight import ...   # native, compiled
  ```
  Requires `allow_all_imports: true` (config-flow options; `domain`/`sys` are
  not in `ALLOWED_IMPORTS`). **Why invalidate_caches:** importlib caches the
  directory listing of a new sys.path entry even on a FAILED import (e.g. files
  mid-push), so later imports fail with `No module named '...'` indefinitely
  until the cache is flushed. Pyscript `@pyscript_compile` is per-function only;
  the native-module path is the way to run C-accelerated/pytest-identical code.
  Also: keep individual `@time_trigger`/`@state_trigger` decorator call-sites
  free of generator expressions — write them as explicit loops/constants.

## How to grow this skill

As you discover new facts, gotchas, or command patterns, append them under the
matching section (or add a section). Keep it concise and durable — entity
facts, working commands, and warnings; not one-off transcripts. Secrets never
belong here.