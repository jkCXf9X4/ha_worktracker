# P8 — Agent config tools (custom component `config_tools`)

Status: **planned 2026-10-22** — design + mechanism verified against HA Core
2026.10 source. Build pending.

Gives the family chat agent bounded read/write control over the YAML config:
read/glob (everybody) and write/check/reload/bind_remote (admin-context only),
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
| Write allowlist | `automations/*.yaml`, `scripts.yaml`, `groups.yaml`, `template/*.yaml` — the reloadable domains only. |
| Read/glob allowlist | Everything under `/config` **except** `secrets.yaml`, `.storage/`, `*.db`, `*.db-wal`, `*.db-shm`, `home-assistant.log*`, `configuration.yaml` (read OK? no — also exclude `groups.yaml.bak`). No paths outside `/config`. |
| Hard denylist (both) | `configuration.yaml`, `secrets.yaml`, `.storage`, DBs, logs, `custom_components/config_tools/` itself. |
| Admin gating | `read_file`/`glob_files` → everyone; `write_file`/`check_config`/`reload`/`bind_remote` → reject unless caller is admin + `llm_context.assistant` is the family agent's assistant name. |
| Size caps | read caps at ~8k chars (token budget); write rejects >64k; glob capped at 100 hits. |
| No secrets in output | read of `secrets.yaml` impossible by allowlist; redact `!secret`-referenced values never read anyway. |
| Determinism | `bind_remote` resolves device/trigger from registry + live enum; agent never invents `device_id`/subtypes. |

## 3. Tools (domain `config_tools`)

### `config_tools__read_file`
- params: `path` (absolute-or-canonical, must resolve under `/config`, allowlist check), `limit_lines?` (default 400).
- Returns file text (prefix `# <path> — <n> lines`) or an error string.
- Used for: agent self-audit, config Q&A ("what runs at 06:22?"), and reverting its own writes (`automations/<file>.bak`).

### `config_tools__glob_files`
- params: `pattern` (relative glob under `/config`, e.g. `automations/*.yaml`).
- Returns up to 100 matching paths. No content.

### `config_tools__write_file`
- params: `path`, `content`.
- Path must be in the write allowlist (canonicalized; reject `..`, symlinks).
- **Flow:** snapshot existing content → write `.bak` → write target → `ha core check`
  (`homeassistant.check_config` service, or in-process `config_util.async_check_ha_config_file`)
  → on errors: **restore `.bak`**, return the error text and confirm nothing changed.
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

### `config_tools__bind_remote`
- Purpose: create a device-automation that wires a **pre-paired** ZHA remote button to a target entity — the flagship use-case from the read/write/glob discussion.
- params (first call): `device_name`, `target_entity_id`, `name` (friendly aliases),
  `trigger_type`/`trigger_subtype` **optional**.
- If `trigger_type`/`subtype` omitted → looks up `device_id` by name via device
  registry and returns the device's **live** trigger list
  (`homeassistant.components.device_automation::async_get_device_automations(
  hass, TRIGGER, [device_id])`) so the model can answer with the exact button.
- Second call (with valid type/subtype): writes a validated automation to
  `automations/<slug>.yaml` (mirrors the structure of `hue_dimmer_isacs.yaml`),
  checks, reloads automation, returns result.
- Guards: unknown device name → helpful error + nearest matches; target entity
  must exist (entity registry); never fabricates ids.

## 4. Component layout (in `ha_config/custom_components/config_tools/`)

```
manifest.json      # domain, version, "platforms": ["llm"], homeassistant>=2026.10
__init__.py        # async_setup() -> True; const
llm.py             # async_get_tools -> LLMTools(tools=[...5 tools])
read_write.py      # path canonicalization, allowlist/denylist, atomic write + .bak
device_automation.py  # device lookup + trigger enum + YAML template build
```
- Implementation notes: prefer `hass.services.async_call(..., blocking=True)` for
  services; use stdlib (`pathlib`, `yaml`) — no new runtime deps; all returns are
  `ToolResult` strings (data=`str`), not dicts, for model simplicity.
- Versioned + exported by Git Exporter (custom_components already under `/config`
  mirror: doorman/hacs/scheduler present).

## 5. Rollout / verification

1. Author component in `ha_config/custom_components/config_tools/` (this repo).
2. Copy to VM `/config/custom_components/config_tools/` via tar-over-SSH.
3. Add `config_tools:` to `configuration.yaml` (one-time, build agent, not a tool),
   `ha core check`, then full core restart (reload alone is not enough — `llm`
   platform lazy-scan happens at boot).
4. Verify: `ha core check` green; `llm` platform loads (log line / `ha core logs`);
   `conversation/process` REST call asking the agent to `glob_files automations/*.yaml`
   and `read_file scripts.yaml` → confirm actual tool execution in the response tools section.
5. Then a real round-trip: agent writes a *new* no-op automation → check → reload →
   delete it again (cleanup) → confirm file gone + reloaded.
6. Then real `bind_remote` carpet-run in review mode (answer trigger list only), pick a
   button, confirm YAML output by eye before applying.
7. Update `docs/AUTOMATIONS.md` via `tools/summarize.py`; commit everything;
   wait for exporter push; verify mirror sha.

## 6. Runbook notes for the agent

- Never touch `configuration.yaml` / `groups.yaml` / `secrets.yaml` / `.storage`; a
  tool call to those is rejected by design — do not work around it.
- After any write, verify (`check_config`) and reload before reporting success.
- If a write would change an existing automation's meaning (not just add new),
  prefer `bind_remote`/add-branch or ask for owner sign-off — this is config, not chat.
- Reverting: `read_file` the `.bak` snapshot then `write_file` it back.

## 7. Out of scope

- No bash, no `shell_command`, no README/`*.md` writes, no `input_*` writes
  (not reloadable), no editing the component's own files, no ZHA pairing/network.
- Run of `bind_remote` applies only to automations (never triggers on its own).