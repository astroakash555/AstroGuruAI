"""KP astrology intelligence orchestrator."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from backend.app.services.reasoning.models import HouseSnapshot, HousesInput, PlanetPositionSnapshot, PlanetPositionsInput
from backend.app.services.reasoning.kp.cusps import analyze_cusps, build_cusps
from backend.app.services.reasoning.kp.event_timing import EventTimingAnalyzer
from backend.app.services.reasoning.kp.models import (
    KPCuspRecord,
    KPChartContext,
    KPAnalysisResult,
    KPPlanetRecord,
    ReasoningObservation,
)
from backend.app.services.reasoning.kp.ruling_planets import analyze_ruling_planets, compute_ruling_planets
from backend.app.services.reasoning.kp.significators import analyze_significators, build_significators
from backend.app.services.reasoning.kp.star_lords import analyze_star_lords
from backend.app.services.reasoning.kp.sub_lords import analyze_sub_lords
from backend.app.services.reasoning.kp.constants import SIGN_NAMES, SIGN_NAME_TO_INDEX, sign_index_from_name
from kp_engine.lords import get_sub_lord


class KPIntelligenceAnalyzer:
    """
    Runs modular KP analysis over structured chart inputs.

    Accepts planet positions and house maps from the reasoning layer and
    returns structured ``ReasoningObservation`` records without API coupling.
    """

    ENGINE_VERSION = "kp_intelligence_v1"

    def __init__(self, *, event_timing: EventTimingAnalyzer | None = None) -> None:
        self._event_timing = event_timing or EventTimingAnalyzer()

    @property
    def event_timing(self) -> EventTimingAnalyzer:
        """Event timing analyzer used by this engine instance."""
        return self._event_timing

    def analyze(
        self,
        *,
        planet_positions: PlanetPositionsInput,
        houses: HousesInput,
        reference_datetime: datetime | None = None,
    ) -> KPAnalysisResult:
        """Execute all KP analysis modules and aggregate observations."""
        context = build_kp_context(
            planet_positions,
            houses,
            reference_datetime=reference_datetime,
        )
        observations: list[ReasoningObservation] = []

        observations.extend(analyze_star_lords(context))
        observations.extend(analyze_sub_lords(context))
        observations.extend(analyze_significators(context))
        observations.extend(analyze_ruling_planets(context))
        observations.extend(analyze_cusps(context))
        observations.extend(self._event_timing.analyze_observations(context))

        event_records = self._event_timing.analyze(context)
        category_counts = _count_by_category(observations)

        return KPAnalysisResult(
            analyzed_at=datetime.now(timezone.utc),
            observations=tuple(observations),
            event_timing=event_records,
            metadata={
                "engine": self.ENGINE_VERSION,
                "lagna_sign": context.lagna_sign_name,
                "planet_count": len(context.planets),
                "cusp_count": len(context.cusps),
                "observation_count": len(observations),
                "supported_events": sum(1 for record in event_records if record.is_supported),
                "category_counts": category_counts,
                "ruling_planets_available": context.ruling_planets is not None,
            },
        )


def build_kp_context(
    planet_positions: PlanetPositionsInput,
    houses: HousesInput,
    *,
    reference_datetime: datetime | None = None,
) -> KPChartContext:
    """Build a KP chart context from reasoning-layer snapshots."""
    lagna_sign_index = _resolve_lagna_sign_index(planet_positions, houses)
    lagna_sign_name = SIGN_NAMES[lagna_sign_index]
    lagna_longitude = _resolve_lagna_longitude(houses, lagna_sign_index)

    planets: dict[str, KPPlanetRecord] = {}
    for snapshot in planet_positions.planets:
        planets[snapshot.name] = _planet_record_from_snapshot(snapshot, lagna_sign_index)

    if "Ketu" not in planets and "Rahu" in planets:
        planets["Ketu"] = _derive_ketu_from_rahu(planets["Rahu"], lagna_sign_index)

    cusps = _build_cusp_records(houses, lagna_sign_index, lagna_longitude)
    base_context = KPChartContext(
        lagna_sign_index=lagna_sign_index,
        lagna_sign_name=lagna_sign_name,
        lagna_longitude=lagna_longitude,
        reference_datetime=reference_datetime,
        planets=planets,
        cusps=cusps,
        significators=(),
        ruling_planets=None,
    )
    significators = build_significators(base_context)
    context = replace(base_context, significators=significators)
    ruling_planets = compute_ruling_planets(context)
    return replace(context, ruling_planets=ruling_planets)


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
        raise ValueError("Lagna sign is required to build KP chart context.")
    return sign_index_from_name(ascendant_sign)


def _first_house_sign(houses: HousesInput) -> str | None:
    for cusp in houses.cusps:
        if cusp.number == 1:
            return cusp.sign
    return houses.cusps[0].sign if houses.cusps else None


def _resolve_lagna_longitude(houses: HousesInput, lagna_sign_index: int) -> float:
    for cusp in houses.cusps:
        if cusp.number == 1 and cusp.longitude is not None:
            return cusp.longitude % 360.0
    return float(lagna_sign_index * 30)


def _build_cusp_records(
    houses: HousesInput,
    lagna_sign_index: int,
    lagna_longitude: float,
) -> tuple[KPCuspRecord, ...]:
    if houses.cusps:
        records: list[KPCuspRecord] = []
        for cusp in houses.cusps:
            longitude = cusp.longitude if cusp.longitude is not None else lagna_longitude + ((cusp.number - 1) * 30.0)
            _, star_lord, sub_lord = get_sub_lord(longitude)
            records.append(
                KPCuspRecord(
                    house=cusp.number,
                    longitude=longitude % 360.0,
                    sign_name=_normalize_sign_name(cusp.sign),
                    star_lord=star_lord,
                    sub_lord=sub_lord,
                )
            )
        return tuple(records)

    placeholder_context = KPChartContext(
        lagna_sign_index=lagna_sign_index,
        lagna_sign_name=SIGN_NAMES[lagna_sign_index],
        lagna_longitude=lagna_longitude,
        reference_datetime=None,
        planets={},
        cusps=(),
        significators=(),
        ruling_planets=None,
    )
    return build_cusps(placeholder_context)


def _planet_record_from_snapshot(
    snapshot: PlanetPositionSnapshot,
    lagna_sign_index: int,
) -> KPPlanetRecord:
    sign_index = sign_index_from_name(snapshot.sign)
    house = snapshot.house if snapshot.house is not None else ((sign_index - lagna_sign_index + 12) % 12) + 1
    nakshatra, star_lord, sub_lord = get_sub_lord(snapshot.longitude)
    return KPPlanetRecord(
        name=snapshot.name,
        longitude=snapshot.longitude,
        sign_name=_normalize_sign_name(snapshot.sign),
        sign_index=sign_index,
        house=house,
        nakshatra=snapshot.nakshatra or nakshatra,
        star_lord=star_lord,
        sub_lord=sub_lord,
    )


def _normalize_sign_name(sign_name: str) -> str:
    normalized = sign_name.strip().title()
    if normalized not in SIGN_NAME_TO_INDEX:
        return sign_name
    return SIGN_NAMES[SIGN_NAME_TO_INDEX[normalized]]


def _derive_ketu_from_rahu(rahu: KPPlanetRecord, lagna_sign_index: int) -> KPPlanetRecord:
    ketu_sign_index = (rahu.sign_index + 6) % 12
    ketu_longitude = (rahu.longitude + 180.0) % 360.0
    ketu_house = ((ketu_sign_index - lagna_sign_index + 12) % 12) + 1
    nakshatra, star_lord, sub_lord = get_sub_lord(ketu_longitude)
    return KPPlanetRecord(
        name="Ketu",
        longitude=ketu_longitude,
        sign_index=ketu_sign_index,
        sign_name=SIGN_NAMES[ketu_sign_index],
        house=ketu_house,
        nakshatra=nakshatra,
        star_lord=star_lord,
        sub_lord=sub_lord,
    )


def _count_by_category(observations: list[ReasoningObservation]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for observation in observations:
        key = observation.category.value
        counts[key] = counts.get(key, 0) + 1
    return counts
