# Light identification — fishing log (2026-10-23)
# Confirmed by physically watching each blink. **APPLIED to the VM 2026-10-23**
# (device->area assignments live; exporter `643e941`; `ha core check` green).
# Used to seed the device->area map in docs/deep_dive_organization.md.

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
> cloud offline) — not strobed. Assignments applied per owner context:
> `p4` Bilvärmare → Utebelysning (outdoor, front), `p11` Julslinga →
> Utebelysning, `p2` Uttag P2 → Kök, `p1` Hörnlampa → Vardagsrum.
> Re-strobe when Tuya is back online if confirmation wanted.

## Applied area registry (2026-10-23) — 11 areas after consolidation

`Entré hall`, `Kök korridor`, `Badrum korridor`, `Vardagsrum` (incl. lekstuga),
`Sovrum`, `Isacs rum`, `Gästrum`, `Hobbyrum` (new), `Kök` (empty room),
`Uterum`, `Utebelysning`. Deleted legacy: `CarPort`, `Other`, `Träningsrum`,
`Ute framsida` (→ Utebelysning), `Kvällsbelysning` (dissolved).
`Uteljussensor` = house-wide, no room.