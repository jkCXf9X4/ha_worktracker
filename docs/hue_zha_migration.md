# Hue → ZHA migration workbook

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
| Entré hall tak | Hue ambiance lamp | `light.entre_hall_tak` | groups → ceiling_lamps |
| Korridor tak | IKEA Dimmable light | `light.korridor_tak` | groups → ceiling_lamps |
| P7 | innr On/Off plug | `light.laslampa_on_off` ("Läslampa") | groups → ceiling_lamps |
| L3_1 | Hue ambiance lamp ("Groventre tak") | `light.l3_1` | automations → ceiling_lights |
| L3_2 | IKEA Color temp ("Carport ingång lampa") | `light.l3_2` | automations → ceiling_lights |
| P6 | innr On/Off plug | `light.p6` | groups → night_lamps (Isacs rum) |
| P8 | OSRAM On/Off plug | `light.p8` | groups → night_lamps (hunden) |
| P9 | OSRAM On/Off plug | `light.steamlink` | — |
| P5 | innr On/Off plug (disabled) | `light.on_off_plug_1` | — |
| L2 | IKEA Color temp ("Cristmas light 2") | `light.l2` | — |
| Korridor 2 | IKEA Color temp | `light.color_temperature_light_1` | — |
| L5 | IKEA Color temp | `light.color_temperature_light_1_3` | — |
| Dimmable light 1 | IKEA Dimmable | `light.dimmable_light_1` | — |
| Hue dimmer switch 1 | battery remote | (re-pair to ZHA, optional) | — |

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
7. Clean `groups.yaml` stale refs (`ute_huvudentre`, `kontor_on_off`,
   `koket_on_off` — never existed; `bokhylla_v` — purged dead).
8. `ha core check` → restart exporter → commit.

## Completion criteria
- No `hue` config entry, no `platform: hue` entities left.
- All 14 physical row devices present on ZHA, live, with canonical entity IDs.
- groups.yaml + automations reference only live ZHA entities.