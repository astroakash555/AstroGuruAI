"""Case learning constants."""

from __future__ import annotations

TRACKED_CATEGORIES = (
    "marriage",
    "career",
    "health",
    "finance",
    "court_case",
)

OUTCOME_SUCCESS_TYPES = ("success", "partial", "recovery", "gain", "advancement", "early")
OUTCOME_FAILURE_TYPES = ("failure", "denial", "loss", "unemployment", "delay", "blocked")
OUTCOME_NEUTRAL_TYPES = ("partial", "mixed", "unknown")

WEAK_RULE_THRESHOLD = 0.45
OBSOLETE_RULE_THRESHOLD = 0.25
REMEDY_SUCCESS_THRESHOLD = 0.5

SUGGESTION_TYPES = (
    "rule_improvement",
    "new_rule_candidate",
    "weak_rule",
    "obsolete_rule",
)
