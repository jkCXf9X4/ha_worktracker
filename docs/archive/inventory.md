# Inventory — Home Assistant build snapshot

Captured: 2026-10-20 over SSH (SSH & Web Terminal add-on) + `.storage` dump.
HA Core: **2026.9.2** running as HAOS VM on Proxmox (`/config` → `/homeassistant`).

This is the "before" picture used as baseline for the cleanup. **Do not overwrite.**

---

## Integrations / config entries

| Domain | Title / note |
|--------|--------------|
| met | "Home" weather (met.no) |
| mobile_app | LON-L29, iPhone, Prinsen, ApplePie (4 phones) |
| hue | Philips Hue bridge |
| zha | ConBee II (dresden elektronik) — Zigbee coordinator |
| samsungtv | QE65Q8FAM — **duplicate entry** ("QE65Q8FAM" + "Samsung 8 Series (65)…") |
| dlna_dmr | [TV] Samsung 8 Series (65) — second TV entry, likely same TV |
| spotify | Spotify |
| tibber | Energy (Erik Rosenlund) |
| tuya | Account used to be `erik.rosenlund.private@gmail.com` — may hold the smart sockets |
| cast | Google Cast |
| unifi | "Default" UniFi controller — **484 registered entities** |
| sun / backup / analytics / hacs / scheduler | system |

Suspicion: TV appears 2–3× (samsungtv ×2, dlna_dmr ×1). One is stale/duplicate.

---

## Entity registry

- **Total entities: 958** (535 disabled, 0 hidden)
- Top domains:
  - `unifi`: 484 (network clients/devices — old phones & IoT = main decay source)
  - `mobile_app`: 195
  - `zha`: 90 (Zigbee over ConBee II)
  - `hue`: 68
  - `hassio`: 40 (supervisor/add-on entities)
  - `tibber`: 27
  - `tuya`: 16
  - others: sun, hacs, script, person, switch, wake_on_lan, input_boolean, met, dlna_dmr, scheduler, backup, updater
- **Devices: 211** total (hue 23, hassio 7, zha 6, deconz 5, hacs 5, tuya 5, mobile_app 4, unifi 4, …)

### Notable entities found
- `input_boolean.vacation` — "Vacation" toggle (the only input_boolean)
- `switch.schedule_sovrum` — Scheduler switch "Sovrum" (bedroom schedule)
- Lights with Swedish names: `light.entre_hall_tak`, `light.korridor_tak`, `light.laslampa_on_off`, `light.vardagsrum`, `light.traningsrum`, `light.kvallsbelysning`, `light.carport_korridor`, `light.gastrum`, `light.sovrum`…, several `light.pX` / `light.lX` / `light.lX_Y` (poorly named Hue/IKEA lights)
- Unifi "Blocked" switches: `switch.pixel_6`, `switch.iphone`, `switch.iphone_hemma`; `switch.home_automation`, `switch.rosor`, `switch.rosor_5g`, `switch.smart_home_wifi`
- Add-on entities present but disabled: advanced_ssh_web_terminal, samba_share, file_editor, usw_flex_mini ports, usg_3p wan/lan, pro_ap ports/LEDs

---

## HACS

Installed custom components (in `/config/custom_components`):

| Repo / local dir | Verdict |
|------------------|---------|
| `hacs` | HACS itself |
| `nielsfaber/scheduler-component` (HACS) | custom Scheduler integration |
| `nielsfaber/scheduler-card` (HACS) | Scheduler card (frontend) |
| `doorman` (local, no HACS) | Yale door lock platform — **old, unknown maintenance** |
| `script_engine` (local, no HACS) | custom script engine — **old, debug-log level active** |
| `samsungtv_tizen` (local, no HACS) | legacy Samsung TV platform — **old; superseded by built-in `samsungtv`** (already present as config entry) |

All three local-only components are legacy hand-installed code, none of them HACS-tracked.

---

## YAML config (classic, mostly untouched)

- `configuration.yaml`: logger (debug for `script_engine`), `history:`, `lock:` via `doorman` platform, `media_player` via legacy `samsungtv_tizen`, `group: !include`, `automation: !include automations.yaml`, `script: !include scripts.yaml`, `sensor: time_date`
- **`automations.yaml` is `[]`** — no YAML automations (everything is UI/`.storage`-driven)
- `scripts.yaml`: 2 scripts using **deprecated `data_template`** (`light_on_with_transition`, `force_light_on_transition`)
- `groups.yaml`: present (small)
- `secrets.yaml`: exists (held out of git)

---

## Schedules (Scheduler integration — `scheduler.storage`)

1. **Sovrum** (bedroom) — `enabled`
   - Weekdays: `06:22:00 → 09:36:00` → `script.light_on_with_transition` on `light.dimmer_fixed_bedroom_light_2` (brightness 200, transition 1200 s)
   - `09:36:00 → 00:00:00` → `light.turn_off` same light

The Scheduler integration is the *current* schedule mechanism. It is UI-based; for versioned / family-chat / textual scheduling we will migrate to YAML-defined `input_datetime` helpers in a later phase.

---

## Observations / smells

- 535 entities already disabled but never purged (registry bloat, DB bloat).
- UniFi integration registers ~484 entities (ports, clients, LEDs); many are noise/unused.
- Duplicate/ghost TV device entries.
- Legacy local custom components (`doorman`, `script_engine`, `samsungtv_tizen`) with no update discipline.
- Deprecated `data_template` in scripts.
- Debug logging left on for `script_engine`.
- 186 MB database; `recorder` not configured → stores everything forever.
- Long-lived token: **not yet provided** (limits live-state/API discovery).

---

## Next steps (tracked in PLAN.md)

- P1: private GitHub repo + Git Exporter add-on (needs user: repo + PAT + install).
- P2 continued: live-entity state check (needs long-lived token) + add-on list (UI).
- P3: cleanup per categories above, staged + versioned.