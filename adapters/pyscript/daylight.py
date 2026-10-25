"""SHADOW adapter: daylight-flag hysteresis.

Deterministic twin of the live template binary_sensor.light_outside. Recomputes
the latched-hysteresis decision on the same triggers (lux + both threshold
helpers + every minute) and writes to `binary_sensor.light_outside_ps`, logging
a warning whenever it disagrees with the live entity.

The latch source is the LIVE flag (``currently_on``), so both implementations
share the same starting state and the comparison isolates the *decision*, not
drift in the latch.

To flip ownership (Phase D): write `binary_sensor.light_outside` and seed the
latch from ``_PS``.
"""

import sys
import importlib

_NATIVE_DOMAIN = "/config/pyscript/native_domain"
if _NATIVE_DOMAIN not in sys.path:
    sys.path.insert(0, _NATIVE_DOMAIN)
importlib.invalidate_caches()

from domain.daylight import DaylightInputs
from domain.daylight.daylight import light_outside

_LIVE = "binary_sensor.light_outside"
_PS = "binary_sensor.light_outside_ps"

_LUX = "sensor.lumi_lumi_sen_ill_mgl01_8b21773c_illuminance"


def _f(entity: str, default: float) -> float:
    raw = str(state.get(entity))
    try:
        return float(raw) if raw not in ("unavailable", "unknown", "") else default
    except ValueError:
        return default


@time_trigger("period(now, 1min)")
@state_trigger(_LUX, "input_number.outside_light_on_threshold", "input_number.outside_light_off_threshold")
def daylight_shadow():
    lux = _f(_LUX, 0.0)
    on_thr = _f("input_number.outside_light_on_threshold", 400.0)
    off_thr = _f("input_number.outside_light_off_threshold", 150.0)
    currently_on = str(state.get(_LIVE)) == "on"

    result = light_outside(
        DaylightInputs(
            lux=lux,
            on_threshold=on_thr,
            off_threshold=off_thr,
            currently_on=currently_on,
        )
    )

    ps_state = "on" if result else "off"
    state.set(_PS, ps_state, lux=round(lux, 1), on_threshold=on_thr, off_threshold=off_thr)

    live = str(state.get(_LIVE))
    if live != ps_state:
        log.warning(
            "PS light_outside MISMATCH live=%s ps=%s (lux=%s on=%s off=%s)",
            live,
            ps_state,
            round(lux, 1),
            on_thr,
            off_thr,
        )
    else:
        log.info("PS light_outside ok=%s (lux=%s)", ps_state, round(lux, 1))