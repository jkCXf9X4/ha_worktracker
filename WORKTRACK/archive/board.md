# Status board

Snapshot owner: build agent. Update after every working session.

Last updated: 2026-10-22

## Phase state

| Phase | Description | Status |
|-------|-------------|--------|
| P0 | SSH access to HA (root, port 2222, key auth) + `ha` CLI works | ✅ done |
| P1 | Versioning: private GitHub repo + Git Exporter pushing `/config` | ✅ done |
| P2a | Inventory snapshot (entities/devices/HACS/config entries/schedules) | ✅ done |
| P2b | Live-state discovery (long-lived token, API) + verify TV duplicates | ✅ done |
| P3 | Balanced cleanup (HACS/add-ons/dead entities/automation sweep/recorder) | ✅ done |
| P4 | Config normalization + YAML schedule helpers/automations (spec exists) | ✅ done |
| P5 | Family Lovelace dashboard + per-user logins | ⬜ open |
| P6 | Family chat agent (OpenRouter conversation integration + persona + scoping) | ⬜ open |
| P7 | Summaries (`tools/summarize.py`), `ADMIN.md`, `proxmox/backups.md`, final verification | ⬜ open |

## Current focus

**P4 done — P5 next.** P4 (YAML automation migration) went live 2026-10-21:
`script_engine` retired (archived under `config/deprecated/`), 14 YAML
automations + `input_*` schedule helpers active, Sovrum + Isac schedules on YAML,
Hue→ZHA migration complete, dashboard rebuilt (6 views), Tibber removed, Tuya
re-auth, Swedish naming pass. Full log: `WORKTRACK/changelog.md`, plus
`docs/cleanup_report.md` and `docs/hue_zha_migration.md`.

Open: #015 family
dashboard (**P5**), #016 chat agent (**P6**), #017/#018 summaries + proxmox
(**P7**), #019 ceiling morning fade, #020 seasonal grouping. (#014 declined —
docs stay in this repo.)

## In progress

- (none — tracker cleaned up 2026-10-22; open items under "Current focus")

## Blocked / waiting on owner

- **No open blockers** — P3/P4 complete; owner decisions applied (TV/media and
  UniFi removed, presence on companion trackers, `doorman` kept, `script_engine`
  migrated to YAML then retired); exposed secrets rotated (#011/#012 done
  2026-10-22). #014 (docs-sync) declined — tracker/docs stay in this repo.

## Done (highlights)

- P0: root SSH via Advanced SSH & Web Terminal add-on; login-shell trick for `ha`; **key auth add-on authorized key added** (SSH no longer needs password).
- P1: Git Exporter live → `ha_config` on GitHub (`main`), excludes configured, `ha core check` passes, first push `65acd1f`.
- P2a: `docs/inventory.md` written.
- P2b: long-lived token provisioned; live state snapshot (436 states); **TV duplication verified** (2 `samsungtv` entries orphaned/`not_loaded`, `dlna_dmr` is the live player); UniFi bloat quantified (148 trackers); `docs/cleanup_report.md` drafted.
- Discovery: `script_engine` read end-to-end; `docs/automation_requirements.md` written.
- P1 fixes: legacy Samsung TV IP/MAC moved to `secrets.yaml`; broken `secrets.yaml` repaired.
- Meta: `.opencode/skills/home-assistant` knowledge base created; this tracker created; `ha_config` added as git submodule.
- P4: YAML automation go-live (`script_engine` retired/archived, 14 automations + helpers); HA Core 2026.10.2; Sovrum + Isac schedules on YAML.
- Hue→ZHA: 10 devices re-paired + renamed to canonical IDs, 5 stale ZHA devices purged, dimmers/remotes bound (`docs/hue_zha_migration.md`).
- Cleanup 2026-10-21: Tuya re-auth, Tibber removed (27 entities), registry audit 0 orphans, dashboard rebuilt (6 views, 38 refs verified live), HACS/floorplan/scheduler cleanups, Swedish naming pass.
- Security 2026-10-22: **exposed secrets rotated** — Yale lock password (#011) + GitHub fine-grained PAT (#012, swapped in the Git Exporter add-on).