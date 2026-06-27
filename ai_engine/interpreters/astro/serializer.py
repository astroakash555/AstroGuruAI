"""Serialize astro interpretation output."""

from __future__ import annotations

from typing import Any

from ai_engine.interpreters.astro.schemas import AstroInterpretationJSON
from ai_engine.interpreters.astro.types import AstroInterpretationResult


def to_json_dict(result: AstroInterpretationResult) -> dict[str, Any]:
    payload = AstroInterpretationJSON(
        generated_at=result.generated_at,
        root_cause_explanation=result.root_cause_explanation,
        affected_planets_explanation=result.affected_planets_explanation,
        affected_houses_explanation=result.affected_houses_explanation,
        dasha_impact_explanation=result.dasha_impact_explanation,
        transit_impact_explanation=result.transit_impact_explanation,
        kp_findings_explanation=result.kp_findings_explanation,
        lal_kitab_findings_explanation=result.lal_kitab_findings_explanation,
        summary=result.summary,
        metadata=dict(result.metadata),
    )
    return payload.model_dump(mode="json")
