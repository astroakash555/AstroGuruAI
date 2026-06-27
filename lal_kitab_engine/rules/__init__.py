"""Default Lal Kitab rules."""

from lal_kitab_engine.rules.dosh import KetuSixthDoshRule, MarsEighthDoshRule, SaturnRahuDoshRule
from lal_kitab_engine.rules.recommendations import (
    JupiterNinthRecommendationRule,
    RahuTwelfthRecommendationRule,
    SaturnSeventhRecommendationRule,
)
from lal_kitab_engine.rules.rin import MatriRinRule, PitraRinRule, StreeRinRule

DEFAULT_LAL_KITAB_RULES = (
    PitraRinRule(),
    MatriRinRule(),
    StreeRinRule(),
    SaturnRahuDoshRule(),
    MarsEighthDoshRule(),
    KetuSixthDoshRule(),
    SaturnSeventhRecommendationRule(),
    RahuTwelfthRecommendationRule(),
    JupiterNinthRecommendationRule(),
)

RIN_RULES = tuple(rule for rule in DEFAULT_LAL_KITAB_RULES if rule.category == "lal_kitab_rin")
DOSH_RULES = tuple(rule for rule in DEFAULT_LAL_KITAB_RULES if rule.category == "lal_kitab_dosh")
RECOMMENDATION_RULES = tuple(
    rule for rule in DEFAULT_LAL_KITAB_RULES if rule.category == "lal_kitab_recommendation"
)

__all__ = [
    "DEFAULT_LAL_KITAB_RULES",
    "DOSH_RULES",
    "RECOMMENDATION_RULES",
    "RIN_RULES",
]
