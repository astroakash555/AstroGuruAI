"""Lagna (D1) Kundali chart builder."""

from __future__ import annotations

from astrology_engine.calculations.houses import assign_whole_sign_houses, calculate_whole_sign_houses
from astrology_engine.core.types import Ascendant, LagnaKundali, PlanetPosition


def build_lagna_kundali(
    ascendant: Ascendant,
    planets: tuple[PlanetPosition, ...],
) -> LagnaKundali:
    """
    Build the D1 Rashi (Lagna) chart using whole-sign house system.

    Planets are placed in rashis with house numbers counted from lagna sign.
    """
    houses = calculate_whole_sign_houses(ascendant)
    planets_with_houses = assign_whole_sign_houses(planets, ascendant)
    return LagnaKundali(
        ascendant=ascendant,
        planets=planets_with_houses,
        houses=houses,
    )
