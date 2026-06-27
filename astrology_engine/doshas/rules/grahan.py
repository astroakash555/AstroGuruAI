"""Grahan Dosha detection rule."""

from __future__ import annotations

from astrology_engine.doshas.base import DoshaRule
from astrology_engine.doshas.rules._helpers import build_detection, condition
from astrology_engine.doshas.types import DoshaDetection
from astrology_engine.yogas.context import ChartContext

ECLIPSE_ORB_DEGREES = 12.0


class GrahanDoshaRule(DoshaRule):
    """
    Grahan Dosha: Sun/Moon afflicted by Rahu or Ketu (eclipse combinations).

    Detects conjunctions within eclipse orb.
    """

    dosha_id = "grahan_dosha"
    dosha_name = "Grahan Dosha"
    category = "eclipse"

    def detect(self, context: ChartContext) -> DoshaDetection:
        combinations = [
            ("Sun", "Rahu", "solar_grahan"),
            ("Sun", "Ketu", "solar_grahan"),
            ("Moon", "Rahu", "lunar_grahan"),
            ("Moon", "Ketu", "lunar_grahan"),
        ]

        active: list[tuple[str, str, str, float]] = []
        for luminary, node, label in combinations:
            separation = _angular_separation(
                context.get_planet(luminary).longitude,
                context.get_planet(node).longitude,
            )
            same_sign = context.planets_in_same_sign(luminary, node)
            if same_sign and separation <= ECLIPSE_ORB_DEGREES:
                active.append((luminary, node, label, separation))

        is_present = len(active) > 0
        severity = min(0.6 + (len(active) * 0.1), 0.95) if is_present else 0.0

        conditions = [
            condition(
                f"{luminary.lower()}_{node.lower()}_conjunction",
                True,
                f"{luminary} and {node} within {separation:.1f}° ({label}).",
            )
            for luminary, node, label, separation in active
        ]
        if not conditions:
            conditions = [condition("eclipse_combinations", False, "No grahan combinations detected.")]

        subtypes = sorted({label for _, _, label, _ in active})
        subtype = subtypes[0] if len(subtypes) == 1 else ("mixed_grahan" if subtypes else None)

        evidence = [
            f"{luminary}-{node} {label} separation {separation:.1f}°."
            for luminary, node, label, separation in active
        ]
        planets = tuple(dict.fromkeys(
            planet for luminary, node, _, _ in active for planet in (luminary, node)
        ))

        return build_detection(
            dosha_id=self.dosha_id,
            dosha_name=self.dosha_name,
            category_key="grahan_dosha",
            is_present=is_present,
            severity=severity,
            description="Forms when Sun or Moon is eclipsed by Rahu/Ketu, indicating shadow influence on vitality or mind.",
            planets=planets,
            houses=tuple(sorted({
                context.house_of_planet(luminary)
                for luminary, _, _, _ in active
            })),
            conditions=conditions,
            evidence=evidence,
            subtype=subtype,
        )


def _angular_separation(first: float, second: float) -> float:
    diff = abs(first - second) % 360.0
    return diff if diff <= 180.0 else 360.0 - diff
