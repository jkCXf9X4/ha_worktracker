# Automationer

Automatiskt genererat av `tools/summarize.py` — **ändra aldrig den här filen för hand.** Kör om + committa på varje konfigurationsändring.

| Automation | När | Utför | Källa |
|------------|-----|-------|-------|
| Hue dimmer Isacs | — | — | `automations/hue_dimmer_isacs.yaml` |
| P4: Ceiling lights follow home status / daylight | ['sensor.home_status', 'input_boolean.light_outside'] → ['awake', 'sleep', 'away', 'on', 'off'] · binary_sensor.ha_ready → on | script.ceiling_lights_sync | `automations/ceiling_lights.yaml` |
| P4: Christmas sockets follow helper | input_boolean.christmas_lights ändras | script.uteljus_sync | `automations/night_lights.yaml` |
| P4: Isacs rum schema (fade-in) | — | — | `automations/room_schedules.yaml` |
| P4: Lock doors on sleep or away | sensor.home_status → ['sleep', 'away'] · binary_sensor.ha_ready → on | script.lock_doors | `automations/locks.yaml` |
| P4: Night lamps follow daylight | input_boolean.light_outside → ['on', 'off'] · binary_sensor.ha_ready → on | script.uteljus_sync | `automations/night_lights.yaml` |
| P4: Outside daylight flag | sensor.lumi_lumi_sen_ill_mgl01_8b21773c_illuminance över input_number.outside_light_on_threshold · sensor.lumi_lumi_sen_ill_mgl01_8b21773c_illuminance under input_number.outside_light_off_threshold · binary_sensor.ha_ready → on | script.outside_light_sync | `automations/outside_light.yaml` |
| P4: Sovrum schema (fade-in, vardagar) | — | — | `automations/room_schedules.yaml` |
| STYRBAR lekstuga | — | — | `automations/styrbar_lekstuga.yaml` |

## Läs mer

- `docs/PLAN.md` — hela bygget · `docs/ADMIN.md` — drift/återställning
- Familjen ändrar schemat själv i appen (dashboard). Värdena sparas och överlever omstart.
