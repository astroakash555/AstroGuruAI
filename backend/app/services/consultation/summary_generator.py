"""Executive summary generation for the consultation brain."""

from __future__ import annotations

from backend.app.services.reasoning.fusion.models import FusionResult


def generate_executive_summary(fusion: FusionResult) -> str:
    """Compose a concise executive summary from fused intelligence."""
    if not fusion.observations and not fusion.root_causes:
        return (
            "The fused intelligence analysis did not surface dominant chart themes. "
            "The present period appears broadly neutral, though routine dasha and transit "
            "monitoring remains advisable."
        )

    lead_observations = fusion.observations[:3]
    lead_titles = ", ".join(item.title for item in lead_observations)
    root_text = fusion.root_causes[0].title if fusion.root_causes else lead_observations[0].title
    conflict_text = ""
    if fusion.conflicts:
        conflict_text = (
            f" {len(fusion.conflicts)} cross-engine interpretation conflict(s) require careful "
            "weighing before major decisions."
        )

    engine_count = len(fusion.metadata.get("active_engines", ()))
    return (
        f"The chart analysis highlights {lead_titles} as the most influential current themes, "
        f"with {root_text} acting as the primary causal focus. "
        f"Overall fused confidence is {fusion.confidence_score:.0%} across "
        f"{engine_count or 'multiple'} intelligence engines.{conflict_text} "
        "The sections below translate these findings into practical life-domain guidance."
    )


def build_executive_summary_section(fusion: FusionResult):
    """Build the executive summary as a structured consultation section."""
    from backend.app.services.consultation.consultation_models import ConsultationSection

    summary = generate_executive_summary(fusion)
    top_observations = fusion.observations[:3]
    root = fusion.root_causes[0].explanation if fusion.root_causes else summary
    positives = tuple(item.title for item in top_observations if item.severity < 0.7)[:3]
    if not positives:
        positives = ("Chart factors remain workable with timely remedial attention.",)
    challenges = tuple(
        item.title for item in top_observations if item.severity >= 0.7 or item.has_conflict
    )[:3]
    if fusion.conflicts:
        challenges = tuple(dict.fromkeys((*challenges, *(c.title for c in fusion.conflicts[:2]))))[:3]
    if not challenges:
        challenges = ("No major conflict cluster dominates the current reading.",)
    advice = tuple(
        item.explanation for item in fusion.recommendations[:2]
    ) or ("Review domain sections below before making major life decisions.",)

    return ConsultationSection(
        section_id="executive_summary",
        title="Executive Summary",
        current_situation=summary,
        root_cause=root,
        positive_factors=positives,
        challenges=challenges,
        timeline="Current dasha and transit cycles set the near-term background for all life domains.",
        actionable_advice=advice,
        confidence=round(fusion.confidence_score, 4),
        supporting_observation_ids=tuple(item.fusion_id for item in top_observations),
    )
