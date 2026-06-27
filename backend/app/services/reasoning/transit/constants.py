"""Transit intelligence constants for the reasoning layer."""

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

TRANSIT_PLANETS: tuple[str, ...] = (
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

SLOW_TRANSIT_PLANETS: tuple[str, ...] = ("Saturn", "Jupiter", "Rahu", "Ketu")

KENDRA_HOUSES: frozenset[int] = frozenset({1, 4, 7, 10})
TRIKONA_HOUSES: frozenset[int] = frozenset({1, 5, 9})
DUSTHANA_HOUSES: frozenset[int] = frozenset({6, 8, 12})
UPACHAYA_HOUSES: frozenset[int] = frozenset({3, 6, 10, 11})

SADE_SATI_HOUSES_FROM_MOON: frozenset[int] = frozenset({12, 1, 2})
DHAIYA_HOUSES_FROM_MOON: frozenset[int] = frozenset({4, 8})

SATURN_ASPECTS: frozenset[int] = frozenset({3, 7, 10})
JUPITER_ASPECTS: frozenset[int] = frozenset({5, 7, 9})
MARS_ASPECTS: frozenset[int] = frozenset({4, 7, 8})
NODE_ASPECTS: frozenset[int] = frozenset({5, 7, 9})
DEFAULT_ASPECTS: frozenset[int] = frozenset({7})

PLANET_ASPECTS: dict[str, frozenset[int]] = {
    "Sun": DEFAULT_ASPECTS,
    "Moon": DEFAULT_ASPECTS,
    "Mars": MARS_ASPECTS,
    "Mercury": DEFAULT_ASPECTS,
    "Jupiter": JUPITER_ASPECTS,
    "Venus": DEFAULT_ASPECTS,
    "Saturn": SATURN_ASPECTS,
    "Rahu": NODE_ASPECTS,
    "Ketu": NODE_ASPECTS,
}

PLANET_TRANSIT_THEMES: dict[str, str] = {
    "Sun": "authority, visibility, and vitality",
    "Moon": "emotions, public mood, and mental focus",
    "Mars": "action, conflict, and initiative",
    "Mercury": "communication, commerce, and learning",
    "Jupiter": "expansion, wisdom, and opportunity",
    "Venus": "relationships, comfort, and material flow",
    "Saturn": "discipline, delay, and karmic pressure",
    "Rahu": "change, ambition, and unconventional growth",
    "Ketu": "detachment, breaks, and spiritual redirection",
}

HOUSE_TRANSIT_THEMES: dict[int, str] = {
    1: "self-image and personal direction",
    2: "wealth, speech, and family matters",
    3: "effort, courage, and communication",
    4: "home, emotional stability, and property",
    5: "creativity, education, and children",
    6: "health, service, and competition",
    7: "partnerships, marriage, and contracts",
    8: "transformation, inheritance, and crises",
    9: "fortune, dharma, and long journeys",
    10: "career, status, and public reputation",
    11: "gains, networks, and fulfillment",
    12: "expenses, foreign lands, and retreat",
}

DOMAIN_ACTIVATION_THRESHOLD: float = 0.42
EVENT_WINDOW_SUPPORT_THRESHOLD: float = 0.40
DASHA_TRANSIT_SUPPORT_THRESHOLD: float = 0.45

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


class TransitObservationCategory(str, Enum):
    """High-level grouping for transit intelligence observations."""

    PLANET_TRANSIT = "planet_transit"
    HOUSE_TRANSIT = "house_transit"
    NATAL_OVERLAY = "natal_overlay"
    ASPECT = "aspect"
    SADE_SATI = "sade_sati"
    DHAIYA = "dhaiya"
    JUPITER = "jupiter"
    RAHU_KETU = "rahu_ketu"
    EVENT_WINDOW = "event_window"
    DASHA_INTERACTION = "dasha_interaction"
    DOMAIN = "domain"


def sign_index_from_name(sign_name: str) -> int:
    """Resolve a sign name to its 0-based index."""
    normalized = sign_name.strip().title()
    if normalized not in SIGN_NAME_TO_INDEX:
        raise ValueError(f"Unknown sign name: {sign_name!r}")
    return SIGN_NAME_TO_INDEX[normalized]
