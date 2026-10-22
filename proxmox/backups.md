# Proxmox — HAOS VM backups (crib sheet)

Konfig-nytt — körs av **ägaren på Proxmox-hosten**, inte av byggagenten. Det här
dokumentet finns för att backuperna faktiskt görs och är återställningsbara.

## Var ligger HA-VM:n

- Hitta VM-ID: `qm list` (leta efter `homeassistant` i namnet) eller `pct list`
  om det är en container i stället. Antag `VMID` nedan = ditt värde.
- De flesta kommandon kräver root på Proxmox-noden (`ssh root@pve` eller
  webbkonsolen).

## En gång: sätt upp vzdump med retention

Gör det i webb-UI (`Datacenter → Backups → Add`) eller via CLI. Rekommendation:

- Datastore: `backup` (eller din backup-store).
- Mode: **Snapshot** (kräver LVM-thin/zfs; ingen VM-downtime).
- Schedule: dagligen.
- Retention: `keep-daily=14, keep-weekly=4, keep-monthly=2`.

Med CLI motsvarar det ungefär:

```bash
vzdump {VMID} --mode snapshot --storage backup --compress zstd \
  --mailnotification failure \
  --prune-backups keep-daily=14,keep-weekly=4,keep-monthly=2
```

Detaljer om varje VM:s eget jobb: `VM → Backup → Add` i webb-UI.

## Innan HAOS/OS-uppgradering

Ta alltid en manuell snapshot direkt före, namngiven så du hittar "tillbaka":

```bash
vzdump {VMID} --mode snapshot --storage backup --compress zstd \
  --notes-template "before HAOS upgrade $(date +%F-%H%M)"
# alternativt via webb-UI: VM → Backup → Backup now
```

Om uppgraderingen misslyckas: `VM → Backups → välj denna → Restore`.

## Återställa en VM från backup

1. Stäng av VM:n (om på): `qm stop {VMID}`.
2. `VM → Backups → välj backup → Restore`.
3. Starta: `qm start {VMID}`.
4. Kontrollera HA: Git Exporter och alla add-ons startar, `ha core check`.
5. Är `/config` inaktuellt i backupen: backa konfig från GitHub (se
   `docs/ADMIN.md` → "Återställa konfiguration från git").

## Vanliga fel

- **"No space left"** → backup-storen full; skärp retention eller byt store.
- **"Can't make snapshot"** → diskarna är inte LVM-thin/zfs; använd `--mode suspend`
  (kort stopp) eller `--mode stop`.
- **Enda lokala backup** → försvinner med noden. Helst: delad storage (NFS) eller
  kopiera nyckelbackups manuellt till annan maskin.

## Verifiera att allt faktiskt backas

- `pvesm status` → store synlig.
- `VM → Backups` → jobben listade.
- Testrestore en VM till en klon (rename) en gång per kvartal — en backup som
  aldrig provats är en backup du inte har.