"""AI consultation brain orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.services.consultation.career_consultant import build_business_section, build_career_section
from backend.app.services.consultation.consultation_models import ConsultationResult, consultation_result_to_dict
from backend.app.services.consultation.education_consultant import build_education_section
from backend.app.services.consultation.finance_consultant import build_finance_section
from backend.app.services.consultation.health_consultant import build_health_section
from backend.app.services.consultation.recommendation_prioritizer import build_priorities, build_risks, build_strengths
from backend.app.services.consultation.relationship_consultant import (
    build_children_section,
    build_family_section,
    build_marriage_section,
    build_relationship_section,
)
from backend.app.services.consultation.spiritual_consultant import build_foreign_travel_section, build_spiritual_section
from backend.app.services.consultation.summary_generator import build_executive_summary_section, generate_executive_summary
from backend.app.services.reasoning.fusion.models import FusionResult


class ConsultationEngine:
    """
    Transforms fused intelligence into structured, astrologer-style consultation output.

    Accepts a ``FusionResult`` and returns JSON-serializable consultation sections,
    priorities, strengths, risks, and overall confidence without LLM coupling.
    """

    ENGINE_VERSION = "consultation_brain_v1"

    def generate(self, fusion: FusionResult) -> ConsultationResult:
        """Generate a complete consultation result from fused intelligence."""
        sections = (
            build_executive_summary_section(fusion),
            build_relationship_section(fusion),
            build_marriage_section(fusion),
            build_career_section(fusion),
            build_business_section(fusion),
            build_finance_section(fusion),
            build_health_section(fusion),
            build_education_section(fusion),
            build_spiritual_section(fusion),
            build_foreign_travel_section(fusion),
            build_family_section(fusion),
            build_children_section(fusion),
        )

        return ConsultationResult(
            generated_at=datetime.now(timezone.utc),
            executive_summary=generate_executive_summary(fusion),
            sections=sections,
            priorities=build_priorities(fusion),
            strengths=build_strengths(fusion),
            risks=build_risks(fusion),
            overall_confidence=round(fusion.confidence_score, 4),
            metadata={
                "engine": self.ENGINE_VERSION,
                "section_count": len(sections),
                "observation_count": len(fusion.observations),
                "root_cause_count": len(fusion.root_causes),
                "recommendation_count": len(fusion.recommendations),
                "conflict_count": len(fusion.conflicts),
                "active_engines": list(fusion.metadata.get("active_engines", ())),
            },
        )

    def generate_json(self, fusion: FusionResult) -> dict:
        """Generate consultation output as a JSON-serializable dictionary."""
        return consultation_result_to_dict(self.generate(fusion))


def generate_consultation(fusion: FusionResult) -> ConsultationResult:
    """Convenience wrapper for consultation generation."""
    return ConsultationEngine().generate(fusion)
