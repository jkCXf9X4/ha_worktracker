# Changelog

Chronological log of changes and decisions. Newest at the bottom.

## 2026-10-20 — Bootstrap session

- **P0 access** — Installed/configured Advanced SSH & Web Terminal add-on.
  Switched add-on shell user to `root` (intended root shell) for full write
  access to `/config` and working `ha` CLI. Discovered: `ha` only works inside
  a login shell (`bash -lc`); SFTP/scp disabled (use tar-over-SSH); never pipe
  scripts via a `-t` SSH session.
- **Inventory (P2a)** — Dumped `.storage` + config over SSH; wrote
  `docs/inventory.md`. Key facts: 958 entities / 211 devices / 535 disabled;
  UniFi dominates; TV likely duplicated; Scheduler holds the "Sovrum" schedule.
- **Automation discovery** — Read the full custom `script_engine` framework +
  scripts; extracted requirements + YAML migration design in
  `docs/automation_requirements.md`.
- **P1 versioning — live** — Git Exporter add-on installed; repo
  `ha_config` on GitHub (private, branch `main`). Excludes configured
  (`.storage/`, `secrets.yaml`, `.ssh/`, DBs, logs). First push blocked by the
  exporter’s secrets check on the legacy Samsung TV IP/MAC → moved values to
  `secrets.yaml` (`!secret`). `ha core check` passes. Push confirmed
  (`f56af23..65acd1f main`).
- **secrets.yaml incident** — file had no trailing newline; an `echo >>` append
  glued lines into invalid YAML and corrupted the Yale password; an earlier
  `sed` patch inserted stray `x27` text. Repaired by atomic rewrite; validated
  with `python3 + yaml`.
- **Security flags (open #011/#012)** — the Yale password and the GitHub PAT
  were visible in tool output; both flagged for rotation.
- **Meta** — `.opencode/skills/home-assistant` knowledge base created;
  `WORKTRACK/` tracker created to carry planning across sessions.

## Decisions

- Versioning model: single GitHub repo; `/config` is the source of truth,
  mirrored by Git Exporter (`config/` subtree in repo). Build agent edits
  `/config` over SSH.
- Cleanup policy: **balanced** — report, stage, disable-not-delete, sign-off on
  ambiguous items, every step a separate commit once versioned.
- Automation target: native HA YAML + `input_*` schedule helpers (1:1 port of
  `script_engine` behaviour), replacing custom Python. Verify over a full
  day/night cycle before retiring legacy components.
- Chat agent: OpenRouter-backed Assist first (privacy-aware via exposed-entity
  scoping); local Ollama as later option.
- Family editing: HA app/dashboard over raw git; the git history + summaries
  provide the "textual definition".
- Tracker/docs: kept locally; optionally mirrored into `/config/docs/`
  (owner decision, backlog #014).