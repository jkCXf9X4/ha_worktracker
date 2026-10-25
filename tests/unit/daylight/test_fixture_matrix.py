"""Fixture-matrix tests: run the policies against tests/fixtures/daylight/*.yaml.

The YAML fixtures are the shared contract between the domain package and the
deployed adapters (pyscript Path E probes). A new behaviour is a new fixture
row; a policy change that contradicts the fixtures fails here. Defaults merge
under the top-level ``defaults`` key.
"""

from __future__ import annotations

import copy
from datetime import datetime, time
from pathlib import Path

import pytest
import yaml
from domain.daylight import (
    Action,
    DaylightInputs,
    FamilySchedule,
    HomeStatusInputs,
    NightLightsInputs,
)
from domain.daylight.daylight import light_outside
from domain.daylight.home_status import home_status
from domain.daylight.night import resolve_night_lights

FIXTURES_DIR = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "daylight"


def _load_matrix(name: str) -> list[dict]:
    doc = yaml.safe_load((FIXTURES_DIR / f"{name}.yaml").read_text())
    defaults = doc.get("defaults", {})
    cases = []
    for case in doc.get("cases", []):
        case = copy.deepcopy(case)
        # shallow-merge defaults under inputs and under schedule
        inputs = {**defaults.get("inputs", {}), **case["inputs"]}
        schedule = {**defaults.get("schedule", {}), **inputs.pop("schedule", {})}
        case["inputs"] = inputs
        case["schedule"] = schedule
        cases.append(case)
    return cases


def _time(s: str) -> time:
    return time.fromisoformat(s)


def _dt(s: str) -> datetime:
    return datetime.fromisoformat(s)


NIGHT_LIGHTS_CASES = _load_matrix("night_lights")
HOME_STATUS_CASES = _load_matrix("home_status")
DAYLIGHT_CASES = _load_matrix("daylight")


@pytest.mark.parametrize("case", NIGHT_LIGHTS_CASES, ids=lambda c: c["name"])
def test_night_lights_matrix(case):
    i = case["inputs"]
    result = resolve_night_lights(
        NightLightsInputs(
            light_outside=bool(i["light_outside"]),
            christmas_lights=bool(i["christmas_lights"]),
            paused=bool(i["paused"]),
            ha_ready=bool(i["ha_ready"]),
        )
    )
    expect = case["expect"]
    assert result.utelampa is Action(expect["utelampa"])
    assert result.sasong is Action(expect["sasong"])


@pytest.mark.parametrize("case", DAYLIGHT_CASES, ids=lambda c: c["name"])
def test_daylight_matrix(case):
    i = case["inputs"]
    result = light_outside(
        DaylightInputs(
            lux=float(i["lux"]),
            on_threshold=float(i["on_threshold"]),
            off_threshold=float(i["off_threshold"]),
            currently_on=bool(i["currently_on"]),
        )
    )
    assert result is bool(case["expect"])


@pytest.mark.parametrize("case", HOME_STATUS_CASES, ids=lambda c: c["name"])
def test_home_status_matrix(case):
    i = case["inputs"]
    s = case["schedule"]
    result = home_status(
        HomeStatusInputs(
            family_home=bool(i["family_home"]),
            now=_dt(i["now"]),
            schedule=FamilySchedule(
                wake_weekday=_time(s["wake_weekday"]),
                wake_weekend=_time(s["wake_weekend"]),
                bedtime_weekday=_time(s["bedtime_weekday"]),
                bedtime_weekend=_time(s["bedtime_weekend"]),
            ),
        )
    )
    expect = case["expect"]
    assert result.status.value == expect["status"]
    assert result.is_workday is bool(expect["is_workday"])
    assert result.next_wake.isoformat(sep=" ", timespec="seconds") == expect["next_wake"]
    assert result.next_bedtime.isoformat(sep=" ", timespec="seconds") == expect["next_bedtime"]
