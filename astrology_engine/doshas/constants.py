"""Dosha detection constants."""

from __future__ import annotations

# Mangal dosha sensitive houses from lagna/Moon reference
MANGAL_DOSHA_HOUSES: frozenset[int] = frozenset({1, 4, 7, 8, 12})

MANGAL_OWN_SIGNS: frozenset[int] = frozenset({0, 7})  # Aries, Scorpio
MANGAL_EXALTATION_SIGN: int = 9  # Capricorn

# Classical planets evaluated for Kaal Sarp enclosure
KAAL_SARP_PLANETS: tuple[str, ...] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
)

# Kaal Sarp sub-types by Rahu house placement
KAAL_SARP_TYPES: dict[int, str] = {
    1: "Anant",
    2: "Kulik",
    3: "Vasuki",
    4: "Shankhpal",
    5: "Padma",
    6: "Mahapadma",
    7: "Takshak",
    8: "Karkotak",
    9: "Shankhachud",
    10: "Ghatak",
    11: "Vishdhar",
    12: "Sheshnag",
}

DOSHA_CATEGORIES: dict[str, str] = {
    "mangal_dosha": "relationship",
    "kaal_sarp_dosha": "karmic",
    "pitra_dosha": "ancestral",
    "grahan_dosha": "eclipse",
    "shrapit_dosha": "karmic_saturn",
}

SEVERITY_LEVELS: tuple[tuple[str, float], ...] = (
    ("critical", 0.85),
    ("high", 0.7),
    ("moderate", 0.5),
    ("low", 0.3),
    ("minimal", 0.0),
)

# Re-use chart analysis constants from yoga module
from astrology_engine.yogas.constants import DEBILITATION_SIGNS, EXALTATION_SIGNS  # noqa: E402
