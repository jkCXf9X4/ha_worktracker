"""Path E pyscript adapters — thin binding of the tested domain to HA.

Design (see docs/TESTED_POLICY_PLAN.md §6 Phase C):
- The *same* `domain/daylight` package that pytest runs ships to the VM as
  native modules under `/config/pyscript/native_domain/` (added to ``sys.path``
  + ``allow_all_imports: true``). "Tested == deployed."
- These files are pyscript scripts (autoloaded from `/config/pyscript/scripts/`).
  They are deliberately thin: gather HA state -> build domain inputs -> call the
  pure policy -> translate the result. NO business rules live here.
- **Shadow mode (this iteration):** adapters write their decisions to
  `sensor.home_status_ps` / `binary_sensor.light_outside_ps` and LOG mismatches
  against the still-live YAML template sensors. They do NOT call any services
  and do NOT touch the live entities — zero behavior change, honours the
  isacs_rum invariant. Flipping ownership of the real entity IDs is Phase D.
- After editing any file here, push to the VM then `pyscript.reload`
  (global_ctx `*`); native modules load fresh on reload.

Entity-stability contract: when ownership flips (Phase D), the derived facts
KEEP the exact IDs `sensor.home_status` / `binary_sensor.light_outside` so all
existing YAML automations react unchanged.
"""