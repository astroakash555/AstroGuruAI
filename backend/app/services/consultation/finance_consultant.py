"""Finance consultation section."""

from __future__ import annotations

from backend.app.services.consultation._domain_utils import build_consultation_section
from backend.app.services.consultation.consultation_models import ConsultationSection, DomainConsultationConfig
from backend.app.services.reasoning.fusion.models import FusionResult

FINANCE = DomainConsultationConfig(
    section_id="finance",
    title="Finance",
    keywords=("finance", "wealth", "money", "income", "2nd", "11th"),
    primary_planets=("Jupiter", "Venus", "Mercury"),
    target_houses=(2, 6, 11),
    timeline_hint="Financial gains and expenses respond to 2nd and 11th-house dasha-transit combinations.",
)


def build_finance_section(fusion: FusionResult) -> ConsultationSection:
    return build_consultation_section(fusion, FINANCE)
