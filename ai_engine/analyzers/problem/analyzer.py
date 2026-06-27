"""Problem Analyzer — main orchestrator."""

from __future__ import annotations

from typing import Any

from ai_engine.analyzers.problem.classifier import classify_problem, normalize_text
from ai_engine.analyzers.problem.mapping import (
    derive_root_cause_indicators,
    map_houses,
    map_planets,
)
from ai_engine.analyzers.problem.serializer import to_json_dict, to_json_string
from ai_engine.analyzers.problem.severity import assess_severity
from ai_engine.analyzers.problem.types import ProblemAnalysisResult, ProblemAnalyzerInput


class ProblemAnalyzer:
    """
    AI-ready problem context analyzer for Vedic astrology workflows.

    Performs rule-based classification today with a structured output contract
    suitable for downstream Gemini/LLM enrichment without generating remedies.
    """

    def analyze(self, problem_input: ProblemAnalyzerInput) -> ProblemAnalysisResult:
        """Analyze client free-text problem and return structured context."""
        normalized = normalize_text(problem_input.problem_text)
        category, alternatives = classify_problem(problem_input.problem_text)
        houses = map_houses(category.category)
        planets = map_planets(category.category)
        severity = assess_severity(normalized, category.category)
        root_causes = derive_root_cause_indicators(category.category, normalized)

        notes = _build_analysis_notes(category.confidence, severity.level, alternatives)

        return ProblemAnalysisResult(
            original_text=problem_input.problem_text.strip(),
            normalized_text=normalized,
            category=category,
            alternative_categories=alternatives,
            houses=houses,
            planets=planets,
            severity=severity,
            root_cause_indicators=root_causes,
            analysis_notes=notes,
            metadata={
                "analyzer": "rule_based_v1",
                "locale": problem_input.locale,
                "client_id": problem_input.client_id,
                "ai_ready": True,
            },
        )

    def analyze_text(self, problem_text: str, *, client_id: str | None = None) -> ProblemAnalysisResult:
        """Convenience wrapper for plain-text analysis."""
        return self.analyze(
            ProblemAnalyzerInput(
                problem_text=problem_text,
                client_id=client_id,
            )
        )

    def analyze_json(self, problem_input: ProblemAnalyzerInput) -> dict[str, Any]:
        """Analyze and return structured JSON dictionary."""
        return to_json_dict(self.analyze(problem_input))

    def analyze_json_string(
        self,
        problem_input: ProblemAnalyzerInput,
        *,
        indent: int | None = 2,
    ) -> str:
        """Analyze and return formatted JSON string."""
        return to_json_string(self.analyze(problem_input), indent=indent)


def _build_analysis_notes(
    confidence: float,
    severity_level: str,
    alternatives: tuple,
) -> tuple[str, ...]:
    notes: list[str] = []

    if confidence < 0.5:
        notes.append("Category confidence is moderate; verify with client before chart targeting.")
    if alternatives:
        alt_labels = ", ".join(match.label for match in alternatives[:2])
        notes.append(f"Alternative themes detected: {alt_labels}.")
    notes.append(f"Severity assessed as '{severity_level}' based on language and domain baseline.")
    notes.append("Output contains analysis context only; no remedies are generated.")

    return tuple(notes)
