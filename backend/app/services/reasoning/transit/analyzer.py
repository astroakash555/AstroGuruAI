"""Transit intelligence orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.services.reasoning.models import (
    DashaInput,
    HousesInput,
    PlanetPositionSnapshot,
    PlanetPositionsInput,
    TransitInput,
    TransitPlanetSnapshot,
)
from backend.app.services.reasoning.transit.aspects import analyze_transit_aspects
from backend.app.services.reasoning.transit.constants import SIGN_LORDS, SIGN_NAMES, SIGN_NAME_TO_INDEX, sign_index_from_name
from backend.app.services.reasoning.transit.dhaiya import analyze_dhaiya
from backend.app.services.reasoning.transit.event_windows import (
    analyze_domain_activation,
    analyze_event_windows,
    event_windows_to_observations,
)
from backend.app.services.reasoning.transit.house_transits import analyze_house_transits, analyze_natal_overlays
from backend.app.services.reasoning.transit.jupiter import analyze_jupiter_transits
from backend.app.services.reasoning.transit.models import (
    NatalPlanetRecord,
    ReasoningObservation,
    TransitAnalysisResult,
    TransitChartContext,
    TransitPlanetRecord,
)
from backend.app.services.reasoning.transit.planet_transits import (
    analyze_dasha_transit_interaction,
    analyze_planet_transits,
)
from backend.app.services.reasoning.transit.rahu_ketu import analyze_rahu_ketu_transits
from backend.app.services.reasoning.transit.sade_sati import analyze_sade_sati


class TransitIntelligenceAnalyzer:
    """
    Runs modular transit analysis over structured chart and transit inputs.

    Accepts transit snapshots plus optional natal chart and dasha context for
    overlays, aspects, and interaction scoring without API coupling.
    """

    ENGINE_VERSION = "transit_intelligence_v1"

    def analyze(
        self,
        *,
        transit: TransitInput,
        planet_positions: PlanetPositionsInput | None = None,
        houses: HousesInput | None = None,
        dasha: DashaInput | None = None,
        reference_datetime: datetime | None = None,
    ) -> TransitAnalysisResult:
        """Execute all transit analysis modules and aggregate outputs."""
        context = build_transit_context(
            transit=transit,
            planet_positions=planet_positions,
            houses=houses,
            dasha=dasha,
            reference_datetime=reference_datetime or transit.reference_datetime,
        )

        observations: list[ReasoningObservation] = []
        observations.extend(analyze_planet_transits(context))
        observations.extend(analyze_house_transits(context))
        observations.extend(analyze_natal_overlays(context))
        observations.extend(analyze_transit_aspects(context))
        observations.extend(analyze_sade_sati(context))
        observations.extend(analyze_dhaiya(context))
        observations.extend(analyze_jupiter_transits(context))
        observations.extend(analyze_rahu_ketu_transits(context))
        observations.extend(analyze_dasha_transit_interaction(context))
        observations.extend(analyze_domain_activation(context))

        event_windows = analyze_event_windows(context)
        observations.extend(event_windows_to_observations(event_windows))

        category_counts = _count_by_category(observations)

        return TransitAnalysisResult(
            analyzed_at=datetime.now(timezone.utc),
            observations=tuple(observations),
            event_windows=event_windows,
            metadata={
                "engine": self.ENGINE_VERSION,
                "transit_planet_count": len(context.transits),
                "natal_planet_count": len(context.natal_planets),
                "observation_count": len(observations),
                "event_window_count": len(event_windows),
                "category_counts": category_counts,
                "has_chart_context": bool(context.natal_planets),
                "has_dasha_context": context.dasha is not None,
            },
        )


def build_transit_context(
    *,
    transit: TransitInput,
    planet_positions: PlanetPositionsInput | None = None,
    houses: HousesInput | None = None,
    dasha: DashaInput | None = None,
    reference_datetime: datetime | None = None,
) -> TransitChartContext:
    """Build a transit chart context from reasoning-layer snapshots."""
    lagna_sign_index = 0
    lagna_sign_name = "Aries"
    moon_sign_index = 1
    moon_sign_name = "Taurus"
    natal_planets: dict[str, NatalPlanetRecord] = {}
    house_lords = {house: SIGN_LORDS[(house - 1) % 12] for house in range(1, 13)}

    if planet_positions is not None and houses is not None:
        lagna_sign_index = _resolve_lagna_sign_index(planet_positions, houses)
        lagna_sign_name = SIGN_NAMES[lagna_sign_index]
        moon_sign_index, moon_sign_name = _resolve_moon_sign(planet_positions, lagna_sign_index)
        house_lords = {
            house: SIGN_LORDS[(lagna_sign_index + house - 1) % 12]
            for house in range(1, 13)
        }

        for snapshot in planet_positions.planets:
            natal_planets[snapshot.name] = _natal_record_from_snapshot(snapshot, lagna_sign_index)

        if "Ketu" not in natal_planets and "Rahu" in natal_planets:
            natal_planets["Ketu"] = _derive_ketu_from_rahu(natal_planets["Rahu"], lagna_sign_index)

    transits = {
        snapshot.planet: _transit_record_from_snapshot(snapshot)
        for snapshot in transit.planets
    }

    return TransitChartContext(
        lagna_sign_index=lagna_sign_index,
        lagna_sign_name=lagna_sign_name,
        moon_sign_index=moon_sign_index,
        moon_sign_name=moon_sign_name,
        reference_datetime=reference_datetime,
        transits=transits,
        natal_planets=natal_planets,
        house_lords=house_lords,
        dasha=dasha,
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
        raise ValueError("Lagna sign is required to build transit chart context.")
    return sign_index_from_name(ascendant_sign)


def _resolve_moon_sign(
    planet_positions: PlanetPositionsInput,
    lagna_sign_index: int,
) -> tuple[int, str]:
    if planet_positions.moon_sign:
        index = sign_index_from_name(planet_positions.moon_sign)
        return index, SIGN_NAMES[index]
    for snapshot in planet_positions.planets:
        if snapshot.name == "Moon":
            index = sign_index_from_name(snapshot.sign)
            return index, SIGN_NAMES[index]
    return lagna_sign_index, SIGN_NAMES[lagna_sign_index]


def _first_house_sign(houses: HousesInput) -> str | None:
    for cusp in houses.cusps:
        if cusp.number == 1:
            return cusp.sign
    return houses.cusps[0].sign if houses.cusps else None


def _natal_record_from_snapshot(
    snapshot: PlanetPositionSnapshot,
    lagna_sign_index: int,
) -> NatalPlanetRecord:
    sign_index = sign_index_from_name(snapshot.sign)
    house = snapshot.house if snapshot.house is not None else ((sign_index - lagna_sign_index + 12) % 12) + 1
    return NatalPlanetRecord(
        name=snapshot.name,
        sign_name=_normalize_sign_name(snapshot.sign),
        sign_index=sign_index,
        house=house,
    )


def _transit_record_from_snapshot(snapshot: TransitPlanetSnapshot) -> TransitPlanetRecord:
    sign_index = sign_index_from_name(snapshot.sign)
    return TransitPlanetRecord(
        planet=snapshot.planet,
        sign_name=_normalize_sign_name(snapshot.sign),
        sign_index=sign_index,
        house_from_lagna=snapshot.house_from_lagna,
        house_from_moon=snapshot.house_from_moon,
        is_retrograde=snapshot.is_retrograde,
    )


def _normalize_sign_name(sign_name: str) -> str:
    normalized = sign_name.strip().title()
    if normalized not in SIGN_NAME_TO_INDEX:
        return sign_name
    return SIGN_NAMES[SIGN_NAME_TO_INDEX[normalized]]


def _derive_ketu_from_rahu(rahu: NatalPlanetRecord, lagna_sign_index: int) -> NatalPlanetRecord:
    ketu_sign_index = (rahu.sign_index + 6) % 12
    ketu_house = ((ketu_sign_index - lagna_sign_index + 12) % 12) + 1
    return NatalPlanetRecord(
        name="Ketu",
        sign_name=SIGN_NAMES[ketu_sign_index],
        sign_index=ketu_sign_index,
        house=ketu_house,
    )


def _count_by_category(observations: list[ReasoningObservation]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for observation in observations:
        key = observation.category.value
        counts[key] = counts.get(key, 0) + 1
    return counts
