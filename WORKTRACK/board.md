# Status board

Snapshot owner: build agent. Update after every working session.

Last updated: 2026-10-20

## Phase state

| Phase | Description | Status |
|-------|-------------|--------|
| P0 | SSH access to HA (root, port 2222, key auth) + `ha` CLI works | ✅ done |
| P1 | Versioning: private GitHub repo + Git Exporter pushing `/config` | ✅ done |
| P2a | Inventory snapshot (entities/devices/HACS/config entries/schedules) | ✅ done |
| P2b | Live-state discovery (long-lived token, API) + verify TV duplicates | ✅ done |
| P3 | Balanced cleanup (HACS/add-ons/dead entities/automation sweep/recorder) | 🔶 in progress |
| P4 | Config normalization + YAML schedule helpers/automations (spec exists) | ⬜ open |
| P5 | Family Lovelace dashboard + per-user logins | ⬜ open |
| P6 | Family chat agent (OpenRouter conversation integration + persona + scoping) | ⬜ open |
| P7 | Summaries (`tools/summarize.py`), `ADMIN.md`, `proxmox/backups.md`, final verification | ⬜ open |

## Current focus

**P3 staged cleanup.** Plan drafted: `docs/cleanup_report.md`. Immediate work:

1. ✅ **P3-1 done**: all TV/media removed (samsungtv×2, dlna_dmr, spotify, cast config entries + legacy samsungtv_tizen component) → `ha_config` `257e19c`.
2. Await sign-off on UniFi tracked-clients limit + mobile-app phone cull.
3. Configure recorder (`purge_keep_days`, `exclude_missing_entities`).
4. Each step = separate commit on `ha_config` (exporter pushes to `/config`).

## In progress

- (none right now — awaiting sign-offs)

## Blocked / waiting on owner

- **Sign-off UniFi**: limit tracked clients to family SSIDs? Which?
- **Sign-off mobile app**: which of 4 phones (LON-L29, iPhone, Prinsen, ApplePie) are active?
- **TV/media removed** — re-add TV via UI later if wanted (clean slate). HACS device `SamsungTV Tizen` leftover.
- **Rotate exposed secrets** (recommended): Yale lock password + GitHub fine-grained PAT were visible in output during P1. Replace PAT in the Git Exporter add-on after creating a new one.
- Decision on docs sync: mirror `docs/` into `/config/docs/` so the GitHub repo (exporter) versioned them too. (Recommended yes.)

## Done (highlights)

- P0: root SSH via Advanced SSH & Web Terminal add-on; login-shell trick for `ha`; **key auth add-on authorized key added** (SSH no longer needs password).
- P1: Git Exporter live → `ha_config` on GitHub (`main`), excludes configured, `ha core check` passes, first push `65acd1f`.
- P2a: `docs/inventory.md` written.
- P2b: long-lived token provisioned; live state snapshot (436 states); **TV duplication verified** (2 `samsungtv` entries orphaned/`not_loaded`, `dlna_dmr` is the live player); UniFi bloat quantified (148 trackers); `docs/cleanup_report.md` drafted.
- Discovery: `script_engine` read end-to-end; `docs/automation_requirements.md` written.
- P1 fixes: legacy Samsung TV IP/MAC moved to `secrets.yaml`; broken `secrets.yaml` repaired.
- Meta: `.opencode/skills/home-assistant` knowledge base created; this tracker created; `ha_config` added as git submodule.