"""Neech Bhang Raj Yoga detection rule."""

from __future__ import annotations

from astrology_engine.yogas.base import YogaRule
from astrology_engine.yogas.constants import DEBILITATION_SIGNS, EXALTATION_SIGNS, KENDRA_HOUSES
from astrology_engine.yogas.context import ChartContext
from astrology_engine.yogas.rules._helpers import build_detection, condition
from astrology_engine.yogas.types import YogaDetection


class NeechBhangRajYogaRule(YogaRule):
    """
    Neech Bhang Raj Yoga: debilitation cancellation leading to elevation.

    Evaluates classical cancellation factors for debilitated planets.
    """

    yoga_id = "neech_bhang_raj"
    yoga_name = "Neech Bhang Raj Yoga"
    category = "cancellation_elevation"

    DEBILITATED_PLANETS = tuple(DEBILITATION_SIGNS.keys())

    def detect(self, context: ChartContext) -> YogaDetection:
        cancellations: list[tuple[str, list[str]]] = []

        for planet_name in self.DEBILITATED_PLANETS:
            sign_index = context.sign_of_planet(planet_name)
            if sign_index != DEBILITATION_SIGNS[planet_name]:
                continue

            reasons = self._cancellation_reasons(context, planet_name)
            if reasons:
                cancellations.append((planet_name, reasons))

        is_present = len(cancellations) > 0
        strength = min(0.7 + (len(cancellations) * 0.08), 0.98) if is_present else 0.0

        conditions = [
            condition(
                "debilitation_cancellation",
                is_present,
                f"{len(cancellations)} debilitated planet(s) with cancellation factors.",
            )
        ]
        evidence = [
            f"{planet}: {', '.join(reasons)}"
            for planet, reasons in cancellations
        ]

        houses = tuple(sorted({
            context.house_of_planet(planet)
            for planet, _ in cancellations
        }))

        return build_detection(
            yoga_id=self.yoga_id,
            yoga_name=self.yoga_name,
            category_key="neech_bhang_raj",
            is_present=is_present,
            strength=strength,
            description="Forms when debilitation of a planet is cancelled, often elevating status after early struggle.",
            planets=tuple(planet for planet, _ in cancellations),
            houses=houses,
            conditions=conditions,
            evidence=evidence,
        )

    def _cancellation_reasons(self, context: ChartContext, planet_name: str) -> list[str]:
        reasons: list[str] = []
        deb_sign = DEBILITATION_SIGNS[planet_name]
        deb_lord = context.lord_of_sign(deb_sign)
        exalt_sign = EXALTATION_SIGNS.get(planet_name)
        exalt_lord = context.lord_of_sign(exalt_sign) if exalt_sign is not None else None

        if context.is_in_kendra_from(planet_name, 1):
            reasons.append("debilitated planet in kendra from lagna")

        if context.is_in_kendra_from(deb_lord, 1):
            reasons.append("dispositor in kendra from lagna")

        moon_house = context.house_of_planet("Moon")
        if context.is_in_kendra_from(planet_name, moon_house):
            reasons.append("debilitated planet in kendra from Moon")

        if context.is_in_kendra_from(deb_lord, moon_house):
            reasons.append("dispositor in kendra from Moon")

        if exalt_lord and context.has_aspect(exalt_lord, planet_name):
            reasons.append(f"aspect from exaltation lord {exalt_lord}")

        if context.planets_in_same_sign(planet_name, deb_lord):
            reasons.append("debilitated planet with dispositor in same sign")

        deb_lord_house = context.house_of_planet(deb_lord)
        if deb_lord_house in KENDRA_HOUSES:
            reasons.append("dispositor placed in kendra house")

        return reasons
