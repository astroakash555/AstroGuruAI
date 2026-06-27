"""Vimshottari dasha balance and sub-period duration helpers."""

from __future__ import annotations

from astrology_engine.core.constants import DEGREES_PER_NAKSHATRA, NAKSHATRA_NAMES
from astrology_engine.dasha.constants import (
    DAYS_PER_DASHA_YEAR,
    VIMSHOTTARI_LORDS,
    VIMSHOTTARI_TOTAL_YEARS,
    VIMSHOTTARI_YEARS,
)
from astrology_engine.dasha.types import DashaBalance
from astrology_engine.utilities.angles import normalize_longitude
from astrology_engine.utilities.vedic import get_nakshatra


def get_dasha_lord_for_longitude(moon_longitude: float) -> tuple[str, int]:
    """Return dasha lord and nakshatra index for a sidereal moon longitude."""
    nakshatra = get_nakshatra(moon_longitude)
    return nakshatra.lord, nakshatra.index


def get_dasha_lord_for_nakshatra(nakshatra_name: str) -> str:
    """Return dasha lord from nakshatra name."""
    normalized = nakshatra_name.strip().lower()
    for index, name in enumerate(NAKSHATRA_NAMES):
        if name.lower() == normalized:
            return get_nakshatra(index * DEGREES_PER_NAKSHATRA + 0.1).lord
    raise ValueError(f"Unknown nakshatra: {nakshatra_name}")


def compute_balance_at_birth(moon_longitude: float) -> DashaBalance:
    """
    Compute remaining mahadasha balance at birth from moon longitude.

    Uses elapsed fraction within the birth nakshatra to derive the balance
    of the nakshatra lord's mahadasha.
    """
    longitude = normalize_longitude(moon_longitude)
    nakshatra = get_nakshatra(longitude)
    position_in_nakshatra = longitude % DEGREES_PER_NAKSHATRA
    elapsed_fraction = position_in_nakshatra / DEGREES_PER_NAKSHATRA
    elapsed_fraction = min(max(elapsed_fraction, 0.0), 1.0)
    remaining_fraction = 1.0 - elapsed_fraction

    full_years = VIMSHOTTARI_YEARS[nakshatra.lord]
    remaining_years = full_years * remaining_fraction
    remaining_days = remaining_years * DAYS_PER_DASHA_YEAR

    return DashaBalance(
        lord=nakshatra.lord,
        elapsed_fraction=elapsed_fraction,
        remaining_fraction=remaining_fraction,
        duration_years=remaining_years,
        duration_days=remaining_days,
    )


def sub_period_duration_years(main_lord: str, sub_lord: str) -> float:
    """
    Compute Vimshottari sub-period duration in years.

    Formula: (main_lord_years × sub_lord_years) / 120
    """
    return (VIMSHOTTARI_YEARS[main_lord] * VIMSHOTTARI_YEARS[sub_lord]) / VIMSHOTTARI_TOTAL_YEARS


def years_to_days(years: float) -> float:
    """Convert dasha years to days."""
    return years * DAYS_PER_DASHA_YEAR


def next_dasha_lord(lord: str) -> str:
    """Return the next lord in the Vimshottari cycle."""
    index = VIMSHOTTARI_LORDS.index(lord)
    return VIMSHOTTARI_LORDS[(index + 1) % len(VIMSHOTTARI_LORDS)]


def lords_from_start(start_lord: str) -> tuple[str, ...]:
    """Return 9 lords beginning from start_lord in Vimshottari order."""
    start_index = VIMSHOTTARI_LORDS.index(start_lord)
    return tuple(VIMSHOTTARI_LORDS[(start_index + offset) % 9] for offset in range(9))
