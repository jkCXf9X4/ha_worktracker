# Subsystem: daylight & home status (pilot cluster)

**Owner:** build agent (this repo). **Status:** Phase A+B+C done, 2026-10-25.

This is the explicit-interface record for the first migrated cluster. It
documents the *intended* contract; the live YAML on the VM is verified against
it (Path V parity / Path E probes).

**Execution state (Path E, shadow):** `domain/daylight` runs natively on the VM
at `/config/pyscript/native_domain/domain/daylight/`; thin pyscript adapters in
`/config/pyscript/scripts/` write `_ps` twin entities and log mismatches —
they do NOT call services. Ownership flip to `sensor.home_status` /
`binary_sensor.light_outside` is Phase D.

## Purpose and responsibilities

Derive the house's time/presence facts and the night/seasonal lighting
decisions:

- `sensor.home_status` — the awake/sleep/away state machine.
- `binary_sensor.light_outside` — latched-lux daylight flag.
- `script.uteljus_sync` — the nightly (utelampa) + seasonal (sasong) rule; the
  single owner of the seasonal rule.

## Inputs, outputs, dependencies

| Input (code) | HA entity | Domain receipt |
|---|---|---|
| `family_home` | `group.family` == home | `HomeStatusInputs.family_home` |
| `now` (local wall) | `now()` | `HomeStatusInputs.now` |
| wake/bedtime | `input_datetime.wake_time_{weekday,weekend}`, `bedtime_{weekday,weekend}` | `FamilySchedule` |
| `lux` | `sensor.lumi_..._illuminance` | `DaylightInputs.lux` |
| on/off thresholds | `input_number.outside_light_{on,off}_threshold` | `DaylightInputs.on_threshold` / `off_threshold` |
| current daylight flag | `binary_sensor.light_outside` | `DaylightInputs.currently_on` |
| christmas mode | `input_boolean.christmas_lights` | `NightLightsInputs.christmas_lights` |
| pause | `input_boolean.automatik_nattlampor` | `NightLightsInputs.paused` |
| readiness | `binary_sensor.ha_ready` | `NightLightsInputs.ha_ready` |

| Output | HA side effect |
|---|---|
| `HomeStatusResult.status` | `sensor.home_status` value |
| `HomeStatusResult.{is_workday,next_wake,next_bedtime}` | sensor attributes |
| `light_outside()` bool | `binary_sensor.light_outside` |
| `NightLightsResult.utelampa` | `label.utelampa` on/off |
| `NightLightsResult.sasong` | `label.sasong` on/off |

Dependencies: none outside the domain package. Adapters map the HA columns.

## State owned / entities permitted to control

- Owns the derived facts `sensor.home_status` + `binary_sensor.light_outside`.
- Controls only `label.utelampa` and `label.sasong`. Never touches the
  sovrum/isac morning fades (`light.isac_tak`, `switch.isac_lekstuga`, bedside).

## Invariants and safety constraints

- **Never trigger any light on in `isacs_rum`** (owner). See `docs/invariants.md`.
- `uteljus_pa` / `uteljus_av` (solo one-taps) never touch `sasong` — seasonal
  ownership lives only in `resolve_night_lights`.
- Hysteresis dead zone (150–400 lux default) suppresses flap; thresholds read
  live from the `input_number` helpers.
- Policy is deterministic on explicit inputs; no HA reads inside `domain/`.

## Behavior when inputs are missing, stale, or unavailable

- Lux `.float(0)` default → `DaylightInputs.lux == 0` → flag goes off if on,
  stays off (matches the deployed template, single-input recovery).
- `home_status` availability is only defined when all schedule helpers + family
  are known — the template renders `unavailable`; the machine keeps its last
  stable state otherwise.
- `ha_ready` off or `paused` on → `resolve_night_lights` returns NOOP for both
  labels (nothing changes).

## Startup, restart, and recovery

- `home_status` re-renders on a `time_pattern` every minute and on startup.
- Daylight flag self-settles from current lux on first render (no state to
  restore).
- Boot reconcile centralised in `script.reconcile_all`, which replays this
  cluster's behavior scripts exactly as their normal triggers would (incl. the
  pause/`ha_ready` gates).

## Files

- `domain/daylight/models.py` — explicit input/output types.
- `domain/daylight/home_status.py` — status machine + schedule boundaries.
- `domain/daylight/daylight.py` — lux hysteresis.
- `domain/daylight/night.py` — seasonal/night decision table.
- `tests/fixtures/daylight/night_lights.yaml` — the decision matrix contract.
- `tests/unit/daylight/` — 29 unit tests covering the above.