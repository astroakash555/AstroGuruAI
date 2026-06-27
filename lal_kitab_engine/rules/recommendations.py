"""Lal Kitab recommendation rules."""

from __future__ import annotations

from lal_kitab_engine.base import LalKitabRule
from lal_kitab_engine.context import LalKitabContext
from lal_kitab_engine.rules._helpers import build_finding, condition
from lal_kitab_engine.types import LalKitabFinding


class SaturnSeventhRecommendationRule(LalKitabRule):
    finding_id = "lk_rec_saturn_7"
    finding_name = "Saturn 7th House Recommendation"
    category = "lal_kitab_recommendation"

    def analyze(self, context: LalKitabContext) -> LalKitabFinding:
        saturn_house = context.house_of("Saturn")
        is_present = saturn_house == 7
        strength = 0.7 if is_present else 0.0

        return build_finding(
            finding_id=self.finding_id,
            finding_name=self.finding_name,
            category_key="recommendation",
            is_present=is_present,
            strength=strength,
            description="Lal Kitab recommendation set when Saturn occupies the 7th house.",
            planets=("Saturn",),
            houses=(7,),
            conditions=[condition("saturn_in_7th", is_present, f"Saturn in house {saturn_house}.")],
            evidence=[f"Saturn in house {saturn_house} triggers LK marriage restraint protocol."],
            recommendation_ids=("lk_saturn_iron_avoid",),
        )


class RahuTwelfthRecommendationRule(LalKitabRule):
    finding_id = "lk_rec_rahu_12"
    finding_name = "Rahu 12th House Recommendation"
    category = "lal_kitab_recommendation"

    def analyze(self, context: LalKitabContext) -> LalKitabFinding:
        rahu_house = context.house_of("Rahu")
        is_present = rahu_house == 12
        strength = 0.68 if is_present else 0.0

        return build_finding(
            finding_id=self.finding_id,
            finding_name=self.finding_name,
            category_key="recommendation",
            is_present=is_present,
            strength=strength,
            description="Lal Kitab recommendation set when Rahu occupies the 12th house.",
            planets=("Rahu",),
            houses=(12,),
            conditions=[condition("rahu_in_12th", is_present, f"Rahu in house {rahu_house}.")],
            evidence=[f"Rahu in house {rahu_house} triggers LK expense-control protocol."],
            recommendation_ids=("lk_rahu_mustard_lamp",),
        )


class JupiterNinthRecommendationRule(LalKitabRule):
    finding_id = "lk_rec_jupiter_9"
    finding_name = "Jupiter 9th House Recommendation"
    category = "lal_kitab_recommendation"

    def analyze(self, context: LalKitabContext) -> LalKitabFinding:
        jupiter_house = context.house_of("Jupiter")
        is_present = jupiter_house == 9
        strength = 0.66 if is_present else 0.0

        return build_finding(
            finding_id=self.finding_id,
            finding_name=self.finding_name,
            category_key="recommendation",
            is_present=is_present,
            strength=strength,
            description="Lal Kitab recommendation set when Jupiter occupies the 9th house.",
            planets=("Jupiter",),
            houses=(9,),
            conditions=[condition("jupiter_in_9th", is_present, f"Jupiter in house {jupiter_house}.")],
            evidence=[f"Jupiter in house {jupiter_house} triggers LK dharma support protocol."],
            recommendation_ids=("lk_jupiter_yellow_donation",),
        )
