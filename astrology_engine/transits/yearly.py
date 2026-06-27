"""Yearly transit builder."""

from __future__ import annotations

from datetime import date

from astrology_engine.transits.analyzer import build_planet_analysis, detect_sign_changes
from astrology_engine.transits.calculator import TransitCalculator
from astrology_engine.transits.constants import TRANSIT_PLANETS
from astrology_engine.transits.types import TransitInput, YearlyTransitResult


def build_yearly_transit(
    calculator: TransitCalculator,
    transit_input: TransitInput,
    year: int,
) -> YearlyTransitResult:
    """
    Build yearly transit analysis using monthly boundary snapshots.

    Samples the 1st and 15th of each month to capture sign ingresses efficiently.
    """
    sample_dates: list[date] = []
    for month in range(1, 13):
        sample_dates.append(date(year, month, 1))
        sample_dates.append(date(year, month, 15))

    snapshots = calculator.snapshots_for_dates(sample_dates, transit_input)
    sign_changes = detect_sign_changes(snapshots)
    analyses = tuple(
        build_planet_analysis(planet, snapshots, transit_input)
        for planet in TRANSIT_PLANETS
    )

    monthly_highlights: list[str] = []
    for month in range(1, 13):
        month_events = [
            event for event in sign_changes if event.datetime.month == month
        ]
        if month_events:
            labels = ", ".join(
                f"{event.planet}→{event.to_sign}" for event in month_events
            )
            monthly_highlights.append(f"{year}-{month:02d}: {labels}")

    highlights: list[str] = []
    for analysis in analyses:
        if analysis.current:
            highlights.append(
                f"{analysis.planet} ends year in {analysis.current.sign.name_en} "
                f"(house {analysis.current.house_from_lagna} from lagna)."
            )
    highlights.extend(monthly_highlights)

    return YearlyTransitResult(
        year=year,
        period_start=date(year, 1, 1),
        period_end=date(year, 12, 31),
        sign_changes=sign_changes,
        monthly_highlights=tuple(monthly_highlights),
        analyses=analyses,
        highlights=tuple(dict.fromkeys(highlights)),
    )
