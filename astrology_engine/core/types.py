"""Typed result objects for astrology engine outputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AyanamsaType(str, Enum):
    LAHIRI = "lahiri"
    RAMAN = "raman"
    KRISHNAMURTI = "krishnamurti"
    YUKTESHWAR = "yukteshwar"


class HouseSystemType(str, Enum):
    WHOLE_SIGN = "whole_sign"
    EQUAL = "equal"
    PLACIDUS = "placidus"
    SRIPATHI = "sripati"


@dataclass(frozen=True)
class ZodiacSign:
    """Zodiac sign metadata derived from ecliptic longitude."""

    index: int
    name_en: str
    name_sa: str
    lord: str
    degree_in_sign: float


@dataclass(frozen=True)
class NakshatraInfo:
    """Lunar mansion information."""

    index: int
    name: str
    lord: str
    pada: int


@dataclass(frozen=True)
class PlanetPosition:
    """Sidereal position of a graha."""

    name: str
    longitude: float
    latitude: float
    speed: float
    is_retrograde: bool
    sign: ZodiacSign
    nakshatra: NakshatraInfo
    house: int | None = None


@dataclass(frozen=True)
class Ascendant:
    """Lagna (ascendant) details."""

    longitude: float
    sign: ZodiacSign
    nakshatra: NakshatraInfo


@dataclass(frozen=True)
class HouseCusp:
    """House cusp for bhava-based charts."""

    number: int
    longitude: float
    sign: ZodiacSign


@dataclass(frozen=True)
class LagnaKundali:
    """D1 Rashi chart with whole-sign house placement."""

    ascendant: Ascendant
    planets: tuple[PlanetPosition, ...]
    houses: tuple[HouseCusp, ...]


@dataclass(frozen=True)
class BhavaChart:
    """Bhava (house cusp) chart with planets mapped to bhavas."""

    ascendant: Ascendant
    house_cusps: tuple[HouseCusp, ...]
    planets: tuple[PlanetPosition, ...]
    planets_by_house: dict[int, tuple[str, ...]]


@dataclass(frozen=True)
class NavamshaChart:
    """D9 Navamsha divisional chart."""

    ascendant: Ascendant
    planets: tuple[PlanetPosition, ...]
    houses: tuple[HouseCusp, ...]


@dataclass(frozen=True)
class ChartMetadata:
    """Computation metadata attached to chart results."""

    julian_day: float
    ayanamsa: str
    house_system: str
    latitude: float
    longitude: float
    datetime_utc: datetime


@dataclass(frozen=True)
class VedicChartBundle:
    """Complete set of primary Vedic charts for a birth moment."""

    metadata: ChartMetadata
    planetary_positions: tuple[PlanetPosition, ...]
    lagna_kundali: LagnaKundali
    bhava_chart: BhavaChart
    navamsha_chart: NavamshaChart
    extra: dict[str, object] = field(default_factory=dict)
