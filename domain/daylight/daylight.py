"""Daylight-flag hysteresis — pure translation of ``template/daylight.yaml``.

A latched threshold: an already-ON flag only flips OFF once lux drops below the
(lower) off-threshold; an OFF flag only flips ON once lux rises above the
(higher) on-threshold. The dead zone between them suppresses flap.
"""

from __future__ import annotations

from .models import DaylightInputs


def light_outside(inputs: DaylightInputs) -> bool:
    """Return the derived daylight flag (True = bright/day) after one transition."""
    if inputs.currently_on:
        return inputs.lux > inputs.off_threshold
    return inputs.lux > inputs.on_threshold
