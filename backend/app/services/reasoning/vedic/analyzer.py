"""Vedic horoscope intelligence orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from backend.app.services.reasoning.models import HousesInput, PlanetPositionSnapshot, PlanetPositionsInput
from backend.app.services.reasoning.vedic.aspects import analyze_aspects
from backend.app.services.reasoning.vedic.constants import (
    SIGN_LORDS,
    SIGN_NAME_TO_INDEX,
    SIGN_NAMES,
    VedicChartContext,
    VedicObservation,
    VedicPlanetRecord,
    sign_index_from_name,
)
from backend.app.services.reasoning.vedic.doshas import detect_doshas
from backend.app.services.reasoning.vedic.house_analysis import analyze_houses
from backend.app.services.reasoning.vedic.planet_strength import analyze_planet_strengths
from backend.app.services.reasoning.vedic.yogas import detect_yogas


@dataclass(frozen=True)
class VedicAnalysisResult:
    """Complete output from the Vedic intelligence analyzer."""

    analyzed_at: datetime
    observations: tuple[VedicObservation, ...]
    metadata: dict[str, object] = field(default_factory=dict)


class VedicIntelligenceAnalyzer:
    """
    Runs modular Vedic analysis over structured chart inputs.

    Accepts planet positions and house maps from the reasoning layer and
    returns structured observations without API or persistence coupling.
    """

    ENGINE_VERSION = "vedic_intelligence_v1"

    def analyze(
        self,
        *,
        planet_positions: PlanetPositionsInput,
        houses: HousesInput,
    ) -> VedicAnalysisResult:
        """Execute all Vedic analysis modules and aggregate observations."""
        context = build_vedic_context(planet_positions, houses)
        observations: list[VedicObservation] = []

        observations.extend(analyze_planet_strengths(context))
        observations.extend(analyze_houses(context))
        observations.extend(detect_yogas(context))
        observations.extend(detect_doshas(context))
        observations.extend(analyze_aspects(context))

        category_counts = _count_by_category(observations)

        return VedicAnalysisResult(
            analyzed_at=datetime.now(timezone.utc),
            observations=tuple(observations),
            metadata={
                "engine": self.ENGINE_VERSION,
                "lagna_sign": context.lagna_sign_name,
                "planet_count": len(context.planets),
                "observation_count": len(observations),
                "category_counts": category_counts,
            },
        )


def build_vedic_context(
    planet_positions: PlanetPositionsInput,
    houses: HousesInput,
) -> VedicChartContext:
    """Build a whole-sign chart context from reasoning-layer snapshots."""
    lagna_sign_index = _resolve_lagna_sign_index(planet_positions, houses)
    lagna_sign_name = SIGN_NAMES[lagna_sign_index]

    planets: dict[str, VedicPlanetRecord] = {}
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

    return VedicChartContext(
        lagna_sign_index=lagna_sign_index,
        lagna_sign_name=lagna_sign_name,
        planets=planets,
        house_lords=house_lords,
        planets_by_house={house: tuple(names) for house, names in planets_by_house.items()},
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
        raise ValueError("Lagna sign is required to build Vedic chart context.")
    return sign_index_from_name(ascendant_sign)


def _first_house_sign(houses: HousesInput) -> str | None:
    for cusp in houses.cusps:
        if cusp.number == 1:
            return cusp.sign
    return houses.cusps[0].sign if houses.cusps else None


def _planet_record_from_snapshot(
    snapshot: PlanetPositionSnapshot,
    lagna_sign_index: int,
) -> VedicPlanetRecord:
    sign_index = sign_index_from_name(snapshot.sign)
    house = snapshot.house if snapshot.house is not None else ((sign_index - lagna_sign_index + 12) % 12) + 1
    return VedicPlanetRecord(
        name=snapshot.name,
        longitude=snapshot.longitude,
        sign_index=sign_index,
        sign_name=_normalize_sign_name(snapshot.sign),
        house=house,
        is_retrograde=snapshot.is_retrograde,
        nakshatra=snapshot.nakshatra,
    )


def _normalize_sign_name(sign_name: str) -> str:
    """Normalize sign names to the canonical English form."""
    normalized = sign_name.strip().title()
    if normalized not in SIGN_NAME_TO_INDEX:
        return sign_name
    return SIGN_NAMES[SIGN_NAME_TO_INDEX[normalized]]


def _derive_ketu_from_rahu(rahu: VedicPlanetRecord, lagna_sign_index: int) -> VedicPlanetRecord:
    ketu_sign_index = (rahu.sign_index + 6) % 12
    ketu_longitude = (rahu.longitude + 180.0) % 360.0
    ketu_house = ((ketu_sign_index - lagna_sign_index + 12) % 12) + 1
    return VedicPlanetRecord(
        name="Ketu",
        longitude=ketu_longitude,
        sign_index=ketu_sign_index,
        sign_name=SIGN_NAMES[ketu_sign_index],
        house=ketu_house,
        is_retrograde=rahu.is_retrograde,
        nakshatra=rahu.nakshatra,
    )


def _count_by_category(observations: list[VedicObservation]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for observation in observations:
        key = observation.category.value
        counts[key] = counts.get(key, 0) + 1
    return counts
