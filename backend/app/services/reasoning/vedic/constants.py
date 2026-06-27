"""Vedic astrology constants and shared chart context for intelligence analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
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
DHANA_HOUSES: frozenset[int] = frozenset({2, 11})

NATURAL_BENEFICS: frozenset[str] = frozenset({"Jupiter", "Venus", "Mercury", "Moon"})
NATURAL_MALEFICS: frozenset[str] = frozenset({"Sun", "Mars", "Saturn", "Rahu", "Ketu"})

# Sign indices 0-11 (Aries to Pisces)
EXALTATION_SIGNS: dict[str, int] = {
    "Sun": 0,
    "Moon": 1,
    "Mars": 9,
    "Mercury": 5,
    "Jupiter": 3,
    "Venus": 11,
    "Saturn": 6,
}

DEBILITATION_SIGNS: dict[str, int] = {
    "Sun": 6,
    "Moon": 7,
    "Mars": 3,
    "Mercury": 11,
    "Jupiter": 9,
    "Venus": 5,
    "Saturn": 0,
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

MOOLATRIKONA_SIGNS: dict[str, int] = {
    "Sun": 4,
    "Moon": 1,
    "Mars": 0,
    "Mercury": 5,
    "Jupiter": 8,
    "Venus": 3,
    "Saturn": 10,
}

# Naisargika (natural) friendship — friends, enemies, neutral companions
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

# Combustion orbs in degrees from the Sun (classical Parashari approximations)
COMBUSTION_ORBS: dict[str, float] = {
    "Moon": 12.0,
    "Mars": 17.0,
    "Mercury": 14.0,
    "Jupiter": 11.0,
    "Venus": 10.0,
    "Saturn": 15.0,
}

# Standard Vedic full aspects by house distance
DEFAULT_ASPECTS: frozenset[int] = frozenset({7})
MARS_ASPECTS: frozenset[int] = frozenset({4, 7, 8})
JUPITER_ASPECTS: frozenset[int] = frozenset({5, 7, 9})
SATURN_ASPECTS: frozenset[int] = frozenset({3, 7, 10})
NODE_ASPECTS: frozenset[int] = frozenset({5, 7, 9})

PLANET_ASPECTS: dict[str, frozenset[int]] = {
    "Mars": MARS_ASPECTS,
    "Jupiter": JUPITER_ASPECTS,
    "Saturn": SATURN_ASPECTS,
    "Rahu": NODE_ASPECTS,
    "Ketu": NODE_ASPECTS,
}

MANGAL_DOSHA_HOUSES: frozenset[int] = frozenset({1, 4, 7, 8, 12})

KAAL_SARP_PLANETS: tuple[str, ...] = CLASSICAL_PLANETS

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

PANCH_MAHAPURUSHA_YOGAS: dict[str, dict[str, object]] = {
    "ruchaka": {"planet": "Mars", "name": "Ruchaka Yoga"},
    "bhadra": {"planet": "Mercury", "name": "Bhadra Yoga"},
    "hamsa": {"planet": "Jupiter", "name": "Hamsa Yoga"},
    "malavya": {"planet": "Venus", "name": "Malavya Yoga"},
    "sasa": {"planet": "Saturn", "name": "Sasa Yoga"},
}

KEMADRUMA_EXCLUDED_FROM_FLANKS: frozenset[str] = frozenset({"Sun", "Rahu", "Ketu"})


class ObservationCategory(str, Enum):
    """High-level grouping for Vedic intelligence observations."""

    PLANET_STRENGTH = "planet_strength"
    HOUSE = "house"
    YOGA = "yoga"
    DOSHA = "dosha"
    ASPECT = "aspect"


class DignityState(str, Enum):
    """Planetary dignity classification."""

    EXALTATION = "exaltation"
    MOOLATRIKONA = "moolatrikona"
    OWN_SIGN = "own_sign"
    FRIENDLY_SIGN = "friendly_sign"
    NEUTRAL_SIGN = "neutral_sign"
    ENEMY_SIGN = "enemy_sign"
    DEBILITATION = "debilitation"


def sign_index_from_name(sign_name: str) -> int:
    """Resolve a sign name to its 0-based index."""
    normalized = sign_name.strip().title()
    if normalized not in SIGN_NAME_TO_INDEX:
        raise ValueError(f"Unknown sign name: {sign_name!r}")
    return SIGN_NAME_TO_INDEX[normalized]


def lord_of_sign(sign_index: int) -> str:
    """Return the planetary lord of a sign index."""
    return SIGN_LORDS[sign_index % 12]


def house_distance(from_house: int, to_house: int) -> int:
    """Return cyclical house count from one bhava to another (1-12)."""
    return ((to_house - from_house + 12) % 12) + 1


def angular_separation(first_longitude: float, second_longitude: float) -> float:
    """Return the smallest angular distance between two longitudes."""
    separation = abs(first_longitude - second_longitude) % 360.0
    return separation if separation <= 180.0 else 360.0 - separation


@dataclass(frozen=True)
class VedicObservation:
    """Structured observation emitted by the Vedic intelligence layer."""

    category: ObservationCategory
    title: str
    explanation: str
    affected_planets: tuple[str, ...] = ()
    affected_houses: tuple[int, ...] = ()
    severity: float = 0.0
    confidence: float = 0.0
    observation_id: str = ""
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class VedicPlanetRecord:
    """Normalized planetary placement used by Vedic analyzers."""

    name: str
    longitude: float
    sign_index: int
    sign_name: str
    house: int
    is_retrograde: bool
    nakshatra: str | None = None


@dataclass(frozen=True)
class VedicChartContext:
    """Whole-sign chart snapshot for Vedic rule evaluation."""

    lagna_sign_index: int
    lagna_sign_name: str
    planets: dict[str, VedicPlanetRecord]
    house_lords: dict[int, str]
    planets_by_house: dict[int, tuple[str, ...]]

    def get_planet(self, name: str) -> VedicPlanetRecord:
        """Return a planet record or raise when the graha is absent."""
        if name not in self.planets:
            raise KeyError(f"Planet {name!r} is not present in the chart context.")
        return self.planets[name]

    def has_planet(self, name: str) -> bool:
        """Return True when the graha exists in the chart context."""
        return name in self.planets

    def house_lord(self, house: int) -> str:
        """Return the lord of a bhava counted from lagna."""
        return self.house_lords[house]

    def house_of_planet(self, name: str) -> int:
        """Return the whole-sign house occupied by a graha."""
        return self.get_planet(name).house

    def sign_of_planet(self, name: str) -> int:
        """Return the sign index occupied by a graha."""
        return self.get_planet(name).sign_index

    def planets_in_same_sign(self, first: str, second: str) -> bool:
        """Return True when two grahas share the same sign."""
        return self.sign_of_planet(first) == self.sign_of_planet(second)

    def house_sign_index(self, house: int) -> int:
        """Return the sign index on the cusp of a whole-sign house."""
        return (self.lagna_sign_index + house - 1) % 12

    def is_in_kendra_from(self, planet_name: str, reference_house: int) -> bool:
        """Return True when a graha occupies a kendra from a reference house."""
        planet_house = self.house_of_planet(planet_name)
        return house_distance(reference_house, planet_house) in KENDRA_HOUSES

    def has_aspect(self, source: str, target: str) -> bool:
        """Return True when source casts a classical aspect onto target."""
        source_house = self.house_of_planet(source)
        target_house = self.house_of_planet(target)
        distance = house_distance(source_house, target_house)
        aspects = PLANET_ASPECTS.get(source, DEFAULT_ASPECTS)
        return distance in aspects

    def aspect_distances(self, source: str, target: str) -> tuple[int, ...]:
        """Return house distances through which source aspects target."""
        source_house = self.house_of_planet(source)
        target_house = self.house_of_planet(target)
        distance = house_distance(source_house, target_house)
        aspects = PLANET_ASPECTS.get(source, DEFAULT_ASPECTS)
        if distance in aspects:
            return (distance,)
        return ()

    def planets_in_house(self, house: int) -> tuple[str, ...]:
        """Return grahas occupying a house."""
        return self.planets_by_house.get(house, ())


def make_observation(
    *,
    observation_id: str,
    category: ObservationCategory,
    title: str,
    explanation: str,
    affected_planets: tuple[str, ...] = (),
    affected_houses: tuple[int, ...] = (),
    severity: float = 0.0,
    confidence: float = 0.0,
    metadata: dict[str, object] | None = None,
) -> VedicObservation:
    """Create a normalized observation with bounded severity and confidence."""
    return VedicObservation(
        observation_id=observation_id,
        category=category,
        title=title,
        explanation=explanation,
        affected_planets=affected_planets,
        affected_houses=affected_houses,
        severity=round(min(max(severity, 0.0), 1.0), 4),
        confidence=round(min(max(confidence, 0.0), 1.0), 4),
        metadata=metadata or {},
    )
