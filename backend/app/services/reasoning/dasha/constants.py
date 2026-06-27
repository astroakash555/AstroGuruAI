"""Dasha intelligence constants for the reasoning layer."""

from __future__ import annotations

from enum import Enum

SIGN_NAMES: tuple[str, ...] = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)

SIGN_NAME_TO_INDEX: dict[str, int] = {name: index for index, name in enumerate(SIGN_NAMES)}

SIGN_LORDS: tuple[str, ...] = (
    "Mars",
    "Venus",
    "Mercury",
    "Moon",
    "Sun",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Saturn",
    "Jupiter",
)

CLASSICAL_PLANETS: tuple[str, ...] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
)

ALL_GRAHAS: tuple[str, ...] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Rahu",
    "Ketu",
)

KENDRA_HOUSES: frozenset[int] = frozenset({1, 4, 7, 10})
TRIKONA_HOUSES: frozenset[int] = frozenset({1, 5, 9})
DUSTHANA_HOUSES: frozenset[int] = frozenset({6, 8, 12})
UPACHAYA_HOUSES: frozenset[int] = frozenset({3, 6, 10, 11})

DOMAIN_ACTIVATION_THRESHOLD: float = 0.42
EVENT_WINDOW_SUPPORT_THRESHOLD: float = 0.40

DIGNITY_SEVERITY_MODIFIERS: dict[str, float] = {
    "exalted": 0.12,
    "moolatrikona": 0.08,
    "own": 0.06,
    "neutral": 0.0,
    "debilitated": -0.14,
}

DIGNITY_CONFIDENCE_MODIFIERS: dict[str, float] = {
    "exalted": 0.06,
    "moolatrikona": 0.04,
    "own": 0.03,
    "neutral": 0.0,
    "debilitated": -0.05,
}

PLANET_DASHA_THEMES: dict[str, str] = {
    "Sun": "authority, vitality, recognition, and father-related themes",
    "Moon": "mind, emotions, public connection, and nurturing cycles",
    "Mars": "courage, competition, property, and decisive action",
    "Mercury": "communication, commerce, learning, and analytical work",
    "Jupiter": "wisdom, expansion, dharma, and guidance",
    "Venus": "relationships, comfort, creativity, and material enjoyment",
    "Saturn": "discipline, delays, service, and karmic consolidation",
    "Rahu": "ambition, foreign exposure, unconventional growth, and obsession",
    "Ketu": "detachment, spirituality, research, and sudden breaks",
}

NATURAL_FRIENDS: dict[str, frozenset[str]] = {
    "Sun": frozenset({"Moon", "Mars", "Jupiter"}),
    "Moon": frozenset({"Sun", "Mercury"}),
    "Mars": frozenset({"Sun", "Moon", "Jupiter"}),
    "Mercury": frozenset({"Sun", "Venus"}),
    "Jupiter": frozenset({"Sun", "Moon", "Mars"}),
    "Venus": frozenset({"Mercury", "Saturn"}),
    "Saturn": frozenset({"Mercury", "Venus"}),
    "Rahu": frozenset({"Mercury", "Saturn", "Venus"}),
    "Ketu": frozenset({"Mars", "Jupiter", "Moon"}),
}

NATURAL_ENEMIES: dict[str, frozenset[str]] = {
    "Sun": frozenset({"Venus", "Saturn"}),
    "Moon": frozenset(set()),
    "Mars": frozenset({"Mercury"}),
    "Mercury": frozenset({"Moon"}),
    "Jupiter": frozenset({"Mercury", "Venus"}),
    "Venus": frozenset({"Sun", "Moon"}),
    "Saturn": frozenset({"Sun", "Moon", "Mars"}),
    "Rahu": frozenset({"Sun", "Moon", "Mars"}),
    "Ketu": frozenset({"Sun", "Moon"}),
}

DOMAIN_TEMPLATES: tuple[dict[str, object], ...] = (
    {
        "domain_id": "marriage",
        "display_name": "Marriage",
        "target_houses": (2, 7, 11),
        "primary_planets": ("Venus", "Jupiter", "Moon"),
    },
    {
        "domain_id": "career",
        "display_name": "Career",
        "target_houses": (2, 6, 10, 11),
        "primary_planets": ("Sun", "Saturn", "Mercury"),
    },
    {
        "domain_id": "finance",
        "display_name": "Finance",
        "target_houses": (2, 6, 11),
        "primary_planets": ("Jupiter", "Venus", "Mercury"),
    },
    {
        "domain_id": "health",
        "display_name": "Health",
        "target_houses": (1, 6, 8, 12),
        "primary_planets": ("Sun", "Moon", "Mars"),
    },
    {
        "domain_id": "education",
        "display_name": "Education",
        "target_houses": (4, 5, 9),
        "primary_planets": ("Mercury", "Jupiter", "Moon"),
    },
    {
        "domain_id": "foreign_settlement",
        "display_name": "Foreign Settlement",
        "target_houses": (3, 9, 12),
        "primary_planets": ("Rahu", "Moon", "Saturn"),
    },
    {
        "domain_id": "spirituality",
        "display_name": "Spirituality",
        "target_houses": (5, 9, 12),
        "primary_planets": ("Jupiter", "Ketu", "Saturn"),
    },
)

HOUSE_ACTIVATION_THEMES: dict[int, str] = {
    1: "self-development and personal initiative",
    2: "wealth, speech, and family resources",
    3: "effort, courage, and communication",
    4: "home, emotional foundation, and property",
    5: "creativity, education, and children",
    6: "service, health routines, and competition",
    7: "partnerships, marriage, and public dealings",
    8: "transformation, inheritance, and hidden matters",
    9: "fortune, dharma, and higher learning",
    10: "career, status, and public reputation",
    11: "gains, networks, and fulfillment of desires",
    12: "expenses, foreign lands, and spiritual withdrawal",
}


class DashaObservationCategory(str, Enum):
    """High-level grouping for dasha intelligence observations."""

    MAHADASHA = "mahadasha"
    ANTARDASHA = "antardasha"
    PRATYANTAR = "pratyantar"
    COMBINED_EFFECT = "combined_effect"
    DIGNITY = "dignity"
    HOUSE_ACTIVATION = "house_activation"
    EVENT_WINDOW = "event_window"
    DOMAIN = "domain"


def sign_index_from_name(sign_name: str) -> int:
    """Resolve a sign name to its 0-based index."""
    normalized = sign_name.strip().title()
    if normalized not in SIGN_NAME_TO_INDEX:
        raise ValueError(f"Unknown sign name: {sign_name!r}")
    return SIGN_NAME_TO_INDEX[normalized]


def lord_of_sign(sign_index: int) -> str:
    """Return the classical lord of a sign index."""
    return SIGN_LORDS[sign_index % 12]
