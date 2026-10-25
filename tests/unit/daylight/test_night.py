"""Unit tests for the night/seasonal rule (``domain.daylight.night``)."""

from __future__ import annotations

from domain.daylight import Action, NightLightsInputs
from domain.daylight.night import resolve_night_lights


def make(
    light_outside: bool = True,
    christmas: bool = False,
    paused: bool = False,
    ha_ready: bool = True,
) -> NightLightsInputs:
    return NightLightsInputs(
        light_outside=light_outside,
        christmas_lights=christmas,
        paused=paused,
        ha_ready=ha_ready,
    )


def test_dark_bright_no_christmas():
    r = resolve_night_lights(make(light_outside=False))
    assert r.utelampa == Action.ON
    assert r.sasong == Action.OFF


def test_bright_no_christmas():
    r = resolve_night_lights(make(light_outside=True))
    assert r.utelampa == Action.OFF
    assert r.sasong == Action.OFF


def test_dark_with_christmas():
    r = resolve_night_lights(make(light_outside=False, christmas=True))
    assert r.utelampa == Action.ON
    assert r.sasong == Action.ON


def test_bright_with_christmas_turns_seasonal_off():
    r = resolve_night_lights(make(light_outside=True, christmas=True))
    assert r.utelampa == Action.OFF
    assert r.sasong == Action.OFF


def test_paused_is_noop_even_when_dark_and_christmas():
    r = resolve_night_lights(make(light_outside=False, christmas=True, paused=True))
    assert r.utelampa == Action.NOOP
    assert r.sasong == Action.NOOP


def test_not_ready_is_noop():
    r = resolve_night_lights(make(light_outside=False, christmas=True, ha_ready=False))
    assert r.utelampa == Action.NOOP
    assert r.sasong == Action.NOOP
