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
| P7 | Summaries (`tools/summarize.py`) · `ADMIN.md` · `proxmox/backups.md` · final verification | ⬜ open |

System is in normal operation — P0–P6 complete, no blockers, secrets rotated.
Next action: **P7** (#017 summaries · #018 proxmox · final verification).

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
- [ ] #017 **Plain-text summaries (P7)** — `tools/summarize.py` →
      `docs/SCHEDULES.md` / `docs/AUTOMATIONS.md` from the YAML; surfaced to the
      chat agent.
- [ ] #018 **Proxmox layer (P7)** — `proxmox/backups.md`: vzdump retention crib
      sheet (config-only; owner runs on Proxmox).
- [ ] #019 **Ceiling morning fade (later)** — restore the unused 30-min fade-in
      (03:00–09:00) from old `script_ceiling_lights_group.py` **if wanted**.
- [ ] #020 **Seasonal night-lamp grouping (later)** — make the `p10/p11/p1`
      Christmas sockets a toggleable group so "night lamps" ≠ "Christmas"
      year-round.

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