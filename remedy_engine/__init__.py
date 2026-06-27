"""Remedy knowledge and matching engine."""

from remedy_engine.engine import RemedyEngine, RemedyMatchContext
from remedy_engine.knowledge import DEFAULT_REMEDIES, RemedyKnowledgeRegistry
from remedy_engine.models import RemedyMatch, RemedyMatchResult, RemedyRecord
from remedy_engine.serializers import remedies_to_json_dict, to_json_dict, to_json_string

__version__ = "0.1.0"

__all__ = [
    "DEFAULT_REMEDIES",
    "RemedyEngine",
    "RemedyKnowledgeRegistry",
    "RemedyMatch",
    "RemedyMatchContext",
    "RemedyMatchResult",
    "RemedyRecord",
    "remedies_to_json_dict",
    "to_json_dict",
    "to_json_string",
]
