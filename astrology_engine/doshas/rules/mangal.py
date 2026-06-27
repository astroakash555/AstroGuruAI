"""Mangal Dosha detection rule."""

from __future__ import annotations

from astrology_engine.doshas.base import DoshaRule
from astrology_engine.doshas.constants import (
    MANGAL_DOSHA_HOUSES,
    MANGAL_EXALTATION_SIGN,
    MANGAL_OWN_SIGNS,
)
from astrology_engine.doshas.rules._helpers import build_detection, condition
from astrology_engine.doshas.types import DoshaDetection
from astrology_engine.yogas.context import ChartContext


class MangalDoshaRule(DoshaRule):
    """
    Mangal Dosha: Mars placed in 1, 4, 7, 8, or 12 from lagna or Moon.

    Reports mitigating factors that reduce severity (analysis only).
    """

    dosha_id = "mangal_dosha"
    dosha_name = "Mangal Dosha"
    category = "relationship"

    def detect(self, context: ChartContext) -> DoshaDetection:
        mars_house = context.house_of_planet("Mars")
        moon_house = context.house_of_planet("Moon")

        from_lagna = mars_house in MANGAL_DOSHA_HOUSES
        moon_sensitive = MangalDoshaRule._sensitive_from_reference(context, "Mars", moon_house)

        is_present = from_lagna or moon_sensitive
        mitigating = self._mitigating_factors(context)

        base_severity = 0.0
        if is_present:
            base_severity = 0.8 if from_lagna and moon_sensitive else 0.65
            base_severity -= min(len(mitigating) * 0.08, 0.35)

        conditions = [
            condition(
                "mars_in_sensitive_house_from_lagna",
                from_lagna,
                f"Mars in house {mars_house} from lagna.",
            ),
            condition(
                "mars_in_sensitive_house_from_moon",
                moon_sensitive,
                f"Mars in house {mars_house} relative to Moon in house {moon_house}.",
            ),
        ]
        evidence = []
        if from_lagna:
            evidence.append(f"Mars occupies house {mars_house} counted from lagna.")
        if moon_sensitive:
            evidence.append(f"Mars triggers sensitive placement from Moon.")
        if mitigating:
            evidence.extend(f"Mitigating factor: {factor}" for factor in mitigating)

        return build_detection(
            dosha_id=self.dosha_id,
            dosha_name=self.dosha_name,
            category_key="mangal_dosha",
            is_present=is_present,
            severity=base_severity,
            description="Associated with Mars in marriage-sensitive houses, often linked to marital friction or delay.",
            planets=("Mars",),
            houses=(mars_house,),
            conditions=conditions,
            evidence=evidence,
            mitigating_factors=mitigating,
        )

    @staticmethod
    def _sensitive_from_reference(context: ChartContext, planet: str, reference_house: int) -> bool:
        planet_house = context.house_of_planet(planet)
        for sensitive in MANGAL_DOSHA_HOUSES:
            target = ((reference_house + sensitive - 2) % 12) + 1
            if planet_house == target:
                return True
        return False

    @staticmethod
    def _mitigating_factors(context: ChartContext) -> list[str]:
        factors: list[str] = []
        mars_sign = context.sign_of_planet("Mars")

        if mars_sign in MANGAL_OWN_SIGNS:
            factors.append("Mars in own sign")
        if mars_sign == MANGAL_EXALTATION_SIGN:
            factors.append("Mars exalted in Capricorn")
        if context.has_aspect("Jupiter", "Mars"):
            factors.append("Jupiter aspects Mars")
        if context.planets_in_same_sign("Mars", "Jupiter"):
            factors.append("Mars conjoined with Jupiter")

        return factors
