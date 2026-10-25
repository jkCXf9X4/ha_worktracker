# Invariants — cross-cutting rules for the whole build

Binding rules for every workstream (probes, spikes, migration, deploy). A rule
is an invariant if breaking it can cause a person to be woken, a property to be
damaged, or a regression the gates can't catch. All invariants hold from
2026-10-25.

## 1. Isac's room is hands-off (OWNER, top priority)

**Never trigger any light on in `isacs_rum`** — `light.isac_tak`,
`switch.isac_lekstuga`, and the bedside lamp. Why: Isac is asleep; the family
must be able to trust the automation.

Scope:
- The sovrum/isac morning-fade automations remain **pure YAML** and are **not**
  part of the migration pilot.
- Live probes, Pyscript spike scripts, and `probe_vm` fixtures must never
  exercise any service path that could reach these entities (or the
  `isacs_rum` area).
- Before any deploy/probe: `automatik_nattlampor`, `automatik_taklampor`,
  `automatik_las` are **off** (the family pause toggles are the kill-switch),
  and the deploy tooling greps the target allowlist against `isacs_rum` data.

## 2. Test HA truthfully

- Never use `automation.trigger` to test a gate/condition — it bypasses
  conditions and updates `last_triggered` (false "it ran"). Use real state
  changes, WS `test_condition`, or the `ha_started` off→on boot replay, and
  read the automation **trace**.
- `homeassistant.set_state` is not a real service; setting `person.*` never
  cascades to `group.family`.
- Trust entity state, not the chat model's report of success.

## 3. Gated agent powers

- `config_tools` is the resident agent's ceiling: admin-gated writes to
  reloadable YAML (`automations/*.yaml`, `scripts.yaml`, `groups.yaml`,
  `template/*.yaml`) only. Never pyscript/python paths, never
  `configuration.yaml`/`secrets.yaml`/`.storage`, never shell.
- Secrets never committed; `secrets.yaml`, `.storage/`, DBs/logs excluded from
  git. Never print the exporter PAT or secrets in tool output.

## 4. Single ownership of devices

Every automatically controlled device has exactly one owner. Ownership is
recorded in the subsystem doc (`docs/subsystems/*`). Others may state intent
through the documented interface, never compete for control.

- Seasonal rule (`label.sasong`) is owned exclusively by
  `domain.daylight.night.resolve_night_lights` / `script.uteljus_sync`; the
  `uteljus_pa/av` one-taps never touch it.
- Boot reconcile: no new `ha_ready -> on` triggers in new automations — extend
  `script.reconcile_all` instead.

## 5. Policy code stays pure

Domain code has: no entity IDs, no service calls, no I/O, no global mutable
state, no Home Assistant imports; deterministic on explicit inputs; typed
dataclasses/enums as the interface. A violation is a merge/review blocker.

## 6. Config source-of-truth split

- VM `/config` = source of truth for config *state* (registry, integrations,
  helpers) — exporter is push-only; remote commits never applied to `/config`.
- This repo = source of truth for *managed logic* (domain package, fixtures,
  tooling, policy docs). Deploys push derived/verified artifacts; the gates
  (`tools/qa.sh`, `mirror == build`, mirror == VM md5) fail on drift.
- Docs/tracker live here, not mirrored to `/config/docs/` (except
  `hue_zha_migration.md`); keep it that way unless the owner reverses #014.

## 7. Safety of deploy

- `tools/qa.sh` must be green before any deploy.
- Deploy runs on a validated git commit; previous exported version preserved
  (git history + md5) for rollback.
- Rollback restores the prior exporter commit's files and re-runs the smallest
  reload; persisted state is accounted for (derived facts recompute on boot).
- Approval required for high-risk device behavior / infra / safety-sensitive
  automation changes.