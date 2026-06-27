"""KP significator analysis."""

from __future__ import annotations

from astrology_engine.core.constants import SIGN_LORDS
from astrology_engine.core.types import LagnaKundali, PlanetPosition, VedicChartBundle
from kp_engine.lords import get_star_lord
from kp_engine.types import SignificatorSet


def analyze_significators(chart: LagnaKundali | VedicChartBundle) -> tuple[SignificatorSet, ...]:
    """Compute KP significator levels A-D for each house."""
    lagna = chart.lagna_kundali if isinstance(chart, VedicChartBundle) else chart
    lagna_sign_index = lagna.ascendant.sign.index
    planets = {planet.name: planet for planet in lagna.planets}
    planet_longitudes = {name: position.longitude for name, position in planets.items()}

    significators: list[SignificatorSet] = []
    for house in range(1, 13):
        level_a = _occupants(house, planets)
        level_b = _planets_in_star_of_occupants(level_a, planet_longitudes)
        house_lord = SIGN_LORDS[(lagna_sign_index + house - 1) % 12]
        level_c = _planets_in_star_of(house_lord, planet_longitudes)
        level_d = (house_lord,) if house_lord in planets else tuple()
        combined = tuple(dict.fromkeys(level_a + level_b + level_c + level_d))

        significators.append(
            SignificatorSet(
                house=house,
                level_a=level_a,
                level_b=level_b,
                level_c=level_c,
                level_d=level_d,
                combined=combined,
            )
        )

    return tuple(significators)


def _occupants(house: int, planets: dict[str, PlanetPosition]) -> tuple[str, ...]:
    return tuple(
        name
        for name, position in planets.items()
        if position.house == house
    )


def _planets_in_star_of(reference: str, longitudes: dict[str, float]) -> tuple[str, ...]:
    if reference not in longitudes:
        return tuple()
    target_star = get_star_lord(longitudes[reference])
    return tuple(
        name
        for name, longitude in longitudes.items()
        if get_star_lord(longitude) == target_star
    )


def _planets_in_star_of_occupants(
    occupants: tuple[str, ...],
    longitudes: dict[str, float],
) -> tuple[str, ...]:
    matched: list[str] = []
    for occupant in occupants:
        matched.extend(_planets_in_star_of(occupant, longitudes))
    return tuple(dict.fromkeys(matched))
