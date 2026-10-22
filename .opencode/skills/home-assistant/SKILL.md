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
  this repo or in any committed file.
- Working connect command:

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

- VM: **HAOS 18.2** on Proxmox. **HA Core 2026.10.2** (upgraded from 2026.9.2 on
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
- Config change loop:
  1. edit files under `/config` over SSH,
  2. `ha core check`,
  3. `ha apps restart 68413af6_git-exporter`,
  4. inspect `ha apps logs 68413af6_git-exporter` for "Exporter finished".
- Because `pull_before_push` is on, commits made directly to the GitHub repo
  also land in `/config` on the next export run.

## Home topology (key entities)

- Groups (YAML): `group.family` = person.sara + person.erik; `group.ceiling_lamps`
  (entre_hall_tak, korridor_tak, laslampa_on_off, bokhylla_h); `group.night_lamps`
  (ute_huvudentre, seasonal sockets p10/p11/p1/p4, p6). Cleaned 2026-10-21: only
  live entities remain (kontor_on_off/koket_on_off never existed; bokhylla_v +
  others purged).
- Locks (Yale via `doorman`): `lock.back`, `lock.main`, `lock.carport`.
- Outside-light sensor (ZHA/Aqara): `sensor.lumi_lumi_sen_ill_mgl01_8b21773c_illuminance` —
  battery, unavailable since 2026-10-19T11:03Z (needs battery; keep device).
- **ZHA migration of the dead Hue bridge COMPLETE (2026-10-21).** All lights and
  plugs are on ZHA (ConBee II) with canonical entity IDs; canonical ID ↔ IEEE
  table in the ZHA section below. Full workbook:
  `docs/archive/hue_zha_migration.md`.
- Integrations: **zha (ConBee II)**, tuya, met, mobile_app ×4 phones. Removed
  2026-10-20/21 (do not expect their entities): hue, samsungtv, dlna_dmr,
  spotify, cast, tibber, unifi.
- **Tuya re-authed 2026-10-21** — entry `916b4f19…` (title
  erik.rosenlund.private@gmail.com) back to `loaded` (was `setup_error`/token
  expired). 5 Tuya devices, **16 entities**. The outsides/gazebo lights ARE
  Tuya smart plugs:
  - `switch.p10_socket` "Slinga uterum" (gazebo light string, dev P10)
  - `switch.p11_socket` "Julslinga" (Christmas string, P11) — seasonal, off
  - `switch.p1_socket` "Hörnlampa_vardagsrum" (P1)
  - `switch.p2_socket` (P2)
  - `switch.p4_socket` (P4, has power/voltage/energy sensors, "Bilvärmare")
  - `light.laundry_nursingtable` (P1 sub-entity "Laundry.NursingTable") and
    `light.outroom_ballsling` (P4 sub-entity "Outroom.BallSling") — real Tuya
    light entities, **not** stale refs; show `unavailable` when the plug is
    physically off/absent (P4/P1 seasonal).
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
  21:30 Fri–Sat).
- Locks on sleep/away (`automations/locks.yaml`); outside-light lux hysteresis
  (400 on / 150 off) (`outside_light.yaml`); ceiling + night lamps
  (`ceiling_lights.yaml`, `night_lights.yaml`); Sovrum bedroom schedule
  06:22–09:36 (Scheduler addon); startup grace `00_startup_grace.yaml`.
- 14 YAML automations active across `/config/automations/` (include_dir_merge_list).
- ZHA remote bindings live as `platform: device` automations in the same dir
  (`styrbar_lekstuga.yaml`, `hue_dimmer_isacs.yaml`).

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
- Live examples: `/config/automations/styrbar_lekstuga.yaml` (STYRBAR →
  `switch.isac_lekstuga`), `/config/automations/hue_dimmer_isacs.yaml`
  (RWL021 → `light.isac_tak`).

### Entity rename recipe
- Find the new ZHA entity via entity_registry unique_id prefix (= the IEEE),
  then `config/entity_registry/update` with `new_entity_id` + `name`.
- innr smart plugs register as `switch.*`, **not** `light.*` (SP 120) — canonical
  IDs must use the switch domain (e.g. `switch.p6`, `switch.laslampa_on_off`);
  groups referencing the old `light.*` IDs then need a ref update.

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

## How to grow this skill

As you discover new facts, gotchas, or command patterns, append them under the
matching section (or add a section). Keep it concise and durable — entity
facts, working commands, and warnings; not one-off transcripts. Secrets never
belong here.