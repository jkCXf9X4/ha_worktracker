"""Daylight/home-status domain package.

Pure Python domain logic for the home-status machine, the outside-light
hysteresis (daylight flag), and the night/seasonal lighting rule. No Home
Assistant imports, no entity IDs, no side effects.

Submodules:
    models        — the explicit input/output types (the adapter contract).
    home_status   — awake/sleep/away machine + schedule boundaries.
    daylight      — latched-lux daylight-flag hysteresis.
    night         — utelampa/sasong decision table (owns the seasonal rule).
"""

from .models import (
    Action,
    DaylightInputs,
    FamilySchedule,
    HomeStatus,
    HomeStatusInputs,
    HomeStatusResult,
    NightLightsInputs,
    NightLightsResult,
)

__all__ = [
    "Action",
    "DaylightInputs",
    "FamilySchedule",
    "HomeStatus",
    "HomeStatusInputs",
    "HomeStatusResult",
    "NightLightsInputs",
    "NightLightsResult",
]
