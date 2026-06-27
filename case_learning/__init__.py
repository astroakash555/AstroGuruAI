"""Case learning public API."""

from case_learning.engine import CaseLearningEngine
from case_learning.serializers.serializer import case_to_dict, learning_report_to_dict, metrics_to_dict

__version__ = "1.0.0"

__all__ = [
    "CaseLearningEngine",
    "case_to_dict",
    "learning_report_to_dict",
    "metrics_to_dict",
]
