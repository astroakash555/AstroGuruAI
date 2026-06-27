"""Serialize reasoning results to JSON."""

from __future__ import annotations

from typing import Any

from reasoning_layer.serializers.schemas import ReasoningJSON
from reasoning_layer.types import ReasoningResult


def to_json_dict(result: ReasoningResult) -> dict[str, Any]:
    payload = ReasoningJSON(
        analyzed_at=result.analyzed_at,
        problem_domain=result.problem_domain,
        root_causes=[
            {
                "cause_type": item.cause_type,
                "primary_factor": item.primary_factor,
                "triggering_planet": item.triggering_planet,
                "supporting_planet": item.supporting_planet,
                "dasha_influence": item.dasha_influence,
                "transit_influence": item.transit_influence,
                "severity": item.severity,
                "audit": [entry.__dict__ for entry in item.audit],
            }
            for item in result.root_causes
        ],
        contradictions=[
            {
                "topic": item.topic,
                "supporting_evidence": list(item.supporting_evidence),
                "opposing_evidence": list(item.opposing_evidence),
                "confidence_score": item.confidence_score,
                "audit": [entry.__dict__ for entry in item.audit],
            }
            for item in result.contradictions
        ],
        confidence={
            "vedic_agreement": result.confidence.vedic_agreement,
            "kp_agreement": result.confidence.kp_agreement,
            "lal_kitab_agreement": result.confidence.lal_kitab_agreement,
            "dasha_agreement": result.confidence.dasha_agreement,
            "transit_agreement": result.confidence.transit_agreement,
            "overall_score": result.confidence.overall_score,
        },
        consensus={
            "agreement_areas": list(result.consensus.agreement_areas),
            "disagreement_areas": list(result.consensus.disagreement_areas),
            "final_consensus": result.consensus.final_consensus,
            "system_stances": dict(result.consensus.system_stances),
            "audit": [entry.__dict__ for entry in result.consensus.audit],
        },
        client_history=(
            {
                "repeated_problems": list(result.client_history.repeated_problems),
                "remedy_effectiveness": list(result.client_history.remedy_effectiveness),
                "detected_patterns": list(result.client_history.detected_patterns),
                "consultation_count": result.client_history.consultation_count,
                "report_count": result.client_history.report_count,
            }
            if result.client_history
            else None
        ),
        audit_trail=[entry.__dict__ for entry in result.audit_trail],
        metadata=dict(result.metadata),
    )
    return payload.model_dump(mode="json")


def to_json_string(result: ReasoningResult, *, indent: int | None = 2) -> str:
    import json

    return json.dumps(to_json_dict(result), indent=indent, ensure_ascii=False)
