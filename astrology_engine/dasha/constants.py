"""Vimshottari dasha constants."""

from __future__ import annotations

# Canonical Vimshottari cycle order (120-year total)
VIMSHOTTARI_LORDS: tuple[str, ...] = (
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
)

VIMSHOTTARI_YEARS: dict[str, float] = {
    "Ketu": 7.0,
    "Venus": 20.0,
    "Sun": 6.0,
    "Moon": 10.0,
    "Mars": 7.0,
    "Rahu": 18.0,
    "Jupiter": 16.0,
    "Saturn": 19.0,
    "Mercury": 17.0,
}

VIMSHOTTARI_TOTAL_YEARS: float = sum(VIMSHOTTARI_YEARS.values())  # 120.0

# Standard conversion factor used in Parashari dasha timelines
DAYS_PER_DASHA_YEAR: float = 365.25

DEFAULT_MAX_YEARS: float = 120.0
