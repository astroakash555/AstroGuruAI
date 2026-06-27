"""Shrapit Dosha detection rule."""

from __future__ import annotations

from astrology_engine.doshas.base import DoshaRule
from astrology_engine.doshas.rules._helpers import build_detection, condition
from astrology_engine.doshas.types import DoshaDetection
from astrology_engine.yogas.constants import KENDRA_HOUSES, TRIKONA_HOUSES
from astrology_engine.yogas.context import ChartContext


class ShrapitDoshaRule(DoshaRule):
    """
    Shrapit Dosha: Saturn and Rahu conjunction or strong mutual affliction.

    Indicates karmic burden from Saturn-Rahu combination.
    """

    dosha_id = "shrapit_dosha"
    dosha_name = "Shrapit Dosha"
    category = "karmic_saturn"

    def detect(self, context: ChartContext) -> DoshaDetection:
        same_sign = context.planets_in_same_sign("Saturn", "Rahu")
        saturn_house = context.house_of_planet("Saturn")
        rahu_house = context.house_of_planet("Rahu")
        mutual_aspect = context.has_aspect("Saturn", "Rahu") or context.has_aspect("Rahu", "Saturn")
        in_kendra = saturn_house in KENDRA_HOUSES or rahu_house in KENDRA_HOUSES
        in_trikona = saturn_house in TRIKONA_HOUSES or rahu_house in TRIKONA_HOUSES

        is_present = same_sign or (mutual_aspect and (in_kendra or in_trikona))
        severity = 0.0
        if same_sign:
            severity = 0.88 if (in_kendra or in_trikona) else 0.78
        elif is_present:
            severity = 0.68

        conditions = [
            condition(
                "saturn_rahu_conjunction",
                same_sign,
                f"Saturn in {context.get_planet('Saturn').sign.name_en}, "
                f"Rahu in {context.get_planet('Rahu').sign.name_en}.",
            ),
            condition(
                "saturn_rahu_mutual_aspect",
                mutual_aspect,
                f"Saturn house {saturn_house}, Rahu house {rahu_house}.",
            ),
        ]
        evidence = []
        if same_sign:
            evidence.append("Saturn and Rahu occupy the same sign.")
        if mutual_aspect:
            evidence.append("Saturn and Rahu share a classical aspect.")
        if in_kendra or in_trikona:
            evidence.append("Saturn-Rahu influence involves kendra/trikona placement.")

        return build_detection(
            dosha_id=self.dosha_id,
            dosha_name=self.dosha_name,
            category_key="shrapit_dosha",
            is_present=is_present,
            severity=severity,
            description="Forms through Saturn-Rahu affliction, often reflecting past-life karmic debt themes.",
            planets=("Saturn", "Rahu"),
            houses=(saturn_house, rahu_house),
            conditions=conditions,
            evidence=evidence,
        )
