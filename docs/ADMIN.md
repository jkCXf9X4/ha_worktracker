# ADMIN — drift, återställning, backups

Operatörshandbok för familjens Home Assistant (HAOS VM på Proxmox,
`192.168.1.248`). Konfigurationen är versionshanterad i den privata GitHub-repon
`ha_config` (skrivs av Git Exporter). Det här dokumentet är "så hanterar du det
när något går sönder".

## Snabbkoll: är allt okej?

- Öppna `http://192.168.1.248:8123` (eller appen). Tas UI inte upp → gå till
  Proxmox och titta på VM-konsolen.
- `Settings → System → Logs` för fel. Vanligaste: ZHA "device left network" (en
  lampa som tappats bort, enstaka), integrationer på `unavailable` (strömavbrott /
  en plugg urdragen).

## De tre säkerhetskopieringslagren

| Lager | Mekanism | Vad det skyddar mot | Återställ syfte |
|-------|----------|---------------------|-----------------|
| 1. Config-as-code | Git Exporter → GitHub `ha_config` (privat, push ~30–60 min) | Allt du gör i UI/konfig, inkl. dashboards, automations, hjälpvariabler | Återställ *bara* konfigurationen; diffa/rolla tillbaka en ändring |
| 2. VM-snapshot | Proxmox `vzdump` (dagligen ×14, veckovis ×4, månadsvis ×2) | En trasig HAOS/OS-uppdatering, hel-VM-krascher | Återställ *hela VM:n* |
| 3. Kördata | HA:s egna backups (`.storage/`, DB, nycklar) + lager 2 | Det som *inte* får finnas i git: `.storage/`, `secrets.yaml`, databas | Återställ registret/enheter/nycklar utan att tappa enhetskopplingar |

Slutsats: **snapshotten (lager 2) är den enda fullständiga säkerheten.** Lägg den
till grund för allt "något är trasigt"-arbete. Git och HA-backups är snabbare,
sne skärs behoven av rätt återställningsgryta.

## Återställa konfiguration från git (lager 1)

Git Exporter är **push-only från `/config`** — ändringar görs på VM:n och
exporteras upp; repot är inte en skrivkanal ned i HA. För att backa en ändring
som redan landat i `/config`:

1. Kolla loggarna: `Settings → Add-ons → Git Exporter → Logs` (senaste commit).
2. Hämta föregående version av den fil du rullar tillbaka på VM:n:
   ```bash
   git -C /config log --oneline -5 -- <fil>
   git -C /config show <sha>:<fil> > /config/<fil>
   ```
3. `ha core check` (via SSH: `bash -lc "ha core check"`), starta om vid behov.
4. Nästa exportversionsläggning commitar tillbaka ändringen med en notis.

Secrets (API-nycklar, Yale-lösenord) ligger i `/config/secrets.yaml` som är
**exkluderad från git** — du kan inte få tillbaka en förlorad hemlighet från
repon. Det kommer enbart från lager 2/3 eller från leverantören (rotera nytt).

## Återställa/återställa VM från Proxmox (lager 2)

Crib-sheet: `proxmox/backups.md`.

- **Innan** en HAOS/OS-uppgradering: ta en manuell snapshot/vzdump och namnge den
  (`vm-<id>-before-<version>`). En uppgradering som misslyckas = en snapshot
  bort.
- Restore: Proxmox → VM → Backups → välj datum → Restore. VM:n måste vara av.
- Efter restore: kontrollera att Git Exportern startar om (den körs som add-on)
  och att `/config` är i rätt tillstånd. `ha core check`.

## Återställa från HA:s egna backups (lager 3)

`Settings → System → Backups`. Full- eller partial-backups tas automatiskt av
lager 2 men kan också göras här manuellt före en större förändring. Verklig
nytta: återställa enheterna/registret utan att tappa ZHA-parning eller
app-inloggningar — det ger *inte* tillbaka konfigurationen (den finns i lager 1).

## Vanliga åtgärder

- **HA omstart:** `bash -lc "ha core restart"` via SSH (eller UI: Settings →
  System → Restart). Efter restart väntar automationerna 1–2 min (startgrace)
  innan de aktiveras.
- **Readiness-givaren (`binary_sensor.ha_ready`)** beror på integrationen
  `uptime` (config entry i `.storage/`, skapas via UI/setup-flöde — finns inte
  i YAML). Friskar man upp `.storage/`/registret helt måste `uptime`
  återskapas, annars startar ingen automation. Görs det: installera "Uptime"
  via Settings → Devices & Services → Add integration och vänta på en reboot.
- **Validera konfig ändring:** `bash -lc "ha core check"` → eventuella fel
  refererar till fil+rad. Rättar du YAML: felen visas innan omstart.
- **App-enheter / närvaro:** 4 telefoner (Erik: LON-L29/Prinsen · Sara:
  iPhone/ApplePie). Närvaro = companion-appen, inte wifi-tracking.
- **Fjärrkontroller (ZHA):** Hue dimmer "Isac" och STYRBAR "lekstuga" binder
  via device-automations. Tappar en knapp sin binding → para om, se
  `.opencode/skills/home-assistant` (ZHA-sektionen).
- **Utelampans sensor** (Aqara) är batteridriven och har varit ur batteri sedan
  2026-10-19: byt batteri, enheten behålls.

## Skydd & hemligheter

- `secrets.yaml`, `.storage/`, SSH-nycklar, databas och loggar är **exkluderade
  från git**. Exporterns "secrets check" blockerar IP/MAC/lösenordsliknande
  rader från att nå GitHub som extra skyddsnät.
- Familjechat-agenten (OpenRouter) skickar enhetsnamn + tillstånd till en
  tredje part (OpenRouter/DeepSeek). Inga kameror finns; Yale-låsen kan bara
  LÅSAS, inte öppnas, via HA. Önskas full lokalt: byt modell till Ollama (en
  konfiguration).
- Rotera: Yale-pin/lösen och GitHub-PAT roterades 2026-10-22 efter en
  exponing i tidig build. Gör samma om du någonsin skriver ut en hemlighet.

## Fortlöpande underhåll

- Svara ärligt på "vad ändrades?" → Git Exporter-loggen / GitHub-historik.
- Kör `python3 tools/summarize.py` + commit vid varje konfig-ändring så
  `docs/SCHEDULES.md` / `docs/AUTOMATIONS.md` aldrig driver från verkligheten.
- Titta då och då i `WORKTRACK/NEXT.md` för öppna spår (#020 säsongsgrupper
  + förbättringskandidaterna #024–#029).