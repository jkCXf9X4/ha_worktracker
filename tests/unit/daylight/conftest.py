"""pytest fixtures and helpers shared across the domain test suite."""

from __future__ import annotations

from datetime import datetime, time

import pytest
from domain.daylight import FamilySchedule

SCHEDULE = FamilySchedule(
    wake_weekday=time(6, 45),
    wake_weekend=time(8, 0),
    bedtime_weekday=time(21, 0),
    bedtime_weekend=time(21, 30),
)


def wall(dt: datetime) -> datetime:
    """Strip tzinfo so all policy inputs are naive local wall time."""
    return dt.replace(tzinfo=None)


@pytest.fixture
def schedule() -> FamilySchedule:
    return SCHEDULE
