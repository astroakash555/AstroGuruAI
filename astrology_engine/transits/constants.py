"""Transit analysis constants."""

from __future__ import annotations

from astrology_engine.core.constants import SE_JUPITER, SE_MEAN_NODE, SE_SATURN

TRANSIT_PLANETS: tuple[str, ...] = ("Saturn", "Jupiter", "Rahu", "Ketu")

TRANSIT_PLANET_IDS: dict[str, int] = {
    "Saturn": SE_SATURN,
    "Jupiter": SE_JUPITER,
    "Rahu": SE_MEAN_NODE,
}

# Classical full aspect offsets (house distance)
SEVENTH_ASPECT: frozenset[int] = frozenset({7})
SATURN_ASPECTS: frozenset[int] = frozenset({3, 7, 10})
JUPITER_ASPECTS: frozenset[int] = frozenset({5, 7, 9})
NODE_ASPECTS: frozenset[int] = frozenset({5, 7, 9})

PLANET_ASPECTS: dict[str, frozenset[int]] = {
    "Saturn": SATURN_ASPECTS,
    "Jupiter": JUPITER_ASPECTS,
    "Rahu": NODE_ASPECTS,
    "Ketu": NODE_ASPECTS,
}

KENDRA_HOUSES: frozenset[int] = frozenset({1, 4, 7, 10})
DUSTHANA_HOUSES: frozenset[int] = frozenset({6, 8, 12})
TRIK_HOUSES: frozenset[int] = frozenset({6, 8, 12})

TRANSIT_THEMES: dict[str, str] = {
    "Saturn": "discipline_karma_obstacles",
    "Jupiter": "growth_wisdom_opportunity",
    "Rahu": "obsession_change_unconventional",
    "Ketu": "detachment_past_karma_spiritual",
}

SADE_SATI_HOUSES_FROM_MOON: frozenset[int] = frozenset({12, 1, 2})
