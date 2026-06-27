"""Astro Intelligence synthesis engine."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from astro_intelligence.analyzers.conflicts import detect_planetary_conflicts
from astro_intelligence.analyzers.houses import detect_affected_houses
from astro_intelligence.analyzers.influences import detect_strongest_influences
from astro_intelligence.analyzers.root_cause import detect_root_cause_planets, rank_root_causes
from astro_intelligence.analyzers.support import detect_supportive_planets
from astro_intelligence.ranking.severity import compute_confidence_score, compute_severity_score
from astro_intelligence.reasoning.evidence import build_reasoning_metadata
from astro_intelligence.serializers.serializer import to_json_dict, to_json_string
from astro_intelligence.types import AstroIntelligenceInput, AstroIntelligenceResult
from remedy_engine.engine import RemedyEngine, RemedyMatchContext


class AstroIntelligenceEngine:
    """
    Rule-based astro intelligence layer.

    Synthesizes chart, timing, and problem context into ranked causes and remedy matches.
    No AI interpretation or prediction text is generated.
    """

    def __init__(self, remedy_engine: RemedyEngine | None = None) -> None:
        self._remedy_engine = remedy_engine or RemedyEngine()

    @property
    def remedy_engine(self) -> RemedyEngine:
        return self._remedy_engine

    def analyze(self, analysis_input: AstroIntelligenceInput) -> AstroIntelligenceResult:
        root_causes = detect_root_cause_planets(analysis_input)
        supportive = detect_supportive_planets(analysis_input)
        affected_houses = detect_affected_houses(analysis_input)
        conflicts = detect_planetary_conflicts(analysis_input)
        ranked_causes = rank_root_causes(analysis_input)
        strongest = detect_strongest_influences(analysis_input)

        problem_severity = None
        categories: tuple[str, ...] = ()
        severity_level = "moderate"
        if analysis_input.problem_analysis:
            problem_severity = analysis_input.problem_analysis.get("severity", {}).get("score")
            categories = (analysis_input.problem_analysis.get("category", {}).get("category", "unknown"),)
            severity_level = analysis_input.problem_analysis.get("severity", {}).get("level", "moderate")

        severity_score = compute_severity_score(
            root_cause_count=len(root_causes),
            affected_house_count=len(affected_houses),
            conflict_count=len(conflicts),
            dosha_count=len(analysis_input.doshas.get("present_doshas", [])),
            problem_severity=problem_severity,
        )

        remedy_context = RemedyMatchContext(
            root_cause_planets=root_causes,
            affected_houses=affected_houses,
            categories=categories,
            severity_level=severity_level,
        )
        remedy_result = self._remedy_engine.match(remedy_context)
        recommended = tuple(
            {
                "remedy_id": match.remedy.remedy_id,
                "remedy_name": match.remedy.remedy_name,
                "astrology_system": match.remedy.astrology_system,
                "match_score": match.match_score,
                "match_reasons": list(match.match_reasons),
                "priority": match.remedy.priority,
            }
            for match in remedy_result.matched_remedies
        )

        reasoning = build_reasoning_metadata(analysis_input)
        confidence_score = compute_confidence_score(
            sections_present=len(reasoning["sections_used"]),
            root_cause_count=len(root_causes),
            remedy_count=len(recommended),
        )

        return AstroIntelligenceResult(
            analyzed_at=datetime.now(timezone.utc),
            root_cause_planets=root_causes,
            supportive_planets=supportive,
            affected_houses=affected_houses,
            planetary_conflicts=conflicts,
            severity_score=severity_score,
            recommended_remedies=recommended,
            confidence_score=confidence_score,
            ranked_causes=ranked_causes,
            metadata={
                "engine": "astro_intelligence_v1",
                "ai_interpretation": False,
                "strongest_influences": list(strongest),
                **reasoning,
            },
        )

    def analyze_json(self, analysis_input: AstroIntelligenceInput) -> dict[str, Any]:
        return to_json_dict(self.analyze(analysis_input))

    def analyze_json_string(self, analysis_input: AstroIntelligenceInput, *, indent: int | None = 2) -> str:
        return to_json_string(self.analyze(analysis_input), indent=indent)
