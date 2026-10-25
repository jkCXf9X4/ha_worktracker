"""Unit tests for the home-status machine (``domain.daylight.home_status``).

Covers the weekday/weekend axes (owner-verified #027: Sun morning = weekend wake,
Sun evening = weekday bedtime), away, and the next-boundary attributes.
"""

from __future__ import annotations

from datetime import datetime

from domain.daylight import FamilySchedule, HomeStatus, HomeStatusInputs
from domain.daylight.home_status import home_status

from .conftest import wall

WEEKDAY_AWAKE = datetime(2026, 10, 26, 8, 0)  # Mon 08:00
WEEKEND_AWAKE = datetime(2026, 10, 25, 8, 0)  # Sun 08:00


def make_inputs(
    family_home: bool,
    now: datetime,
    schedule: FamilySchedule,
) -> HomeStatusInputs:
    return HomeStatusInputs(family_home=family_home, now=wall(now), schedule=schedule)


def test_weekday_morning_is_awake(schedule):
    result = home_status(make_inputs(True, WEEKDAY_AWAKE, schedule))
    assert result.status == HomeStatus.AWAKE


def test_weekday_after_bedtime_is_sleep(schedule):
    result = home_status(make_inputs(True, datetime(2026, 10, 26, 22, 0), schedule))
    assert result.status == HomeStatus.SLEEP


def test_sunday_morning_uses_weekend_wake(schedule):
    # Sun 08:00 is past weekday wake (06:45) but BEFORE weekend wake (08:00) →
    # still sleep. This pins the #027 Sunday-axis decision.
    result = home_status(make_inputs(True, datetime(2026, 10, 25, 7, 30), schedule))
    assert result.status == HomeStatus.SLEEP
    late = home_status(make_inputs(True, datetime(2026, 10, 25, 9, 0), schedule))
    assert late.status == HomeStatus.AWAKE


def test_sunday_evening_uses_weekday_bedtime(schedule):
    # Sun 21:15: within weekend bedtime axis (21:30) which is NOT yet reached →
    # awake under weekday bedtime (21:00)? No: Sun bedtime axis is weekday (21:00),
    # so 21:15 is already past bed → sleep.
    result = home_status(make_inputs(True, datetime(2026, 10, 25, 21, 15), schedule))
    assert result.status == HomeStatus.SLEEP


def test_saturday_evening_uses_weekend_bedtime(schedule):
    # Sat 21:15 < weekend bedtime (21:30) → awake.
    result = home_status(make_inputs(True, datetime(2026, 10, 24, 21, 15), schedule))
    assert result.status == HomeStatus.AWAKE


def test_away_always_away(schedule):
    result = home_status(make_inputs(False, WEEKDAY_AWAKE, schedule))
    assert result.status == HomeStatus.AWAY
    result_night = home_status(make_inputs(False, datetime(2026, 10, 26, 23, 0), schedule))
    assert result_night.status == HomeStatus.AWAY


def test_exactly_at_wake_is_awake_at_bedtime_is_sleep(schedule):
    awake = home_status(make_inputs(True, datetime(2026, 10, 26, 6, 45), schedule))
    assert awake.status == HomeStatus.AWAKE
    bed = home_status(make_inputs(True, datetime(2026, 10, 26, 21, 0), schedule))
    assert bed.status == HomeStatus.SLEEP


def test_is_workday(schedule):
    assert home_status(make_inputs(True, WEEKDAY_AWAKE, schedule)).is_workday is True
    assert home_status(make_inputs(True, WEEKEND_AWAKE, schedule)).is_workday is False


def test_next_wake_today_or_tomorrow(schedule):
    before = home_status(make_inputs(True, datetime(2026, 10, 26, 5, 0), schedule))
    assert before.next_wake == datetime(2026, 10, 26, 6, 45)
    after = home_status(make_inputs(True, datetime(2026, 10, 26, 12, 0), schedule))
    assert after.next_wake == datetime(2026, 10, 27, 6, 45)


def test_next_bedtime_rolls_to_weekend_axis(schedule):
    # Sat before bed → today Sat 21:30 (weekend axis).
    sat = home_status(make_inputs(True, datetime(2026, 10, 24, 20, 0), schedule))
    assert sat.next_bedtime == datetime(2026, 10, 24, 21, 30)
    # Sun after bed → tomorrow Mon (weekday axis) 21:00.
    sun = home_status(make_inputs(True, datetime(2026, 10, 25, 22, 0), schedule))
    assert sun.next_bedtime == datetime(2026, 10, 26, 21, 0)
