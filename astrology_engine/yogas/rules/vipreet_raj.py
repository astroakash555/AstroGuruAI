"""Vipreet Raj Yoga detection rule."""

from __future__ import annotations

from astrology_engine.yogas.base import YogaRule
from astrology_engine.yogas.constants import DUSTHANA_HOUSES
from astrology_engine.yogas.context import ChartContext
from astrology_engine.yogas.rules._helpers import build_detection, condition
from astrology_engine.yogas.types import YogaDetection


class VipreetRajYogaRule(YogaRule):
    """
    Vipreet Raj Yoga: dusthana lords (6, 8, 12) placed in dusthana houses.

    Includes Harsha, Sarala, and Vimala sub-patterns.
    """

    yoga_id = "vipreet_raj"
    yoga_name = "Vipreet Raj Yoga"
    category = "turnaround"

    def detect(self, context: ChartContext) -> YogaDetection:
        matches: list[tuple[int, str, int]] = []

        for house in DUSTHANA_HOUSES:
            lord = context.house_lord(house)
            lord_house = context.house_of_planet(lord)
            if lord_house in DUSTHANA_HOUSES:
                matches.append((house, lord, lord_house))

        is_present = len(matches) > 0
        strength = min(0.65 + (len(matches) * 0.1), 0.95) if is_present else 0.0

        subtypes = []
        for source_house, lord, placed_in in matches:
            if source_house == 6 and placed_in == 6:
                subtypes.append("Harsha Yoga")
            elif source_house == 8 and placed_in == 8:
                subtypes.append("Sarala Yoga")
            elif source_house == 12 and placed_in == 12:
                subtypes.append("Vimala Yoga")
            else:
                subtypes.append(f"{lord} ({source_house} lord in house {placed_in})")

        conditions = [
            condition(
                "dusthana_lord_in_dusthana",
                is_present,
                f"{len(matches)} dusthana lord placement(s) in trik houses.",
            )
        ]
        evidence = [f"Subtype indicator: {label}" for label in subtypes]

        return build_detection(
            yoga_id=self.yoga_id,
            yoga_name=self.yoga_name,
            category_key="vipreet_raj",
            is_present=is_present,
            strength=strength,
            description="Forms when lords of difficult houses occupy dusthana houses, turning adversity into rise.",
            planets=tuple(sorted({match[1] for match in matches})),
            houses=tuple(sorted({match[2] for match in matches})),
            conditions=conditions,
            evidence=evidence,
        )
