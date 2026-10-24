# Home Assistant best practices — curated reference + audit of this build

Compiled 2026-10-23 from official docs (home-assistant.io/docs), the
contributor/developer guides, and HA community threads (notably Taras's
data-driven automation patterns). Where the official docs and community
practice disagree, the official position wins and the community refinement is
noted.

This document has two halves:

1. **The practices** — a concise, current reference for how configuration and
   automations are *supposed* to be structured in 2026 HA.
2. **Audit of this build** — how `config/` measures up today, with concrete
   file:line references and the deltas worth acting on.

---

## Part 1 — The practices

### 1.1 The five tools (pick the right one)

From [Which tool to use](https://www.home-assistant.io/docs/automation/which-tool-to-use/):

| Tool | Is | Use when | Not for |
|------|----|----------|---------|
| **Automation** | Steps that start by themselves on a change | Something should react to a state/time/event change | Steps you start yourself (button/voice) — use a script |
| **Script** | A saved list of steps, started by you/other automations | Same steps from dashboard, Assist, or several automations; needs **fields** for variants | Reacting to a change by itself |
| **Scene** | A saved set of states applied at once | Several devices → one specific state together | Sequential steps, waits, decisions |
| **Blueprint** | Reusable template (automation/script/template) with inputs | Same automation for several rooms/devices, or community-made | A one-off automation — write it directly |
| **Helper** | An entity *you* create (toggle/timer/schedule/number/datetime/template) | The automation must *remember* something, or family should change behavior without editing YAML | Reacting to changes or running steps |

**Common combinations** (all apply to this build):

- Automation → runs a script when it needs variants (`fields`), instead of
  duplicating the action list.
- Toggle helper + condition → pause an automation from the dashboard.
- Timer helper instead of a long `delay` → survives restarts (a plain `delay`
  is abandoned on restart).
- **Schedule helper instead of several hard-coded time triggers** → family
  edits the schedule, not the YAML. (This is exactly the P4 migration.)
- Blueprint instantiated per room/device (motion light, remote binding).

**Community refinement (Taras pattern, [Variables in a script](https://community.home-assistant.io/t/variables-in-a-script/509650)):** N
near-duplicate automations (same shape, different entities) should be
consolidated into *one* automation that is data-driven — a `variables` dict keyed
by `object_id`, a single state trigger over all entities, and a `choose`/
template that reads the matching entry. Fewer automations = fewer places to fix
a bug. Don't over-apply it: if the behaviors genuinely diverge, separate
automations with clear aliases are still better than a template monster.

### 1.2 Configuration structure

- **UI-first.** Device/integration setup lives in the UI (`.storage`), not
  YAML. YAML is only for automations, scripts, scenes, helpers, customizations,
  and integrations that require it.
- **Split `configuration.yaml`** with `!include`; one logical unit per file.
  Use *labeled* keys for repeated domains so both UI and hand-written items
  coexist:
  ```yaml
  automation manual: !include_dir_merge_list automations/
  automation ui: !include automations.yaml
  ```
- **Directory includes** (`!include_dir_*`) are the cleanest for many files —
  but only `.yaml` extensions are scanned (`.yml` is ignored). Note: `!include_dir_merge_list`
  **silently drops files that are dicts instead of lists** (gotcha hit in this
  build, §2 / WORKTRACK #021) — `check_config` won't catch it either.
- **Packages** (`homeassistant.packages`) when an integration doesn't allow
  multiple top-level keys and you want feature-cohesion.
- **Secrets**: centralize all credentials/IPs/MACs in `secrets.yaml`
  (excluded from git; referenced via `!secret key`). It is **not encrypted** —
  protect the file and its backups.
- Keep `default_config:` and the standard `automation/script/scene` includes.

### 1.3 YAML style

- 2-space indentation, **no tabs**, no trailing-whitespace traps (HA is
  case-sensitive; a bad `\t` fails the literal load).
- Booleans vs states: quote real states — `'on'`/`'off'` — because bare `on`
  is parsed as boolean `true`. Same for the string values of `input_select`
  options and entity state comparisons.
- Fixed-width font editor; validate with `ha core check` before restarting;
  debug with **Traces** (automation testing panel).
- Comments: explain *why*, not *what* — the code is the what.
- Prefer the modern keys: `trigger:`/`condition:`/`action:` (not deprecated
  `trigger:`/`condition:`/`action:` mixing). No `data_template:` — use `data:`.

### 1.4 Automations

- **Triggers react to a moment, not a duration.** "While X is true" needs a
  trigger for the change + a condition for the context. State triggers do not
  react on a transition *from* `unavailable`/`unknown` (the recovery is not a
  change — use plain `state` trigger if you must catch it).
- **Prefer semantic/entity triggers** (`light.turned_on`, `temperature crossed`)
  over generic `state`/`numeric_state` where an option exists; they handle unit
  conversion and don't misfire on unrelated transitions.
- **Multiple triggers + `id`** + a `trigger`-condition branch to do different
  things per cause in one automation.
- **Set `mode` explicitly** (`single`/`queued`/`restart`/`parallel`) on anything
  with delays or shared state. Understand the startup behavior: triggers don't
  fire at boot unless you add a `homeassistant: start` trigger — use that +
  full conditions for restart reconciliation rather than `initial:`-based
  hacks (see §2, the P10 findings).
- **Templates in triggers**: only *limited* templates are allowed on most
  trigger keys; do heavy templating in `condition:`/`action:`.
- **Blueprints**: give them `id`s, `min_version`, selectors for inputs; use
  `trigger: device` in remote automations (this build already does).
- **Keep YAML automations as YAML lists** under `automation:` — a single dict
  in a file is silently dropped by `include_dir_merge_list`.

### 1.5 Helpers — persistence gotchas

- **`initial:` is re-applied on every HA start and silently overwrites live
  edited values.** For anything the family edits (schedule times, toggles,
  brightness), *omit* `initial:` so HA restores the last value across restarts.
  This is a documented-but-easily-missed behavior and was a real bug here
  (P10: family schedule edits reset every boot).
- Use helpers as **knobs the automations consult**, not control-flow
  duplication. Automations read helpers in conditions or templates; edits flow
  through UI/chat → helper → automation.
- `input_boolean` = state you set; `input_datetime`/`input_number` = values
  the family tunes; `input_select` = enumerations; `schedule` helper = weekly
  time blocks (replace hand-rolled time-window logic + weekday conditions).

### 1.6 Organization: registry taxonomy, not YAML

| Tool | Purpose | YAML vs registry |
|------|---------|------------------|
| **Area** | physical room; device→area; target in automations | registry (UI) |
| **Floor** | groups areas; target floors | registry (UI) |
| **Label** | cross-cutting (e.g. "high energy", "Christmas"); an entity can have many; filter tables; target labels | registry (UI) |
| **Category** | organize tables (automations/scenes/scripts/helpers) | registry (UI) |
| **Group integration** | merge entities into ONE controllable entity | **YAML** (`group:`) |

Devices/entities get exactly one area+floor but many labels. Use labels for
"Christmas lamps" instead of only `christmas_sockets` group gymnastics when the
organizing concern is cross-cutting. Groups (`group:`) are for *control*, not
organization.

### 1.7 Security

- Strong unique passwords + **MFA** per account; least-privilege divisions.
- Secrets in `secrets.yaml`; keep it out of git (and out of any sync).
- Remote access via HA Cloud, TLS/Let's Encrypt, or **VPN** — never raw port
  forward of the UI.
- Webhooks: unique non-guessable IDs, `local_only: true` unless needed, never
  destructive actions.
- Rotate anything that was once printed/committed (this build did: Yale
  password + GitHub PAT, 2026-10-22).
- Keep HA up to date monthly.

### 1.8 Versioning / deployment

- Config-as-code: full `/config` in git, including UI state (Lovelace, registries
  via Git Exporter add-on committed snapshots), secrets/`.storage`/DB excluded,
  plaintext-secrets check as a safety net. (This build: exactly that.)
- Validate (`ha core check`) → deploy → verify traces → commit; one logical
  change per commit; mirror-vs-live verification (md5) after deploys.
- Generated docs must not drift: regenerate summaries on every config change.

---

## Part 2 — Audit of this build (archived)

The dated 2026-10-23 audit of `config/` (conformance list + deltas, all since
implemented) is archived at `docs/archive/build_audit_2026-10-23.md`. The
deliverables it drove — labels (`taklampa`/`natthorn`/`sasong`/`utelampa`),
pause toggles (`automatik_*`), the Taras ceiling consolidation, `home_status`
simplification, and the `ha_ready` startup gate — are all live and summarized
in `.opencode/skills/home-assistant/SKILL.md` + `WORKTRACK/NEXT.md`.

## Sources

- Official YAML guide & style guide — home-assistant.io/docs/configuration/yaml/
- Splitting configuration — home-assistant.io/docs/configuration/splitting_configuration/
- Securing HA — home-assistant.io/docs/configuration/secrets/ + /securing/
- Automation triggers — home-assistant.io/docs/automation/trigger/
- Which tool to use (the five tools) — home-assistant.io/docs/automation/which-tool-to-use/
- Organizing (areas/floors/labels/categories/groups) — home-assistant.io/docs/organizing/
- Community: "Variables in a script" (data-driven automation consolidation) —
  community.home-assistant.io/t/variables-in-a-script/509650