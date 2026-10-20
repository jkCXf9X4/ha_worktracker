---
name: home-assistant
description: Living operational knowledge base for the rosenlund home Home Assistant setup (HAOS VM at 192.168.1.248, /config, script_engine custom automations, Git Exporter versioning, UniFi/ZHA/Hue/Tuya/Tibber). Use whenever connecting to this HA instance, reading or editing its config/entities/automations/schedules, or working on the versioning + cleanup + migration build. Append new learnings here as they are discovered.
---

# Home Assistant — operational knowledge

This is a living reference, maintained while working on the build. Good places
for deeper context: `docs/PLAN.md`, `docs/inventory.md`,
`docs/automation_requirements.md` (kept in the HA config at `/config/docs/*` and
mirrored to the GitHub repo).

## Accessing the instance

- **SSH & Web Terminal add-on** at `192.168.1.248:2222`, user **`root`**
  (add-on maps `/config` read-write and provides a root shell).
- Password is supplied by the owner during a session — do **not** persist it in
  this repo or in any committed file.
- Working connect command:

  ```bash
  sshpass -p "$HA_PASS" ssh -p 2222 -o StrictHostKeyChecking=accept-new \
    -o PreferredAuthentications=password -o PubkeyAuthentication=no root@192.168.1.248 '<cmd>'
  ```

### Critical shell quirks
- The **`ha` CLI (supervisor)** only works inside a **login shell**: wrap with
  `bash -lc "ha ..."`. A plain non-login command fails with
  `unauthorized: missing or invalid API token`.
- **Never pass `-t`/`-tt` when piping a script via stdin** (`ssh ... 'python3 -' < f.py`) —
  a TTY turns it into an interactive REPL and hangs. Use *plain* ssh (no `-t`);
  reserve `-tt` + `bash -lc "..."` for `ha` commands.
- **SFTP/scp is disabled** (`subsystem request failed`). Transfer files with
  tar-over-ssh:
  ```bash
  # pull:  ssh ... 'tar -C /config -cf - .storage' > dump.tar
  # push:  tar -C src -cf - . | ssh ... 'tar -C /config -xf -'
  ```

### Standalone commands
- `ha apps info 68413af6_git-exporter` — exporter options (includes plaintext PAT; don't print).
- `ha core check` — validate config (watch for secrets/IP/MAC complaints).
- `ha core restart`, `ha apps restart 68413af6_git-exporter`, `ha apps logs 68413af6_git-exporter`.
- `ha addons` is deprecated → use `ha apps`.

## Environment facts

- VM: **HAOS 18.2** on Proxmox. **HA Core 2026.9.2**. `/config` → symlink to `/homeassistant`.
- SSH container: **Alpine 3.24** (has `python3` + `yaml`, git, etc.).
- Install add-ons present: Advanced SSH & Web Terminal (`a0d7b954_ssh`), Samba
  share (`core_samba`), File editor (`core_configurator`), Home Assistant Git
  Exporter (`68413af6_git-exporter`).
- `/config/custom_components/`: `doorman`, `hacs`, `samsungtv_tizen`,
  `scheduler`, `script_engine` (scheduler + scheduler-card are HACS-tracked;
  the other three are legacy hand-installed).

## Versioning / Git Exporter

- **Git Exporter** mirrors `/config` → private GitHub repo `ha_config`
  (branch `main`, `pull_before_push: true`, interval-based).
- Exporter places exported config under **`config/`** in the repo.
- **Keep excluded** (set in add-on, matches `.gitignore`): `.storage/`,
  `secrets.yaml`, `.ssh/`, `.cloud/`, `*.db*`, `*.log*`, `__pycache__`, `tts/`, `deps/`.
- The exporter's **secrets check blocks commits** on IP/MAC/`password:`-type
  lines (patterns shown in logs). Move such values into `secrets.yaml` (excluded
  → not pushed) and reference with `!secret key`.
- **Git Exporter is PUSH-ONLY from `/config`** — verified 2026-10-20. Even with
  `pull_before_push: true`, remote commits are only fetched to avoid merge
  conflicts; they are **NOT** applied to `/config`. A commit pushed straight to
  the GitHub repo was silently reverted on the next export. **All config edits
  must go on the VM** (`/config/...` over SSH), then the exporter versions them.
- Config change loop:
  1. edit files under `/config` over SSH,
  2. `ha core check`,
  3. `ha apps restart 68413af6_git-exporter`,
  4. inspect `ha apps logs 68413af6_git-exporter` for "Exporter finished".
- Because `pull_before_push` is on, commits made directly to the GitHub repo
  also land in `/config` on the next export run.

## Home topology (key entities)

- Groups (YAML): `group.family` = person.sara + person.erik; `group.ceiling_lamps`
  (− entre_hall_tak, korridor_tak, laslampa_on_off, bokhylla_h/v); `group.night_lamps`
  (− ute_huvudentre, kontor_on_off, koket_on_off, p8, + seasonal sockets p10/p11/p1/p4, p6).
- Locks (Yale via `doorman`): `lock.back`, `lock.main`, `lock.carport`.
- Outside-light sensor (ZHA/Aqara): `sensor.lumi_lumi_sen_ill_mgl01_8b21773c_illuminance`.
- Bedroom dimmer (ZHA): `light.dimmer_fixed_bedroom_light_2`; night-corner Hue: `light.l3_1`/`light.l3_2`.
- Integrations: hue, zha (ConBee II), samsungtv (+ dlna_dmr, likely duplicate TV
  entries), spotify, tibber, tuya (sockets p1–p11), unifi (~484 entities, main
  stale-device source), met, cast, mobile_app x4 phones.
- Registry scale: ~958 entities, 211 devices, 535 disabled-but-not-purged.

## Automations ("script_engine")

All automation logic ran in custom Python `custom_components/script_engine` +
`/config/script_engine/*.py`. Responsibilities and the YAML/`input_*`
migration design live in `docs/automation_requirements.md`. Summary:

- Home-status machine `awake/sleep/away` (hard-coded wake 06:45, bedtime 21:00
  Sun–Thu / 21:30 Fri–Sat) — target of the schedule-helper refactor.
- Locks on sleep/away; outside-light lux hysteresis (400 on / 150 off);
  ceiling + night lamps; Sovrum bedroom schedule 06:22–09:36 (Scheduler addon).
- Decorator semantics: `ToState` = edge-triggered state-change condition;
  `Delay(minutes)` = startup grace + time-window (not a debounce).

## Gotchas / lessons learned

- **`secrets.yaml` hygiene**: the file had no trailing newline, so appending with
  `echo >> ` glued lines together into invalid YAML and corrupted the Yale
  password. Always validate with `python3 -c "import yaml; yaml.safe_load(open(...))"`.
  Prefer rewriting the file atomically over `sed` on it.
- **Never output `secrets.yaml`, the add-on PAT, or `ha apps info ... options`**
  (it prints the PAT verbatim). Redact anything sensitive from tool output.
- Watch for stray duplicate is in config: legacy `samsungtv_tizen` platform vs
  the built-in `samsungtv` config entries produce duplicated TV entities; the
  legacy platform keeps an IP+MAC in `configuration.yaml` (already moved to
  secrets).
- `configuration.yaml` is ancient style (deprecated `data_template`, bare
  `sensor:`/`script:` platform includes). Normalization is part of the build.
- Editing a file that a running instance depends on (configuration.yaml,
  secrets.yaml) — changes apply on next restart/core reload only; existing
  in-memory config keeps working meanwhile.

## How to grow this skill

As you discover new facts, gotchas, or command patterns, append them under the
matching section (or add a section). Keep it concise and durable — entity
facts, working commands, and warnings; not one-off transcripts. Secrets never
belong here.