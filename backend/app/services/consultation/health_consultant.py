"""Health consultation section."""

from __future__ import annotations

from backend.app.services.consultation._domain_utils import build_consultation_section
from backend.app.services.consultation.consultation_models import ConsultationSection, DomainConsultationConfig
from backend.app.services.reasoning.fusion.models import FusionResult

HEALTH = DomainConsultationConfig(
    section_id="health",
    title="Health",
    keywords=("health", "vitality", "illness", "6th", "8th", "12th"),
    primary_planets=("Sun", "Moon", "Mars"),
    target_houses=(1, 6, 8, 12),
    timeline_hint="Health sensitivity rises during dusthana transits and malefic dasha sub-periods.",
)


def build_health_section(fusion: FusionResult) -> ConsultationSection:
    return build_consultation_section(fusion, HEALTH)
