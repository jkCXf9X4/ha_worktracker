# Light identification — fishing log (2026-10-23)

> **Status: COMPLETED — archived reference.** Used to seed the device→area map
> (now live in the skill + the area registry on the VM). Kept as the one-time
> physical-identification record; nothing here is pending.

# Confirmed by physically watching each blink. **APPLIED to the VM 2026-10-23**
# (device->area assignments live; exporter `643e941`; `ha core check` green).
# Used to seed the device->area map in docs/archive/deep_dive_organization.md.

| Entity | Friendly | Physical location (confirmed) | Area |
|--------|----------|-------------------------------|------|
| light.l3_1 | Groventre tak | Kök korridor, by the bedroom | Kök korridor |
| light.l3_2 | Carport ingång lampa | Kök korridor, by the carport entrance | Kök korridor |
| light.korridor_tak | Korridor tak | Badrum korridor, by the kitchen | Badrum korridor |
| light.color_temperature_light_1 | Korridor 2 | Badrum korridor, by the carport entrance | Badrum korridor |
| light.entre_hall_tak | Entré hall tak | Entré hall | Entré hall |
| light.gastrum_tak | Gästrum tak | Gästrum, ceiling | Gästrum |
| light.dimmer_fixed_livingroom_light | Vardagsrum väggdimmer | Vardagsrum, ceiling | Vardagsrum |
| light.dimmer_fixed_bedroom_light_2 | Sovrum väggdimmer | Sovrum, ceiling | Sovrum |
| light.bokhylla_h_light | Bokhylla höger | Vardagsrum, bookshelf | Vardagsrum |
| light.ute_huvudentre | Ute huvudentré | Outdoor, main entrance | Utebelysning |
| switch.laslampa_on_off | Gästrum fönster | Gästrum, window lamp | Gästrum |
| switch.hobby_rum_fonster | Hobbyrum fönster | Hobbyrum, window lamp | Hobbyrum |
| switch.isac_lekstuga | Isacs lekstuga | Vardagsrum, Isacs playhouse | Vardagsrum |
| switch.p10_socket | Slinga uterum | Uterum, outdoor pergola light | Uterum |

> Skip Isac's room lights entirely (Isac asleep) — `light.isac_tak`, Isacs
> sänglampa (p6). Do not flash those.

> Tuya plugs `p1`/`p2`/`p4`/`p11` were `unavailable` during the session (Tuya
> cloud offline) — not strobed. **P4 plug broke and was physically replaced by
> the P11 plug** (2026-10-23): `switch.p4_socket` is gone from the registry and
> `switch.p11_socket` took over its role as the front outdoor light following the
> daylight machine. Applied: `night_lamps` uses `p11`; `christmas_sockets` now
> `p10`/`p1`/`p6`. `p2` Uttag P2 → Kök, `p1` Hörnlampa → Vardagsrum.
> Re-strobe the Tuya plugs when back online if confirmation wanted.

## Applied area registry (2026-10-23) — 11 areas after consolidation

`Entré hall`, `Kök korridor`, `Badrum korridor`, `Vardagsrum` (incl. lekstuga),
`Sovrum`, `Isacs rum`, `Gästrum`, `Hobbyrum` (new), `Kök` (empty room),
`Uterum`, `Utebelysning`. Deleted legacy: `CarPort`, `Other`, `Träningsrum`,
`Ute framsida` (→ Utebelysning), `Kvällsbelysning` (dissolved).
`Uteljussensor` = house-wide, no room.

## Dashboard rebuilt 2026-10-23 — area cards

Belysning view = control groups + 9 compact area cards; Utomhus = Utebelysning +
Uterum + Säsongsbelysning; 11 area icons set in the registry. Applied via WS
`lovelace/config/save`; exporter `9defb98`. Diagnostic entities excluded per
area (`update.*`, power sensors, child-locks, remote battery).