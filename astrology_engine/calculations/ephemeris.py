"""Swiss Ephemeris session wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Final

from astrology_engine.core.constants import (
    HOUSE_SYSTEM_EQUAL,
    HOUSE_SYSTEM_PLACIDUS,
    HOUSE_SYSTEM_SRIPATHI,
    HOUSE_SYSTEM_WHOLE_SIGN,
    SE_MEAN_NODE,
    SE_TRUE_NODE,
    SEFLG_SIDEREAL,
    SEFLG_SPEED,
    SEFLG_SWIEPH,
    SE_SIDM_KRISHNAMURTI,
    SE_SIDM_LAHIRI,
    SE_SIDM_RAMAN,
    SE_SIDM_YUKTESHWAR,
)
from astrology_engine.core.types import AyanamsaType, HouseSystemType
from astrology_engine.utilities.angles import normalize_longitude
from astrology_engine.utilities.datetime_utils import datetime_to_julian_day

AYANAMSA_MAP: Final[dict[AyanamsaType, int]] = {
    AyanamsaType.LAHIRI: SE_SIDM_LAHIRI,
    AyanamsaType.RAMAN: SE_SIDM_RAMAN,
    AyanamsaType.KRISHNAMURTI: SE_SIDM_KRISHNAMURTI,
    AyanamsaType.YUKTESHWAR: SE_SIDM_YUKTESHWAR,
}

HOUSE_SYSTEM_MAP: Final[dict[HouseSystemType, bytes]] = {
    HouseSystemType.WHOLE_SIGN: HOUSE_SYSTEM_WHOLE_SIGN,
    HouseSystemType.EQUAL: HOUSE_SYSTEM_EQUAL,
    HouseSystemType.PLACIDUS: HOUSE_SYSTEM_PLACIDUS,
    HouseSystemType.SRIPATHI: HOUSE_SYSTEM_SRIPATHI,
}


def _import_swisseph():
    """Import Swiss Ephemeris with a helpful installation message."""
    try:
        import swisseph as swe
    except ImportError as exc:
        raise ImportError(
            "pyswisseph is required for astrology calculations. "
            "Install with: pip install pyswisseph"
        ) from exc
    return swe


@dataclass
class EphemerisConfig:
    """Configuration for Swiss Ephemeris computations."""

    ayanamsa: AyanamsaType = AyanamsaType.LAHIRI
    house_system: HouseSystemType = HouseSystemType.WHOLE_SIGN
    use_true_node: bool = False


class EphemerisService:
    """Thin wrapper around Swiss Ephemeris with sidereal Vedic defaults."""

    def __init__(self, config: EphemerisConfig | None = None) -> None:
        self.config = config or EphemerisConfig()
        self._swe = _import_swisseph()
        self._apply_sidereal_mode()

    def _apply_sidereal_mode(self) -> None:
        self._swe.set_sid_mode(AYANAMSA_MAP[self.config.ayanamsa])

    def get_julian_day(self, dt: datetime) -> float:
        return datetime_to_julian_day(dt)

    def get_ayanamsa(self, julian_day: float) -> float:
        return self._swe.get_ayanamsa_ut(julian_day)

    def calc_planet_ut(self, julian_day: float, planet_id: int) -> tuple[float, float, float, float]:
        """
        Calculate sidereal planet position.

        Returns (longitude, latitude, distance, speed_in_longitude).
        """
        flags = SEFLG_SWIEPH | SEFLG_SIDEREAL | SEFLG_SPEED
        result, _ = self._swe.calc_ut(julian_day, planet_id, flags)
        longitude, latitude, distance, speed = result[0], result[1], result[2], result[3]
        return longitude, latitude, distance, speed

    def calc_houses_ut(
        self,
        julian_day: float,
        latitude: float,
        longitude: float,
        house_system: HouseSystemType | None = None,
    ) -> tuple[tuple[float, ...], tuple[float, ...]]:
        """
        Return sidereal house cusps (1-12) and ascmc points from Swiss Ephemeris.

        swe.houses() returns tropical longitudes even when set_sid_mode() is active.
        Planets use SEFLG_SIDEREAL in calc_ut; house angles must be converted here
        by subtracting the Lahiri ayanamsa exactly once.
        """
        hsys = HOUSE_SYSTEM_MAP[house_system or self.config.house_system]
        cusps, ascmc = self._swe.houses(julian_day, latitude, longitude, hsys)
        ayanamsa = self.get_ayanamsa(julian_day)
        sidereal_cusps = tuple(self._tropical_to_sidereal_longitude(cusp, ayanamsa) for cusp in cusps)
        sidereal_ascmc = tuple(
            self._tropical_to_sidereal_longitude(value, ayanamsa) for value in ascmc
        )
        return sidereal_cusps, sidereal_ascmc

    @staticmethod
    def _tropical_to_sidereal_longitude(tropical_longitude: float, ayanamsa: float) -> float:
        """Convert a tropical ecliptic longitude to sidereal using ayanamsa at UT."""
        return normalize_longitude(tropical_longitude - ayanamsa)

    def node_planet_id(self) -> int:
        return SE_TRUE_NODE if self.config.use_true_node else SE_MEAN_NODE
