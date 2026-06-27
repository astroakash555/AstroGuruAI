"""Lal Kitab constants."""

from __future__ import annotations

LAL_KITAB_CATEGORIES: dict[str, str] = {
    "planet_house": "planet_by_house",
    "rin": "lal_kitab_rin",
    "dosh": "lal_kitab_dosh",
    "recommendation": "lal_kitab_recommendation",
}

DUSTHANA_HOUSES: frozenset[int] = frozenset({6, 8, 12})
KENDRA_HOUSES: frozenset[int] = frozenset({1, 4, 7, 10})

PLANET_EFFECT_CODES: dict[tuple[str, int], str] = {
    ("Sun", 10): "authority_visibility",
    ("Moon", 4): "domestic_emotion",
    ("Mars", 8): "accident_debt_pressure",
    ("Mercury", 6): "dispute_service",
    ("Jupiter", 9): "guidance_dharma",
    ("Venus", 7): "relationship_harmony",
    ("Saturn", 7): "marriage_delay",
    ("Saturn", 8): "chronic_obstacle",
    ("Rahu", 12): "hidden_expense",
    ("Ketu", 6): "service_detachment",
}

RIN_TYPES: dict[str, str] = {
    "pitra_rin": "Pitra Rin",
    "matri_rin": "Matri Rin",
    "stree_rin": "Stree Rin",
    "bhratri_rin": "Bhratri Rin",
    "rnanubandh_rin": "Rnanubandh Rin",
}
