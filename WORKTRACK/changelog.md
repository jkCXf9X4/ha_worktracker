# Changelog

Chronological log of changes and decisions. Newest at the bottom.

## 2026-10-20 — P3-1: TV/media removed (clean slate)

- **Owner decision**: remove all TV + media for a clean slate.
- Deleted config entries: 2× `samsungtv`, `dlna_dmr`, `spotify`, `cast` (REST API).
- Removed entities (websocket registry): `media_player.tv_samsung_8_series_65`,
  `update.samsungtv_tizen_update`, `switch.samsungtv_tizen_pre_release`,
  `switch.wake_up_tv`, `device_tracker.tv_samsung`.
- Removed device `Samsung QE65Q8FAM`; deleted `custom_components/samsungtv_tizen/`
  (legacy, 1600+ lines); stripped `media_player: samsungtv_tizen` block from
  `configuration.yaml`; removed orphaned `samsungtv_tizen_host/mac` secrets.
- `ha core check` passes; exporter pushed `65acd1f..257e19c main`.
- Remaining: HACS device `SamsungTV Tizen` + repo id `223541049` flagged for later
  HACS cleanup (device API can't remove it).
- Tool lesson: HA websocket commands need **incrementing message `id`** per call
  (`id_reuse` error otherwise); used `uv` + `websockets` for registry removal.

## 2026-10-20 — P2b live discovery + cleanup report

- **SSH key auth** — added this machine's `id_ed25519` pubkey to the SSH & Web
  Terminal add-on `authorized_keys`; root SSH now works without a password
  (verified 192.168.1.248:2222). Multiple keys on the add-on; machine key now one.
- **P2b — long-lived token provisioned** (read-only discovery). Live API
  snapshot: **436 states**, 148 of them `device_tracker` (UniFi bloat).
- **TV duplication VERIFIED (P3-1)** — 2 `samsungtv` config entries
  (`QE65Q8FAM` `5d639020…`, `Samsung 8 Series…` `899d236f…`) are `not_loaded`
  orphans (no devices, no entities). `dlna_dmr`
  (`media_player.tv_samsung_8_series_65`) is the one live player.
  `device_tracker.tv_samsung` (UniFi, MAC `64:1c:b0:8f:59:1f`) = same TV, keep.
- **P2b — registry refresh** — 965 entities (424 enabled / 541 disabled), 212
  devices; `disabled_by`: integration 518 / user 16 / device 7.
- **UniFi bloat quantified (P3-2)** — integration options empty (defaults track
  everything); many raw-MAC `unifi_default_*` trackers.
- **`docs/cleanup_report.md` drafted** — TV plan + UniFi + recorder + open
  sign-off items. Tracker updated (P2b done, P3 in progress).

## 2026-10-20 — Bootstrap session

- **P0 access** — Installed/configured Advanced SSH & Web Terminal add-on.
  Switched add-on shell user to `root` (intended root shell) for full write
  access to `/config` and working `ha` CLI. Discovered: `ha` only works inside
  a login shell (`bash -lc`); SFTP/scp disabled (use tar-over-SSH); never pipe
  scripts via a `-t` SSH session.
- **Inventory (P2a)** — Dumped `.storage` + config over SSH; wrote
  `docs/inventory.md`. Key facts: 958 entities / 211 devices / 535 disabled;
  UniFi dominates; TV likely duplicated; Scheduler holds the "Sovrum" schedule.
- **Automation discovery** — Read the full custom `script_engine` framework +
  scripts; extracted requirements + YAML migration design in
  `docs/automation_requirements.md`.
- **P1 versioning — live** — Git Exporter add-on installed; repo
  `ha_config` on GitHub (private, branch `main`). Excludes configured
  (`.storage/`, `secrets.yaml`, `.ssh/`, DBs, logs). First push blocked by the
  exporter’s secrets check on the legacy Samsung TV IP/MAC → moved values to
  `secrets.yaml` (`!secret`). `ha core check` passes. Push confirmed
  (`f56af23..65acd1f main`).
- **secrets.yaml incident** — file had no trailing newline; an `echo >>` append
  glued lines into invalid YAML and corrupted the Yale password; an earlier
  `sed` patch inserted stray `x27` text. Repaired by atomic rewrite; validated
  with `python3 + yaml`.
- **Security flags (open #011/#012)** — the Yale password and the GitHub PAT
  were visible in tool output; both flagged for rotation.
- **Meta** — `.opencode/skills/home-assistant` knowledge base created;
  `WORKTRACK/` tracker created to carry planning across sessions.

## Decisions

- Versioning model: single GitHub repo; `/config` is the source of truth,
  mirrored by Git Exporter (`config/` subtree in repo). Build agent edits
  `/config` over SSH.
- Cleanup policy: **balanced** — report, stage, disable-not-delete, sign-off on
  ambiguous items, every step a separate commit once versioned.
- Automation target: native HA YAML + `input_*` schedule helpers (1:1 port of
  `script_engine` behaviour), replacing custom Python. Verify over a full
  day/night cycle before retiring legacy components.
- Chat agent: OpenRouter-backed Assist first (privacy-aware via exposed-entity
  scoping); local Ollama as later option.
- Family editing: HA app/dashboard over raw git; the git history + summaries
  provide the "textual definition".
- Tracker/docs: kept locally; optionally mirrored into `/config/docs/`
  (owner decision, backlog #014).