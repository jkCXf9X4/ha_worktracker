# Automation requirements & migration design

> **Status: SUPERSEDED 2026-10-21 — archived.** The YAML port described here was
> implemented and went live (P4); current behaviour lives in the live
> `automations/` + `input_*` helpers. Kept for reference only.

Extracted (2026-10-20) from the custom Python `script_engine` automations in
`/config/script_engine/*.py` plus the Scheduler integration and `groups.yaml`.

Purpose: faithful specification of **what the home automates today**, and the
YAML + `input_*`-helper design that preserves the behaviour while making
schedules **textual/editable** (family dashboard + chat agent + git).

---

## 1. Domain facts (real entity IDs)

| Thing | Entity |
|-------|--------|
| Family group | `group.family` = `person.sara`, `person.erik` |
| Ceiling lamps | `group.ceiling_lamps` = `light.entre_hall_tak`, `light.korridor_tak`, `light.laslampa_on_off`, `light.bokhylla_h_light`, `light.bokhylla_v_light` |
| Night lamps | `group.night_lamps` = `light.ute_huvudentre`, `light.kontor_on_off`, `light.koket_on_off`, `light.p8` (dog), + seasonal: `switch.p10_socket` (ute framsida), `switch.p11_socket` (julgranslinga), `switch.p1_socket` (köket stjärnor), `light.p6` (Isacs rum), `switch.p4_socket` |
| Locks | `lock.back`, `lock.main` (also `lock.carport` in one group) |
| Outside light sensor | `sensor.lumi_lumi_sen_ill_mgl01_8b21773c_illuminance` (Aqara, ZHA) |
| Night-corner dim lights | `light.l3_1`, `light.l3_2` (Hue) |
| Bedroom dimmer (Sovrum) | `light.dimmer_fixed_bedroom_light_2` (ZHA) |

---

## 2. Current logic (from `script_engine` + Scheduler)

### 2.1 Home-status machine (`script_time.py`)
Virtual state `script_engine.home_status` ∈ {`sleep`, `awake`, `away`}.
- Bedtime: **21:00** on Sun–Thu, **21:30** on Fri–Sat.
- Wake: **06:45** (all days; weekend value is identical).
- `family home` + time in `[wake, bedtime)` → `awake`.
- `family home` + time in `[bedtime, wake)` (overnight) → `sleep`.
- `family` `not_home` → `away`.
- Re-evaluated on person-group changes and time events.

### 2.2 Door locks (`script_locks.py`)
- home-status → `sleep`: lock `back` + `main` (1 min grace).
- home-status → `away`: lock `back` + `main` (1 min grace).
- Skips a lock already `locked`.

### 2.3 Outside light-state machine (`script_light_sensor.py`)
Virtual boolean `script_engine.light_outside`.
- Illuminance **> 400 lux** → light outside = `True`.
- Illuminance **< 150 lux** → light outside = `False`.
- (hysteresis 150–400.)

### 2.4 Ceiling lights (`script_ceiling_lights.py`)
- `awake` + dark outside → **on** ceiling lamps.
- `awake` + bright outside → **off** ceiling lamps.
- `sleep` → **off** ceiling lamps **and** dim `light.l3_1`/`light.l3_2` to brightness **56** (night corner).
- `away` → **off** ceiling lamps.
- (Unused variant had: turning on 03:00–09:00 uses a 30 min transition “morning fade”.)

### 2.5 Night lights (`script_night_lights.py`)
- dark outside → **on** night-lamp group (incl. seasonal sockets).
- bright outside → **off** night-lamp group.

### 2.6 Bedroom schedule — Scheduler integration
Schedule **“Sovrum”** (workdays):
- `06:22 → 09:36`: `script.light_on_with_transition` on `light.dimmer_fixed_bedroom_light_2` → brightness 200, transition 1200 s.
- `09:36 → 24:00`: `light.turn_off` same light.

---

## 3. Hard-coded values → editable `input_*` helpers

These become the **textual schedules** the family can change (wall/chat) and see summarized.

| Helper | Meaning | Default |
|--------|---------|---------|
| `input_datetime.wake_time_weekday` | Morning alarm: Mon–Fri | 06:45 |
| `input_datetime.wake_time_weekend` | Morning alarm: Sat–Sun | 06:45 |
| `input_datetime.bedtime_weekday` | Lights out / lock-up: Sun–Thu | 21:00 |
| `input_datetime.bedtime_weekend` | Lights out / lock-up: Fri–Sat | 21:30 |
| `input_datetime.sovrum_on_time` | Bedroom fade-in time (workdays) | 06:22 |
| `input_datetime.sovrum_off_time` | Bedroom off time (workdays) | 09:36 |
| `input_number.outside_light_on_threshold` | Lux to declare daylight | 400 |
| `input_number.outside_light_off_threshold` | Lux to declare dark | 150 |
| `input_number.night_corner_brightness` | Corner-dimmer level at sleep | 56 |
| `input_number.sovrum_brightness` | Bedroom morning brightness | 200 |
| `input_boolean.light_outside` | Derived daylight flag | — (state machine) |
| `input_select.home_status` | Derived `awake/sleep/away` | — (state machine) |

(Exact “weekday list” for bedtimes: keep Sun–Thu as in the original; document it.)

---

## 4. Proposed YAML architecture (replaces `script_engine`)

Mirror each Python rule 1:1 into standard automations — no traffic light, pure
native HA:

- **1 template sensor** `sensor.home_status` — derived from `group.family` +
  `now()`, auto-refreshes every minute (matches the Python re-evaluation model).
- **2 automations** for outside-light hysteresis (on above threshold / off below),
  mirroring `_Script_LightSensorOutside`.
- **2 automations** for locks (`home_status` → sleep/away, 1 min delay), mirroring
  `_Script_Locks`.
- **4 automations** for ceiling lights (+ air-corner dim), mirroring
  `_Script_CeilingLights`.
- **2 automations** for night lamps, mirroring `_Script_NightLights`.
- **2 automations** for the bedroom (Sovrum) daily schedule using the helpers +
  the existing `script.light_on_with_transition`.

Config layout (to land in `/config`):

```text
configuration.yaml         # lean core + !include_dir_*
automations/
  home_status.yaml
  outside_light.yaml
  locks.yaml
  ceiling_lights.yaml
  night_lights.yaml
  sovrum.yaml
input_datetime/schedules.yaml
input_number/schedules.yaml
input_select/home_status.yaml
input_boolean/light_outside.yaml
script/light_on_with_transition.yaml   # modernized (no deprecated data_template)
```

---

## 5. What this buys us

- **Textual schedules**: the whole “calendar” of the house in a few YAML files →
  git-diffable, reviewable, family-questionable.
- **Chat agent integration**: helpers are exposed entities — the Assist LLM reads
  the current schedule and changes helper values; automations just follow.
- **Summaries**: `tools/summarize.py` renders `SCHEDULES.md` / `AUTOMATIONS.md`
  from the same YAML.
- **Retirement of custom code**: `custom_components/script_engine`, the Scheduler
  custom integration, and the deprecated `data_template` scripts can be removed
  once the port is verified (kept in git history via `config/deprecated/`).

---

## 6. Migration-order safeguards

1. Land after versioning (P1) so every step is reversible in git.
2. Build + verify the YAML port while `script_engine` still runs; compare logs
   (`script_engine` debug logging already active).
3. Disable `script_engine`; let YAML take over; observe a full day/night cycle.
4. Only then uninstall components / prune entities.