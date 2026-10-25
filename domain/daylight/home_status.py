"""The family home-status machine — pure translation of ``template/home_status.yaml``.

Decision
    - ``away``  : family not home.
    - ``sleep`` : family home + overnight  [bedtime, wake).
    - ``awake`` : family home + daytime    [wake, bedtime).

Weekday axes differ for wake vs bedtime (owner-verified, #027):
    - wake    uses ``[Mon..Fri]``  → weekday wake, else weekend wake.
    - bedtime uses ``[Sun..Thu]``  → weekday bedtime, else weekend bedtime
      (a Sunday evening bed is a "weekday bedtime").
States compare as zero-padded HH:MM:SS strings (lexicographic == clock order),
so no timestamp math is needed for the core decision. The ``now`` input must be
in local wall time.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, time, timedelta

from .models import FamilySchedule, HomeStatus, HomeStatusInputs, HomeStatusResult

_WAKE_WEEKDAY = frozenset({0, 1, 2, 3, 4})  # Mon..Fri
_BED_WEEKDAY = frozenset({6, 0, 1, 2, 3})  # Sun..Thu


def home_status(inputs: HomeStatusInputs) -> HomeStatusResult:
    """Compute the home-status machine given explicit time/presence inputs."""
    now = inputs.now
    wd = now.weekday()

    if not inputs.family_home:
        status = HomeStatus.AWAY
    else:
        today = now.strftime("%H:%M:%S")
        wake = _pick_wake(inputs.schedule, wd)
        bed = _pick_bed(inputs.schedule, wd)
        status = HomeStatus.AWAKE if wake <= today < bed else HomeStatus.SLEEP

    return HomeStatusResult(
        status=status,
        is_workday=wd in _WAKE_WEEKDAY,
        next_wake=_next_boundary(now, inputs.schedule, _pick_wake),
        next_bedtime=_next_boundary(now, inputs.schedule, _pick_bed),
    )


def _pick_wake(schedule: FamilySchedule, weekday: int) -> str:
    return _fmt(schedule.wake_weekday if weekday in _WAKE_WEEKDAY else schedule.wake_weekend)


def _pick_bed(schedule: FamilySchedule, weekday: int) -> str:
    return _fmt(schedule.bedtime_weekday if weekday in _BED_WEEKDAY else schedule.bedtime_weekend)


def _fmt(t: time) -> str:
    """Serialize a time input to zero-padded HH:MM:SS for lexicographic compare."""
    return t.strftime("%H:%M:%S")


def _boundary_on(day: datetime, hhmmss: str) -> datetime:
    hh, mm, ss = (int(x) for x in hhmmss.split(":"))
    return day.replace(hour=hh, minute=mm, second=ss)


def _next_boundary(
    now: datetime,
    schedule: FamilySchedule,
    picker: Callable[[FamilySchedule, int], str],
) -> datetime:
    """Next boundary from ``now``, replicating the template's axis handling.

    Mirrors ``template/home_status.yaml`` ``next_wake``/``next_bedtime``: the
    boundary uses *today's* weekday axis if still ahead, otherwise *tomorrow's*
    weekday axis (so a Saturday-after-bed ``next_bedtime`` lands on the Sunday
    **weekday** 21:00, not the weekend 21:30).
    """
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_axis = picker(schedule, now.weekday())
    if _boundary_on(today, today_axis) > now:
        return _boundary_on(today, today_axis)
    tomorrow = today + timedelta(days=1)
    tomorrow_axis = picker(schedule, (now.weekday() + 1) % 7)
    return _boundary_on(tomorrow, tomorrow_axis)
