# Automationer

Automatiskt genererat av `tools/summarize.py` — **ändra aldrig den här filen för hand.** Kör om + committa på varje konfigurationsändring.

| Automation | När | Utför | Källa |
|------------|-----|-------|-------|
| Gästrum: plugg följer dim | light.gastrum_tak ändras · light.gastrum_tak → off | script.plug_follow_room_dim | `automations/plug_dim.yaml` |
| Hue dimmer Isacs | — | — | `automations/hue_dimmer_isacs.yaml` |
| P4: Ceiling lights follow home status / daylight | ['sensor.home_status', 'binary_sensor.light_outside'] → ['awake', 'sleep', 'away', 'on', 'off'] | script.ceiling_lights_sync | `automations/ceiling_lights.yaml` |
| P4: Christmas sockets follow helper | input_boolean.christmas_lights ändras | script.uteljus_sync | `automations/night_lights.yaml` |
| P4: Isacs rum schema (fade-in) | — | — | `automations/room_schedules.yaml` |
| P4: Lock doors on sleep or away | sensor.home_status → ['sleep', 'away'] | script.lock_by_status | `automations/locks.yaml` |
| P4: Night lamps follow daylight | binary_sensor.light_outside → ['on', 'off'] | script.uteljus_sync | `automations/night_lights.yaml` |
| P4: Reconcile lights/locks after boot | binary_sensor.ha_ready → on | script.reconcile_all | `automations/boot_reconcile.yaml` |
| P4: Sovrum schema (fade-in, vardagar) | — | — | `automations/room_schedules.yaml` |
| STYRBAR lekstuga | — | — | `automations/styrbar_lekstuga.yaml` |

## Läs mer

- `docs/PLAN.md` — hela bygget · `docs/ADMIN.md` — drift/återställning
- Familjen ändrar schemat själv i appen (dashboard). Värdena sparas och överlever omstart.
