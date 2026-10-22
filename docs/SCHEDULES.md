# Scheman

Automatiskt genererat av `tools/summarize.py` — **ändra aldrig den här filen för hand.** Kör om + committa på varje konfigurationsändring så att den aldrig driver från verkligheten.

## Schema-hjälpvariabler (input_*)

| Enhet | Beskrivning | Värde-id | Fil |
|-------|-------------|----------|-----|
| `input_datetime.wake_time_weekday` | Wake time Mon-Fri (tid) | 06:45 | `input_datetime/schedules.yaml` |
| `input_datetime.wake_time_weekend` | Wake time Sat-Sun (tid) | 06:45 | `input_datetime/schedules.yaml` |
| `input_datetime.bedtime_weekday` | Bedtime Sun-Thu (tid) | 21:00 | `input_datetime/schedules.yaml` |
| `input_datetime.bedtime_weekend` | Bedtime Fri-Sat (tid) | 21:30 | `input_datetime/schedules.yaml` |
| `input_datetime.sovrum_on_time` | Sovrum (bedroom) on workdays (tid) | 06:22 | `input_datetime/schedules.yaml` |
| `input_datetime.sovrum_off_time` | Sovrum (bedroom) off workdays (tid) | 09:36 | `input_datetime/schedules.yaml` |
| `input_datetime.isac_on_time` | Isacs room on (morning fade) time (tid) | 06:30 | `input_datetime/schedules.yaml` |
| `input_number.sovrum_brightness` | Sovrum (bedroom) brightness (siffra) | 200 | `input_number/schedules.yaml` |
| `input_number.isac_brightness` | Isacs room morning fade brightness (siffra) | 200 | `input_number/schedules.yaml` |
| `input_number.night_corner_brightness` | Night corner dim brightness (siffra) | 56 | `input_number/schedules.yaml` |
| `input_number.outside_light_on_threshold` | Outside light on above (lux) (siffra) | 400 | `input_number/schedules.yaml` |
| `input_number.outside_light_off_threshold` | Outside light off below (lux) (siffra) | 150 | `input_number/schedules.yaml` |

## Tidstyrda automations

| Automation | När | Gör |
|------------|-----|-----|
| P4: Isacs room morning fade-in | klockan (input_datetime.isac_on_time) | script.light_on_with_transition |
| P4: Sovrum morning fade-in | klockan (input_datetime.sovrum_on_time) · vardagar (mån–fre) | script.light_on_with_transition |
| P4: Sovrum off | klockan (input_datetime.sovrum_off_time) · vardagar (mån–fre) | light.turn_off |
