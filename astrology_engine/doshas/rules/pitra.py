"""Pitra Dosha detection rule."""

from __future__ import annotations

from astrology_engine.doshas.base import DoshaRule
from astrology_engine.doshas.rules._helpers import build_detection, condition
from astrology_engine.doshas.types import DoshaDetection
from astrology_engine.yogas.constants import DUSTHANA_HOUSES
from astrology_engine.yogas.context import ChartContext


class PitraDoshaRule(DoshaRule):
    """
    Pitra Dosha: ancestral karmic indicators via Sun, 9th house, and nodes.

    Evaluates multiple classical combinations.
    """

    dosha_id = "pitra_dosha"
    dosha_name = "Pitra Dosha"
    category = "ancestral"

    def detect(self, context: ChartContext) -> DoshaDetection:
        ninth_lord = context.house_lord(9)
        ninth_lord_house = context.house_of_planet(ninth_lord)
        rahu_house = context.house_of_planet("Rahu")
        saturn_house = context.house_of_planet("Saturn")

        sun_with_rahu = context.planets_in_same_sign("Sun", "Rahu")
        sun_with_ketu = context.planets_in_same_sign("Sun", "Ketu")
        rahu_in_9th = rahu_house == 9
        ketu_in_9th = context.house_of_planet("Ketu") == 9
        ninth_lord_in_dusthana = ninth_lord_house in DUSTHANA_HOUSES
        saturn_in_9th = saturn_house == 9
        sun_in_dusthana = context.house_of_planet("Sun") in DUSTHANA_HOUSES
        ninth_lord_with_nodes = (
            context.planets_in_same_sign(ninth_lord, "Rahu")
            or context.planets_in_same_sign(ninth_lord, "Ketu")
        )

        triggers = {
            "sun_conjunct_rahu": sun_with_rahu,
            "sun_conjunct_ketu": sun_with_ketu,
            "rahu_in_9th_house": rahu_in_9th,
            "ketu_in_9th_house": ketu_in_9th,
            "ninth_lord_in_dusthana": ninth_lord_in_dusthana,
            "saturn_in_9th_house": saturn_in_9th,
            "sun_in_dusthana": sun_in_dusthana,
            "ninth_lord_with_nodes": ninth_lord_with_nodes,
        }
        active = [name for name, met in triggers.items() if met]
        is_present = len(active) >= 1

        severity = min(0.55 + (len(active) * 0.08), 0.95) if is_present else 0.0
        conditions = [
            condition(key, value, key.replace("_", " "))
            for key, value in triggers.items()
            if value
        ]
        if not conditions:
            conditions = [
                condition("pitra_indicators", False, "No primary pitra dosha indicators found.")
            ]

        evidence = [f"Active indicator: {label.replace('_', ' ')}" for label in active]
        planets = tuple(dict.fromkeys(
            ["Sun", "Rahu", "Ketu", ninth_lord, "Saturn"]
        ))
        houses = tuple(sorted({9, rahu_house, context.house_of_planet("Sun"), ninth_lord_house}))

        return build_detection(
            dosha_id=self.dosha_id,
            dosha_name=self.dosha_name,
            category_key="pitra_dosha",
            is_present=is_present,
            severity=severity,
            description="Linked to ancestral karmic patterns through Sun, 9th house, and nodal afflictions.",
            planets=planets,
            houses=houses,
            conditions=conditions,
            evidence=evidence,
        )
