"""Budhaditya Yoga detection rule."""

from __future__ import annotations

from astrology_engine.yogas.base import YogaRule
from astrology_engine.yogas.context import ChartContext
from astrology_engine.yogas.rules._helpers import build_detection, condition
from astrology_engine.yogas.types import YogaDetection


class BudhadityaYogaRule(YogaRule):
    """Budhaditya Yoga: Sun and Mercury conjoined in the same sign."""

    yoga_id = "budhaditya"
    yoga_name = "Budhaditya Yoga"
    category = "intelligence"

    COMBUSTION_ORB_DEGREES = 14.0

    def detect(self, context: ChartContext) -> YogaDetection:
        same_sign = context.planets_in_same_sign("Sun", "Mercury")
        sun = context.get_planet("Sun")
        mercury = context.get_planet("Mercury")
        separation = abs(sun.longitude - mercury.longitude)
        if separation > 180:
            separation = 360 - separation
        not_combust = separation > self.COMBUSTION_ORB_DEGREES

        conditions = [
            condition(
                "sun_mercury_conjunction",
                same_sign,
                f"Sun in {sun.sign.name_en}, Mercury in {mercury.sign.name_en}.",
            ),
            condition(
                "mercury_not_deeply_combust",
                not_combust,
                f"Separation between Sun and Mercury is {separation:.2f} degrees.",
            ),
        ]

        is_present = same_sign
        strength = 0.9 if same_sign and not_combust else (0.65 if same_sign else 0.0)
        evidence = []
        if same_sign:
            evidence.append("Sun and Mercury share the same sign.")
        if same_sign and not_combust:
            evidence.append("Mercury retains independent strength (not deeply combust).")
        elif same_sign:
            evidence.append("Mercury is combust; yoga present but reduced strength.")

        return build_detection(
            yoga_id=self.yoga_id,
            yoga_name=self.yoga_name,
            category_key="budhaditya",
            is_present=is_present,
            strength=strength,
            description="Forms when Sun and Mercury are together, indicating sharp intellect and communication skill.",
            planets=("Sun", "Mercury"),
            houses=(context.house_of_planet("Sun"), context.house_of_planet("Mercury")),
            conditions=conditions,
            evidence=evidence,
        )
