# Tested-Policy Architecture Plan — HA automation as a maintainable Python project

Status: **planned (2026-10-25)** — owner-decided, not yet started. This is the
design record for evolving the YAML automation stack into a modular, testable,
LLM-maintainable architecture. It supersedes nothing live; it plans forward.
Implementation progress is tracked in `WORKTRACK/NEXT.md` and the delivery
record in `WORKTRACK/archive/changelog.md`.

Repo: `ha_config_worktracker` (management/docs/tooling) with `ha_config` as the
mirror submodule. Source of truth for *config state* is the HA VM `/config`
(push-only Git Exporter); source of truth for *managed logic* becomes this repo
(see §4 — reconciliation rule).

---

## 1. Motivation

The current stack (pure YAML automations + `input_*` helpers + behavior-box
scripts + templates) is small — 8 automation files (~158 lines), 12 scripts
(~361 lines) — and works. The scaling problem is not "YAML can't express it",
it is **verifiability**: the only quality gate today is `ha core check`
(syntax). Nobody can prove the deployed YAML *implements the intended policy*,
and the LLM build agent has no regression net. The architecture brief
proposes a three-layer, framework-independent Python shape; this plan adapts
it to this repo with concrete, bounded steps.

Key facts that shaped the plan:

- **Pyscript was shelved 2026-10-20** (silent watchdog, scripts never
  evaluated) — but the current Pyscript **2.1.0 supports HA 2026.5+** (we run
  2026.10.2), and the docs point to likely, cheaply-diagnosable causes
  (config-method mixing, the 2.0.0 decorator-manager refactor w/ the documented
  `legacy_decorators: true` fallback, watchdog/inotify in the container). See
  §6 Phase A+.
- **Config source-of-truth is the VM**, and the exporter is push-only. Any
  plan must respect that (reconciliation rule, §4).
- **Standing convention (binding):** native YAML + helpers + behavior-box
  scripts; custom Python retired. This plan re-opens Python *deliberately and
  incrementally*, through a go/no-go gate, not by fiat.

---

## 2. Architecture (three layers)

### Domain & policy layer
- Pure Python functions, domain models, decision rules, state transitions.
- **No** Home Assistant imports, entity access, network calls, filesystem, timers.
- Owns: the policy decisions. Inputs (time, occupancy, modes, overrides) are
  passed explicitly; the policy never reads them from HA itself.
- Runs identically under `pytest` on the dev machine and (Path E) as native
  compiled modules on the VM.

### Adapter layer
- **Binding** ("when"): subscribe to state changes, events, time triggers.
- **Ports**: gather + validate inputs, translate to domain models, invoke
  policy, translate results to service calls, log decisions/failures, handle
  duplicates/concurrency/restarts/missing inputs.
- Thin. Does **not** re-implement business rules.
- Initial form: the existing YAML automations + behavior-box scripts (Status
  Quo, "verify" mode). Candidate migration: Pyscript adapters (Path E) or a
  custom integration adapter. The domain layer does not change between them.

### Infrastructure layer
- HA entities, integrations, configuration, deployment, logging, monitoring.
- Not managed by this plan beyond what already exists (`ha core check`,
  exporter, `config_tools`).

---

## 3. Principles (from the brief, adapted)

1. **Separation of concerns** — domain/adapter/infra; domain depends on nothing.
2. **Explicit interfaces** — each subsystem documents purpose, inputs/outputs,
   dependencies, state owned, entities permitted to control, invariants,
   missing/stale-input behavior, startup/restart/recovery. (New
   `docs/subsystems/*` + `docs/invariants.md`.)
3. **Single ownership** — every automatically controlled device has one owner;
   others communicate via the documented interface (`script.uteljus_sync` owns
   the seasonal rule; `uteljus_pa/av` never touch `sasong`, etc.).
4. **Minimal migration** — migrate one subsystem at a time; keep native YAML
   where appropriate; do not rewrite the whole system up front.
5. **Repo is source of truth for managed logic** — production uses a known git
   commit; `mirror == build` checks catch drift (reconciliation rule, §4).
6. **No framework-specific abstractions in the domain** in anticipation of a
   possible future migration — only build what there is a demonstrated need for.

---

## 4. Reconciliation rule: VM is source of truth for state, repo for logic

- **VM `/config` stays source of truth** for runtime/config state: entity
  registry, integrations, `input_*` live values, everything the resident chat
  agent touches.
- **This repo becomes source of truth for managed logic**: the domain package,
  the golden matrices/fixtures, the deploy/verification tooling, and the policy
  docs. Deployment writes *derived/verified artifacts* onto `/config`; a check
  (`mirror == build`, mirror == VM md5) fails on drift.
- This preserves the exporter's push-only model while giving the LLM build
  agent a place where its work is provable *before* it touches the live VM.

---

## 5. Dev chain (execution-layer-agnostic)

```
local repo (managed logic)
  1. edit domain/ policy in pure Python (+ doc guides)
  2. uv run pytest / ruff / mypy             # unit + type + lint gates
  3. tools/qa.sh: yaml.safe_load of all automations/scripts/templates
     + (Path V) golden/Jinja parity; (Path E) adapter-driven fixtures
     + tools/summarize.py consistency (existing)
deploy (build agent, single gate)
  4. tar-over-SSH push → check → reload/restart smallest runtime → md5 verify
  5. tools/probe_vm.py (WS, read-only): render_template, test_condition,
     boot-reconcile trace inspection
  6. commit + docs + worktrack; record rollback point
rollback
  7. prior commit's exported files → tar-push back → check → reload
```

Two build agents must **not** blur:

- **Build agent** (this opencode, on this machine): full repo + SSH. Real
  development + tests + deploy live here.
- **Resident chat agent** (`config_tools` + OpenRouter intents, inside HA):
  family-facing, deliberately bounded to reloadable YAML + exposure-gated
  `call_service`. It never gains Python/policy control. `config_tools`
  `write_file` cannot write pyscript paths — a feature.

---

## 6. Phases

### Phase A — Quality skeleton (decoupled; lands regardless of spike outcome)

- `pyproject.toml` via **uv** + `uv.lock`. Domain = pure stdlib
  (dataclasses/enum/datetime/typing) → zero VM pip requirements. Dev deps:
  `pytest`, `ruff`, `mypy`, `pyyaml`; `jinja2` is added only if Path V's
  parity harness is needed.
- Layout (in this repo; `ha_config` submodule stays the mirror):
  ```
  domain/daylight/{__init__,models,home_status,daylight,night}.py
  adapters/pyscript/...                     # Path E only, added after A+
  tests/{unit/daylight, fixtures/daylight, parity/}
  tools/{qa.sh, deploy.py, probe_vm.py, summarize.py}
  docs/subsystems/daylight.md   docs/invariants.md
  ```
- `tools/qa.sh`: `pytest` + `ruff check` + `mypy domain/` + `summarize.py`
  consistency gate (exit 1 on failure). Zero HA access. **Green before any
  deploy.**
- Update `SKILL.md` dev-chain section + `WORKTRACK/NEXT.md` + changelog.

### Phase A+ — Bounded Pyscript spike (go/no-go gate, ~1–2 SSH sessions)

**Isac-safety invariant is active from here on** (§8). Ordered diagnostic
ladder:

1. HACS-install pyscript (HACS-default) → core restart → add integration **via
   UI config flow only**. **No `pyscript:` block in `configuration.yaml`** —
   Oct-20's suspected YAML+UI config-method mixing is deliberately avoided
   (Pyscript docs: "you can't mix these two methods").
2. Probe file under `/config/pyscript/`: module-load `log.info`, set
   `sensor.pyscript_probe`, one `@time_trigger("startup")` function. Check:
   integration listed, no setup errors, probe sensor appears.
3. Module loads but startup trigger never fires → new-decorator-subsystem bug →
   **`legacy_decorators: true`** (documented fallback, never attempted 10-20).
4. Watchdog: `touch` the file → confirm auto-reload (rules in/out the
   container-inotify suspect).
5. Debug logging at `custom_components.pyscript.apps.*: debug` (2.x logger
   path — the changelog only set the parent `custom_components.pyscript`).
6. If green: `pyscript.generate_stubs` (IDE stubs in `modules/stubs`) +
   **Jupyter kernel** → live REPL for the LLM agent on the VM.
7. Record findings + decision in changelog.

**Gate:** spike green → **Path E**; red → **Path V**. Nothing before this is
wasted either way.

### Phase B — Domain extraction (identical for both paths)

- `home_status.py`: `{family_home, weekday, now, wake_wd/we, bed_wd/we}` →
  `away|sleep|awake` + attrs (`is_workday`, `next_wake`, `next_bedtime`).
  Exact translation of `template/home_status.yaml`.
- `daylight.py`: `{lux, on_thr, off_thr, current_state}` → latched hysteresis
  (default 400 on / 150 off). Translation of `template/daylight.yaml`.
- `night.py`: `{light_outside, christmas_lights, paused, ha_ready}` →
  `{utelampa: on|off|skip, sasong: on|off|skip}`. Translation of the
  `script.uteljus_sync` decision table.
- `tests/fixtures/daylight/*.yaml`: matrices incl. boundary,
  `unavailable`/stale inputs, conflicting modes, failure cases (brief §6).
  Doc comments map fixture fields → real entities; **entity_ids never appear in
  policy code**.

### Phase C — Binding layer (spike-conditional)

**Path E (primary, contingent on A+ green):**
- Domain ships as **native compiled** modules under `/config/pyscript/
  native_domain/` — NOT `/config/pyscript/modules/` (that tree is re-parsed by
  pyscript's AST interpreter, which is not native and cannot run dataclasses/
  StrEnum; verified 2026-10-25). Bootstrapped via `sys.path.insert(0, ...)` +
  `importlib.invalidate_caches()` + `allow_all_imports: true`. The
  `invalidate_caches()` is load-bearing: importlib caches a failed directory
  scan of a new sys.path entry (e.g. files mid-push) and later imports then
  fail silently. Native = full language, compiled speed, and the *same file
  pytest runs*. Pure stdlib → no VM pip.
- Thin pyscript adapters in `/config/pyscript/scripts/daylight.py`:
  `@state_trigger`/`@time_trigger` on the existing entities → gather inputs →
  call domain → call services.
- **Entity-stability contract:** derived facts keep exact IDs
  (`sensor.home_status`, `binary_sensor.light_outside`) so existing YAML
  automations/scripts react unchanged; only the *decision origin* moves.
- Native-module changes are outside pyscript's hot-reload graph → changes need
  `pyscript.reload`/restart on deploy (documented).
- **Shadow-mode first (done 2026-10-25, Phase C):** adapters write `_ps` twin
  entities (`sensor.home_status_ps`, `binary_sensor.light_outside_ps`,
  `sensor.night_lights_ps`) and log mismatches vs the still-live YAML — zero
  service calls, zero behavior change. Flipping ownership of the real IDs is
  Phase D.

**Path V (fallback, fully planned):** domain = tested specification; golden
matrix + Jinja parity harness (sandboxed Jinja2, stubbed `states()`/`is_state()`
/`now()`/`as_timestamp`/`timestamp_custom`/`timedelta`) renders the *actual
deployed templates* against the same fixtures and asserts Python output ==
live-template output. Bounded, cross-checked duplication. For script-only rules
(`uteljus_sync`) parity is via live `test_condition`/trace, not local execution.

### Phase D — Deploy / verify / rollback (pilot cluster)

- `tools/deploy.py`: tar-over-SSH push (native domain modules + pyscript dir)
  → `pyscript.reload` (**not** full core restart) → `ha core check` unaffected
  → exporter restart → md5 `mirror == VM` verify → probe smoke.
- `tools/probe_vm.py` (WS, read-only): `render_template` smoke of still-live
  templates, `test_condition` on cluster gate conditions, boot-reconcile
  **trace inspection**. Uses the honest-testing recipes in the skill — never
  `automation.trigger` for gate checks; never trusts `last_triggered` alone.
- **Pre-deploy safety ritual:** `automatik_nattlampor`, `automatik_taklampor`,
  `automatik_las` **off**; grep the domain allowlist against `isacs_rum` area/
  label data.
- Rollback: restore previous exporter commit's files → `pyscript.reload` →
  toggles stay off → probe. Derived facts are recomputed, not stored → no
  persisted-state rollback needed.

### Phase E — Agent workflow + evaluation gate

- Encode the brief's §7 discipline into `SKILL.md` + `docs/invariants.md`
  (incl. the binding `isacs_rum` invariant, §8). **DONE 2026-10-25:** skill
  "§7 agent workflow" + "Managed-logic deploy path" + "Pyscript gotchas"
  sections; invariants doc enumerates the rules.
- **Success test (the acceptance demo, run when Phase D (ownership flip) is
  ready):** change the off-hysteresis threshold in `daylight.py` → `qa.sh` +
  fixtures force the matrix update → `deploy.py` → probe green → rollback
  tested. Demonstrates: localized change, independent domain validation,
  adapter integration, safe deploy/rollback with no collateral behavior
  change.

---

## 7. Deployment & safety

- Dev and production environments are separate (this repo + VM).
- Deploy only a validated commit; preserve the currently deployed version and
  relevant config before applying (exporter git + md5 baseline).
- Validate before release; controlled install; reload/restart the smallest
  affected runtime (`pyscript.reload`, not a full restart); post-deployment
  health check + log inspection; documented rollback accounting for persisted
  state and physical actions (toggles off first).
- Credentials stay out of git and logs; least-privilege access; approval
  required for high-risk device behavior / infra / safety-sensitive changes.

---

## 8. Binding invariants

1. **NEVER trigger any light on in `isacs_rum`** (owner instruction, Isac
   asleep): `light.isac_tak`, `switch.isac_lekstuga`, the bedside lamp. Applies
   to all workstreams — probes, spikes, pilot, tests. The sovrum/isac
   morning-fade automations stay pure YAML and are **not** part of the pilot.
2. Never use `automation.trigger` to test gates/conditions (bypasses
   conditions, pollutes `last_triggered`). Use real state changes, WS
   `test_condition`, or the `ha_started` off→on boot replay; read **traces**.
3. `config_tools` sandbox remains the resident agent's ceiling: admin-gated
   writes to reloadable YAML only; no pyscript/python paths; secrets never in
   git/logs.
4. Per-subsystem entity ownership — a subsystem only controls what its module
   documents; cross-subsystem intent flows through documented interfaces.
5. Policy code is pure: no entity_ids, no service calls, no I/O, no global
   mutable state, deterministic on explicit inputs.

---

## 9. Risks / assumptions (honest)

| Risk | Mitigation |
|------|-----------|
| Pyscript still broken on HA 2026.10.2 even with `legacy_decorators` | Phase A+ drop is clean → Path V, which is fully planned; zero loss |
| Jinja parity harness can't stub a filter used by a pilot template | Falls back to live smoke-only for that template; flagged, not blocked |
| `allow_all_imports: true` broadens pyscript's import surface | Acceptable for self-authored code (docs bless it); secrets stay out of `/config/pyscript`; `config_tools` cannot write there |
| Native modules outside hot-reload graph | Deploy step always `pyscript.reload`; documented |
| Oct-20 root cause is an unfixed new-decorator bug | Spike ladder isolates it in ~2 sessions; `legacy_decorators` is the documented escape hatch |

---

## 10. Success criterion

The LLM build agent can make a **localized** change to a subsystem, validate
its domain behavior independently (`qa.sh`), demonstrate the adapter
integrates (`probe_vm` / parity), and **deploy or roll back** without
unintentionally affecting unrelated automation — and never once touching a
light in Isac's room.