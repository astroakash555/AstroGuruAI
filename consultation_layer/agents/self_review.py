"""Self Review Agent."""

from __future__ import annotations

from consultation_layer.constants import AGENT_SELF_REVIEW, WEAK_REMEDY_THRESHOLD
from consultation_layer.types import AgentFinding, SelfReviewResult, SeniorGuruConclusion
from reasoning_layer.types import AuditEntry


def review_consultation(
    specialists: tuple[AgentFinding, ...],
    senior_guru: SeniorGuruConclusion,
) -> SelfReviewResult:
    contradictions: list[dict[str, object]] = []
    missing_evidence: list[str] = []
    weak_remedies: list[dict[str, object]] = []
    unsupported: list[str] = []

    for conflict in senior_guru.resolved_conflicts:
        if conflict.get("confidence_score", 100) < 55:
            contradictions.append(
                {
                    "topic": conflict.get("topic"),
                    "confidence_score": conflict.get("confidence_score"),
                    "status": "unresolved_low_confidence",
                }
            )

    for agent in specialists:
        if not agent.evidence:
            missing_evidence.append(f"{agent.agent_id}:no_evidence")
        if not agent.audit:
            missing_evidence.append(f"{agent.agent_id}:no_audit")

    if not senior_guru.strongest_causes:
        missing_evidence.append("senior_guru:no_causes_selected")

    for remedy in senior_guru.strongest_remedies:
        score = remedy.get("match_score") or 0
        if score < WEAK_REMEDY_THRESHOLD:
            weak_remedies.append(
                {
                    "remedy_id": remedy.get("remedy_id"),
                    "match_score": score,
                    "reason": "below_threshold",
                }
            )

    if not senior_guru.audit:
        unsupported.append("senior_guru_conclusion")

    for agent in specialists:
        if agent.confidence >= 0.5 and not agent.audit:
            unsupported.append(agent.agent_id)

    penalty = (
        len(contradictions) * 8
        + len(missing_evidence) * 6
        + len(weak_remedies) * 5
        + len(unsupported) * 10
    )
    review_score = max(0, min(100, 100 - penalty))

    audit = (
        AuditEntry(
            rule_source="self_review_engine",
            engine_source=AGENT_SELF_REVIEW,
            reason_used=(
                f"Review score {review_score} after checks: "
                f"contradictions={len(contradictions)}, "
                f"missing={len(missing_evidence)}, "
                f"weak_remedies={len(weak_remedies)}"
            ),
        ),
    )

    return SelfReviewResult(
        contradictions_found=tuple(contradictions),
        missing_evidence=tuple(missing_evidence),
        weak_remedies=tuple(weak_remedies),
        unsupported_conclusions=tuple(unsupported),
        review_score=review_score,
        audit=audit,
    )
