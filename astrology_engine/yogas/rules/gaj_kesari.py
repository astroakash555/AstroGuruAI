"""Gaj Kesari Yoga detection rule."""

from __future__ import annotations

from astrology_engine.yogas.base import YogaRule
from astrology_engine.yogas.context import ChartContext
from astrology_engine.yogas.rules._helpers import build_detection, condition
from astrology_engine.yogas.types import YogaDetection


class GajKesariYogaRule(YogaRule):
    """
    Gaj Kesari Yoga: Jupiter in a kendra (1, 4, 7, 10) from the Moon.

    Also checks kendra from lagna as supplementary strength indicator.
    """

    yoga_id = "gaj_kesari"
    yoga_name = "Gaj Kesari Yoga"
    category = "wealth_wisdom"

    def detect(self, context: ChartContext) -> YogaDetection:
        moon_house = context.house_of_planet("Moon")
        jupiter_from_moon = context.is_in_kendra_from("Jupiter", moon_house)
        jupiter_from_lagna = context.is_in_kendra_from("Jupiter", 1)

        conditions = [
            condition(
                "jupiter_kendra_from_moon",
                jupiter_from_moon,
                f"Jupiter in house {context.house_of_planet('Jupiter')} "
                f"relative to Moon in house {moon_house}.",
            ),
            condition(
                "jupiter_kendra_from_lagna",
                jupiter_from_lagna,
                f"Jupiter in house {context.house_of_planet('Jupiter')} relative to lagna.",
            ),
        ]

        is_present = jupiter_from_moon
        strength = 0.85 if jupiter_from_moon and jupiter_from_lagna else (0.75 if jupiter_from_moon else 0.0)
        evidence = []
        if jupiter_from_moon:
            evidence.append("Jupiter occupies a kendra from Moon.")
        if jupiter_from_lagna:
            evidence.append("Jupiter also occupies a kendra from lagna (strength booster).")

        return build_detection(
            yoga_id=self.yoga_id,
            yoga_name=self.yoga_name,
            category_key="gaj_kesari",
            is_present=is_present,
            strength=strength,
            description="Forms when Jupiter is placed in a kendra house from the Moon, granting wisdom and prosperity.",
            planets=("Moon", "Jupiter"),
            houses=(moon_house, context.house_of_planet("Jupiter")),
            conditions=conditions,
            evidence=evidence,
        )
