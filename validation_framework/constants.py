"""Validation framework constants."""

from __future__ import annotations

BENCHMARK_CATEGORIES = (
    "marriage",
    "divorce",
    "career",
    "government_job",
    "business",
    "health",
    "court_case",
    "foreign_settlement",
    "wealth",
    "raj_yoga",
)

ACCURACY_METRICS = (
    "planet_accuracy",
    "house_accuracy",
    "dasha_accuracy",
    "transit_accuracy",
    "remedy_accuracy",
)

FAILURE_THRESHOLD = 60.0
LOW_METRIC_THRESHOLD = 0.4

METRIC_RETRAINING_MAP: dict[str, str] = {
    "planet_accuracy": "Expand planet significator rules in knowledge_brain and astro_intelligence root cause weights.",
    "house_accuracy": "Improve house mapping in problem_analyzer and affected house detection.",
    "dasha_accuracy": "Calibrate dasha lord scoring in reasoning_layer dasha signal engine.",
    "transit_accuracy": "Add transit impact rules for slow-moving graha natal overlays.",
    "remedy_accuracy": "Expand remedy_engine KB matches and Lal Kitab remedy linkage.",
}
