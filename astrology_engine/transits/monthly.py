"""Monthly transit builder."""

from __future__ import annotations

import calendar
from datetime import date

from astrology_engine.transits.analyzer import build_planet_analysis, detect_sign_changes
from astrology_engine.transits.calculator import TransitCalculator
from astrology_engine.transits.constants import TRANSIT_PLANETS
from astrology_engine.transits.types import MonthlyTransitResult, TransitInput


def build_monthly_transit(
    calculator: TransitCalculator,
    transit_input: TransitInput,
    year: int,
    month: int,
) -> MonthlyTransitResult:
    """Build monthly transit analysis with daily sampling and sign change detection."""
    last_day = calendar.monthrange(year, month)[1]
    period_start = date(year, month, 1)
    period_end = date(year, month, last_day)
    dates = [date(year, month, day) for day in range(1, last_day + 1)]

    daily_snapshots = calculator.snapshots_for_dates(dates, transit_input)
    sign_changes = detect_sign_changes(daily_snapshots)
    analyses = tuple(
        build_planet_analysis(planet, daily_snapshots, transit_input)
        for planet in TRANSIT_PLANETS
    )

    highlights: list[str] = []
    for planet in TRANSIT_PLANETS:
        planet_analysis = next(item for item in analyses if item.planet == planet)
        highlights.extend(planet_analysis.highlights[:2])
    for event in sign_changes:
        highlights.append(
            f"{event.planet} moves from {event.from_sign} to {event.to_sign} on {event.datetime.date()}."
        )

    return MonthlyTransitResult(
        year=year,
        month=month,
        period_start=period_start,
        period_end=period_end,
        sign_changes=sign_changes,
        daily_snapshots=daily_snapshots,
        analyses=analyses,
        highlights=tuple(dict.fromkeys(highlights)),
    )
