"""Validation framework public API."""

from validation_framework.datasets.builder import build_all_benchmarks
from validation_framework.datasets.loader import BenchmarkLoader
from validation_framework.engine import ValidationEngine
from validation_framework.failed_cases.store import FailedCaseStore
from validation_framework.serializers.serializer import to_json_dict, to_json_string
from validation_framework.types import (
    AccuracyMetrics,
    CaseStudy,
    CaseValidationResult,
    ValidationReport,
)

__version__ = "1.0.0"

__all__ = [
    "AccuracyMetrics",
    "BenchmarkLoader",
    "CaseStudy",
    "CaseValidationResult",
    "FailedCaseStore",
    "ValidationEngine",
    "ValidationReport",
    "build_all_benchmarks",
    "to_json_dict",
    "to_json_string",
]
