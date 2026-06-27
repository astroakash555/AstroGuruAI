"""Relationship, marriage, family, and children consultation sections."""

from __future__ import annotations

from backend.app.services.consultation._domain_utils import build_consultation_section
from backend.app.services.consultation.consultation_models import ConsultationSection, DomainConsultationConfig
from backend.app.services.reasoning.fusion.models import FusionResult

RELATIONSHIP = DomainConsultationConfig(
    section_id="relationship",
    title="Relationship",
    keywords=("relationship", "venus", "moon", "partner", "7th"),
    primary_planets=("Venus", "Moon"),
    target_houses=(2, 7, 11),
    timeline_hint="Venus and Moon periods often bring relationship turning points.",
)

MARRIAGE = DomainConsultationConfig(
    section_id="marriage",
    title="Marriage",
    keywords=("marriage", "spouse", "venus", "jupiter", "7th"),
    primary_planets=("Venus", "Jupiter", "Moon"),
    target_houses=(2, 7, 11),
    timeline_hint="Marriage themes peak when 7th-house significators are activated by dasha or transit.",
)

FAMILY = DomainConsultationConfig(
    section_id="family",
    title="Family",
    keywords=("family", "home", "moon", "4th", "2nd"),
    primary_planets=("Moon", "Sun"),
    target_houses=(2, 4, 11),
    timeline_hint="Family matters respond to Moon and 4th-house activation cycles.",
)

CHILDREN = DomainConsultationConfig(
    section_id="children",
    title="Children",
    keywords=("children", "progeny", "5th", "jupiter", "moon"),
    primary_planets=("Jupiter", "Moon"),
    target_houses=(5, 9, 11),
    timeline_hint="Children-related outcomes often align with 5th-house dasha and transit support.",
)


def build_relationship_section(fusion: FusionResult) -> ConsultationSection:
    return build_consultation_section(fusion, RELATIONSHIP)


def build_marriage_section(fusion: FusionResult) -> ConsultationSection:
    return build_consultation_section(fusion, MARRIAGE)


def build_family_section(fusion: FusionResult) -> ConsultationSection:
    return build_consultation_section(fusion, FAMILY)


def build_children_section(fusion: FusionResult) -> ConsultationSection:
    return build_consultation_section(fusion, CHILDREN)
