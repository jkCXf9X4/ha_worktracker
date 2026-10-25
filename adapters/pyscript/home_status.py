"""SHADOW adapter: home-status machine.

Deterministic twin of the live template-derived `sensor.home_status`. Recomputes
the domain decision on the same triggers the template uses (every minute + the
four schedule helpers + family presence) and writes the result to
`sensor.home_status_ps`, logging a warning whenever it disagrees with the live
entity. Does NOT call services and does NOT touch the live entity.

To flip ownership (Phase D): change the write target to `sensor.home_status`,
removing the `_ps` suffix and the live-template comparison.
"""

import sys
import importlib

_NATIVE_DOMAIN = "/config/pyscript/native_domain"
if _NATIVE_DOMAIN not in sys.path:
    sys.path.insert(0, _NATIVE_DOMAIN)
importlib.invalidate_caches()

from datetime import datetime, time

from domain.daylight import FamilySchedule, HomeStatusInputs
from domain.daylight.home_status import home_status

_LIVE = "sensor.home_status"
_PS = "sensor.home_status_ps"

_HELPERS = (
    "input_datetime.wake_time_weekday",
    "input_datetime.wake_time_weekend",
    "input_datetime.bedtime_weekday",
    "input_datetime.bedtime_weekend",
)


def _schedule() -> FamilySchedule | None:
    raw = [str(state.get(h)) for h in _HELPERS]
    for v in raw:
        if v in ("unavailable", "unknown", ""):
            log.info("PS home_status skip: schedule helper unavailable (%s)", raw)
            return None
    return FamilySchedule(
        wake_weekday=time.fromisoformat(raw[0]),
        wake_weekend=time.fromisoformat(raw[1]),
        bedtime_weekday=time.fromisoformat(raw[2]),
        bedtime_weekend=time.fromisoformat(raw[3]),
    )


@time_trigger("period(now, 1min)")
@state_trigger("group.family", "input_datetime.wake_time_weekday", "input_datetime.wake_time_weekend", "input_datetime.bedtime_weekday", "input_datetime.bedtime_weekend")
def home_status_shadow():
    schedule = _schedule()
    if schedule is None:
        return

    now = datetime.now().replace(tzinfo=None)
    family_home = str(state.get("group.family")) == "home"

    result = home_status(
        HomeStatusInputs(family_home=family_home, now=now, schedule=schedule)
    )

    state.set(
        _PS,
        result.status.value,
        is_workday=result.is_workday,
        next_wake=result.next_wake.isoformat(sep=" ", timespec="minutes"),
        next_bedtime=result.next_bedtime.isoformat(sep=" ", timespec="minutes"),
    )

    live = str(state.get(_LIVE))
    if live != result.status.value:
        log.warning(
            "PS home_status MISMATCH live=%s ps=%s (family=%s now=%s)",
            live,
            result.status.value,
            family_home,
            now,
        )
    else:
        log.info("PS home_status ok=%s", result.status.value)