# Cleanup report — HA build (P3, staged)

Status: **executed** — P3 cleanup complete (2026-10-20/21) + P4 YAML go-live
(2026-10-21). Historical record; live state → `WORKTRACK/NEXT.md`.
Policy: report first, stage changes, **disable-not-delete**, sign-off on ambiguous
items, every step a separate commit (once versioned). All changes reversible via
the git history layer.

Live snapshot (token + registry + state API):
- Entities: **965** (424 enabled / 518 integration-disabled / 16 user-disabled / 7 device-disabled)
- Devices: **212**
- Live states: 436 (148 device_tracker = UniFi bloat)

---

## TV duplication — VERIFIED (P3-1)

| Entry | State | Verdict |
|-------|-------|---------|
| `samsungtv` "QE65Q8FAM" (`5d639020…`) | **not_loaded**, no devices/entities | **remove** (orphan) |
| `samsungtv` "Samsung 8 Series (65)…" (`899d236f…`) | **not_loaded**, no devices/entities | **remove** (orphan) |
| `dlna_dmr` "[TV] Samsung 8 Series (65)" (`fe24ffd3…`) | loaded → `media_player.tv_samsung_8_series_65` | **keep** (the live player) |
| `device_tracker.tv_samsung` | UniFi, MAC `64:1c:b0:8f:59:1f` (same TV) | keep |
| `update.samsungtv_tizen_update` (+ `switch…pre_release`) | HACS legacy device `SamsungTV Tizen` | keep until P4; then remove with legacy comp |

Finder: config entries show 3 TV entries; device registry has 2 `QE65Q8FAM` devices
(dlna + unifi) and 1 legacy hacs device; only dlna_dmr produces a media_player.

**Plan:** delete the 2 orphan `samsungtv` config entries (API `send_config_entry` /
storage edit + restart). No entities/devices attached, so nothing else changes.

---

## UniFi entity bloat (P3-2, backlog #002)

- 148 live `device_tracker` entities; 27 source=router, 3 gps; many `unifi_default_*`
  with raw-MAC names and `not_home` state (old/burnt clients).
- **P3-2 RESOLVED (2026-10-20):** UniFi integration **removed entirely** on owner
  decision. Live states dropped **433 → 250** (~183 UniFi entities gone: trackers,
  switches, sensors).
- **Presence now runs purely on mobile_app companion trackers** (GPS/SSID-based,
  zero MAC/IP/SSID config — self-registering phones):
  - `person.erik` → `device_tracker.huawii` (LON-L29, re-enabled) + `device_tracker.prinsen`
  - `person.sara` → `device_tracker.iphone_3` (iPhone) + `device_tracker.applepie`
  - 4 mobile_app trackers are the only device_trackers left.
- NO YAML/automation referenced UniFi entities (verified) → safe removal.
- UniFi still available for network monitoring by re-adding the integration (UI)
  if ever needed; presence stays independent.

---

## Disabled-but-never-purged entities (P3-3, backlog #003)

- 518 integration-disabled + 16 user-disabled + 7 device-disabled = **541**.
- Recorder was unconfigured (186 MB, stores everything forever).
- **P3-3 done:** `recorder: purge_keep_days: 30, commit_interval: 5` written to
  `/config/configuration.yaml` (`47e11f5`). Restart + first purge done 2026-10-20
  (events capped, states 30-day). Note: `exclude_missing_entities` is NOT a
  recorder option — retention is `purge_keep_days` (default `auto_purge` runs
  nightly). `purge_interval: 1` from `47e11f5` no longer in current config
  (`0d8ced8`).

---

## Legacy custom components (P3-4 / P4, backlog #004)

`doorman`, `script_engine`, `samsungtv_tizen` — none HACS-tracked. Hold until P4
YAML migration is verified over a full day/night; then archive + remove.

### HACS audit (2026-10-20)

| Component | Version | Source | Last activity | Verdict |
|-----------|---------|--------|---------------|---------|
| `doorman` (Yale lock) | 0.0.1 | fork of `espenfjo/homeassistant-doorman` | upstream 2019-08; fork 2021-09 | **dead** → replace |
| `script_engine` | 0.4.0 | `jkCXf9X4/hass_script_engine` (private) | 2023-12 | **dead** → migrate to native YAML (P4) |
| `samsungtv_tizen` | — | removed this session (P3-1) | — | ✅ removed |
| `nielsfaber/scheduler-component` | HACS | scheduler | 2026-03 (active) | ✅ keep |
| `nielsfaber/scheduler-card` | HACS | scheduler-card | active | ✅ keep |

**Doorman replacement candidates** (Yale lock):
- `jockesyk/homeassistant-yale-doorman-via-smarthub` — active (2025-11), 20★
- `hiall-fyi/yale_smart_alarm_ce` — new (2026-09), aligned with the newer Yale
  Smart Alarm Hub
- Note: current `doorman` is cloud-polling (`iot_class: cloud_polling`) and talks
  to Yale; replacement affects the 3 locks (`lock.back/main/carport`). Needs
  owner decision in P4 — verify Yale account/app access before switching.

---

## Config hygiene (P4, backlog #005, #007)

- `scripts.yaml` uses deprecated `data_template` (2 scripts).
- `logger` debug for `custom_components.script_engine` left on.

---

## Owner sign-offs (all resolved 2026-10-20/21)

1. ~~Remove 2 orphan samsungtv entries?~~ → **yes** — removed with all TV/media (clean slate).
2. ~~UniFi tracked-clients limit — which SSIDs/clients to keep?~~ → **n/a** — whole integration removed.
3. ~~Mobile app phones — which 4 are active~~ → **LON-L29/Prinsen (Erik), iPhone/ApplePie (Sara)** — the only trackers left.

---

## TV/media — REMOVED (executed 2026-10-20)

Full clean slate decision by owner: removed **all TV + media** integrations.

Removed:
- Config entries: 2× `samsungtv`, 1× `dlna_dmr`, 1× `spotify`, 1× `cast`
- Entities (registry): `media_player.tv_samsung_8_series_65`,
  `update.samsungtv_tizen_update`, `switch.samsungtv_tizen_pre_release`,
  `switch.wake_up_tv`, `device_tracker.tv_samsung`
- Devices: `ef961764` (Samsung QE65Q8FAM) removed
- `custom_components/samsungtv_tizen` (legacy component, full delete)
- `media_player: samsungtv_tizen` platform block in `configuration.yaml`
- `secrets.yaml`: removed `samsungtv_tizen_host` / `samsungtv_tizen_mac`

Result: no `media_player`, `cast`, `spotify`, `samsungtv`, `dlna` entities remain.
`ha core check` passes. Pushed to `ha_config` as `257e19c` (Git Exporter).

Leftover: HACS device `SamsungTV Tizen` (`2944bb5e`, no entities) — removal not
supported via device API; will be dropped when HACS refreshes or on next HACS
cleanup. HACS repo id `223541049` (`jaruba/ha-samsungtv-tizen`) still listed;
flag as "not installed" cleanup later.

## Change log (staged)

- 2026-10-20: report drafted from P2b live discovery. Next: execute P3-1 (TV).
- 2026-10-20: **P3-1 executed** — all TV/media removed, versioned `257e19c`.
- P3-2 executed: UniFi removed; presence on mobile_app companion trackers.
- P3-3 executed: recorder retention live.
- **P4 (2026-10-21)**: automation migration to **YAML** went live (owner decision
  2026-10-20; Pyscript prototyped then shelved). `script_engine` retired +
  archived under `config/deprecated/`; 14 automations + `input_*` helpers active,
  `ha core check` passes, day/night cycle verified. Hue→ZHA migration + naming
  pass completed the same session.