# P8 — Agent config tools (custom component `config_tools`)

Status: **DEPLOYED + VERIFIED, v0.4.0 (2026-10-24)** — 10 tools live on the VM
(`/config/custom_components/config_tools/`, manifest `version: 0.4.0`),
`config_tools:` in `configuration.yaml`, HA restarted, and the tools exercised
end-to-end through the chat agent. Toolset: `read_file`, `glob_files`,
`write_file`, `check_config`, `reload`, `find_device`, `device_triggers`,
`call_service` (P9), and — added in **v0.4.0** — `set_label` (entity-registry
labels) + `restart_core` (admin). The two registry tools close the
pre-existing gap: the agent can now resolve a friendly device name to a
`device_id`, enumerate the device's **live** trigger types, and relabel entities
via the registry — no hand-editing `.storage`. `bind_remote` stays deliberately
absent (the generic tools now cover that flow). The 5 schedule-writer scripts
were **removed** from `scripts.yaml` (owner decision: *Remove them entirely*);
live `input_*` helper values are not changeable by the agent — writes target
reloadable YAML only (v0.4.0 now also allows `input_*/*.yaml` writes, which
report "needs restart_core" since helpers have no reload service).

Design (mechanism + rationale) below; rollout executed per §5.

Gives the family chat agent bounded read/write control over the YAML config:
read/glob (everybody) and write/check/reload (admin-context only),
WITHOUT bash access. Registered as a custom component `llm` platform, so tools
appear in the same `assist` API the OpenRouter agent already uses.

## 1. Mechanism (verified in HA 2026.10 source)

- Custom components can contribute LLM tools by shipping an `llm.py` platform
  with `async_get_tools(hass, llm_context, api_id) -> LLMTools | None`, and
  declaring `"platforms": ["llm"]` in `manifest.json`
  (`homeassistant/components/llm/__init__.py`). The `llm` integration merges
  every loaded integration's platforms into the API instance
  (`async_get_tools` → `AssistAPI.async_get_api_instance`).
- The platform is only scanned for integrations in `hass.config.top_level_components`
  (`integration_platform.py::LazyIntegrationPlatforms.async_get_platforms`) →
  **the component must be loaded at startup** (`config_tools:` empty key in
  `configuration.yaml` + one core restart; write-tool can never touch that file).
- The `open_router` agent (`components/open_router/entity.py`) sends every
  `chat_log.llm_api.tools` to the model (JSON function schemas), and the chat
  loop (`conversation/chat_log.py::async_add_delta_content_stream`)
  **auto-executes tool calls** (via `APIInstance.async_call_tool`), appends
  `tool_result` content, and iterates while `unresponded_tool_results`. So a
  custom `Tool.async_call(hass, tool_input, llm_context)` is all that's needed —
  no agent-side changes.
- Tool names must be prefixed `{domain}__` (`config_tools__…`) or LLM platform
  validation raises a warning (`_async_report_tool_issues`).
- **No bash:** `shell_command`/`command_line`/`rest_command`/`python_script` all
  live in `configuration.yaml`, which is never writable by a tool. The component
  Python itself is trusted (ours, versioned); the **tools are the sandbox**.

## 2. Security model

| Rule | Detail |
|------|--------|
| Write allowlist | `automations/*.yaml`, `scripts.yaml`, `groups.yaml`, `template/*.yaml`, `input_boolean/*.yaml`, `input_number/*.yaml`, `input_datetime/*.yaml` (helpers: no reload service → report "needs restart_core", v0.4.0) — the reloadable domains + helpers. |
| Read/glob allowlist | Everything under `/config` **except** `secrets.yaml`, `.storage/`, `*.db`, `*.db-wal`, `*.db-shm`, `home-assistant.log*`, `configuration.yaml` (read OK? no — also exclude `groups.yaml.bak`). No paths outside `/config`. |
| Hard denylist (both) | `configuration.yaml`, `secrets.yaml`, `.storage`, DBs, logs, `custom_components/config_tools/` itself. |
| Admin gating | `read_file`/`glob_files` → everyone; `call_service` → any logged-in user, exposure-bound (`async_should_expose`); `write_file`/`check_config`/`reload`/`set_label`/`restart_core` → reject unless caller is admin + `llm_context.assistant` is the family agent's assistant name. |
| Size caps | read caps at ~8k chars (token budget); write rejects >64k; glob capped at 100 hits. |
| No secrets in output | read of `secrets.yaml` impossible by allowlist; redact `!secret`-referenced values never read anyway. |
| Determinism | `bind_remote` resolves device/trigger from registry + live enum; agent never invents `device_id`/subtypes. |

## 3. Tools (domain `config_tools`) — implemented

All **10** are implemented in `custom_components/config_tools/`:
`manifest.json` (`platforms: ["llm"]`), `__init__.py` (`CONFIG_SCHEMA =
cv.empty_config_schema`), `llm.py` (`async_get_tools` returns all tools
for `api_id == "assist"`), `tools.py` (pure-Python + HA registry/device-automation
helpers; no shell, no new deps).

### `config_tools__read_file`
- params: `path` (relative, must resolve under `/config`, allowlist check).
- Returns file text (truncated at ~8k chars) or an error string.
- Used for: agent self-audit, config Q&A ("what runs at 06:22?").

### `config_tools__glob_files`
- params: `pattern` (relative glob under `/config`, e.g. `automations/*.yaml`).
- Returns up to 100 matching paths. No content.

### `config_tools__write_file`
- params: `path`, `content`.
- Path must be in the write allowlist (canonicalized; reject `..`, symlinks).
- **Flow:** snapshot existing content in memory → write target → full config
  check (`async_check_ha_config_file`)
  → on errors: **restore the snapshot** (or delete the new file), return the error text
  and confirm nothing changed.
  On success: `automation.reload`/`script.reload`/`group.reload`/`template.reload`
  per file, return "written + reloaded".
- Note: `check_config` validates the whole config (not just the target file); report
  pre-existing unrelated errors as such (compare-before).

### `config_tools__check_config`
- params: none (optional `domain` to target reload after).
- Runs the same full validation as the write flow; returns errors/issues list or "OK".
- Lets the agent verify state before/after any change and diagnose.

### `config_tools__reload`
- params: `integration` ∈ `automation | script | group | template`.
- Calls the corresponding reload service; returns success/failure message.
- Explicit separate tool so the agent can reload after a write even if check passed.
- (script/group/template reload is cheap; automation reload re-reads all files.)

### `config_tools__find_device` — added v0.2.0
- params: `query` (case-insensitive substring over device name / name_by_user,
  e.g. "styrbar", "dimmer", "hue").
- Returns ≤10 matches: `device_id` (the uuid used in `platform: device`
  triggers), name, manufacturer, model, area, and the `entity_id`s registered
  to the device. Read-only, everyone.
- Closes the pre-existing gap: the agent no longer needs an existing
  automation file to learn a `device_id`.

### `config_tools__device_triggers` — added v0.2.0
- params: `device_id` (from `find_device`).
- Returns the device's **live** device-automation triggers via
  `device_automation.async_get_device_automations(hass, TRIGGER, [device_id])`
  — the real `domain`/`type`/`subtype` pairs (e.g.
  `zha` / `remote_button_short_press` / `turn_on`). Read-only, everyone.
- Hard rule for the agent: **never guess trigger type/subtype; call this tool
  and use exactly what it returns.** (Same lifecycle source as the old `bind_remote`
  plan, now exposed as read-only tools + generic `write_file` for the actual edit.)

### `config_tools__call_service` — P9 (v0.3.0 → hardened **v0.3.1**, dep + verified live)
- **Why:** the `assist` LLM API only surfaces entity intents + exposed scripts +
  custom `llm` platform tools; there is no generic "expose any service" toggle.
  HA's built-in `ActionTool` (helpers/llm.py) is script-only for schemas (its
  param cache covers scripts, not arbitrary services; and scripts surface natively
  via `script/llm.py::ScriptTool`) → for *arbitrary* params on *arbitrary* exposed
  entities we build the tool ourselves. ZHA lights report `supported_features` =
  `40` = FLASH(8)+TRANSITION(32), so blinking via `light.turn_on` `flash:` is
  physically supported — but entity intents (`light__HassLightSet`) can't carry
  `flash`/`effect`/`transition`.
- **Native alternative (prefer for named actions):** an exposed **script** becomes
  a `script.*` tool automatically, with its parameter schema derived from the
  script's `fields` (`ActionTool`). `scripts.yaml::korridor_blink` demonstrates
  this: `fields: flash|transition` → the agent can "blinka korridorlampan" with
  `flash: short` as a native script call — no component code. Use `call_service`
  only for the generic gap (any light/switch, arbitrary data).
- **Allowlist** (single source of truth in `const.py`):

  | domain   | services                         |
  |----------|----------------------------------|
  | `light`  | `turn_on`, `turn_off`, `toggle`  |
  | `switch` | `turn_on`, `turn_off`, `toggle`  |

  `group.*` entities work through core's group expansion. Extend later on
  request (e.g. `scene`, `homeassistant.turn_*`).
- params: `service` (e.g. `"light.turn_on"`), `entity_id` (ONE exposed entity,
  single target keeps it simple + bounded; groups cover multi-light cases),
  `data` (**typed** probatio schema: `flash` (In short/long), `brightness_pct`
  0-100, `brightness` 0-255, `brightness_step` -255..255, `transition` ≥0,
  `effect`, `color_temp_kelvin`, `color_temp`, `color_name`, `white`, `profile`,
  `xy_color`/`rgb_color`/`rgbw_color`/`rgbww_color`/`hs_color` as value arrays).
  Unknown keys fail at parse time with a "did you mean" hint instead of a raw
  free-form dict.
- Flow: split `service` → `domain.service_name` → allowlist check (else error
  listing allowed services) → target must exist in the **entity registry** AND be
  exposed to `llm_context.assistant` via
  `homeassistant.exposed_entities.async_should_expose` (**exposure gating only —
  no admin gate; v0.3.1**) → `service_data = {**data, "entity_id": entity_id}` →
  `hass.services.async_call(..., blocking=True)` (HA's own schema validation
  backstops the typed `data`) → re-reads the entity state and returns
  `{"result": "ok", "entity_id", "state", "attributes"}`; all failures relayed
  with `error=True` and logged (`_LOGGER.warning/info`).
- Why exposure-only is the right boundary: it matches HA's own assistant security
  model (built-in intents don't require admin; the exposure registry *is* the
  per-assistant permission). Admin stays on the config-writing tools where the
  blast radius is far larger.
- Component layout addition: `const.py` (`ALLOWED_SERVICE_ACTIONS`), `tools.py`
  (`CallServiceTool`, typed data, atomic write, `_LOGGER`), `llm.py` (tool #8),
  `manifest.json` → `0.3.1` (`integration_type: service`, honest `iot_class`).

### `config_tools__set_label` — added v0.4.0
- params: `entity_id`, `labels` (list to set as the entity's labels, replaces).
- Called on the **entity registry** (`registry.async_update_entity(entity_id,
  labels=[...])`), with label-registry validation (`label_registry.async_get`).
  Admin-gated like `write_file`/`check_config`/`reload`; returns the new label
  list. Verified live end-to-end by the chat agent (returned
  `["slack_borta","taklampa"]` on the room dimmer). This is how the agent
  assigns/updates the role labels (`taklampa`, `sasong`, …) without touching
  `.storage` by hand.
- **HA 2026.10 API note:** entity-registry updates ARE the sync
  `EntityRegistry.async_update_entity(entity_id, **changes)` (returns the entry) —
  `async_update` / `registry.entities.async_update` do not exist.

### `config_tools__restart_core` — added v0.4.0
- params: none.
- Admin-gated; schedules `homeassistant.restart`. Returns an "ok, restarting"
  message. Recomputation/state validation before calling is the caller's job.

### `config_tools__bind_remote` — **NOT BUILT** *(superseded by v0.2.0 tools)*
- **Owner decision 2026-10-22: "way too specific" → dropped.** Its two real
  capabilities — device_registry lookup + live trigger enum — are now
  `find_device` + `device_triggers`, and the automation YAML edit itself goes
  through `write_file` (list-format rule below). No separate binding tool
  needed.

## 4. Component layout (`ha_config/config/custom_components/config_tools/`)

```
manifest.json      # domain, version, "platforms": ["llm"]
__init__.py        # async_setup() -> True; CONFIG_SCHEMA = cv.empty_config_schema
const.py           # DOMAIN = "config_tools"; ALLOWED_SERVICE_ACTIONS (P9)
llm.py             # async_get_tools -> LLMTools(tools=[...10 tools])
tools.py           # path canonicalization, allowlist/denylist, in-memory revert, CallServiceTool, SetLabelTool, RestartCoreTool
```
- Implementation notes: pure stdlib (`pathlib`); all returns are `ToolResult`
  dicts (`data={"result"|"error": ...}`); write flow snapshots to memory (no
  `.bak` files on disk — reloadable dirs only glob `*.yaml`, and filesystem
  litter would confuse the exporter).
- Versioned + exported by Git Exporter (custom_components already under `/config`
  mirror: doorman/hacs/scheduler present).

## 5. Rollout / verification — EXECUTED 2026-10-22 ✅

### 5a. Agent knowledge layer (offline, no internet)
The OpenRouter agent has **no internet access**, so all operational knowledge is
embedded where it can read it:
- **System prompt** (conversation subentry in `.storage`) now includes a
  "TEKNISK DEL" block: tool list + hard rules (YAML-list format, never invent
  device_id/type/subtype, check+reload after write, never touch
  configuration.yaml/secrets/.storage/DBs, input_* live values not changeable,
  ask when ambiguous) + pointers to the two reference docs below.
- **`/config/docs/AGENT_HANDBOOK.md`** (~6.4 kB): rules, file conventions, key
  entities/groups, the current automation set, and the per-request workflow.
- **`/config/docs/AGENT_EXAMPLES.md`** (~3.8 kB): working YAML examples
  (device-button, time w/ startup grace, dim-up with `mode: restart`, lux
  numeric_state), the WRONG single-mapping shape, and the find→triggers→write
  recipe.
Both docs are readable by the agent via `config_tools__read_file` (under
`/config/docs/`) and are versioned in `ha_config/config/docs/` (exported).

### 5b. Component rollout

1. Author component in `ha_config/custom_components/config_tools/` (this repo). ✅
2. Copy to VM `/config/custom_components/config_tools/` via tar-over-SSH. ✅
3. Add `config_tools:` to `configuration.yaml` (one-time, build agent, not a tool),
   `ha core check`, then full core restart (reload alone is not enough — `llm`
   platform lazy-scan happens at boot). ✅ (`ha core check` green; restarted.)
4. Verify: `ha core check` green; `llm` platform loads (log line / `ha core logs`);
   `conversation/process` REST call asking the agent to `glob_files automations/*.yaml`
   and `read_file scripts.yaml` → confirm actual tool execution in the response tools section. ✅
   (Agent listed the 9 real automation files and the 2 remaining scripts —
    `read_file`/`glob_files` confirmed; custom-integration import warning is benign.)
5. Then a real round-trip: agent writes a *new* no-op automation → check → reload →
   delete it again (cleanup) → confirm file gone + reloaded. **⚠️ GOTCHA** — the
   agent's `write_file`+`check_config`+`reload` chain reported success, but the
   automation entity never registered: the model wrote a single YAML mapping while
   `automation: !include_dir_merge_list automations/` requires **each file to be a
   YAML list**. `check_config` passes (valid YAML, silently dropped by the merge),
   so the write tool cannot catch this by design. Confirmed the file+reload path is
   correct with a list-format file (entity appeared), then cleaned up the test file.
   → **Runbook rule:** the chat agent must write `automations/*.yaml` files as YAML
   *lists* (start with `- id: ...`); a single mapping is silently ignored.
6. Update `docs/SCHEDULES.md`/`docs/AUTOMATIONS.md` via `tools/summarize.py`;
   commit everything; wait for exporter push; verify mirror sha. ✅ (Pushed
   `a57db80..71e48ed`; sha-verified live == mirror for configuration.yaml,
   scripts.yaml, all config_tools files.)
7. **Not done:** stale `conversation` exposure entries for the deleted schedule
   scripts remain (inert — `homeassistant/expose_entity` list still shows them;
   entities no longer exist). Cosmetic; clear on next maintenance pass if desired.

## 6. Runbook notes for the agent

- Never touch `configuration.yaml` / `groups.yaml` / `secrets.yaml` / `.storage`; a
  tool call to those is rejected by design — do not work around it.
- After any write, verify (`check_config`) and reload before reporting success.
- If a write would change an existing automation's meaning (not just add new),
  ask for owner sign-off — this is config, not chat.
- Reverting your own change: `read_file` the current file, fix the YAML, and
  `write_file` it back (previous content was restored automatically if the
  check failed).

## 7. Out of scope

- No bash, no `shell_command`, no README/`*.md` writes, no editing the
  component's own files, no ZHA pairing/network.
- `input_*/*.yaml` writes (v0.4.0) are allowed but NOT reloadable — the tool
  reports "needs restart_core"; helper live values remain out of the agent's
  reach (family edits them on the dashboard).
- `bind_remote` not built (owner decision); device-automation wiring is a
  manual build-agent step for now.