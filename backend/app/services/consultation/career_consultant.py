"""Career and business consultation sections."""

from __future__ import annotations

from backend.app.services.consultation._domain_utils import build_consultation_section
from backend.app.services.consultation.consultation_models import ConsultationSection, DomainConsultationConfig
from backend.app.services.reasoning.fusion.models import FusionResult

CAREER = DomainConsultationConfig(
    section_id="career",
    title="Career",
    keywords=("career", "profession", "status", "10th", "saturn", "sun"),
    primary_planets=("Sun", "Saturn", "Mercury"),
    target_houses=(2, 6, 10, 11),
    timeline_hint="Career shifts often follow 10th-house dasha lords and Saturn transit pressure.",
)

BUSINESS = DomainConsultationConfig(
    section_id="business",
    title="Business",
    keywords=("business", "commerce", "trade", "mercury", "venus", "profit"),
    primary_planets=("Mercury", "Venus", "Jupiter"),
    target_houses=(2, 7, 10, 11),
    timeline_hint="Business expansion windows appear when Mercury-Venus support combines with strong 11th-house activation.",
)


def build_career_section(fusion: FusionResult) -> ConsultationSection:
    return build_consultation_section(fusion, CAREER)


def build_business_section(fusion: FusionResult) -> ConsultationSection:
    return build_consultation_section(fusion, BUSINESS)
