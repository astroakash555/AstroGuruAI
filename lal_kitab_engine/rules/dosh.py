"""Lal Kitab Dosh detection rules."""

from __future__ import annotations

from lal_kitab_engine.base import LalKitabRule
from lal_kitab_engine.context import LalKitabContext
from lal_kitab_engine.rules._helpers import build_finding, condition
from lal_kitab_engine.types import LalKitabFinding


class SaturnRahuDoshRule(LalKitabRule):
    finding_id = "saturn_rahu_dosh"
    finding_name = "Saturn-Rahu Dosh"
    category = "lal_kitab_dosh"

    def analyze(self, context: LalKitabContext) -> LalKitabFinding:
        saturn_house = context.house_of("Saturn")
        rahu_house = context.house_of("Rahu")
        same_house = saturn_house == rahu_house
        dusthana_pair = saturn_house in {6, 8, 12} and rahu_house in {6, 8, 12}
        is_present = same_house or dusthana_pair
        strength = 0.84 if same_house else (0.72 if dusthana_pair else 0.15)

        return build_finding(
            finding_id=self.finding_id,
            finding_name=self.finding_name,
            category_key="dosh",
            is_present=is_present,
            strength=strength,
            description="Saturn-Rahu combined dosh indicator in Lal Kitab framework.",
            planets=("Saturn", "Rahu"),
            houses=(saturn_house, rahu_house),
            conditions=[
                condition("same_house", same_house, f"Saturn and Rahu share house {saturn_house}."),
                condition("dusthana_pair", dusthana_pair, "Both grahas linked through dusthana."),
            ],
            evidence=[f"Saturn in house {saturn_house}.", f"Rahu in house {rahu_house}."],
            recommendation_ids=("lk_rahu_mustard_lamp", "lk_saturn_iron_avoid"),
        )


class MarsEighthDoshRule(LalKitabRule):
    finding_id = "mars_8th_dosh"
    finding_name = "Mars 8th House Dosh"
    category = "lal_kitab_dosh"

    def analyze(self, context: LalKitabContext) -> LalKitabFinding:
        mars_house = context.house_of("Mars")
        is_present = mars_house == 8
        strength = 0.8 if is_present else 0.1

        return build_finding(
            finding_id=self.finding_id,
            finding_name=self.finding_name,
            category_key="dosh",
            is_present=is_present,
            strength=strength,
            description="Mars in 8th house dosh indicator in Lal Kitab framework.",
            planets=("Mars",),
            houses=(8,),
            conditions=[condition("mars_in_8th", is_present, f"Mars in house {mars_house}.")],
            evidence=[f"Mars placed in house {mars_house}."],
            recommendation_ids=("lk_mars_sweet_distribution",),
        )


class KetuSixthDoshRule(LalKitabRule):
    finding_id = "ketu_6th_dosh"
    finding_name = "Ketu 6th House Dosh"
    category = "lal_kitab_dosh"

    def analyze(self, context: LalKitabContext) -> LalKitabFinding:
        ketu_house = context.house_of("Ketu")
        is_present = ketu_house == 6
        strength = 0.74 if is_present else 0.12

        return build_finding(
            finding_id=self.finding_id,
            finding_name=self.finding_name,
            category_key="dosh",
            is_present=is_present,
            strength=strength,
            description="Ketu in 6th house service-dispute dosh indicator.",
            planets=("Ketu",),
            houses=(6,),
            conditions=[condition("ketu_in_6th", is_present, f"Ketu in house {ketu_house}.")],
            evidence=[f"Ketu placed in house {ketu_house}."],
            recommendation_ids=("lk_mars_sweet_distribution",),
        )
