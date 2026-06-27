"""Lal Kitab constants for the reasoning intelligence layer."""

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

DUSTHANA_HOUSES: frozenset[int] = frozenset({6, 8, 12})
KENDRA_HOUSES: frozenset[int] = frozenset({1, 4, 7, 10})
TRIK_HOUSES: frozenset[int] = frozenset({6, 8, 12})

RIN_TYPES: tuple[str, ...] = (
    "pitra_rin",
    "matra_rin",
    "stri_rin",
    "guru_rin",
    "dev_rin",
)

RIN_DISPLAY_NAMES: dict[str, str] = {
    "pitra_rin": "Pitra Rin",
    "matra_rin": "Matra Rin",
    "stri_rin": "Stri Rin",
    "guru_rin": "Guru Rin",
    "dev_rin": "Dev Rin",
}

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

PLANET_EFFECT_DESCRIPTIONS: dict[str, str] = {
    "authority_visibility": "Supports authority, visibility, and public recognition.",
    "domestic_emotion": "Emphasizes domestic comfort and emotional sensitivity.",
    "accident_debt_pressure": "Indicates accident risk, debt pressure, and sudden strain.",
    "dispute_service": "Links the graha to disputes, service, and daily obligations.",
    "guidance_dharma": "Supports guidance, dharma, and mentor-like protection.",
    "relationship_harmony": "Relates to partnership harmony and social grace.",
    "marriage_delay": "Can delay or burden marriage and contractual bonds.",
    "chronic_obstacle": "Creates chronic obstacles and endurance tests.",
    "hidden_expense": "Activates hidden expenses and subconscious restlessness.",
    "service_detachment": "Produces service themes with detachment or dispute edges.",
    "general_house_influence": "Expresses the graha through the occupied house themes.",
}

HOUSE_THEMES: dict[int, str] = {
    1: "self and vitality",
    2: "wealth and speech",
    3: "courage and siblings",
    4: "home and mother",
    5: "children and merit",
    6: "service and conflict",
    7: "marriage and partnerships",
    8: "longevity and sudden events",
    9: "fortune and dharma",
    10: "career and status",
    11: "gains and networks",
    12: "loss and liberation",
}

PLANETARY_COMBINATIONS: tuple[dict[str, object], ...] = (
    {
        "combination_id": "saturn_rahu",
        "title": "Saturn-Rahu Combination",
        "planets": ("Saturn", "Rahu"),
        "description": "Saturn and Rahu linked through conjunction or dusthana axis.",
    },
    {
        "combination_id": "mars_saturn",
        "title": "Mars-Saturn Combination",
        "planets": ("Mars", "Saturn"),
        "description": "Mars and Saturn combine to produce pressure, conflict, or endurance tests.",
    },
    {
        "combination_id": "sun_moon",
        "title": "Sun-Moon Combination",
        "planets": ("Sun", "Moon"),
        "description": "Sun and Moon share a house, intensifying identity and emotional polarity.",
    },
    {
        "combination_id": "venus_mars",
        "title": "Venus-Mars Combination",
        "planets": ("Venus", "Mars"),
        "description": "Venus and Mars combine to affect passion, marriage, and desire patterns.",
    },
    {
        "combination_id": "jupiter_rahu",
        "title": "Jupiter-Rahu Combination",
        "planets": ("Jupiter", "Rahu"),
        "description": "Jupiter and Rahu linked through shared house or dharma-expansion axis.",
    },
)

REMEDY_TEMPLATES: dict[str, dict[str, object]] = {
    "pitra_rin": {
        "title": "Pitra Rin Jupiter Offering",
        "explanation": "Offer yellow items on Thursdays and maintain ancestral respect rituals.",
        "priority": "high",
        "expected_duration": "40 days",
        "planets": ("Sun", "Jupiter"),
        "houses": (9,),
        "confidence": 0.88,
    },
    "matra_rin": {
        "title": "Matra Rin Moon Stabilization",
        "explanation": "Keep silver with you and avoid disrespect toward mother figures.",
        "priority": "high",
        "expected_duration": "43 days",
        "planets": ("Moon",),
        "houses": (4,),
        "confidence": 0.86,
    },
    "stri_rin": {
        "title": "Stri Rin Venus Harmony",
        "explanation": "Offer white flowers on Fridays and avoid harsh speech toward women.",
        "priority": "high",
        "expected_duration": "40 days",
        "planets": ("Venus",),
        "houses": (7,),
        "confidence": 0.85,
    },
    "guru_rin": {
        "title": "Guru Rin Teacher Respect",
        "explanation": "Serve teachers or elders and avoid criticizing guidance figures.",
        "priority": "medium",
        "expected_duration": "52 days",
        "planets": ("Jupiter",),
        "houses": (9,),
        "confidence": 0.84,
    },
    "dev_rin": {
        "title": "Dev Rin Sun Worship",
        "explanation": "Perform daily sunrise gratitude and avoid ego-driven ritual neglect.",
        "priority": "medium",
        "expected_duration": "40 days",
        "planets": ("Sun", "Ketu"),
        "houses": (12,),
        "confidence": 0.83,
    },
    "saturn_rahu": {
        "title": "Saturn-Rahu Mustard Lamp",
        "explanation": "Light a mustard-oil lamp on Saturdays and simplify hidden expenses.",
        "priority": "high",
        "expected_duration": "45 days",
        "planets": ("Saturn", "Rahu"),
        "houses": (8, 12),
        "confidence": 0.87,
    },
    "mars_eighth": {
        "title": "Mars 8th House Sweet Distribution",
        "explanation": "Distribute sweets on Tuesdays and avoid reckless aggression.",
        "priority": "high",
        "expected_duration": "40 days",
        "planets": ("Mars",),
        "houses": (8,),
        "confidence": 0.86,
    },
    "saturn_seventh": {
        "title": "Saturn 7th House Restraint",
        "explanation": "Avoid iron gifts in marriage matters and practice patient partnership conduct.",
        "priority": "medium",
        "expected_duration": "90 days",
        "planets": ("Saturn",),
        "houses": (7,),
        "confidence": 0.82,
    },
    "rahu_twelfth": {
        "title": "Rahu 12th House Expense Control",
        "explanation": "Track sleep and foreign expenses carefully; donate on Saturdays.",
        "priority": "medium",
        "expected_duration": "43 days",
        "planets": ("Rahu",),
        "houses": (12,),
        "confidence": 0.81,
    },
    "general_planet_house": {
        "title": "Lal Kitab House Remedy",
        "explanation": "Follow Lal Kitab house-specific conduct corrections for the activated graha.",
        "priority": "low",
        "expected_duration": "40 days",
        "planets": (),
        "houses": (),
        "confidence": 0.75,
    },
}


class LalKitabObservationCategory(str, Enum):
    """High-level grouping for Lal Kitab intelligence observations."""

    PLANET = "planet"
    HOUSE = "house"
    RIN = "rin"
    COMBINATION = "combination"
    REMEDY = "remedy"


def sign_index_from_name(sign_name: str) -> int:
    """Resolve a sign name to its 0-based index."""
    normalized = sign_name.strip().title()
    if normalized not in SIGN_NAME_TO_INDEX:
        raise ValueError(f"Unknown sign name: {sign_name!r}")
    return SIGN_NAME_TO_INDEX[normalized]


def lord_of_sign(sign_index: int) -> str:
    """Return the planetary lord of a sign index."""
    return SIGN_LORDS[sign_index % 12]
