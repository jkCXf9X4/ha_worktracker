# P9 — `config_tools__call_service`: whitelisted service-action tool for the chat agent

Status: **DEPLOYED + VERIFIED 2026-10-23 (v0.3.0), hardened v0.3.1** —
component + `AGENT_HANDBOOK.md` deployed to the VM via tar-over-SSH, core
restarted, exercised live through the chat agent (real `light.turn_off`/
`turn_on` state change via the tool + real HA validation error on a bogus
`data` field relayed verbatim), exporter pushed (`989e5a0` verified; v0.3.1
pending), committed. Implementation history in this file.

> **v0.3.1 hardening (2026-10-23, applied here / deferred above)**
> Critical review led to these adjustments (see §6):
> 1. **Admin gate dropped for `call_service`** — now *exposure-only* (the
>    exposure registry is HA's own per-assistant permission model). Admin gate
>    remains on `write_file`/`check_config`/`reload`.
> 2. **`data` is a typed probatio schema** (enumerated fields) instead of the
>    opaque `selector.ObjectSelector()` → unknown keys fail at parse time with
>    a helpful "did you mean '...'" error; HA's service schema still backstops.
> 3. **`_atomic_write` is real now** (tempfile + `os.replace`, chmod 0644) —
>    a crash can no longer leave a truncated YAML file.
> 4. **`_LOGGER` added** — `info` on every successful `call_service`,
>    `warning` on failures, `exception` on reload/device-trigger errors.
> 5. **`manifest.json`** → `0.3.1`, `"integration_type": "service"`, honest
>    `iot_class: local_polling`.
> 6. **Native alternative documented + added:** `scripts.yaml::korridor_blink`
>    (`fields: flash|transition`) — exposed scripts surface as `script.*` LLM
>    tools automatically, so the blink use-case is achievable with zero
>    component code; `call_service` remains for the generic gap.

## Goal

Give the family chat agent (OpenRouter/DeepSeek, assist LLM API) the ability to
call a **small whitelist of HA services** — e.g. `light.turn_on` with `flash:
short|long` — so it can physically **blink lamps** and pass real service
parameters the entity intents (`intent__HassTurnOn`, `light__HassLightSet`)
cannot carry (`flash`, `effect`, `transition`).

Background verified:
- ZHA lights report `supported_features` = `40` = FLASH(8)+TRANSITION(32) → they
  physically support blinking via `light.turn_on` `flash:`.
- The `assist` API (helpers/llm.py) only surfaces entity intents + exposed
  scripts + custom `llm`-platform tools. No generic "expose any service" toggle.
- HA's `ActionTool` (helpers/llm.py:764) is script-only for schema (its param
  cache covers scripts, not arbitrary services) → we build the tool ourselves.

## 1. Component changes (`ha_config/config/custom_components/config_tools/`)

### `const.py`
Add the allowlist (single source of truth):
```python
ALLOWED_SERVICE_ACTIONS = {
    "light": {"turn_on", "turn_off", "toggle"},
    "switch": {"turn_on", "turn_off", "toggle"},
}
```
(light/switch only. `group.*` entities work via core's group expansion.)

### `tools.py` — new `CallServiceTool`
- `name = f"{DOMAIN}__call_service"`, `title = "Call allowed service action"`,
  `integration = DOMAIN`.
- `parameters` (probatio.Schema):
  - `service` (required str) — e.g. `"light.turn_on"`.
  - `entity_id` (required str) — **one** exposed entity (single target keeps it
    simple + bounded; groups cover multi-light cases).
  - `data` (optional dict) — service-specific fields (`flash`, `brightness_pct`,
    `transition`, `effect`, …).
- `async_call` flow:
  1. Split `service` → `domain`, `service_name`.
  2. Allowlist check `domain in ALLOWED_SERVICE_ACTIONS and service_name in
     ALLOWED_SERVICE_ACTIONS[domain]` else error (list allowed services).
  3. Admin gate — reuse `_is_admin(hass, llm_context)` (same as
     `write_file`/`reload`). Decide per deployment: plan = **admin-gated**;
     relax to "any user, exposure-bound" if family members must blink too.
  4. Target resolution — entity must exist in entity_registry AND be exposed to
     `llm_context.assistant` via
     `homeassistant.exposed_entities.async_should_expose`; else error.
  5. `service_data = {**(data or {}), "entity_id": entity_id}`.
  6. `hass.services.async_call(domain, service_name, service_data,
     context=llm_context.context, blocking=True)`.
     HA's own schema validation runs here → bad/typo'd fields return the real
     Voluptuous error to the model.
  7. Result: re-read entity state after the blocking call →
     `ToolResult(data={"result": "ok", "entity_id": …, "state": …, "attributes": …})`;
     errors relayed with `error=True`.

### `llm.py`
Register `CallServiceTool()` in the `async_get_tools` list (7 → 8 tools).

### `manifest.json`
Bump version `0.2.0` → `0.3.0`.

## 2. Agent handbook + docs

### `config/docs/AGENT_HANDBOOK.md` (read by the agent via `config_tools__read_file`)
- Add `config_tools__call_service` row to the tools table.
- New section "Call a service action (e.g. blink a lamp)":
  - Get the real `entity_id` first (live-context / GetLiveContext tool) —
    **never invent entity ids**.
  - Example: `call_service service="light.turn_on" entity_id="light.korridor_tak" data={"flash":"short","transition":2}`.
  - Notes: single exposed entity, admin-only, `data` fields must match the real
    HA service (HA rejects bad fields), prefer this over intents when a
    parameter (flash/effect/transition) is needed.
- Extend "Absolute rules" with the "never invent entity ids; use live-context"
  rule.

### `docs/AGENT_TOOLS.md` (P8 design doc)
- Add §3.6: `config_tools__call_service` — allowlist table, admin gate,
  exposure boundary, error semantics, why not `ActionTool`.

### `.opencode/skills/home-assistant/SKILL.md`
- Extend the config_tools section: new tool, allowlist, admin+exposure gating,
  "blink = `light.turn_on` flash short/long", feature-bit background
  (40 = FLASH+TRANSITION), deploy/verify notes.

## 3. Deploy + verify (on the VM) — **EXECUTED 2026-10-23 ✅**

1. Edit component + handbook locally; `yaml.safe_load`/py-compile-verify; push via
   tar-over-SSH to `/config/...` (md5-verified VM == mirror). ✅
2. `ha core restart` (new Python code; config_tools is already top-level, no
   `configuration.yaml` change). `ha core check` green. ✅
3. Verify via `conversation/process` (agent
   `conversation.deepseek_deepseek_v4_flash_0731`):
   - "blinka korridorlampan" → real side effect: the model called the tool with
     `light.turn_on` `data={"flash":"short"}`; a deterministic follow-up forced
     the tool to `light.turn_off` → state flipped `on`→`off` and back `on` via
     `light.turn_on`, with `response.data.success == []` (intent path would
     populate `success`, so an empty list is the discriminator that the tool
     ran, not the built-in entity intent). ✅
   - bogus field (`data={"bogus_field":123}`) → the tool returned the REAL HA
     validation error verbatim: `Service call failed: not a valid option at
     'bogus_field'`, `error: true`; lamp untouched (still `on`). ✅
4. Git Exporter: restarted → "Exporter finished" → push `989e5a0`; mirror files
   md5-match the VM and the local repo. ✅
5. Committed repo (component + handbook + docs); `WORKTRACK/NEXT.md` +
   `docs/PLAN.md` progress log updated. ✅
6. Findings appended to the skill + this doc. ✅

### Verification notes / findings
- `llm_context.assistant` == `"conversation"` for the OpenRouter agent
  (conversation/models.py `as_llm_context`), so the exposure check
  `exposed_entities.async_should_expose(hass, "conversation", entity_id)` is
  the right boundary for all-in exposure.
- `data` is declared as `selector.ObjectSelector()` in the probatio.Schema → the
  model sees `{"type":"object"}` and HA's own service schema rejects bad keys.
- Admin gate passed with the long-lived token (admin user). If family members
  must blink too, flip `CallServiceTool.async_call` to exposure-bound (drop the
  `_is_admin` check).
- **Pre-existing fix carried in:** the VM had an older broken `_device_entity_ids`
  (`registry.get_entries_for_device_id` on `EntityRegistry` instead of
  `registry.entities.*`) — the repo version deployed here uses
  `registry.entities.get_entries_for_device_id` (HA 2026.10 API), fixing
  `find_device` on the live instance.

## 4. Open decisions (confirm before executing)

- ~~**Admin gating**~~ **RESOLVED 2026-10-23:** dropped for `call_service`;
  exposure-bound only (matches HA's native assistant-access model — the
  exposure registry is the per-assistant permission). Admin stays on the
  config-writing tools.
- **Allowlist scope**: light/switch only. Extend later (e.g. `scene`,
  `homeassistant.turn_*`) on request.

## 5. Open decisions → outcome / review follow-up (2026-10-23)

Critical review of the deployed setup (`tools.py`, manifest, docs) produced
§1-4 adjustments above. Full write-up of the review findings is in the session
log; durable conclusions are captured in `.opencode/skills/home-assistant/
SKILL.md` (config_tools__call_service section) and `AGENT_TOOLS.md` §3.6.