"""Phase 3 AI and dashboard exports."""

from ai_engine.analyzers import ProblemAnalyzer, ProblemAnalyzerInput, ProblemAnalysisResult, ProblemCategory
from ai_engine.interpreters.astro import AstroInterpretationEngine, AstroInterpretationInput, AstroInterpretationResult
from ai_engine.interpreters.remedy import RemedyGenerationEngine, RemedyGenerationInput, RemedyGenerationResult
from ai_engine.providers.gemini import GeminiClient, GeminiConfig
from ai_engine.writers.client_report import ClientReportInput, ClientReportResult, ClientReportWriter

__version__ = "0.2.0"

__all__ = [
    "AstroInterpretationEngine",
    "AstroInterpretationInput",
    "AstroInterpretationResult",
    "ClientReportInput",
    "ClientReportResult",
    "ClientReportWriter",
    "GeminiClient",
    "GeminiConfig",
    "ProblemAnalysisResult",
    "ProblemAnalyzer",
    "ProblemAnalyzerInput",
    "ProblemCategory",
    "RemedyGenerationEngine",
    "RemedyGenerationInput",
    "RemedyGenerationResult",
]
