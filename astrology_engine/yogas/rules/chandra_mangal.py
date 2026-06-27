"""Chandra Mangal Yoga detection rule."""

from __future__ import annotations

from astrology_engine.yogas.base import YogaRule
from astrology_engine.yogas.context import ChartContext
from astrology_engine.yogas.rules._helpers import build_detection, condition
from astrology_engine.yogas.types import YogaDetection


class ChandraMangalYogaRule(YogaRule):
    """Chandra Mangal Yoga: Moon and Mars conjoined in the same sign."""

    yoga_id = "chandra_mangal"
    yoga_name = "Chandra Mangal Yoga"
    category = "wealth_drive"

    def detect(self, context: ChartContext) -> YogaDetection:
        same_sign = context.planets_in_same_sign("Moon", "Mars")
        moon = context.get_planet("Moon")
        mars = context.get_planet("Mars")

        conditions = [
            condition(
                "moon_mars_conjunction",
                same_sign,
                f"Moon in {moon.sign.name_en} (house {moon.house}), "
                f"Mars in {mars.sign.name_en} (house {mars.house}).",
            )
        ]

        is_present = same_sign
        strength = 0.8 if same_sign else 0.0
        evidence = ["Moon and Mars occupy the same sign, indicating wealth through enterprise."] if same_sign else []

        return build_detection(
            yoga_id=self.yoga_id,
            yoga_name=self.yoga_name,
            category_key="chandra_mangal",
            is_present=is_present,
            strength=strength,
            description="Forms when Moon and Mars are together, linking emotion with action for material gain.",
            planets=("Moon", "Mars"),
            houses=(context.house_of_planet("Moon"), context.house_of_planet("Mars")),
            conditions=conditions,
            evidence=evidence,
        )
