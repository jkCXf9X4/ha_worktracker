"""SHADOW adapter: night/seasonal rule (utelampa + sasong).

Deterministic twin of ``script.uteljus_sync``'s decision table. Recomputes on
the same triggers (daylight flag + christmas helper) and writes the decision to
``sensor.night_lights_ps`` for inspection. Shadow mode NEVER calls services —
the isacs_rum invariant holds by construction. Ownership of the actual service
call stays with ``script.uteljus_sync`` until Phase D.
"""

import sys
import importlib

_NATIVE_DOMAIN = "/config/pyscript/native_domain"
if _NATIVE_DOMAIN not in sys.path:
    sys.path.insert(0, _NATIVE_DOMAIN)
importlib.invalidate_caches()

from domain.daylight import NightLightsInputs
from domain.daylight.night import resolve_night_lights

_PS = "sensor.night_lights_ps"


def _flag(entity: str) -> bool:
    return str(state.get(entity)) == "on"


@time_trigger("startup")
@state_trigger("binary_sensor.light_outside", "input_boolean.christmas_lights")
def night_lights_shadow():
    result = resolve_night_lights(
        NightLightsInputs(
            light_outside=_flag("binary_sensor.light_outside"),
            christmas_lights=_flag("input_boolean.christmas_lights"),
            paused=not _flag("input_boolean.automatik_nattlampor"),
            ha_ready=_flag("binary_sensor.ha_ready"),
        )
    )

    state.set(
        _PS,
        "computed",
        utelampa=result.utelampa.value,
        sasong=result.sasong.value,
        light_outside=_flag("binary_sensor.light_outside"),
        christmas_lights=_flag("input_boolean.christmas_lights"),
        paused=not _flag("input_boolean.automatik_nattlampor"),
        ha_ready=_flag("binary_sensor.ha_ready"),
    )
    log.info(
        "PS night_lights decision utelampa=%s sasong=%s",
        result.utelampa.value,
        result.sasong.value,
    )