"""Education consultation section."""

from __future__ import annotations

from backend.app.services.consultation._domain_utils import build_consultation_section
from backend.app.services.consultation.consultation_models import ConsultationSection, DomainConsultationConfig
from backend.app.services.reasoning.fusion.models import FusionResult

EDUCATION = DomainConsultationConfig(
    section_id="education",
    title="Education",
    keywords=("education", "learning", "study", "mercury", "jupiter", "5th"),
    primary_planets=("Mercury", "Jupiter", "Moon"),
    target_houses=(4, 5, 9),
    timeline_hint="Educational progress strengthens when Mercury-Jupiter dasha support aligns with 5th-house activation.",
)


def build_education_section(fusion: FusionResult) -> ConsultationSection:
    return build_consultation_section(fusion, EDUCATION)
