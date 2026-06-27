"""Multi-agent consultation layer public API."""

from consultation_layer.engine import ConsultationEngine, consultation_input_from_unified_report
from consultation_layer.serializers.serializer import to_json_dict, to_json_string
from consultation_layer.types import (
    AgentFinding,
    ConsultationInput,
    ConsultationResult,
    SelfReviewResult,
    SeniorGuruConclusion,
)

__version__ = "1.0.0"

__all__ = [
    "AgentFinding",
    "ConsultationEngine",
    "ConsultationInput",
    "ConsultationResult",
    "SelfReviewResult",
    "SeniorGuruConclusion",
    "consultation_input_from_unified_report",
    "to_json_dict",
    "to_json_string",
]
