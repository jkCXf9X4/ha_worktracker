# Frontend pairing — Python backend ↔ family chat agent

**Status:** designed 2026-10-26, not yet implemented. Companion to
`docs/TESTED_POLICY_PLAN.md` (Path E) and `docs/invariants.md`.

## 1. Goal and pairing principle

The backend (`domain/daylight` + pyscript adapters) is the **sole owner of the
decisions** — pure, pytest-tested, deployed as native modules under
`/config/pyscript/native_domain/`. The frontend is the family chat agent
(OpenRouter conversation agent, `conversation.deepseek_deepseek_v4_flash_0731`,
`assist` LLM API + `config_tools`).

> The frontend must be able to **reason with** the policy and **request intent
> through** it — but never **act as** the policy or **past** it.

"Reason with" = query the same pure functions and entities the adapters use, so
explanations and what-ifs are provably consistent with what actually runs.
"Intent through" = every mutation routes through an owning, documented script or
automation (single-ownership invariant), never a raw service call that bypasses
a decision owner.

## 2. Three surfaces

| Surface | Mechanism | Now | Contract safety |
|---|---|---|---|
| **Read facts** | Exposed derived entities (`sensor.home_status`, `binary_sensor.light_outside`, `_ps` twins with decision attributes) | ✅ live | Read-only |
| **Reason / what-if** | `config_tools__policy_query` tool (runs the same `domain` functions) | ❌ missing | Read-only |
| **Intent** | Exposed wrapper scripts (native `script.*` ActionTool) | ❌ missing | Routes through owners |

The `assist` LLM API does NOT expose arbitrary services — so reason goes through
an `llm`-platform tool (config_tools), intent goes through **scripts** (which
HA auto-exposes as tools), not raw helper/entity control.

## 3. Surface 2 — `config_tools__policy_query` (read-only oracle)

Implemented in `custom_components/config_tools/` (the existing `llm` platform —
no new agent/component plumbing).

- **Imports the same files pyscript runs:** `/config/pyscript/native_domain`
  via the verified idiom (`sys.path.insert(0, ...)` +
  `importlib.invalidate_caches()`, `allow_all_imports` irrelevant here since
  HA core does the importing). HA core shares the module with pyscript's native
  context, so *reasoning and execution cannot drift*.
- **Params (probatio schema):**
  - `cluster`: one of `home_status` | `daylight` | `night_lights` (required).
  - `inputs`: optional JSON of input overrides (e.g. `{"lux": 100}`,
    `{"paused": true}`, `{"now": "2026-10-26T21:00:00"}`). Omitted inputs are
    snapshotted from current HA state into the exact `*Inputs` dataclasses the
    adapters use.
- **Returns:** structured `{cluster, inputs_used, decision, attrs}` where
  `decision` is the enum value(s) (`status`, `light_outside`, `utelampa`/
  `sasong`) and `attrs` the dashboard attributes (`is_workday`, `next_wake`,
  `next_bedtime`).
- **Drift guard (load-bearing):** the tool keeps an md5 signature of the
  `domain/` files it last imported. On each call it recomputes the signature;
  if it changed (a deploy pushed new files), it drops `domain.*` from
  `sys.modules`, invalidates importlib caches, and re-imports. So after
  `pyscript.reload` the oracle always matches what the adapters run.
- **Annotations:** `read_only=True, destructive=False, idempotent=True`. No
  admin gate (consistent with read tools) — the tool only *computes*.
- **Examples the agent can now answer honestly:**
  - "Vad händer med nattlamporna om jag pausar automatik nattlampor?" →
    `night_lights` with `inputs={"paused": true}`.
  - "När vaknar vi nästa gång?" → `home_status`, read `attrs.next_wake`.
  - "Varför är light_outside på?" → `daylight` snapshot + decision.
  - "Om uteljuset sjunker till 100 lux, släcks utelampan?" → `daylight` with
    `inputs={"lux": 100}`.

## 4. Surface 3 — intent via exposed wrapper scripts

Decision (2026-10-26): **exposed wrapper scripts**, not a broadened
`call_service` allowlist. HA natively exposes `script.*` entities as LLM tools
(ActionTool, schema = the script `fields`, returning the `response_variable`
string), so intent works with zero component code.

- Add small behavior-box scripts to `/config/scripts.yaml` (or a
  `scripts/*.yaml`-style file), each a thin wrapper that flips a **documented
  input helper** and ends with `stop` + `response_variable`:
  - `script.toggle_christmas_lights` → `input_boolean.christmas_lights` toggle
    (the seasonal rule's owner `script.sasong_sync` reacts via the christmas
    toggle automation).
  - `script.pause_nattlampor` / `script.pause_taklampor` /
    `script.pause_las` → the three `automatik_*` kill-switch toggles
    (family pause gates).
  - Optional: `script.set_schedule_override`-style writers if the owner ever
    wants schedule edits back (2026-10-22 removed them by owner decision — do
    NOT reintroduce without a new decision).
- **Why wrappers and not a helper allowlist in `call_service`:**
  - The wrapper script *is* the documented interface; it can add guards
    (e.g. refuse when `ha_ready` is off), and its existence/description is the
    reviewable artifact.
  - A bare `input_boolean` allowlist would let the agent flip arbitrary helpers
    (including `ha_started`) with no guardrail.
  - It matches the already-established pattern (`script.goodnight`,
    `script.uteljus_pa/av`, the removed-but-working 5 schedule writers).
- **Exposure:** each wrapper exposed to `conversation` via
  `homeassistant/expose_entity`. The three `automatik_*` toggles themselves stay
  unexposed to the agent (only their script wrappers exist as tools).
- **Safety note (from the skill):** `automation.trigger` bypasses conditions;
  these wrappers flip input toggles and rely on *real state-change triggers*,
  so they exercise the honest path (no fake `last_triggered`).

## 5. Hard red lines (unchanged, restated for the frontend)

- No agent path may write to `/config/pyscript/` or any `domain/` file —
  `config_tools.write_file` already cannot (path allowlist), a feature.
- No agent path may call services on `label.utelampa`/`label.sasong` directly —
  single ownership lives in `resolve_night_lights`/`script.uteljus_sync`.
- No agent path may reach `light.isac_tak` / `switch.isac_lekstuga` / the
  bedside lamp *as automation*. **Owner decision 2026-10-26: keep these exposed
  to the chat agent** (family manual intent via voice/chat is allowed; the
  invariant targets probes/spikes/automations). This is recorded here so the
  "never trigger on in isacs_rum" wording is understood as automation-scoped.
- `policy_query` computes decisions only — it never calls services.

## 6. Rollout

1. Implement `PolicyQueryTool` in `custom_components/config_tools/`
   (`tools.py` + `llm.py` tool list; bump manifest to 0.5.0).
2. Unit-reason: run the domain package directly under pytest for the tool's
   snapshot/override mapping (small adapter tests in this repo's `tests/`).
3. Deploy via the established path: push `config_tools/` + core restart (the
   `llm` platform lazy-scan needs it), exporter sync.
4. Add the wrapper scripts to `/config/scripts.yaml` (list format!), expose
   them, verify each through `conversation/process`.
5. Verify tool via `conversation/process` prompts + confirm the side effect is
   absent (read-only) and, for scripts, that the owning automation/script
   reacted (trace / state change).
6. Update `docs/AGENT_TOOLS.md`, this doc, `WORKTRACK/NEXT.md`, changelog.

## 7. Non-goals (this design)

- No new conversation agent / custom sentence engine.
- No reverse path: the chat agent stays unable to edit policy.
- No broadening of `ALLOWED_SERVICE_ACTIONS` (remains `light|switch`
  on/off/toggle) and no new writable path in `config_tools`.