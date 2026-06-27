"""Reasoning layer public API."""

from reasoning_layer.engine import ReasoningEngine, reasoning_input_from_unified_report
from reasoning_layer.history.store import ClientHistoryStore
from reasoning_layer.serializers.serializer import to_json_dict, to_json_string
from reasoning_layer.types import (
    AuditEntry,
    ConfidenceBreakdown,
    ConsensusResult,
    ContradictionFinding,
    ReasoningInput,
    ReasoningResult,
    RootCauseFinding,
)

__version__ = "1.0.0"

__all__ = [
    "AuditEntry",
    "ClientHistoryStore",
    "ConfidenceBreakdown",
    "ConsensusResult",
    "ContradictionFinding",
    "ReasoningEngine",
    "ReasoningInput",
    "ReasoningResult",
    "RootCauseFinding",
    "reasoning_input_from_unified_report",
    "to_json_dict",
    "to_json_string",
]
