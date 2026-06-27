"""Learning report generator."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from case_learning.constants import TRACKED_CATEGORIES
from case_learning.types import ConsultationCase, LearningReport


def generate_learning_report(
    *,
    cases: tuple[ConsultationCase, ...],
    metrics,
    suggestions,
    feedback_loops,
) -> LearningReport:
    category_tracking = {
        category: metrics.category_breakdown.get(category, {"count": 0})
        for category in TRACKED_CATEGORIES
    }

    return LearningReport(
        report_id=str(uuid4()),
        generated_at=datetime.now(timezone.utc),
        total_cases=len(cases),
        metrics=metrics,
        category_tracking=category_tracking,
        suggestions=suggestions,
        feedback_loops=feedback_loops,
        metadata={
            "engine": "case_learning_v1",
            "ai_prediction": False,
            "suggestion_count": len(suggestions),
            "feedback_loop_count": len(feedback_loops),
        },
    )
