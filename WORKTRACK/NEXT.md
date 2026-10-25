# NEXT — living tracker (HA build)

Forward-looking tracker. Ops how-to lives in the skill
(`.opencode/skills/home-assistant`), deep docs in `docs/`. This file answers
"where are we, what's next". Completed work lives in `WORKTRACK/archive/changelog.md`.

Snapshot owner: build agent. Update after every working session.
Last updated: 2026-10-25

## Phase state

| Phase | Description | Status |
|-------|-------------|--------|
| P0 | SSH access to HA (root, port 2222) + `ha` CLI | ✅ done |
| P1 | Versioning: private GitHub repo + Git Exporter pushing `/config` | ✅ done |
| P2 | Inventory (P2a) + live-state discovery (P2b) | ✅ done |
| P3 | Balanced cleanup (TV/UniFi/recorder/registry/legacy/Tibber) | ✅ done |
| P4 | YAML automation migration (script_engine retired, 9 automations + helpers) | ✅ done |
| P5 | Family Lovelace dashboard + per-user logins | ✅ done |
| P6 | Family chat agent (OpenRouter + persona + scoping) | ✅ done |
| P7 | Summaries (`tools/summarize.py`) · `ADMIN.md` · `proxmox/backups.md` · final verification | ✅ done |
| P8 | Agent config tools (`config_tools` llm-platform: read/glob/write/check/reload, no bash) | ✅ done |
| P9 | `config_tools__call_service` (allowlisted service tool, exposure-gated, v0.3.1) | ✅ done |
| P10 | Config review patch (startup grace, `initial:` removal, nattmode script, blueprints, 12 orphans purged) | ✅ done |

System is in **normal operation** — P0–P10 complete + the 2026-10-23/24
simplification rounds (labels/areas, behavior-box scripts, boot reconcile,
room-schedule blueprint, daylight template, gates-in-scripts, config_tools
v0.4.0), no blockers. Full delivery record:
`WORKTRACK/archive/changelog.md`.

## Open work

The last owner-verification item (#027) resolved 2026-10-24: the deployed
`home_status` string-compare matches the intended weekday/weekend axes (Sunday
morning = weekend wake; Sunday evening = weekday bedtime — "morning after is
early"). No regression observed.

**⬜ Next block — Tested-policy architecture (planned 2026-10-25).** Design
record: `docs/TESTED_POLICY_PLAN.md`. Evolution of the YAML stack into a
three-layer, testable, LLM-maintainable Python shape — domain package
(pure, pytest-tested) + adapter binding + existing infra. Decoupled quality
infra lands first regardless of runtime; a bounded Pyscript spike gates the
execution layer (Path E = native domain modules + thin pyscript adapters;
Path V = golden/Jinja-parity verification against live YAML).

- ✅ P-A: quality skeleton — `uv`/`pyproject.toml` + `uv.lock`; ruff (managed
  code only) + mypy (strict) + pytest gate; `domain/daylight/{models,
  home_status,daylight,night}` extracted + typed; 29 unit tests + YAML fixture
  matrix (`tests/fixtures/daylight/night_lights.yaml`); `tools/qa.sh` green;
  `docs/subsystems/daylight.md` + `docs/invariants.md`; skill dev-chain section
- ✅ P-A+: **Pyscript spike = GO (2026-10-25, 21:4x).** pyscript 2.1.0 installed
  as manual custom_component + config-entry via **UI flow only** (source `user`,
  `allow_all_imports: false`), *no* `pyscript:` block — the Oct-20 root-cause
  fix. Verified live over WS: module load, `@time_trigger("startup")` fires
  (probe sensors), watchdog auto-reloads new files without restart,
  `pyscript.reload` works, `generate_stubs` produced IDE stubs (with
  `?return_response`), debug logs at `custom_components.pyscript.*` show full
  traces. Probes removed after verification (inert). Export blocked once by the
  add-on's IP check on pyscript's `services.yaml` loopback default → repo-root
  `.gitallowed` (`ha_config`) unblocked it; exporter pushed `7d694a1`.
  **Decision: Path E.** Bound invariants (isacs_rum, honest-testing) active.
- ✅ P-C: binding layer — Path E adapters **live in shadow mode**. `domain/
  daylight` shipped to `/config/pyscript/native_domain/` as native modules +
  thin pyscript adapters in `/config/pyscript/scripts/` writing `_ps` twins and
  logging mismatches (no service calls). **Verified live**: home_status_ps ==
  home_status (sleep), light_outside_ps == light_outside (off), night_lights_ps
  = {utelampa on, sasong off}; native import confirmed via correct idiom
  (`sys.path.insert(0)` + `importlib.invalidate_caches()`, `allow_all_imports:
  true` after options flow). Tools: `tools/deploy.py` (qa → isacs_rum guard →
  tar-over-SSH → pyscript.reload).
- ⬜ P-D: ownership flip (`_ps` → real IDs), `tools/probe_vm.py`, rollback
  ritual, exporter sync of `/config/pyscript/`
- ⬜ P-E: §7 agent workflow in skill + invariants doc + success-test

**Binding invariant (all workstreams, from owner):** never trigger any light
on in `isacs_rum` (`light.isac_tak`, `switch.isac_lekstuga`, bedside) — Isac is
asleep. Pilot cluster excludes the sovrum/isac fades (stay pure YAML).

## Recently completed (working-log shorthand; detail in the changelog)

- **2026-10-24 — Hue dimmer Isac + bedside lamp** (`720ca7d`): `switch.p6`
  attached to the hue dimmer via `zha_remote_lights` blueprint's new optional
  `target_switch`; single ON = ceiling+bedside, double ON = bedside only +
  ceiling off, OFF = both. Verified live. Skill + agent docs (handbook/examples,
  `b3136d1`) updated with the single-vs-double-trigger pattern and the
  `condition: template` boolean-render gotcha. Detail: changelog 2026-10-24.
- **2026-10-24 — #027 RESOLVED + agent prompt refresh + exposure cleanup:**
  owner confirmed the `home_status` Sunday axis (Sun morning = weekend, Sun
  evening = weekday bedtime) — deployed template already matches;
  chat-agent system prompt ("TEKNISK DEL") refreshed to config_tools v0.4.0
  (10 tools, `set_label`/`restart_core`, `script.*`-tool preference, labels/
  areas architecture) via the reconfigure flow; 5 stale `expose_entity` entries
  removed (`group.ceiling_lamps`, `group.night_lamps`, the 3 deleted scenes).
- **2026-10-24 round 3 — simplification round 2** (`d6d7684`): daylight flag →
  `binary_sensor.light_outside` latched-hysteresis template (`template/daylight.yaml`),
  seasonal rule single-sourced in `script.uteljus_sync`, boot reconcile
  centralized (`boot_reconcile.yaml` → `script.reconcile_all`; convention: no
  `ha_ready -> on` triggers in new automations — extend `reconcile_all`),
  registry renames + orphan purge (`script.lock_by_status`,
  `binary_sensor.light_outside`), `/config/docs/` agent docs rewritten to live
  state. Live: 9 automations + 12 scripts.
- **2026-10-24 round 2 — gates-in-scripts + room pauses + agent tools** (`cd8c26a`/`f0d9ffe`):
  gates folded into behavior-box scripts (if/then wrapper — YAML scripts have no
  top-level `condition`), `automatik_sovrum`/`automatik_isac` room pause toggles,
  `home_status` string compare (#024) + `next_wake`/`next_bedtime` attrs (#033),
  config_tools **v0.4.0** (`set_label`, `restart_core`, `input_*` write allowlist).
- **2026-10-24 round 1 — scripts/templates/helpers simplification** (`66156a5`):
  behavior-box scripts, `room_schedule` blueprint instances, `ha_started` →
  native `binary_sensor.ha_ready`, timer-based pause removed.
- **2026-10-23 — design-review fixes** (`7d1edf0`): `ha_ready`-gated outside
  re-sync, christmas pause gate, blueprint isoweekday/locale fix, mode: restart.
- **2026-10-23 — labels/areas + collapse round** (`3e94474`, `643e941`,
  `9defb98`, `9e45290`): 11 areas mapped, 4 labels (`taklampa`/`natthorn`/
  `sasong`/`utelampa`), twin automations collapsed 6→3, scenes deleted,
  pause toggles, goodnight script, area-card dashboard.

## Improvement candidates

Best-practice review, 2026-10-23 — sourced from online HA best practices
(official docs + community) and audited against `config/`. Full reference:
`docs/BEST_PRACTICES.md` (live Part-1 reference; the dated audit is archived at
`docs/archive/build_audit_2026-10-23.md`). **All candidates now closed**
(#024–#026/#028–#035 done — delivery record in the changelog; #027 owner-
verified 2026-10-24; #020 resolved; the `schedule`-helper migration was
evaluated and **rejected**, full analysis:
`docs/archive/deep_dive_home_status.md` §Option A). No owner-decision items
remain open.

## Standing decisions & conventions (binding for future work)

- **Source of truth = HA `/config` on the VM.** Git Exporter mirrors it to
  GitHub (`ha_config`, `main`) but is **push-only** — remote commits are never
  applied to `/config`. All config edits go on the VM over SSH → `ha core check`
  → exporter push.
- Automation logic = native YAML + `input_*` schedule helpers (the family/chat
  surface); custom Python retired/archived.
- Cleanup policy: balanced — report first, stage, disable-not-delete, owner
  sign-off, each step a separate versioned commit.
- Docs/tracker live in this repo (`ha_worktracker`); **not** mirrored to
  `/config/docs/` (#014 declined 2026-10-22) — `hue_zha_migration.md` is the sole
  doc on the VM.
- Security: secrets never committed (`secrets.yaml` excluded, tool output
  redacted). Exposed secrets rotated 2026-10-22 (#011/#012).
- Statuses: ⛔ blocked · ⬜ open · 🔨 in progress · ✅ done · 🗑 won't-do

## Operating reminders (full detail in the skill)

- **Access**: `ssh root@192.168.1.248 -p 2222` (key auth). `ha` CLI only via a
  login shell (`bash -lc "ha ..."`). SFTP/scp disabled → use tar-over-SSH.
- **Config loop**: edit on VM → `ha core check` → restart exporter → check
  `ha apps logs ...` for "Exporter finished".
- **Logging**: append session notes to `WORKTRACK/archive/changelog.md` (single
  chronological log); only genuinely open items live in this file.