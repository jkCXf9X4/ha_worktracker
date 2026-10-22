# Hue → ZHA migration workbook

> **Status: COMPLETED 2026-10-21 — kept as reference only.** The device↔canonical
> entity-ID↔IEEE address map and reset recipes below remain useful for future
> re-pairing/replacement work. The migration itself is done; all rows are
> re-paired or confirmed purged.

The Philips Hue bridge (192.168.1.128) is malfunctioning/dead (`setup_retry`,
unreachable). Scope decision (2026-10-20): **move all Hue Zigbee devices onto
the HA-managed ZHA network (ConBee II)** and retire the Hue integration.

ZHA is already patched before migrating: 5 stale/dead devices purged (4×
`lumi.weather` offline 994d + `bokhylla_v` offline 541d), HA Core upgraded
2026.9.2 → 2026.10.2. A cosmetic `assert ieee in self.device_proxies`
startup-race error is a known upstream issue (present in both versions) and is
benign — ZHA loads, devices poll normally.

## Principle: entity IDs must be preserved

Config references (groups.yaml, automations/ceiling_lights.yaml) target the
current entity IDs (`light.entre_hall_tak`, `light.l3_1`, …). When a device
rejoins via ZHA it gets an auto-generated ID. The post-join step therefore
**renames each new ZHA entity to its canonical entity ID**, so `groups.yaml`
and the automations keep working unchanged.

The dead Hue entries must be removed from the entity registry first so the
canonical ID is free for the ZHA replacement.

## Migration map

| Physical device (Hue name) | Type / model | Canonical entity_id | Config usage |
|---|---|---|---|
| Entré hall tak | Hue ambiance lamp | `light.entre_hall_tak` | groups → ceiling_lamps | ✅ 2026-10-21 (IEEE `00:17:88:01:02:5d:20:78`) |
| Korridor tak | IKEA Dimmable light | `light.korridor_tak` | groups → ceiling_lamps |
| P7 | innr On/Off plug (window light, guest room) | `switch.laslampa_on_off` (was `light.laslampa_on_off`; innr registers as switch) | groups → ceiling_lamps (ref fix needed) | ✅ 2026-10-21 (IEEE `00:15:8d:00:01:fd:e8:60`) |
| L3_1 | Hue ambiance lamp ("Groventre tak") | `light.l3_1` | automations → ceiling_lights | ✅ 2026-10-21 (IEEE `00:17:88:01:02:5f:a1:d1`) |
| L3_2 | IKEA Color temp ("Carport ingång lampa") | `light.l3_2` | automations → ceiling_lights | ✅ 2026-10-21 (IEEE `8c:6f:b9:ff:fe:1e:fb:59`) |
| P6 | innr On/Off plug | `switch.p6` (was `light.p6`; innr SP 120 registers as switch) | groups → night_lamps (Isacs rum) | ✅ 2026-10-21 (IEEE `00:15:8d:00:01:fd:ec:ab`) |
| P8 | OSRAM On/Off plug (hunden) | `light.p8` → purged (never re-paired) | groups → night_lamps (ref removed) | ❌ physically disconnected — purged 2026-10-21 |
| P9 | OSRAM On/Off plug | `light.steamlink` → purged | — | ❌ physically disconnected — purged 2026-10-21 |
| P5 | innr On/Off plug (disabled) | `light.on_off_plug_1` → purged | — | ❌ physically disconnected — purged 2026-10-21 |
| L2 | IKEA Color temp ("Cristmas light 2") | `light.l2` → purged | — | ❌ physically disconnected — purged 2026-10-21 |
| L5 | IKEA Color temp | `light.color_temperature_light_1_3` → purged | — | ❌ physically disconnected — purged 2026-10-21 |
| Korridor 2 | IKEA Color temp | `light.color_temperature_light_1` | — | ✅ 2026-10-21 (IEEE `68:0a:e2:ff:fe:97:37:28`, E14 opal) |
| Dimmable light 1 | IKEA Dimmable | `light.dimmable_light_1` → purged | — | ❌ physically disconnected — purged 2026-10-21 |
| — (new) | IKEA TRETAKT Smart plug (Isacs play house) | `switch.isac_lekstuga` | — | ✅ 2026-10-21 (IEEE `14:2d:41:ff:fe:e7:3f:0b`, not from Hue bridge) |
| — (new) | IKEA STYRBAR dimmer (Isacs play house) | device "STYRBAR Isacs lekstuga" (buttons via `zha_event`) | — | ✅ 2026-10-21 (IEEE `34:10:f4:ff:fe:fd:43:2b`, not from Hue bridge) |
| — (new) | IKEA E27 WS globe, guest room **ceiling** (mesh router, added for coverage) | `light.gastrum_tak` | — | ✅ 2026-10-21 (IEEE `8c:6f:b9:ff:fe:1e:f9:36`, not from Hue bridge) |
| — (new) | IKEA E27 WS globe, Isacs room **ceiling** (previous "Isacs ceiling IKEA", now paired; mesh router) | `light.isac_tak` | — | ✅ 2026-10-21 (IEEE `8c:6f:b9:ff:fe:1e:fb:40`, not from Hue bridge) |
| — (new) | innr SP 120 plug, hobby room **window** | `switch.hobby_rum_fonster` | — | ✅ 2026-10-21 (IEEE `00:15:8d:00:01:fe:98:f0`, not from Hue bridge) |
| — (found) | IKEA E27 WW 806lm, outdoor main entrance — **was already on ZHA from baseline**, unnamed (flashing for identification) | `light.ute_huvudentre` | groups → night_lamps (stale ref now RESOLVED) | ✅ 2026-10-21 (IEEE `58:8e:81:ff:fe:07:1b:b6`) |
| Hue dimmer switch 1 | battery remote | (re-pair to ZHA, optional) | — | ✅ 2026-10-21 (IEEE `00:17:88:01:02:d4:f7:ba`, buttons via `zha_event`) |

### Virtual rooms (die with bridge, NOT re-paired)
`light.vardagsrum`, `light.hall`, `light.korridor`, `light.traningsrum`,
`light.kvallsbelysning`, `light.carport_korridor`, `light.gastrum`,
`light.other` — Hue *Room* grouping entities. Recreate as HA groups/scenes if
needed.
23 Hue scenes + 4 bridge automations (`switch.automation_vakna_*`,
`automation_somna`) also live on the bridge and will be dropped; the vakna/somna
behaviour is already superseded by the P4 YAML schedule helpers + automations.

## Procedure

1. Pre-flight (done): ZHA patched, stale devices purged, HA Core current.
2. Remove the dead `hue` config entry (`1001ec21…`) and its entities → frees
   canonical entity IDs.
3. Start ZHA permit-join (`zha.permit`, duration 254, re-run as needed).
4. For each device row above, physically reset at the wall while permit is open:
   - **Hue / IKEA bulbs**: power-cycle 6–10× with ~1s between toggles.
   - **innr / OSRAM plugs (P5–P9)**: hold the pairing button ~10s until it
     blinks fast.
   - **Hue dimmer switch**: hold the setup button ~10s until LED blinks.
5. Watch for the join (`zha/devices` count grows) → rename the new entity to
   the canonical entity_id + set friendly name → confirm state is live
   (`available`).
6. Verify `group.ceiling_lamps` / `group.night_lamps` / ceiling_lights
   automation members resolve to live entities.
7. Clean `groups.yaml` stale refs (done 2026-10-21): domain fixes
   (`light.laslampa_on_off`→`switch.laslampa_on_off`, `light.p6`→`switch.p6`),
   removed never-connected (`kontor_on_off`, `koket_on_off`, `light.p8`),
   removed purified dead (`bokhylla_v`).
   P8/P9/P5/L2/L5/Dimmable light 1 → **purged** (physically disconnected per
   owner; no config refs remain; entity_registry remnants can be raised later).
8. `ha core check` → restart core (reload groups) → restart exporter → commit.

## Completion criteria
- No `hue` config entry, no `platform: hue` entities left.
- All 14 physical row devices present on ZHA, live, with canonical entity IDs.
- groups.yaml + automations reference only live ZHA entities.