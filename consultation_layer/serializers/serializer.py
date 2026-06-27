"""Serialize consultation results to JSON."""

from __future__ import annotations

from typing import Any

from consultation_layer.serializers.schemas import ConsultationJSON
from consultation_layer.types import ConsultationResult


def to_json_dict(result: ConsultationResult) -> dict[str, Any]:
    payload = ConsultationJSON(
        consultation_id=result.consultation_id,
        analyzed_at=result.analyzed_at,
        problem_text=result.problem_text,
        specialist_agents=[
            {
                "agent_id": agent.agent_id,
                "agent_role": agent.agent_role,
                "findings": agent.findings,
                "evidence": list(agent.evidence),
                "confidence": agent.confidence,
                "audit": [entry.__dict__ for entry in agent.audit],
            }
            for agent in result.specialist_agents
        ],
        senior_guru={
            "compared_findings": result.senior_guru.compared_findings,
            "resolved_conflicts": list(result.senior_guru.resolved_conflicts),
            "strongest_causes": list(result.senior_guru.strongest_causes),
            "strongest_remedies": list(result.senior_guru.strongest_remedies),
            "final_conclusion": result.senior_guru.final_conclusion,
            "audit": [entry.__dict__ for entry in result.senior_guru.audit],
        },
        self_review={
            "contradictions_found": list(result.self_review.contradictions_found),
            "missing_evidence": list(result.self_review.missing_evidence),
            "weak_remedies": list(result.self_review.weak_remedies),
            "unsupported_conclusions": list(result.self_review.unsupported_conclusions),
            "review_score": result.self_review.review_score,
            "audit": [entry.__dict__ for entry in result.self_review.audit],
        },
        audit_trail=[entry.__dict__ for entry in result.audit_trail],
        metadata=dict(result.metadata),
    )
    return payload.model_dump(mode="json")


def to_json_string(result: ConsultationResult, *, indent: int | None = 2) -> str:
    import json

    return json.dumps(to_json_dict(result), indent=indent, ensure_ascii=False)
