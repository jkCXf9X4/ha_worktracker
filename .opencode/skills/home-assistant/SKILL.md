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
  (ute_huvudentre, p4_socket). **Since 2026-10-23:** seasonal sockets live in
  `group.christmas_sockets` (p10/p11/p1/p6), gated by
  `input_boolean.christmas_lights` in `night_lights.yaml`. Scenes in
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
  21:30 Fri–Sat). Template is **trigger-based via `time_pattern` every minute**
  (added 2026-10-23 — a state-based template never re-ran on the clock, so the
  awake/sleep transitions were stuck until someone arrived/left).
- Locks on sleep/away (`automations/locks.yaml`); outside-light lux hysteresis
  (400 on / 150 off, **read live from the input_number helpers**
  `outside_light_on/off_threshold` via `above:`/`below:` entity refs)
  (`outside_light.yaml`); ceiling + night lamps (`ceiling_lights.yaml` —
  sleep action now `script.turn_on script.nattmode`, `night_lights.yaml`);
  Sovrum + Isac morning fades (`sovrum.yaml`, `isac_room.yaml`);
  single startup grace `00_startup_grace.yaml` (`input_boolean.ha_started`,
  forced off every boot via `initial: false`, on after 2 min; the 1-min/2-min
  split + `ha_started_2min` were removed 2026-10-23).
- **17 YAML automations active** across `/config/automations/`
  (include_dir_merge_list). State automations also trigger on
  `input_boolean.ha_started -> on` to reconcile lights/locks after a reboot;
  the outside-light automations re-sync the daylight flag on `homeassistant
  start` (numeric_state alone only fires on a threshold crossing).
- **17 automation entities, 0 unavailable** (2026-10-23): the 12 orphaned
  registry entries were removed via WebSocket `config/entity_registry/remove`.
- ZHA remote bindings are **blueprint instances** (added 2026-10-23):
  `automations/hue_dimmer_isacs.yaml` + `styrbar_lekstuga.yaml` use
  `blueprints/automation/zha_remote_lights.yaml` / `zha_remote_switch.yaml`
  (`use_blueprint: path: <filename>.yaml`, **no `local/` prefix**).

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
  (RWL021 → `light.isac_tak`).

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

## config_tools component (P8 — 2026-10-22, built, not yet deployed)

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
  type/subtype enum), plus (v0.3.0) **`call_service`** (see below).
  `write_file`/`check_config`/`reload`/`call_service` require an **admin**
  caller (checked via `llm_context.context.user_id` →
  `hass.auth.async_get_user().is_admin`).
- Security: pure `pathlib`; path canonicalized under `config_dir`; write only
  `automations/*.yaml`, `scripts.yaml`, `groups.yaml`, `template/*.yaml`; never
  `configuration.yaml`/`secrets.yaml`/`.storage`/DBs/logs/config_tools itself.
  write→`async_check_ha_config_file`→reload, reverting in memory on check
  failure. **No shell** (shell_command/command_line/py_script all live in
  `configuration.yaml`, never writable).
- Load: needs `config_tools:` (empty) in `configuration.yaml` + **core restart**
  — the `llm` platform lazy-scan only sees top-level components at boot.
- **Deployed + verified 2026-10-22 (v0.2.0):** all 7 tools exercised through
  the chat agent via `conversation/process` — incl. `find_device`→
  `device_triggers`→`write_file` round-trip on `styrbar_lekstuga.yaml`
  (dim_up retargeted then reverted).
- **Agent knowledge layer (offline, no internet):** the OpenRouter agent prompt
  (conversation subentry, `.storage`) was extended with a "TEKNISK DEL" block of
  hard rules + two reference docs it reads via `read_file`:
  `/config/docs/AGENT_HANDBOOK.md` and `/config/docs/AGENT_EXAMPLES.md`
  (both exported/versioned). Update the prompt via the **reconfigure flow**:
  1. `POST /api/config/config_entries/subentries/flow`
     body `{"handler": ["<entry_id>", "conversation"], "subentry_id": "<subentry_id>"}`
     → returns `flow_id` (the init form).
  2. `POST /api/config/config_entries/subentries/flow/{flow_id}` with the flat
     form fields `{"model","prompt","llm_hass_api":["assist"],"web_search"}` →
     returns `"reason": "reconfigure_successful"`. Do NOT wrap in `step_id`.
  (subentries/update websocket only changes `title`, not `data`.)
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
- Plan + findings: `docs/call_service_tool_P9_PLAN.md`.

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
  (live `input_boolean.ha_started` kept the old "HA startat (1 min)"). Fix with
  WebSocket `config/entity_registry/update` (`entity_id` + `name`), or the UI —
  not by editing YAML.
- **Purging stale entities**: when automations are replaced/renamed, the old
  registry entities stay `unavailable` (e.g. the retired `ha_started_2min`,
  the 8 old per-button remote automations). Safe automated removal:
  WebSocket `config/entity_registry/remove` per `entity_id` (done 2026-10-23;
  avoids hand-editing `.storage/core.entity_registry`).

## How to grow this skill

As you discover new facts, gotchas, or command patterns, append them under the
matching section (or add a section). Keep it concise and durable — entity
facts, working commands, and warnings; not one-off transcripts. Secrets never
belong here.