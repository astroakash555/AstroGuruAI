"""Chart context for yoga rule evaluation."""

from __future__ import annotations

from dataclasses import dataclass

from astrology_engine.core.constants import SIGN_LORDS
from astrology_engine.core.types import Ascendant, LagnaKundali, PlanetPosition, VedicChartBundle
from astrology_engine.yogas.constants import KENDRA_HOUSES


@dataclass(frozen=True)
class ChartContext:
    """
    Normalized chart snapshot used by yoga rules.

    Built from lagna kundali whole-sign placements.
    """

    ascendant: Ascendant
    planets: dict[str, PlanetPosition]
    house_lords: dict[int, str]
    lagna_sign_index: int

    def get_planet(self, name: str) -> PlanetPosition:
        return self.planets[name]

    def house_lord(self, house: int) -> str:
        return self.house_lords[house]

    def house_of_planet(self, name: str) -> int:
        planet = self.get_planet(name)
        if planet.house is None:
            raise ValueError(f"House not assigned for planet {name}.")
        return planet.house

    def sign_of_planet(self, name: str) -> int:
        return self.get_planet(name).sign.index

    def planets_in_same_sign(self, first: str, second: str) -> bool:
        return self.sign_of_planet(first) == self.sign_of_planet(second)

    def house_distance(self, from_house: int, to_house: int) -> int:
        """Return bhava count from one house to another (1-12 cyclical)."""
        return ((to_house - from_house + 12) % 12) + 1

    def is_in_kendra_from(self, planet_name: str, reference_house: int) -> bool:
        planet_house = self.house_of_planet(planet_name)
        distance = self.house_distance(reference_house, planet_house)
        return distance in KENDRA_HOUSES

    def house_sign_index(self, house: int) -> int:
        return (self.lagna_sign_index + house - 1) % 12

    def lord_of_sign(self, sign_index: int) -> str:
        return SIGN_LORDS[sign_index]

    def has_aspect(self, source: str, target: str) -> bool:
        """Check 7th-house aspect plus classical special aspects."""
        source_house = self.house_of_planet(source)
        target_house = self.house_of_planet(target)
        distance = self.house_distance(source_house, target_house)

        if distance == 7:
            return True

        from astrology_engine.yogas.constants import SPECIAL_ASPECTS

        special = SPECIAL_ASPECTS.get(source)
        if special and distance in special:
            return True
        return False


def build_chart_context(chart: LagnaKundali | VedicChartBundle) -> ChartContext:
    """Build yoga evaluation context from a computed chart."""
    if isinstance(chart, VedicChartBundle):
        lagna = chart.lagna_kundali
    else:
        lagna = chart

    planets = {planet.name: planet for planet in lagna.planets}
    lagna_sign_index = lagna.ascendant.sign.index
    house_lords = {
        house: SIGN_LORDS[(lagna_sign_index + house - 1) % 12]
        for house in range(1, 13)
    }

    return ChartContext(
        ascendant=lagna.ascendant,
        planets=planets,
        house_lords=house_lords,
        lagna_sign_index=lagna_sign_index,
    )
