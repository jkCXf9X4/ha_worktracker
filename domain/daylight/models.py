"""Domain models for the daylight/home-status policy cluster.

Pure Python — no Home Assistant imports, no entity IDs, no I/O. These types are
the *explicit interface* the adapters use: adapters read HA state, build
:class:`HomeStatusInputs` / :class:`DaylightInputs` / :class:`NightLightsInputs`,
call the policy functions in :mod:`domain.daylight`, and translate the results
back into service calls.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from enum import StrEnum


class HomeStatus(StrEnum):
    """The family-status machine states (mirrors ``sensor.home_status``)."""

    AWAY = "away"
    SLEEP = "sleep"
    AWAKE = "awake"


class Action(StrEnum):
    """A binary device action a policy can request."""

    ON = "on"
    OFF = "off"
    NOOP = "noop"  # leave the device untouched


@dataclass(frozen=True)
class FamilySchedule:
    """The family's wake/bedtime calendar (from the ``input_datetime.*`` helpers).

    The weekday/weekend axes differ for wake vs bedtime (verified owner
    decision, #027): wake uses Mon–Fri / Sat–Sun; bedtime uses Sun–Thu /
    Fri–Sat so that a Sunday evening bed still counts as "weekday bedtime".
    """

    wake_weekday: time
    wake_weekend: time
    bedtime_weekday: time
    bedtime_weekend: time


@dataclass(frozen=True)
class HomeStatusInputs:
    """Inputs for :func:`domain.daylight.home_status.home_status`."""

    family_home: bool
    now: datetime
    schedule: FamilySchedule


@dataclass(frozen=True)
class HomeStatusResult:
    """Decision + dashboard-ready attributes of the status machine."""

    status: HomeStatus
    is_workday: bool
    next_wake: datetime
    next_bedtime: datetime


@dataclass(frozen=True)
class DaylightInputs:
    """Inputs for :func:`domain.daylight.daylight.light_outside`."""

    lux: float
    on_threshold: float
    off_threshold: float
    currently_on: bool


@dataclass(frozen=True)
class NightLightsInputs:
    """Inputs for :func:`domain.daylight.night.resolve_night_lights`.

    ``light_outside`` is the daylight flag (True = bright/day) — NOT the utelampa
    switch state. ``paused`` maps to the ``automatik_nattlampor`` pause toggle.
    """

    light_outside: bool
    christmas_lights: bool
    paused: bool
    ha_ready: bool


@dataclass(frozen=True)
class NightLightsResult:
    """The ``utelampa``/``sasong`` actions the nightly/seasonal rule requests."""

    utelampa: Action
    sasong: Action
