"""Daily transit builder."""

from __future__ import annotations

from datetime import date, datetime, time

from astrology_engine.transits.analyzer import build_planet_analysis
from astrology_engine.transits.calculator import TransitCalculator
from astrology_engine.transits.constants import TRANSIT_PLANETS
from astrology_engine.transits.types import DailyTransitResult, TransitInput


def build_daily_transit(
    calculator: TransitCalculator,
    transit_input: TransitInput,
    target_date: date,
    *,
    local_time: time = time(12, 0),
) -> DailyTransitResult:
    """Build daily transit analysis for a specific date."""
    from astrology_engine.utilities.datetime_utils import resolve_timezone

    tz = resolve_timezone(transit_input.timezone)
    when = datetime.combine(target_date, local_time, tzinfo=tz)
    snapshots = calculator.snapshot_at(when, transit_input)
    analyses = tuple(
        build_planet_analysis(planet, snapshots, transit_input)
        for planet in TRANSIT_PLANETS
    )
    return DailyTransitResult(
        date=target_date,
        snapshots=snapshots,
        analyses=analyses,
    )
