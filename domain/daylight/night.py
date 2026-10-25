"""Night/seasonal lighting rule — pure translation of ``script.uteljus_sync``.

Single home of the seasonal rule. Resolves the ``utelampa`` (front outdoor)
label from the daylight flag, and the ``sasong`` (seasonal sockets) label from
``christmas_lights`` + daylight, in one call. Self-gated: the whole rule NOOPs
while paused (``automatik_nattlampor`` off) or before HA is ready. The solo
one-tap scripts (``uteljus_pa`` / ``uteljus_av``) intentionally never touch
``sasong`` — ownership lives here, not in the one-taps.
"""

from __future__ import annotations

from .models import Action, NightLightsInputs, NightLightsResult


def resolve_night_lights(inputs: NightLightsInputs) -> NightLightsResult:
    """Decision table for the nightly/seasonal rule.

    ``light_outside`` is the *daylight flag* (True = bright): utelampa turns ON
    when it is dark (flag off).
    """
    if inputs.paused or not inputs.ha_ready:
        return NightLightsResult(utelampa=Action.NOOP, sasong=Action.NOOP)

    utelampa = Action.OFF if inputs.light_outside else Action.ON
    sasong = Action.ON if (inputs.christmas_lights and not inputs.light_outside) else Action.OFF

    return NightLightsResult(utelampa=utelampa, sasong=sasong)
