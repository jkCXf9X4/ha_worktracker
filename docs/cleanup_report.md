# Cleanup report — HA build (P3, staged)

Status: **draft** — baseline + findings from P2b live discovery (2026-10-20).
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
- UniFi options storage is empty (`unifi_data` has no `track_clients` tuning) →
  integration default tracks everything.
- **Recommend:** limit tracked clients via UniFi integration options
  (`track_clients` + `ssid_filter` for the two family AP SSIDs), then
  clean stale `device_tracker.unifi_default_*` entities from the registry.
- Needs owner sign-off: which devices are still in use (see "at-home" list below).

At-home trackers (13, live): prinsen, tv_samsung, unifi_default_6c:1f…, unifi,
yale, home_assistent, iphone_hemma, unifi_default_50:eb…, pixel_6_2, usw_flex_mini,
pro_ap, long_range_sovrum, usg_3p — mostly infra + 2 phones.

---

## Disabled-but-never-purged entities (P3-3, backlog #003)

- 518 integration-disabled + 16 user-disabled + 7 device-disabled = **541**.
- Recorder not configured (`purge_keep_days` unset) → DB 186 MB kept forever.
- **Plan:** add `recorder: exclude_missing_entities: [30]` + `purge_keep_days: 30`;
  run a recorder purge; then clean registry entries that never resolve.

---

## Legacy custom components (P3-4 / P4, backlog #004)

`doorman`, `script_engine`, `samsungtv_tizen` — none HACS-tracked. Hold until P4
YAML migration is verified over a full day/night; then archive + remove.

---

## Config hygiene (P4, backlog #005, #007)

- `scripts.yaml` uses deprecated `data_template` (2 scripts).
- `logger` debug for `custom_components.script_engine` left on.

---

## Open items needing owner sign-off

1. **Remove 2 orphan samsungtv entries?** (recommended yes, no visible downside)
2. **UniFi tracked-clients limit** — which SSIDs/clients to keep? (family wifi vs IoT)
3. **Mobile app phones** — LON-L29, iPhone, Prinsen, ApplePie: which 4 are active

---

## Change log (staged)

- 2026-10-20: report drafted from P2b live discovery. Next: execute P3-1 (TV).