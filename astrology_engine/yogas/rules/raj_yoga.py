"""Raj Yoga detection rule."""

from __future__ import annotations

from astrology_engine.yogas.base import YogaRule
from astrology_engine.yogas.constants import KENDRA_HOUSES, TRIKONA_HOUSES
from astrology_engine.yogas.context import ChartContext
from astrology_engine.yogas.rules._helpers import build_detection, condition
from astrology_engine.yogas.types import YogaDetection


class RajYogaRule(YogaRule):
    """
    Raj Yoga: association between kendra and trikona lords.

    Detected when a kendra lord and trikona lord conjoin, aspect, or occupy
    each other's signs (exchange simplified via same-sign/conjunction check).
    """

    yoga_id = "raj_yoga"
    yoga_name = "Raj Yoga"
    category = "power_status"

    def detect(self, context: ChartContext) -> YogaDetection:
        kendra_lords = {context.house_lord(house) for house in KENDRA_HOUSES}
        trikona_lords = {context.house_lord(house) for house in TRIKONA_HOUSES}

        pairs: list[tuple[str, str, str]] = []
        for kendra_lord in kendra_lords:
            for trikona_lord in trikona_lords:
                if kendra_lord == trikona_lord:
                    continue
                relation = self._relation(context, kendra_lord, trikona_lord)
                if relation:
                    pairs.append((kendra_lord, trikona_lord, relation))

        is_present = len(pairs) > 0
        strength = min(0.7 + (len(pairs) * 0.05), 1.0) if is_present else 0.0

        conditions = [
            condition(
                "kendra_trikona_lord_association",
                is_present,
                f"Found {len(pairs)} kendra-trikona lord association(s).",
            )
        ]
        evidence = [
            f"{kendra} and {trikona} linked via {relation}."
            for kendra, trikona, relation in pairs[:5]
        ]

        houses = tuple(sorted(set(
            house
            for house in range(1, 13)
            if context.house_lord(house) in {p[0] for p in pairs} | {p[1] for p in pairs}
        )))

        return build_detection(
            yoga_id=self.yoga_id,
            yoga_name=self.yoga_name,
            category_key="raj_yoga",
            is_present=is_present,
            strength=strength,
            description="Forms through connection between kendra and trikona house lords, indicating authority and success.",
            planets=tuple(sorted({planet for pair in pairs for planet in pair[:2]})),
            houses=houses,
            conditions=conditions,
            evidence=evidence,
        )

    @staticmethod
    def _relation(context: ChartContext, first: str, second: str) -> str | None:
        if context.planets_in_same_sign(first, second):
            return "conjunction"
        if context.has_aspect(first, second) or context.has_aspect(second, first):
            return "aspect"
        first_sign = context.sign_of_planet(first)
        second_sign = context.sign_of_planet(second)
        if context.lord_of_sign(first_sign) == second and context.lord_of_sign(second_sign) == first:
            return "mutual_reception"
        return None
