"""Lal Kitab chart context."""

from __future__ import annotations

from dataclasses import dataclass

from astrology_engine.core.constants import SIGN_LORDS
from astrology_engine.core.types import LagnaKundali, PlanetPosition, VedicChartBundle
from lal_kitab_engine.constants import DUSTHANA_HOUSES, KENDRA_HOUSES


@dataclass(frozen=True)
class LalKitabContext:
    """Normalized chart snapshot for Lal Kitab rule evaluation."""

    lagna_sign: str
    lagna_sign_index: int
    planets: dict[str, PlanetPosition]

    def house_of(self, planet: str) -> int:
        house = self.planets[planet].house
        if house is None:
            raise ValueError(f"House not assigned for {planet}.")
        return house

    def sign_of(self, planet: str) -> str:
        return self.planets[planet].sign.name_en

    def planets_in_house(self, house: int) -> tuple[str, ...]:
        return tuple(
            name
            for name, position in self.planets.items()
            if position.house == house
        )

    def is_dusthana(self, house: int) -> bool:
        return house in DUSTHANA_HOUSES

    def is_kendra(self, house: int) -> bool:
        return house in KENDRA_HOUSES

    def house_lord(self, house: int) -> str:
        sign_index = (self.lagna_sign_index + house - 1) % 12
        return SIGN_LORDS[sign_index]


def build_lal_kitab_context(chart: LagnaKundali | VedicChartBundle) -> LalKitabContext:
    lagna = chart.lagna_kundali if isinstance(chart, VedicChartBundle) else chart
    planets = {planet.name: planet for planet in lagna.planets}
    return LalKitabContext(
        lagna_sign=lagna.ascendant.sign.name_en,
        lagna_sign_index=lagna.ascendant.sign.index,
        planets=planets,
    )
