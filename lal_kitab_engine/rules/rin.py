"""Lal Kitab Rin detection rules."""

from __future__ import annotations

from lal_kitab_engine.base import LalKitabRule
from lal_kitab_engine.context import LalKitabContext
from lal_kitab_engine.rules._helpers import build_finding, condition
from lal_kitab_engine.types import LalKitabFinding


class PitraRinRule(LalKitabRule):
    finding_id = "pitra_rin"
    finding_name = "Pitra Rin"
    category = "lal_kitab_rin"

    def analyze(self, context: LalKitabContext) -> LalKitabFinding:
        sun_house = context.house_of("Sun")
        saturn_house = context.house_of("Saturn")
        sun_in_9 = sun_house == 9
        saturn_afflicts_sun_axis = saturn_house in {9, 12}
        is_present = sun_in_9 and saturn_afflicts_sun_axis
        strength = 0.82 if is_present else 0.2

        return build_finding(
            finding_id=self.finding_id,
            finding_name=self.finding_name,
            category_key="rin",
            is_present=is_present,
            strength=strength,
            description="Pitra Rin indicator from Sun-Saturn 9th/12th axis in Lal Kitab framework.",
            planets=("Sun", "Saturn"),
            houses=(9, 12),
            conditions=[
                condition("sun_in_9th", sun_in_9, f"Sun in house {sun_house}."),
                condition("saturn_on_dharma_axis", saturn_afflicts_sun_axis, f"Saturn in house {saturn_house}."),
            ],
            evidence=[f"Sun placed in house {sun_house}.", f"Saturn placed in house {saturn_house}."],
            recommendation_ids=("lk_jupiter_yellow_donation",),
        )


class MatriRinRule(LalKitabRule):
    finding_id = "matri_rin"
    finding_name = "Matri Rin"
    category = "lal_kitab_rin"

    def analyze(self, context: LalKitabContext) -> LalKitabFinding:
        moon_house = context.house_of("Moon")
        rahu_house = context.house_of("Rahu")
        is_present = moon_house == 4 and rahu_house in {4, 8}
        strength = 0.78 if is_present else 0.18

        return build_finding(
            finding_id=self.finding_id,
            finding_name=self.finding_name,
            category_key="rin",
            is_present=is_present,
            strength=strength,
            description="Matri Rin indicator from Moon-Rahu 4th/8th linkage.",
            planets=("Moon", "Rahu"),
            houses=(4, 8),
            conditions=[
                condition("moon_in_4th", moon_house == 4, f"Moon in house {moon_house}."),
                condition("rahu_links_4_8", rahu_house in {4, 8}, f"Rahu in house {rahu_house}."),
            ],
            evidence=[f"Moon in house {moon_house}.", f"Rahu in house {rahu_house}."],
            recommendation_ids=("lk_moon_silver_keep",),
        )


class StreeRinRule(LalKitabRule):
    finding_id = "stree_rin"
    finding_name = "Stree Rin"
    category = "lal_kitab_rin"

    def analyze(self, context: LalKitabContext) -> LalKitabFinding:
        venus_house = context.house_of("Venus")
        mars_house = context.house_of("Mars")
        is_present = venus_house == 7 and mars_house in {7, 8}
        strength = 0.76 if is_present else 0.16

        return build_finding(
            finding_id=self.finding_id,
            finding_name=self.finding_name,
            category_key="rin",
            is_present=is_present,
            strength=strength,
            description="Stree Rin indicator from Venus-Mars 7th/8th relationship stress.",
            planets=("Venus", "Mars"),
            houses=(7, 8),
            conditions=[
                condition("venus_in_7th", venus_house == 7, f"Venus in house {venus_house}."),
                condition("mars_in_7_8", mars_house in {7, 8}, f"Mars in house {mars_house}."),
            ],
            evidence=[f"Venus in house {venus_house}.", f"Mars in house {mars_house}."],
            recommendation_ids=("lk_venus_white_flowers",),
        )
