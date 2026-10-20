# Status board

Snapshot owner: build agent. Update after every working session.

Last updated: 2026-10-20

## Phase state

| Phase | Description | Status |
|-------|-------------|--------|
| P0 | SSH access to HA (root, port 2222) + `ha` CLI works | ✅ done |
| P1 | Versioning: private GitHub repo + Git Exporter pushing `/config` | ✅ done |
| P2a | Inventory snapshot (entities/devices/HACS/config entries/schedules) | ✅ done |
| P2b | Live-state discovery (long-lived token, API) + verify TV duplicates | ⬜ open |
| P3 | Balanced cleanup (HACS/add-ons/dead entities/automation sweep/recorder) | ⬜ open |
| P4 | Config normalization + YAML schedule helpers/automations (spec exists) | ⬜ open |
| P5 | Family Lovelace dashboard + per-user logins | ⬜ open |
| P6 | Family chat agent (OpenRouter conversation integration + persona + scoping) | ⬜ open |
| P7 | Summaries (`tools/summarize.py`), `ADMIN.md`, `proxmox/backups.md`, final verification | ⬜ open |

## Current focus

**P2b → P3.** Finish discovery, then start the staged cleanup. Immediate work:

1. Get the HA **long-lived token** from the owner (read-only API discovery).
2. Confirm TV duplicate situation (`samsungtv` ×2 + `dlna_dmr`) and prune.
3. Produce the cleanup plan (from `docs/inventory.md` observations) → `docs/cleanup_report.md`.
4. Execute cleanup in separate versioned steps (disable-not-delete).

## In progress

- (none right now — awaiting token/P2b)

## Blocked / waiting on owner

- **Long-lived HA token** for entity/state API discovery (blocking P2b/P3 depth).
- **Rotate exposed secrets** (recommended): Yale lock password + GitHub fine-grained PAT were visible in output during P1. Replace PAT in the Git Exporter add-on after creating a new one.
- Decision on docs sync: mirror `docs/` into `/config/docs/` so the GitHub repo (exporter) versioned them too. (Recommended yes.)

## Done (highlights)

- P0: root SSH via Advanced SSH & Web Terminal add-on; login-shell trick for `ha`.
- P1: Git Exporter live → `ha_config` on GitHub (`main`), excludes configured, `ha core check` passes, first push `65acd1f`.
- P2a: `docs/inventory.md` written.
- Discovery: `script_engine` read end-to-end; `docs/automation_requirements.md` written.
- P1 fixes: legacy Samsung TV IP/MAC moved to `secrets.yaml`; broken `secrets.yaml` repaired.
- Meta: `.opencode/skills/home-assistant` knowledge base created; this tracker created.