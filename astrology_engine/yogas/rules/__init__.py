"""Built-in yoga detection rules."""

from astrology_engine.yogas.rules.budhaditya import BudhadityaYogaRule
from astrology_engine.yogas.rules.chandra_mangal import ChandraMangalYogaRule
from astrology_engine.yogas.rules.gaj_kesari import GajKesariYogaRule
from astrology_engine.yogas.rules.neech_bhang_raj import NeechBhangRajYogaRule
from astrology_engine.yogas.rules.raj_yoga import RajYogaRule
from astrology_engine.yogas.rules.vipreet_raj import VipreetRajYogaRule

DEFAULT_YOGA_RULES = (
    GajKesariYogaRule(),
    RajYogaRule(),
    VipreetRajYogaRule(),
    BudhadityaYogaRule(),
    ChandraMangalYogaRule(),
    NeechBhangRajYogaRule(),
)

__all__ = [
    "BudhadityaYogaRule",
    "ChandraMangalYogaRule",
    "DEFAULT_YOGA_RULES",
    "GajKesariYogaRule",
    "NeechBhangRajYogaRule",
    "RajYogaRule",
    "VipreetRajYogaRule",
]
