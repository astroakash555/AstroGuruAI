"""Built-in dosha detection rules."""

from astrology_engine.doshas.rules.grahan import GrahanDoshaRule
from astrology_engine.doshas.rules.kaal_sarp import KaalSarpDoshaRule
from astrology_engine.doshas.rules.mangal import MangalDoshaRule
from astrology_engine.doshas.rules.pitra import PitraDoshaRule
from astrology_engine.doshas.rules.shrapit import ShrapitDoshaRule

DEFAULT_DOSHA_RULES = (
    MangalDoshaRule(),
    KaalSarpDoshaRule(),
    PitraDoshaRule(),
    GrahanDoshaRule(),
    ShrapitDoshaRule(),
)

__all__ = [
    "DEFAULT_DOSHA_RULES",
    "GrahanDoshaRule",
    "KaalSarpDoshaRule",
    "MangalDoshaRule",
    "PitraDoshaRule",
    "ShrapitDoshaRule",
]
