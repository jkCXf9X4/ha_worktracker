# NEXT — living tracker (HA build)

Forward-looking tracker. Ops how-to lives in the skill
(`.opencode/skills/home-assistant`), deep docs in `docs/`. This file answers
"where are we, what's next". Completed work lives in `WORKTRACK/archive/changelog.md`.

Snapshot owner: build agent. Update after every working session.
Last updated: 2026-10-23

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
| P9 | `config_tools__call_service` (allowlisted service tool, exposure-gated, v0.3.1) | ✅ done |
| P10 | Config review patch (startup grace, `initial:` removal, nattmode script, blueprints, 12 orphans purged) | ✅ done |

System is in **normal operation** — P0–P10 complete, no blockers, secrets
rotated. Remaining work is optional enhancements (#020) and improvement
candidates (#024–#029, all waiting on owner decision). Full history:
`WORKTRACK/archive/changelog.md`.

## Open work

- [x] #020 **Seasonal night-lamp grouping** — **RESOLVED 2026-10-23** (owner):
      P4 plug broke, P11 physically replaced it and now does the old P4 job as
      the front outdoor light. `night_lamps` = ute_huvudentre + **p11**;
      `christmas_sockets` = p10/p1/p6. Applied + reloaded live.

Nothing else is in flight.

## Improvement candidates

Best-practice review, 2026-10-23 — sourced from online HA best practices
(official docs + community) and audited against `config/`. Full reference:
`docs/BEST_PRACTICES.md`; `home_status` machine: `docs/deep_dive_home_status.md`.
Nothing deployed — each waits on ⬜ owner decision before edit.

- [ ] #024 **`home_status` template simplification (option B)** — replace the
      `as_timestamp`/date-concat math in `template/home_status.yaml` with a
      zero-padded `HH:MM:SS` lexicographic compare (equivalent output, ~70%
      shorter). Candidate patch verified-equivalent; needs `ha core check` +
      live edge-trigger trace after apply. Owner sign-off: `docs/deep_dive_home_status.md`.
- [ ] #025 **Startup-grace gate repetition** — `input_boolean.ha_started` +
      the same 2-condition checklist duplicated across ceiling_lights (×4),
      night_lights (×2), locks (×2), sovrum (×2), isac (×1). Optional: collapse
      into one blueprint. Current form is correct/readable — only if column
      count matters.
- [ ] #026 **Ceiling-lights consolidation (Taras pattern)** — four same-shape
      automations in `automations/ceiling_lights.yaml` → one data-driven
      automation (state trigger over the 3 entities + `choose` on object_id →
      action). ~99→~35 lines, one place to edit. Trade-off: loses per-behavior
      greppability. Style choice, not a bug fix.
- [ ] #027 **Two hunts for the old `home_status` string compare** — verify at
      the same time: (a) the candidate `wake > bed` midnight flip behaves like
      today (it does — no regression), (b) owner confirms "Sun = weekday-bed"
      axis is intended family behaviour.
- [ ] #028 **Labels for seasonal sockets** — `switch.p10/p11/p1/p6` handled via
      `christmas_sockets` group + sync automation today; a **label** would let
      targeting survive group re-edits and dissolve #020 churn. Current approach
      works — incremental.
- [ ] #029 **Scenes vs groups membership duplication** — `scenes/scenes.yaml`
      re-list the same lights as `groups.yaml`. Keep the in-file "keep in sync"
      warning honest or derive scenes from groups. Minor.
- [x] ~~schedule helper migration~~ **Rejected** — native `schedule` helper was
      evaluated as a `home_status` replacement and is the wrong tool for this
      build: no runtime `schedule.set` service (family/agent edit
      `input_datetime`), blocks can't cross midnight, weekday/weekend axes don't
      map. Documented so it isn't re-proposed: `docs/deep_dive_home_status.md`
      §Option A.

### Organization round (room grouping, helpers, templates, scripts, automations) — 2026-10-23

Live registry research (areas + device map pulled read-only over SSH) + full
best-practice analysis: `docs/deep_dive_organization.md`. All ⬜ owner-decision.

- [x] #030 **Normalize area registry + map all devices** — **APPLIED 2026-10-23**:
      area registry consolidated+renamed live (11 areas: Entré hall, Kök
      korridor, Badrum korridor, Vardagsrum, Sovrum, Isacs rum, Gästrum,
      Hobbyrum(new), Kök, Uterum, Utebelysning); legacy CarPort/Other/
      Träningsrum/Ute framsida/Kvällsbelysning deleted; all physical devices
      device→area mapped (fished + owner placements, `docs/fishing_log.md`);
      Uteljussensor house-wide. `ha core check` green, exporter `643e941`.
      **Dashboard rebuilt 2026-10-23 as area cards** (Belysning + Utomhus;
      11 compact cards, diagnostics excluded; area icons set; exporter `9defb98`).
      **#030 DONE.**
- [ ] #031 **Labels for cross-cutting concerns** — `säsong` (p10/p11/p1/p6),
      `utebelysning`; target labels from automations instead of group edits.
      Sharpen/supersede #028. Needs #030.
- [ ] #032 **Pause-toggle helpers** — `input_boolean.automatik_taklampor` /
      `automatik_nattlampor` / `automatik_uteljus` gate their automations so the
      family can pause a behavior from the dashboard without editing YAML.
- [ ] #033 **`next_wake`/`next_bedtime` template sensor** — derived next
      wake/sleep boundary for the dashboard (defer until #024 lands).
- [ ] #034 **`script.goodnight`** — one voice/dashboard action: ceiling off,
      night-corner dim (`script.nattmode`), doors locked. Manual convenience on
      top of the automatic sleep behavior.
- [ ] #035 **Christmas sockets via label + scenes/groups de-dup** — target
      label `säsong` instead of `christmas_sockets` group (resolves #020);
      scenes.yaml membership follows area ownership. Needs #030/#031.

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