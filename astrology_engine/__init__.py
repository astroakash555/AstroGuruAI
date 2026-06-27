"""Astrology computation engine — isolated from AI and API layers."""

from astrology_engine.core.base import AstrologyEngine, BirthData
from astrology_engine.core.types import (
    AyanamsaType,
    Ascendant,
    BhavaChart,
    ChartMetadata,
    HouseSystemType,
    LagnaKundali,
    NakshatraInfo,
    NavamshaChart,
    PlanetPosition,
    VedicChartBundle,
    ZodiacSign,
)
from astrology_engine.dasha import DashaBirthInput, VimshottariDashaEngine, VimshottariDashaResult
from astrology_engine.doshas import DoshaDetectionEngine, DoshaDetectionResult
from astrology_engine.engine import EngineInput, VedicAstrologyEngine
from astrology_engine.transits import (
    TransitAnalysisResult,
    TransitEngine,
    TransitInput,
    to_json_dict,
    to_json_string,
)
from astrology_engine.yogas import YogaDetectionEngine, YogaDetectionResult

__version__ = "0.1.0"

__all__ = [
    "Ascendant",
    "AstrologyEngine",
    "AyanamsaType",
    "BhavaChart",
    "BirthData",
    "DashaBirthInput",
    "DoshaDetectionEngine",
    "DoshaDetectionResult",
    "EngineInput",
    "HouseSystemType",
    "LagnaKundali",
    "NakshatraInfo",
    "NavamshaChart",
    "PlanetPosition",
    "TransitAnalysisResult",
    "TransitEngine",
    "TransitInput",
    "VedicAstrologyEngine",
    "VedicChartBundle",
    "VimshottariDashaEngine",
    "VimshottariDashaResult",
    "YogaDetectionEngine",
    "YogaDetectionResult",
    "ZodiacSign",
    "to_json_dict",
    "to_json_string",
]
