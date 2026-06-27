"""Spiritual growth and foreign travel consultation sections."""

from __future__ import annotations

from backend.app.services.consultation._domain_utils import build_consultation_section
from backend.app.services.consultation.consultation_models import ConsultationSection, DomainConsultationConfig
from backend.app.services.reasoning.fusion.models import FusionResult

SPIRITUAL_GROWTH = DomainConsultationConfig(
    section_id="spiritual_growth",
    title="Spiritual Growth",
    keywords=("spiritual", "dharma", "meditation", "ketu", "jupiter", "9th"),
    primary_planets=("Jupiter", "Ketu", "Saturn"),
    target_houses=(5, 9, 12),
    timeline_hint="Spiritual deepening often follows Ketu or 12th-house transit-dasha activation.",
)

FOREIGN_TRAVEL = DomainConsultationConfig(
    section_id="foreign_travel",
    title="Foreign Travel",
    keywords=("foreign", "travel", "abroad", "settlement", "rahu", "12th"),
    primary_planets=("Rahu", "Moon", "Saturn"),
    target_houses=(3, 9, 12),
    timeline_hint="Foreign movement windows appear when Rahu or 12th-house themes are activated in dasha and transit.",
)


def build_spiritual_section(fusion: FusionResult) -> ConsultationSection:
    return build_consultation_section(fusion, SPIRITUAL_GROWTH)


def build_foreign_travel_section(fusion: FusionResult) -> ConsultationSection:
    return build_consultation_section(fusion, FOREIGN_TRAVEL)
