# Automationer

Automatiskt genererat av `tools/summarize.py` — **ändra aldrig den här filen för hand.** Kör om + committa på varje konfigurationsändring.

| Automation | När | Utför | Källa |
|------------|-----|-------|-------|
| Hue dimmer Isacs: dim down | fjärris (`dim_down`) | light.turn_on | `automations/hue_dimmer_isacs.yaml` |
| Hue dimmer Isacs: dim up | fjärris (`dim_up`) | light.turn_on | `automations/hue_dimmer_isacs.yaml` |
| Hue dimmer Isacs: off | fjärris (`turn_off`) | light.turn_off | `automations/hue_dimmer_isacs.yaml` |
| Hue dimmer Isacs: on | fjärris (`turn_on`) | light.turn_on | `automations/hue_dimmer_isacs.yaml` |
| P4: Ceiling lights off on away | sensor.home_status → away | homeassistant.turn_off | `automations/ceiling_lights.yaml` |
| P4: Ceiling lights off when awake & bright | sensor.home_status → awake · input_boolean.light_outside → on | homeassistant.turn_off | `automations/ceiling_lights.yaml` |
| P4: Ceiling lights on when awake & dark | sensor.home_status → awake · input_boolean.light_outside → off | homeassistant.turn_on | `automations/ceiling_lights.yaml` |
| P4: Ceiling off + night corner dim on sleep | sensor.home_status → sleep | homeassistant.turn_off, light.turn_on, light.turn_on | `automations/ceiling_lights.yaml` |
| P4: HA ready 1 min | HA-start | input_boolean.turn_on | `automations/00_startup_grace.yaml` |
| P4: HA ready 2 min | HA-start | input_boolean.turn_on | `automations/00_startup_grace.yaml` |
| P4: Isacs room morning fade-in | klockan (input_datetime.isac_on_time) | script.light_on_with_transition | `automations/isac_room.yaml` |
| P4: Lock doors on away | sensor.home_status → away | lock.lock, lock.lock | `automations/locks.yaml` |
| P4: Lock doors on sleep | sensor.home_status → sleep | lock.lock, lock.lock | `automations/locks.yaml` |
| P4: Night lamps off when bright | input_boolean.light_outside → on | homeassistant.turn_off | `automations/night_lights.yaml` |
| P4: Night lamps on when dark | input_boolean.light_outside → off | homeassistant.turn_on | `automations/night_lights.yaml` |
| P4: Outside daylight flag off | sensor.lumi_lumi_sen_ill_mgl01_8b21773c_illuminance under 150 | input_boolean.turn_off | `automations/outside_light.yaml` |
| P4: Outside daylight flag on | sensor.lumi_lumi_sen_ill_mgl01_8b21773c_illuminance över 400 | input_boolean.turn_on | `automations/outside_light.yaml` |
| P4: Sovrum morning fade-in | klockan (input_datetime.sovrum_on_time) · vardagar (mån–fre) | script.light_on_with_transition | `automations/sovrum.yaml` |
| P4: Sovrum off | klockan (input_datetime.sovrum_off_time) · vardagar (mån–fre) | light.turn_off | `automations/sovrum.yaml` |
| STYRBAR lekstuga: dim down | fjärris (`dim_down`) | switch.turn_off | `automations/styrbar_lekstuga.yaml` |
| STYRBAR lekstuga: dim up | fjärris (`dim_up`) | switch.turn_on | `automations/styrbar_lekstuga.yaml` |
| STYRBAR lekstuga: off | fjärris (`turn_off`) | switch.turn_off | `automations/styrbar_lekstuga.yaml` |
| STYRBAR lekstuga: on | fjärris (`turn_on`) | switch.turn_on | `automations/styrbar_lekstuga.yaml` |

## Läs mer

- `docs/PLAN.md` — hela bygget · `docs/ADMIN.md` — drift/återställning
- Familjen: ringa schemat i appen/chatten (agenten styr samma `input_*`).
