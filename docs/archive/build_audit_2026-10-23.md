# Audit of this build — snapshot 2026-10-23

> **Status: SUPERSEDED/snapshot — archived.** This is the dated audit of
> `config/` that accompanied `docs/BEST_PRACTICES.md` (§2) before the
> 2026-10-23/24 simplification rounds. Nearly every "delta" below was then
> **implemented**: ceiling automations consolidated (Taras, #026), labels added
> (`taklampa`/`natthorn`/`sasong`/`utelampa`), pause toggles added
> (`automatik_*`, #032), `home_status` math simplified (#024), startup-grace
> collapsed (#025/`ha_ready`), scenes deleted. Kept for the record; the live
> reference (practices) is `docs/BEST_PRACTICES.md`.

Snapshot of the audit (2026-10-23), deltas originally listed in BEST_PRACTICES §2:

### Already conformant (good) — as of the snapshot

- UI + YAML split right; `!include_dir_merge_list` pattern correct.
- Secrets hygiene (Yale creds `!secret`, exporter excludes, embargos).
- `initial:` removed from schedule helpers (P10 fix).
- Scripts over duplicated action lists (`light_on_with_transition`, `nattmode`).
- Blueprints for remote binding (ZHA RWL021 + STYRBAR).
- Hysteresis as two numeric_state automations with `input_number` thresholds.

### Deltas worth acting on — snapshot findings (all since DONE)

1. Startup-grace gate repeats in every automation → **#025/#026**: consolidated
   into `00_startup_grace` + one data-driven automation, later replaced by
   native `binary_sensor.ha_ready` + `script.reconcile_all` (2026-10-24).
2. Four ceiling automations share one shape → **#026 DONE**: one Taras
   data-driven automation over `sensor.home_status` + `light_outside`.
3. `groups.yaml` vs `scenes.yaml` duplicate membership → **RESOLVED**: scenes
   deleted (labels + scripts replace them).
4. `home_status` timestamp math → **#024 DONE**: lexicographic `HH:MM:SS`
   compare; `schedule` helper rejected (see
   `docs/archive/deep_dive_home_status.md`).
5. `group.family` uses `person.*` → correct, no change.
6. Labels unused (Christmas via `christmas_sockets` group) → **#028/#031 **DONE**:
   labels `sasong`/`taklampa`/`natthorn`/`utelampa`; groups deleted.
7. Trigger duplication / quoting → already good, no change.
8. Deprecated-style artifacts (`deprecated/` archive, logger debug levels) → fine.

### Deliberately not changed at snapshot time

- The `ha_started` gate *semantics* (2-min grace) — design decision, later
  replaced by native `binary_sensor.ha_ready` (2026-10-24).
- The four ceiling automations' readability over consolidation — later
  consolidated anyway (#026).
- No security/webhook issues (no webhooks, no remote access).