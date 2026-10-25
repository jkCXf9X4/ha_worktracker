"""Unit tests for the daylight-flag hysteresis (``domain.daylight.daylight``)."""

from __future__ import annotations

from domain.daylight import DaylightInputs
from domain.daylight.daylight import light_outside

ON = 400
OFF = 150


def make(
    lux: float,
    currently_on: bool,
    on_thr: float = ON,
    off_thr: float = OFF,
) -> DaylightInputs:
    return DaylightInputs(
        lux=lux, on_threshold=on_thr, off_threshold=off_thr, currently_on=currently_on
    )


def test_off_flag_turns_on_only_above_on_threshold():
    assert light_outside(make(399, False)) is False
    assert light_outside(make(401, False)) is True
    assert light_outside(make(400, False)) is False  # strict > avoids boundary pulse


def test_on_flag_turns_off_only_below_off_threshold():
    assert light_outside(make(151, True)) is True
    assert light_outside(make(149, True)) is False
    assert light_outside(make(150, True)) is False  # strict >


def test_dead_zone_holds_state():
    # In the 150–400 dead zone the flag latches: it does not flap.
    assert light_outside(make(300, True)) is True
    assert light_outside(make(300, False)) is False


def test_custom_thresholds():
    assert light_outside(make(0, False, on_thr=20, off_thr=5)) is False
    assert light_outside(make(25, False, on_thr=20, off_thr=5)) is True
    assert light_outside(make(25, True, on_thr=20, off_thr=5)) is True
    assert light_outside(make(3, True, on_thr=20, off_thr=5)) is False


def test_unavailable_lux_maps_to_zero():
    # The template float(0) default makes a missing sensor read 0 lux.
    assert light_outside(make(0, False)) is False
    assert light_outside(make(0, True)) is False
