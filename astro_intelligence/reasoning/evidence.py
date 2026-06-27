"""Evidence reasoning helpers."""

from __future__ import annotations

from typing import Any


def build_reasoning_metadata(analysis_input) -> dict[str, Any]:
    """Build structured reasoning metadata without natural language prediction."""
    sections = [
        "kundali",
        "navamsha",
        "dasha",
        "yogas",
        "doshas",
        "transits",
    ]
    if analysis_input.problem_analysis:
        sections.append("problem_analysis")
    if analysis_input.lal_kitab:
        sections.append("lal_kitab")
    if analysis_input.kp_analysis:
        sections.append("kp_analysis")

    return {
        "reasoning_engine": "rule_based_v1",
        "sections_used": sections,
        "ai_interpretation": False,
    }
