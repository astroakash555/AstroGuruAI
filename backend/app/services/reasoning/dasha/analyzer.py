"""Dasha intelligence orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.services.reasoning.dasha.antardasha import analyze_antardasha
from backend.app.services.reasoning.dasha.constants import SIGN_LORDS, SIGN_NAMES, SIGN_NAME_TO_INDEX, sign_index_from_name
from backend.app.services.reasoning.dasha.effects import (
    analyze_combined_effects,
    analyze_dignity_modifiers,
    analyze_domain_activation,
    analyze_house_activation,
)
from backend.app.services.reasoning.dasha.event_windows import analyze_event_windows, event_windows_to_observations
from backend.app.services.reasoning.dasha.mahadasha import analyze_mahadasha
from backend.app.services.reasoning.dasha.models import (
    DashaAnalysisResult,
    DashaChartContext,
    DashaPlanetRecord,
    ReasoningObservation,
)
from backend.app.services.reasoning.dasha.pratyantardasha import analyze_pratyantardasha
from backend.app.services.reasoning.models import DashaInput, HousesInput, PlanetPositionSnapshot, PlanetPositionsInput
from backend.app.services.reasoning.vedic.constants import (
    DEBILITATION_SIGNS,
    EXALTATION_SIGNS,
    MOOLATRIKONA_SIGNS,
    OWN_SIGNS,
)


class DashaIntelligenceAnalyzer:
    """
    Runs modular dasha analysis over structured dasha and chart inputs.

    Accepts dasha timelines plus optional natal chart data for dignity,
    house activation, and domain scoring without API coupling.
    """

    ENGINE_VERSION = "dasha_intelligence_v1"

    def analyze(
        self,
        *,
        dasha: DashaInput,
        planet_positions: PlanetPositionsInput | None = None,
        houses: HousesInput | None = None,
        reference_datetime: datetime | None = None,
    ) -> DashaAnalysisResult:
        """Execute all dasha analysis modules and aggregate outputs."""
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
            reference_datetime=reference_datetime,
        )

        observations: list[ReasoningObservation] = []
        observations.extend(analyze_mahadasha(context))
        observations.extend(analyze_antardasha(context))
        observations.extend(analyze_pratyantardasha(context))
        observations.extend(analyze_combined_effects(context))
        observations.extend(analyze_dignity_modifiers(context))
        observations.extend(analyze_house_activation(context))
        observations.extend(analyze_domain_activation(context))

        event_windows = analyze_event_windows(context)
        observations.extend(event_windows_to_observations(event_windows))

        category_counts = _count_by_category(observations)
        active_levels = tuple(
            level
            for level in ("mahadasha", "antardasha", "pratyantar")
            if context.active_period(level) is not None
        )

        return DashaAnalysisResult(
            analyzed_at=datetime.now(timezone.utc),
            observations=tuple(observations),
            event_windows=event_windows,
            metadata={
                "engine": self.ENGINE_VERSION,
                "system": dasha.system,
                "active_levels": active_levels,
                "observation_count": len(observations),
                "event_window_count": len(event_windows),
                "category_counts": category_counts,
                "has_chart_context": bool(context.planets),
            },
        )


def build_dasha_context(
    *,
    dasha: DashaInput,
    planet_positions: PlanetPositionsInput | None = None,
    houses: HousesInput | None = None,
    reference_datetime: datetime | None = None,
) -> DashaChartContext:
    """Build a dasha chart context from reasoning-layer snapshots."""
    lagna_sign_index = 0
    lagna_sign_name = "Aries"
    planets: dict[str, DashaPlanetRecord] = {}
    house_lords: dict[int, str] = {house: SIGN_LORDS[(house - 1) % 12] for house in range(1, 13)}

    if planet_positions is not None and houses is not None:
        lagna_sign_index = _resolve_lagna_sign_index(planet_positions, houses)
        lagna_sign_name = SIGN_NAMES[lagna_sign_index]
        house_lords = {
            house: SIGN_LORDS[(lagna_sign_index + house - 1) % 12]
            for house in range(1, 13)
        }

        for snapshot in planet_positions.planets:
            planets[snapshot.name] = _planet_record_from_snapshot(snapshot, lagna_sign_index)

        if "Ketu" not in planets and "Rahu" in planets:
            planets["Ketu"] = _derive_ketu_from_rahu(planets["Rahu"], lagna_sign_index)

    houses_ruled_by = _invert_house_lords(house_lords)

    return DashaChartContext(
        lagna_sign_index=lagna_sign_index,
        lagna_sign_name=lagna_sign_name,
        dasha=dasha,
        reference_datetime=reference_datetime,
        planets=planets,
        house_lords=house_lords,
        houses_ruled_by=houses_ruled_by,
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
        raise ValueError("Lagna sign is required to build dasha chart context.")
    return sign_index_from_name(ascendant_sign)


def _first_house_sign(houses: HousesInput) -> str | None:
    for cusp in houses.cusps:
        if cusp.number == 1:
            return cusp.sign
    return houses.cusps[0].sign if houses.cusps else None


def _planet_record_from_snapshot(
    snapshot: PlanetPositionSnapshot,
    lagna_sign_index: int,
) -> DashaPlanetRecord:
    sign_index = sign_index_from_name(snapshot.sign)
    house = snapshot.house if snapshot.house is not None else ((sign_index - lagna_sign_index + 12) % 12) + 1
    dignity = _resolve_dignity(snapshot.name, sign_index)
    return DashaPlanetRecord(
        name=snapshot.name,
        longitude=snapshot.longitude,
        sign_name=_normalize_sign_name(snapshot.sign),
        sign_index=sign_index,
        house=house,
        dignity=dignity,
        is_retrograde=snapshot.is_retrograde,
    )


def _normalize_sign_name(sign_name: str) -> str:
    normalized = sign_name.strip().title()
    if normalized not in SIGN_NAME_TO_INDEX:
        return sign_name
    return SIGN_NAMES[SIGN_NAME_TO_INDEX[normalized]]


def _derive_ketu_from_rahu(rahu: DashaPlanetRecord, lagna_sign_index: int) -> DashaPlanetRecord:
    ketu_sign_index = (rahu.sign_index + 6) % 12
    ketu_longitude = (rahu.longitude + 180.0) % 360.0
    ketu_house = ((ketu_sign_index - lagna_sign_index + 12) % 12) + 1
    return DashaPlanetRecord(
        name="Ketu",
        longitude=ketu_longitude,
        sign_name=SIGN_NAMES[ketu_sign_index],
        sign_index=ketu_sign_index,
        house=ketu_house,
        dignity=_resolve_dignity("Ketu", ketu_sign_index),
        is_retrograde=rahu.is_retrograde,
    )


def _resolve_dignity(planet: str, sign_index: int) -> str:
    """Resolve classical dignity for a graha in a sign."""
    if planet in EXALTATION_SIGNS and EXALTATION_SIGNS[planet] == sign_index:
        return "exalted"
    if planet in DEBILITATION_SIGNS and DEBILITATION_SIGNS[planet] == sign_index:
        return "debilitated"
    if planet in MOOLATRIKONA_SIGNS and MOOLATRIKONA_SIGNS[planet] == sign_index:
        return "moolatrikona"
    if planet in OWN_SIGNS and sign_index in OWN_SIGNS[planet]:
        return "own"
    return "neutral"


def _invert_house_lords(house_lords: dict[int, str]) -> dict[str, tuple[int, ...]]:
    ruled: dict[str, list[int]] = {}
    for house, lord in house_lords.items():
        ruled.setdefault(lord, []).append(house)
    return {lord: tuple(sorted(values)) for lord, values in ruled.items()}


def _count_by_category(observations: list[ReasoningObservation]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for observation in observations:
        key = observation.category.value
        counts[key] = counts.get(key, 0) + 1
    return counts
