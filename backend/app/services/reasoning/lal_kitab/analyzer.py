"""Lal Kitab intelligence orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.services.reasoning.lal_kitab.combinations import analyze_planetary_combinations
from backend.app.services.reasoning.lal_kitab.debts import analyze_rin_debts
from backend.app.services.reasoning.lal_kitab.houses import analyze_house_rules
from backend.app.services.reasoning.lal_kitab.models import (
    LalKitabAnalysisResult,
    LalKitabChartContext,
    LalKitabPlanetRecord,
    ReasoningObservation,
)
from backend.app.services.reasoning.lal_kitab.planets import analyze_planet_interpretations
from backend.app.services.reasoning.lal_kitab.remedies import analyze_remedy_observations, generate_remedies
from backend.app.services.reasoning.lal_kitab.constants import SIGN_LORDS, SIGN_NAMES, SIGN_NAME_TO_INDEX, sign_index_from_name
from backend.app.services.reasoning.models import HousesInput, PlanetPositionSnapshot, PlanetPositionsInput


class LalKitabIntelligenceAnalyzer:
    """
    Runs modular Lal Kitab analysis over structured chart inputs.

    Accepts planet positions and house maps from the reasoning layer and
    returns structured observations and remedies without API coupling.
    """

    ENGINE_VERSION = "lal_kitab_intelligence_v1"

    def analyze(
        self,
        *,
        planet_positions: PlanetPositionsInput,
        houses: HousesInput,
    ) -> LalKitabAnalysisResult:
        """Execute all Lal Kitab analysis modules and aggregate outputs."""
        context = build_lal_kitab_context(planet_positions, houses)
        observations: list[ReasoningObservation] = []

        observations.extend(analyze_planet_interpretations(context))
        observations.extend(analyze_house_rules(context))
        observations.extend(analyze_rin_debts(context))
        observations.extend(analyze_planetary_combinations(context))

        base_observations = tuple(observations)
        remedies = generate_remedies(context, base_observations)
        observations.extend(analyze_remedy_observations(remedies))

        category_counts = _count_by_category(observations)
        present_rin_count = sum(
            1
            for item in observations
            if item.category.value == "rin" and item.metadata.get("is_present") is True
        )

        return LalKitabAnalysisResult(
            analyzed_at=datetime.now(timezone.utc),
            observations=tuple(observations),
            remedies=remedies,
            metadata={
                "engine": self.ENGINE_VERSION,
                "lagna_sign": context.lagna_sign_name,
                "planet_count": len(context.planets),
                "observation_count": len(observations),
                "remedy_count": len(remedies),
                "present_rin_count": present_rin_count,
                "category_counts": category_counts,
            },
        )


def build_lal_kitab_context(
    planet_positions: PlanetPositionsInput,
    houses: HousesInput,
) -> LalKitabChartContext:
    """Build a Lal Kitab chart context from reasoning-layer snapshots."""
    lagna_sign_index = _resolve_lagna_sign_index(planet_positions, houses)
    lagna_sign_name = SIGN_NAMES[lagna_sign_index]

    planets: dict[str, LalKitabPlanetRecord] = {}
    for snapshot in planet_positions.planets:
        planets[snapshot.name] = _planet_record_from_snapshot(snapshot, lagna_sign_index)

    if "Ketu" not in planets and "Rahu" in planets:
        planets["Ketu"] = _derive_ketu_from_rahu(planets["Rahu"], lagna_sign_index)

    planets_by_house: dict[int, list[str]] = {house: [] for house in range(1, 13)}
    for name, planet in planets.items():
        planets_by_house[planet.house].append(name)

    house_lords = {
        house: SIGN_LORDS[(lagna_sign_index + house - 1) % 12]
        for house in range(1, 13)
    }

    return LalKitabChartContext(
        lagna_sign_index=lagna_sign_index,
        lagna_sign_name=lagna_sign_name,
        planets=planets,
        planets_by_house={house: tuple(names) for house, names in planets_by_house.items()},
        house_lords=house_lords,
    )


def _resolve_lagna_sign_index(
    planet_positions: PlanetPositionsInput,
    houses: HousesInput,
) -> int:
    ascendant_sign = (
        houses.ascendant_sign
        or planet_positions.ascendant_sign
        or _first_house_sign(houses)
    )
    if ascendant_sign is None:
        raise ValueError("Lagna sign is required to build Lal Kitab chart context.")
    return sign_index_from_name(ascendant_sign)


def _first_house_sign(houses: HousesInput) -> str | None:
    for cusp in houses.cusps:
        if cusp.number == 1:
            return cusp.sign
    return houses.cusps[0].sign if houses.cusps else None


def _planet_record_from_snapshot(
    snapshot: PlanetPositionSnapshot,
    lagna_sign_index: int,
) -> LalKitabPlanetRecord:
    sign_index = sign_index_from_name(snapshot.sign)
    house = snapshot.house if snapshot.house is not None else ((sign_index - lagna_sign_index + 12) % 12) + 1
    return LalKitabPlanetRecord(
        name=snapshot.name,
        longitude=snapshot.longitude,
        sign_name=_normalize_sign_name(snapshot.sign),
        sign_index=sign_index,
        house=house,
        is_retrograde=snapshot.is_retrograde,
    )


def _normalize_sign_name(sign_name: str) -> str:
    normalized = sign_name.strip().title()
    if normalized not in SIGN_NAME_TO_INDEX:
        return sign_name
    return SIGN_NAMES[SIGN_NAME_TO_INDEX[normalized]]


def _derive_ketu_from_rahu(rahu: LalKitabPlanetRecord, lagna_sign_index: int) -> LalKitabPlanetRecord:
    ketu_sign_index = (rahu.sign_index + 6) % 12
    ketu_longitude = (rahu.longitude + 180.0) % 360.0
    ketu_house = ((ketu_sign_index - lagna_sign_index + 12) % 12) + 1
    return LalKitabPlanetRecord(
        name="Ketu",
        longitude=ketu_longitude,
        sign_index=ketu_sign_index,
        sign_name=SIGN_NAMES[ketu_sign_index],
        house=ketu_house,
        is_retrograde=rahu.is_retrograde,
    )


def _count_by_category(observations: list[ReasoningObservation]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for observation in observations:
        key = observation.category.value
        counts[key] = counts.get(key, 0) + 1
    return counts
