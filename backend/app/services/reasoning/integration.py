"""End-to-end intelligence integration for unified report generation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from astrology_engine.core.types import LagnaKundali
from backend.app.services.reasoning.fusion import FusionContext, IntelligenceFusionEngine
from backend.app.services.reasoning.fusion.models import FusionResult
from backend.app.services.reasoning.kp.analyzer import KPIntelligenceAnalyzer
from backend.app.services.reasoning.lal_kitab.analyzer import LalKitabIntelligenceAnalyzer
from backend.app.services.reasoning.models import HouseSnapshot, HousesInput, PlanetPositionSnapshot, PlanetPositionsInput
from backend.app.services.reasoning.serializers import (
    fusion_result_to_dict,
    kp_result_to_dict,
    lal_kitab_result_to_dict,
    vedic_result_to_dict,
)
from backend.app.services.reasoning.vedic.analyzer import VedicIntelligenceAnalyzer


@dataclass(frozen=True)
class IntelligencePipelineResult:
    """Structured intelligence outputs attached to unified reports."""

    vedic: dict[str, Any]
    kp: dict[str, Any]
    lal_kitab: dict[str, Any]
    fusion: dict[str, Any]
    fusion_result: FusionResult


class IntelligenceReportIntegration:
    """
    Runs Vedic, KP, and Lal Kitab analyzers and fuses their observations.

    This integration layer replaces the legacy ``reasoning_layer`` path inside
    report generation while preserving deterministic, typed analyzer outputs.
    """

    def __init__(
        self,
        *,
        vedic_analyzer: VedicIntelligenceAnalyzer | None = None,
        kp_analyzer: KPIntelligenceAnalyzer | None = None,
        lal_kitab_analyzer: LalKitabIntelligenceAnalyzer | None = None,
        fusion_engine: IntelligenceFusionEngine | None = None,
    ) -> None:
        self._vedic = vedic_analyzer or VedicIntelligenceAnalyzer()
        self._kp = kp_analyzer or KPIntelligenceAnalyzer()
        self._lal_kitab = lal_kitab_analyzer or LalKitabIntelligenceAnalyzer()
        self._fusion = fusion_engine or IntelligenceFusionEngine()

    def run(
        self,
        *,
        planet_positions: PlanetPositionsInput,
        houses: HousesInput,
        reference_datetime: datetime | None = None,
    ) -> IntelligencePipelineResult:
        """Execute all intelligence analyzers and return serialized report sections."""
        vedic_result = self._vedic.analyze(
            planet_positions=planet_positions,
            houses=houses,
        )
        kp_result = self._kp.analyze(
            planet_positions=planet_positions,
            houses=houses,
            reference_datetime=reference_datetime,
        )
        lal_kitab_result = self._lal_kitab.analyze(
            planet_positions=planet_positions,
            houses=houses,
        )
        fusion_result = self._fusion.fuse(
            FusionContext(
                planet_positions=planet_positions,
                houses=houses,
                reference_datetime=reference_datetime,
            )
        )

        return IntelligencePipelineResult(
            vedic=vedic_result_to_dict(vedic_result),
            kp=kp_result_to_dict(kp_result),
            lal_kitab=lal_kitab_result_to_dict(lal_kitab_result),
            fusion=fusion_result_to_dict(fusion_result),
            fusion_result=fusion_result,
        )


def chart_inputs_from_lagna(lagna: LagnaKundali) -> tuple[PlanetPositionsInput, HousesInput]:
    """Build reasoning-layer chart inputs from a computed lagna kundali."""
    ascendant_sign = lagna.ascendant.sign.name_en
    planets = tuple(
        PlanetPositionSnapshot(
            name=planet.name,
            longitude=planet.longitude,
            sign=planet.sign.name_en,
            house=planet.house,
            nakshatra=planet.nakshatra.name,
            is_retrograde=planet.is_retrograde,
        )
        for planet in lagna.planets
    )
    cusps = tuple(
        HouseSnapshot(
            number=house.number,
            sign=house.sign.name_en,
            longitude=house.longitude,
        )
        for house in lagna.houses
    )
    return (
        PlanetPositionsInput(
            ascendant_sign=ascendant_sign,
            moon_sign=_moon_sign_from_lagna(lagna),
            planets=planets,
        ),
        HousesInput(
            ascendant_sign=ascendant_sign,
            house_system="whole_sign",
            cusps=cusps,
        ),
    )


def fusion_confidence_score(intelligence: IntelligencePipelineResult) -> int | None:
    """Convert fusion confidence to the unified report summary scale (0-100)."""
    confidence = intelligence.fusion.get("confidence")
    if confidence is None:
        return None
    return int(round(float(confidence) * 100))


def _moon_sign_from_lagna(lagna: LagnaKundali) -> str | None:
    for planet in lagna.planets:
        if planet.name == "Moon":
            return planet.sign.name_en
    return None
