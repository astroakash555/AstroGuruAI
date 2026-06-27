"""KP star lord and sub lord calculations."""

from __future__ import annotations

from astrology_engine.core.constants import DEGREES_PER_NAKSHATRA
from astrology_engine.dasha.constants import VIMSHOTTARI_LORDS, VIMSHOTTARI_TOTAL_YEARS, VIMSHOTTARI_YEARS
from astrology_engine.utilities.angles import normalize_longitude
from astrology_engine.utilities.vedic import get_nakshatra


def get_star_lord(longitude: float) -> str:
    """Return KP star lord (nakshatra lord) for a sidereal longitude."""
    return get_nakshatra(longitude).lord


def get_sub_lord(longitude: float) -> tuple[str, str, str]:
    """Return nakshatra name, star lord, and sub lord for a sidereal longitude."""
    normalized = normalize_longitude(longitude)
    nakshatra = get_nakshatra(normalized)
    offset = normalized % DEGREES_PER_NAKSHATRA

    start_index = VIMSHOTTARI_LORDS.index(nakshatra.lord)
    ordered_lords = VIMSHOTTARI_LORDS[start_index:] + VIMSHOTTARI_LORDS[:start_index]

    remaining = offset
    sub_lord = nakshatra.lord
    for lord in ordered_lords:
        sub_span = DEGREES_PER_NAKSHATRA * (VIMSHOTTARI_YEARS[lord] / VIMSHOTTARI_TOTAL_YEARS)
        if remaining < sub_span:
            sub_lord = lord
            break
        remaining -= sub_span

    return nakshatra.name, nakshatra.lord, sub_lord
