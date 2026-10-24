# NEXT — living tracker (HA build)

Forward-looking tracker. Ops how-to lives in the skill
(`.opencode/skills/home-assistant`), deep docs in `docs/`. This file answers
"where are we, what's next". Completed work lives in `WORKTRACK/archive/changelog.md`.

Snapshot owner: build agent. Update after every working session.
Last updated: 2026-10-24

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
      **Follow-up 2026-10-23:** p6 (Isacs sänglampa) **removed from `sasong`** —
      it was wrongly following the dusk→dawn seasonal rule whenever
      `christmas_lights` was on. Now a manual lamp. `sasong` = p10/p1.
- [x] **Scripts/templates/helpers simplification (2026-10-24)** — behavior boxes
      finished (`ceiling_lights_sync`, `uteljus_sync` absorbing `sasong_sync`,
      `outside_light_sync`); `room_schedule` blueprint instance per room;
      `home_status` attributes (`is_workday`, `next_wake`, `next_bedtime`);
      `light_on_with_transition` gained label targeting; `slack_borta` away
      label; `ha_started` flag retired → native `binary_sensor.ha_ready`
      (uptime integration); timer-based pause **removed** (owner decision —
      `automatik_*` dashboard toggles are the single pause mechanism). Full log:
      `WORKTRACK/archive/changelog.md`. Exporter `66156a5`.

- [x] **Design-review fixes (2026-10-24)** — closed the "strange/off" items from
      a fresh review of the post-simplification config (`/tmp/opencode/review_findings.md`):
      - **outside_light boot re-sync** now triggers on `binary_sensor.ha_ready ->
        on` instead of raw `homeassistant start` (the start event fires before the
        ZHA lux sensor is up, so the flag kept its restored value until the next
        threshold crossing). Exporter `7d1edf0`.
      - **`p4_christmas_sockets_sync`** now also gated on `automatik_nattlampor`
        (was only `ha_ready` — inconsistent with `p4_night_lights`, which shares
        `script.uteljus_sync`). Verified live via `test_condition`: False while the
        pause toggle is off.
      - **`room_schedule` blueprint**: weekday check switched from
        `strftime('%a').lower()` to locale-proof `now().isoweekday() in weekdays`
        (select values now numeric strings "1".."7" + instances updated); the
        `fade_out` trigger became a conditional template `at`
        (`[states(off_entity)] if off_enabled else []`) so a disabled off-time
        renders an empty list instead of firing a no-op trigger daily.
      - **`light_on_with_transition`**: label field description now warns that it
        only touches light-domain members; script gained `mode: restart`.
      - ADMIN.md documents the `uptime` config-entry dependency behind
        `binary_sensor.ha_ready` (`.storage`-resident, must be re-created if
        `.storage` is rebuilt).
      - Re-verified: 7 automations all `on`, `ha core check` green,
        `automatik_nattlampor`=off, bedroom light untouched. Exporter `7d1edf0`.
      Full log: `WORKTRACK/archive/changelog.md`.

- [x] **Gates-in-scripts + room pauses + home_status simplification + agent
      tools (2026-10-24, owner request)** — Exporter `cd8c26a` (+`f0d9ffe`):
      - **Gates folded into behavior-box scripts** (`if:`/`then:` wrapper at the
        top of `ceiling_lights_sync`, `uteljus_sync`, `outside_light_sync`,
        `lock_by_status`) — automations are now trigger→script only. **GOTCHA:
        YAML `script:` objects have NO top-level `condition` key** (HA disables
        the script); use `- if:`/`then:`. `lock_doors`/`nattmode` stay ungated
        so `goodnight` always locks.
      - **Room-schedule pause toggles:** `input_boolean.automatik_sovrum` /
        `automatik_isac` + blueprint `pause_entity` input.
      - **#024 DONE:** `home_status` state uses lexicographic `HH:MM:SS`
        compare (proof: 0 mismatches offline). **#033 DONE:** `next_wake`/
        `next_bedtime` attributes added.
      - **config_tools v0.4.0:** write allowlist += `input_*/*.yaml` (no reload —
        returns "needs restart_core"); new `set_label` tool (registry
        `async_update_entity`, verified live via the chat agent) + `restart_core`.
      - **Latent blueprint bug fixed:** room_schedule `fade_out` trigger's
        variable template (`off_enabled` undefined in limited `at:` templates)
        + flow-style `{label,value}` selector options failed validation; both
        rewritten (plain `at: !input off_entity` + block-form options).
      Full log: `WORKTRACK/archive/changelog.md`.

- [x] **Scripts/templates/helpers simplification (2026-10-24, round 2)** — the
      daylight fact became `binary_sensor.light_outside` (latched-hysteresis
      template `template/daylight.yaml`) replacing `outside_light.yaml` +
      `input_boolean.light_outside` + `script.outside_light_sync`; the seasonal
      `christmas_lights` rule is single-sourced in `script.uteljus_sync`
      (`uteljus_pa/av` are pure utelampa one-taps now); boot reconcile centralized
      in `automations/boot_reconcile.yaml` → `script.reconcile_all`
      (**convention: no `ha_ready -> on` triggers in new automations — extend
      reconcile_all instead**); registry fixed `script.lock_by_status` +
      `binary_sensor.light_outside` entity names and purged the 3 deleted
      entities' orphans; agent handbook/examples rewritten to live state.
      Live: 9 automations + 12 scripts, reconcile verified on real `ha_ready`
      boot replay. Full log + exporter commit `d6d7684`:
      `WORKTRACK/archive/changelog.md`.

Nothing else is in flight.

## Improvement candidates

Best-practice review, 2026-10-23 — sourced from online HA best practices
(official docs + community) and audited against `config/`. Full reference:
`docs/BEST_PRACTICES.md`; `home_status` machine: `docs/deep_dive_home_status.md`.
Nothing deployed — each waits on ⬜ owner decision before edit.

- [x] #024 **`home_status` template simplification (option B)** — **DONE
      2026-10-24**: `template/home_status.yaml` now compares zero-padded
      `HH:MM:SS` strings lexicographically instead of `as_timestamp`/date-concat
      math; equivalence verified offline (0 mismatches, all weekdays × minutes).
      Live: sensor renders `awake` with `is_workday`/`next_wake`/`next_bedtime`.
      (#033 landed in the same edit, see below.)
- [x] #025 **Startup-grace gate repetition** — 12 automations share the
      `ha_started` + checklist gate; **superseded by the #026 consolidation**
      (2026-10-23): the ceiling/night automations got the gate folded into a
      single location. Remaining per-file duplication is small and acceptable.
- [x] #026 **Ceiling-lights consolidation (Taras pattern)** — **DONE 2026-10-23**:
      four same-shape automations → one data-driven automation over
      `sensor.home_status` + `input_boolean.light_outside` + `choose`, targeting
      label `taklampa`. ~99→~40 lines; 4 orphaned registry automations purged.
- [ ] #027 **Two hunts for the old `home_status` string compare** — verify at
      the same time: (a) the candidate `wake > bed` midnight flip behaves like
      today (it does — no regression), (b) owner confirms "Sun = weekday-bed"
      axis is intended family behaviour.
- [x] #028 **Labels for seasonal sockets** — **DONE 2026-10-23**: labels
      `taklampa`/`natthorn`/`sasong`/`utelampa` created + entities assigned;
      night/ceiling automations target them (`target.label_id`; verified live —
      `entity_id: label.X` is a silent no-op). `christmas_sockets` group gone.
- [x] #029 **Scenes vs groups membership duplication** — **RESOLVED 2026-10-23**:
      groups.yaml now holds only `family`; scene comment points to the labels
      instead of dead group names.
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
- [x] #031 **Labels for cross-cutting concerns** — **DONE 2026-10-23**: labels
      `taklampa`/`natthorn`/`sasong`/`utelampa` created + assigned; ceiling,
      night-light, christmas and nattmode automations target them. Groups
      `ceiling_lamps`/`night_lamps`/`christmas_sockets` deleted.
- [x] #032 **Pause-toggle helpers** — **DONE 2026-10-23**: `input_boolean/
      automatik.yaml` adds `automatik_taklampor` + `automatik_nattlampor`
      (default on, restored across restarts). Ceiling automation and both night
      automations gated on their toggle. `automatik_uteljus` not added — the
      daylight flag (`light_outside`) is the sensor, not a behavior worth pausing.
      **Ext 2026-10-23**: + `automatik_las` gate for the merged lock automation;
      Automatik card shows all 3 toggles.
- [x] #033 **`next_wake`/`next_bedtime` template sensor** — **DONE 2026-10-24**:
      shipped as `home_status` attributes in the #024 rewrite (they were the
      only consumers; no separate sensor entity needed).
- [x] #034 **`script.goodnight`** — **DONE 2026-10-23**: composes `script.nattmode`
      + `script.lock_doors`; verified live (ceiling off, night corner dim, doors
      locked). Voice/dashboard "god natt" one-shot.
- [x] #035 **Christmas sockets via label + scenes/groups de-dup** — **DONE PARTIAL
      2026-10-23**: label `sasong` replaces the `christmas_sockets` group (#028/
      #031); scenes keep static membership (scenes can't target labels) but the
      comment documents the label source. **Superseded 2026-10-23**: scenes
      deleted entirely (see round below) — labels + scripts fully replace them.
- [x] **Script behavior-boxes + twin-automation collapse round** — **DONE
      2026-10-23**:
      - `scripts/uteljus_pa`, `uteljus_av`, `sasong_sync`, `lock_doors`,
        `goodnight`, `taklampa_pa` (label-driven one-taps replacing the static
        scenes); `nattmode` + `light_on_with_transition` (area param) from #026.
      - Twin automations collapsed 6→3: `night_lights` (`to: [on, off]` + one
        `choose` on `light_outside`→`uteljus_pa`/`uteljus_av`), `locks`
        (`to: [sleep, away]`→`lock_doors`, gated on `automatik_las`),
        `outside_light` (both thresholds + one `choose` on current lux).
      - `scenes.yaml` deleted — the 2 static scenes duplicated the taklampa /
        utelampa labels 1:1 and scenes can't target labels. `script.taklampa_pa`
        (= label taklampa) + `script.uteljus_pa` (= label utelampa) replace them.
      - 6 orphaned registry entities purged via WebSocket (old `p4_lock_doors_*`,
        `p4_night_lamps_*`, `p4_outside_daylight_flag_*` + 5 leftover `set_*`
        scripts from an earlier cleanup). Result: 11 automations + 9 scripts,
        0 unavailable.
      - Verified live on the real trigger path: `automatik_las` gate blocks/rises
        lock on the `ha_started` boot re-trigger; night fully off in bright /
        all on after dark; `taklampa_pa` turns all 5 fixtures on. Note: the
        `automation.trigger` *service* bypasses conditions — use real state
        changes or `test_condition` to verify gates.
      - `ha core check` green, exporter `3e94474`.

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