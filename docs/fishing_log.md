# Light identification — fishing log (2026-10-23)
# Confirmed by physically watching each blink. Read-only; used to seed the
# device->area map in docs/deep_dive_organization.md.

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
> cloud offline) — not strobed. Owner placements from earlier context:
> `p4` Bilvärmare → Utebelysning, `p11` Julslinga → Utebelysning (outdoor),
> `p2` → Kök (proposed), `p1` Hörnlampa → Vardagsrum (already in registry).
> Re-strobe when Tuya is back online if needed.