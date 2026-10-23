# NEXT — living tracker (HA build)

Forward-looking tracker, distilled 2026-10-22 from the archived logs in
`WORKTRACK/archive/`. Ops how-to lives in the skill
(`.opencode/skills/home-assistant`), deep docs in `docs/`. This file answers
"where are we, what's next".

Snapshot owner: build agent. Update after every working session.
Last updated: 2026-10-22

## Phase state

| Phase | Description | Status |
|-------|-------------|--------|
| P0 | SSH access to HA (root, port 2222) + `ha` CLI | ✅ done |
| P1 | Versioning: private GitHub repo + Git Exporter pushing `/config` | ✅ done |
| P2 | Inventory (P2a) + live-state discovery (P2b) | ✅ done |
| P3 | Balanced cleanup (TV/UniFi/recorder/registry/legacy/Tibber) | ✅ done |
| P4 | YAML automation migration (script_engine retired, 14 automations + helpers) | ✅ done |
| P5 | Family Lovelace dashboard + per-user logins | ✅ done |
| P6 | Family chat agent (OpenRouter + persona + scoping) | ✅ done |
| P7 | Summaries (`tools/summarize.py`) · `ADMIN.md` · `proxmox/backups.md` · final verification | ✅ done |
| P8 | Agent config tools (`config_tools` llm-platform: read/glob/write/check/reload, no bash) | ✅ done |

System is in normal operation — **P0–P8 complete, no blockers, secrets
rotated.** Build milestones done; remaining items are optional enhancements
(#019/#020).

## Open work

- [x] #015 **Family dashboard (P5)** — Schema view rebuilt (2026-10-22) into
      real family schedule pickers: Familj (wake/bedtime weekday+weekend), Sovrum
      (fade start/off/brightness), Isacs rum (fade start/brightness), Utomhusljus
      & natt (lux thresholds + night dim) — all on existing `input_*` helpers
      (no new helpers). Scheduler-card removed from the view + its stale
      `scheduler-card.js` resource dropped. Users Erik+Sara already exist w/
      logins+apps; per-user roles **left as-is (owner decision 2026-10-22)** —
      no kid account.
- [x] #016 **Family chat agent (P6)** — OpenRouter conversation integration,
      persona, exposed-device scoping to schedule helpers only (privacy bound);
      local Ollama as an optional later switch.
      - **owner decision 2026-10-22 (all-in scope):** expose ALL entities +
        full service access, no carve-outs (no cameras exist; Yale locks can only
        be locked by HA, not unlocked → small risk). Privacy cost accepted
        (states go to OpenRouter).
      - **DONE 2026-10-22:** native `open_router` integration (built into HA
        2026.10, config-flow, key in `.storage` = never committed). Agent
        `conversation.deepseek_deepseek_v4_flash_0731` (deepseek v4 flash
        0731), persona in Swedish (family scheduling + light control), default
        Assist pipeline switched to it (language sv). **Key discovery:** the
        `assist` LLM API only surfaces entity-control intents + a live-context
        tool — NOT arbitrary services. Schedule/helper writes therefore go
        through 5 exposed LLM-tool scripts (`set_family_schedule`,
        `set_sovrum_schedule`, `set_isac_schedule`, `set_outside_lux`,
        `set_night_dim`), each with description + field descriptions +
        stop/response_variable confirmation. All 281 entities exposed to
        `conversation` (275 + re-exposed 3 groups + 3 locks; time/date/sun/zone
        hidden). Verified live: reads presence, toggles lights, writes
        wake_time helper (agent-initiated value persisted).
- [x] #017 **Plain-text summaries (P7)** — DONE 2026-10-22.
      `tools/summarize.py` parses `input_*` helpers + `automations/` from the
      `ha_config/config` mirror → `docs/SCHEDULES.md` + `docs/AUTOMATIONS.md`
      (Swedish, tables, cross-referenced; warns on dangling helper refs).
      Verified 23 automations / 15 helpers; re-run + commit on config changes.
      Agent persona references the docs (docs live in this repo, not on VM).
- [x] #018 **Proxmox layer (P7)** — DONE 2026-10-22. `proxmox/backups.md`:
      vzdump retention crib sheet (daily×14 / weekly×4 / monthly×2, snapshot
      mode), pre-upgrade manual snapshot, restore steps, verify-always rule;
      `docs/ADMIN.md` = operator how-to (3 backup layers, restore from each,
      common ops, secrets hygiene). Config-only; owner runs on Proxmox.
- [x] #019 **Ceiling morning fade** — 🗑 **WON'T-DO (owner decision
      2026-10-22):** "remove that one, it will never be relevant". The 30-min
      03:00–09:00 fade-in from old `script_ceiling_lights_group.py` stays
      unrealized; current instant ceiling-on behaviour stands.
- [ ] #020 **Seasonal night-lamp grouping (later)** — make the `p10/p11/p1`
      Christmas sockets a toggleable group so "night lamps" ≠ "Christmas"
      year-round.
- [x] #022 **`config_tools__call_service` (P9) — DONE + DEPLOYED 2026-10-23,
      hardened v0.3.1** — whitelisted service-action tool so the chat agent can call
      e.g. `light.turn_on` with `flash: short/long` (blink lamps) and real
      service params the entity intents can't carry (`flash`, `effect`,
      `transition`). Living plan: `docs/call_service_tool_P9_PLAN.md`.
      - **Component (v0.3.1):** `CallServiceTool` in `config_tools` (allowlist
        `light|switch` turn_on/off/toggle in `const.py`, entity-registry +
        **exposure-only** gating (no admin gate) in `tools.py`, registered 8th
        in `llm.py`, manifest → 0.3.1 with `integration_type: service`).
        `data` = **typed probatio schema** (`flash`, `brightness_pct`,
        `brightness`, `transition`, `effect`, `color_temp_kelvin`, `color_temp`,
        `color_name`, `white`, `profile`, `xy_color`/`rgb_color`/`rgbw_color`/
        `rgbww_color`/`hs_color` arrays) → parse-time "did you mean" errors;
        HA's service schema backstops. Writes are atomic (tempfile+`os.replace`);
        `_LOGGER` on every call.
      - **Why:** ZHA lights report `supported_features` 40 = FLASH+TRANSITION, so
        blink is physically possible, but HA's `ActionTool` schema cache is
        script-only and the assist API has no generic service exposure.
      - **Native alternative (prefer for named actions):** an exposed **script**
        surfaces as a `script.*` tool automatically (schema from its `fields`).
        `scripts.yaml::korridor_blink` (`fields: flash|transition`) added so
        "blinka korridorlampan" works with zero component code; `call_service`
        covers the generic gap (any exposed light/switch, arbitrary data).
      - **DEPLOYED + VERIFIED 2026-10-23 (v0.3.0), hardened v0.3.1:** code +
        `AGENT_HANDBOOK.md` pushed via
        tar-over-SSH, `ha core check` green, core restarted. Live via
        `conversation/process`: forced `light.turn_off` → state `on`→`off` and
        back `on` with `response.data.success == []` (empty list = tool path, the
        built-in intent would populate `success`); bogus field returned verbatim
        `Service call failed: not a valid option at 'bogus_field'`. Exporter push
        `989e5a0`, mirror md5 == VM == local.
      - **GOTCHA fixed en route:** the VM's old `find_device` was broken
        (`registry.get_entries_for_device_id` instead of
        `registry.entities.get_entries_for_device_id`) — the repo version fixed
        it. **Admin gate RESOLVED:** dropped for `call_service` (exposure bound
        only, per HA's native model); admin stays on write/check/reload.
- [x] #021 **Agent config tools (P8)** — ✅ **DONE + DEPLOYED 2026-10-22**:
       custom component `config_tools` = `llm` platform adding bounded tools to
       the family chat agent: `read_file`/`glob_files` (everyone) +
       `write_file`/`check_config`/`reload` (admin-context), restricted to
       reloadable YAML, **no bash** (`docs/AGENT_TOOLS.md`).
       - Component in `/config/custom_components/config_tools/` (manifest,
         __init__, const, llm, tools); `config_tools:` added to
         `configuration.yaml`; `ha core check` green; core restarted.
       - **Verified live via `conversation/process`:** agent called `glob_files`
         (listed the 9 real automation files) + `read_file` (read scripts.yaml)
         + `write_file`→check→reload round-trip (file written, automation entity
         registered for a YAML-list file, test file then removed).
       - **v0.2.0 (same day):** added `find_device` (registry lookup by name →
         `device_id`) + `device_triggers` (live type/subtype enum) — closes the
         gap the dropped `bind_remote` was meant to fill. Verified live: agent
         listed STYRBAR device_id + 16 real triggers, then did a full
         find→triggers→write→check→reload edit of `styrbar_lekstuga.yaml`
         (retargeted dim_up, then reverted).
       - **GOTCHA discovered:** `automation: !include_dir_merge_list` silently
         drops single-mapping YAML files — automations must be written as YAML
         *lists*; `check_config` cannot catch it. Runbook rule added.
       - **Owner decisions:** `bind_remote` dropped ("way too specific"; its two
         capabilities superseded by `find_device` + `device_triggers`); the 5
         schedule-writer scripts removed from `scripts.yaml` (generic tools
         replace them; live `input_*` value changes are now out of the agent's
         reach — family changes schedules via dashboard pickers).
       - Cleanup left: stale inert `conversation` exposure entries for the old
         script entities (harmless; entities don't exist anymore).

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
  chronological log); tick completed items here in NEXT.md.