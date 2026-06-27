"""KP astrology constants for the reasoning intelligence layer."""

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

SIGNIFICATOR_LEVELS: tuple[str, ...] = ("level_a", "level_b", "level_c", "level_d")

WEEKDAY_LORDS: dict[int, str] = {
    0: "Moon",
    1: "Mars",
    2: "Mercury",
    3: "Jupiter",
    4: "Venus",
    5: "Saturn",
    6: "Sun",
}

EVENT_SUPPORT_THRESHOLD: float = 0.45

EVENT_TEMPLATES: tuple[dict[str, object], ...] = (
    {
        "event_id": "marriage_event",
        "event_type": "marriage",
        "target_houses": (2, 7, 11),
        "primary_planets": ("Venus", "Jupiter"),
    },
    {
        "event_id": "career_event",
        "event_type": "career",
        "target_houses": (2, 6, 10, 11),
        "primary_planets": ("Sun", "Saturn", "Mercury"),
    },
    {
        "event_id": "health_event",
        "event_type": "health",
        "target_houses": (1, 6, 8, 12),
        "primary_planets": ("Sun", "Moon", "Mars"),
    },
    {
        "event_id": "finance_event",
        "event_type": "finance",
        "target_houses": (2, 6, 11),
        "primary_planets": ("Jupiter", "Venus", "Mercury"),
    },
    {
        "event_id": "legal_event",
        "event_type": "legal",
        "target_houses": (6, 8, 12),
        "primary_planets": ("Saturn", "Mars", "Mercury"),
    },
)


class KPObservationCategory(str, Enum):
    """High-level grouping for KP intelligence observations."""

    STAR_LORD = "star_lord"
    SUB_LORD = "sub_lord"
    SIGNIFICATOR = "significator"
    RULING_PLANET = "ruling_planet"
    CUSP = "cusp"
    EVENT_TIMING = "event_timing"


def sign_index_from_name(sign_name: str) -> int:
    """Resolve a sign name to its 0-based index."""
    normalized = sign_name.strip().title()
    if normalized not in SIGN_NAME_TO_INDEX:
        raise ValueError(f"Unknown sign name: {sign_name!r}")
    return SIGN_NAME_TO_INDEX[normalized]


def lord_of_sign(sign_index: int) -> str:
    """Return the planetary lord of a sign index."""
    return SIGN_LORDS[sign_index % 12]


def sign_name_from_longitude(longitude: float) -> str:
    """Return the sign name for a sidereal longitude."""
    index = int(longitude % 360.0 // 30) % 12
    return SIGN_NAMES[index]
