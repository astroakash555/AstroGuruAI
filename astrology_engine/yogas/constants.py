"""Yoga detection constants."""

from __future__ import annotations

# Kendra, trikona, and dusthana house sets
KENDRA_HOUSES: frozenset[int] = frozenset({1, 4, 7, 10})
TRIKONA_HOUSES: frozenset[int] = frozenset({1, 5, 9})
DUSTHANA_HOUSES: frozenset[int] = frozenset({6, 8, 12})

# Sign indices 0-11 (Aries to Pisces)
DEBILITATION_SIGNS: dict[str, int] = {
    "Sun": 6,       # Libra
    "Moon": 7,      # Scorpio
    "Mars": 3,      # Cancer
    "Mercury": 11,  # Pisces
    "Jupiter": 9,   # Capricorn
    "Venus": 5,     # Virgo
    "Saturn": 0,    # Aries
}

EXALTATION_SIGNS: dict[str, int] = {
    "Sun": 0,       # Aries
    "Moon": 1,      # Taurus
    "Mars": 9,      # Capricorn
    "Mercury": 5,   # Virgo
    "Jupiter": 3,   # Cancer
    "Venus": 11,    # Pisces
    "Saturn": 6,    # Libra
}

OWN_SIGNS: dict[str, tuple[int, ...]] = {
    "Sun": (4,),
    "Moon": (3,),
    "Mars": (0, 7),
    "Mercury": (2, 5),
    "Jupiter": (8, 11),
    "Venus": (1, 6),
    "Saturn": (9, 10),
}

# Planets with special full aspects: Mars 4,7,8; Jupiter 5,7,9; Saturn 3,7,10
SPECIAL_ASPECTS: dict[str, frozenset[int]] = {
    "Mars": frozenset({4, 7, 8}),
    "Jupiter": frozenset({5, 7, 9}),
    "Saturn": frozenset({3, 7, 10}),
}

YOGA_CATEGORIES: dict[str, str] = {
    "gaj_kesari": "wealth_wisdom",
    "raj_yoga": "power_status",
    "vipreet_raj": "turnaround",
    "budhaditya": "intelligence",
    "chandra_mangal": "wealth_drive",
    "neech_bhang_raj": "cancellation_elevation",
}
