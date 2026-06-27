"""Fusion and recommendation consistency metrics."""

from __future__ import annotations

from typing import Any

from backend.app.services.evaluation.models import MetricRecord, clamp_score


def compute_fusion_consistency(
    fusion: dict[str, Any],
    observations_by_engine: dict[str, tuple],
) -> MetricRecord:
    """
    Evaluate internal consistency of fused intelligence output.

    Checks root-cause linkage, recommendation coverage, conflict burden, and
    alignment between declared fusion confidence and ranked observations.
    """
    fused_observations = fusion.get("observations", [])
    root_causes = fusion.get("root_causes", [])
    recommendations = fusion.get("recommendations", [])
    conflicts = fusion.get("conflicts", [])
    fusion_confidence = float(fusion.get("confidence") or 0.0)

    checks: list[float] = []
    details: dict[str, Any] = {
        "fused_observation_count": len(fused_observations),
        "root_cause_count": len(root_causes),
        "recommendation_count": len(recommendations),
        "conflict_count": len(conflicts),
    }

    if not fused_observations and not observations_by_engine:
        return MetricRecord(
            metric_id="fusion_consistency",
            name="Fusion Consistency",
            score=0.0,
            weight=0.20,
            details=details,
        )

    if fused_observations:
        linked_root_causes = _linked_root_cause_ratio(fused_observations, root_causes)
        checks.append(linked_root_causes)
        details["linked_root_cause_ratio"] = linked_root_causes

        engine_support_ratio = _engine_support_ratio(fused_observations)
        checks.append(engine_support_ratio)
        details["engine_support_ratio"] = engine_support_ratio

        confidence_alignment = _confidence_alignment(fused_observations, fusion_confidence)
        checks.append(confidence_alignment)
        details["confidence_alignment"] = confidence_alignment
    elif observations_by_engine:
        checks.append(0.35)
        details["empty_fusion_penalty"] = True

    conflict_penalty = min(len(conflicts) * 0.08, 0.32)
    conflict_score = clamp_score(1.0 - conflict_penalty)
    checks.append(conflict_score)
    details["conflict_score"] = conflict_score

    recommendation_coverage = _recommendation_root_cause_coverage(recommendations, root_causes)
    checks.append(recommendation_coverage)
    details["recommendation_root_cause_coverage"] = recommendation_coverage

    score = sum(checks) / len(checks) if checks else 0.0

    return MetricRecord(
        metric_id="fusion_consistency",
        name="Fusion Consistency",
        score=clamp_score(score),
        weight=0.20,
        details=details,
    )


def compute_recommendation_consistency(
    unified_report: dict[str, Any],
    fusion: dict[str, Any],
) -> MetricRecord:
    """
    Evaluate consistency between fusion recommendations and report remedies.

    Compares fusion recommendations, astro intelligence remedies, and remedy
    engine matches for overlapping guidance themes.
    """
    fusion_recommendations = fusion.get("recommendations", [])
    astro = unified_report.get("astro_intelligence", {})
    remedy_section = unified_report.get("remedy_recommendations", {})

    fusion_titles = {_normalize_text(item.get("title", "")) for item in fusion_recommendations}
    fusion_root_links = {
        _normalize_text(str(cause))
        for item in fusion_recommendations
        for cause in item.get("supporting_root_causes", [])
    }
    root_cause_titles = {
        _normalize_text(item.get("title", ""))
        for item in fusion.get("root_causes", [])
    }

    linked_ratio = (
        len(fusion_root_links & root_cause_titles) / len(fusion_root_links)
        if fusion_root_links
        else 1.0
    )

    astro_remedies = astro.get("recommended_remedies", [])
    remedy_matches = remedy_section.get("matched_remedies", [])
    downstream_ids = {
        str(item.get("remedy_id") or item.get("remedy", {}).get("remedy_id") or "")
        for item in (*astro_remedies, *remedy_matches)
        if isinstance(item, dict)
    }
    downstream_ids.discard("")

    fusion_keywords = _keyword_set(
        " ".join(
            f"{item.get('title', '')} {item.get('explanation', '')}"
            for item in fusion_recommendations
            if isinstance(item, dict)
        )
    )
    remedy_keywords = _keyword_set(
        " ".join(
            f"{item.get('title', '')} {item.get('explanation', '')} {item.get('remedy_id', '')}"
            for item in astro_remedies
            if isinstance(item, dict)
        )
    )
    remedy_overlap = (
        len(fusion_keywords & remedy_keywords) / len(fusion_keywords)
        if fusion_keywords
        else (1.0 if not downstream_ids else 0.7)
    )

    title_overlap = (
        len(fusion_titles & {_normalize_text(item.get("title", "")) for item in astro_remedies})
        / len(fusion_titles)
        if fusion_titles
        else 1.0
    )

    score = clamp_score((0.45 * linked_ratio) + (0.35 * remedy_overlap) + (0.20 * title_overlap))

    return MetricRecord(
        metric_id="recommendation_consistency",
        name="Recommendation Consistency",
        score=score,
        weight=0.15,
        details={
            "fusion_recommendation_count": len(fusion_recommendations),
            "linked_root_cause_ratio": round(linked_ratio, 4),
            "remedy_keyword_overlap": round(remedy_overlap, 4),
            "title_overlap": round(title_overlap, 4),
            "downstream_remedy_count": len(downstream_ids),
        },
    )


def _linked_root_cause_ratio(
    fused_observations: list[Any],
    root_causes: list[Any],
) -> float:
    if not root_causes:
        return 1.0 if fused_observations else 0.0

    source_ids = {
        str(obs_id)
        for item in fused_observations
        for obs_id in (item.get("source_observation_ids") or [item.get("fusion_id")])
        if obs_id
    }
    supporting_ids = {
        str(obs_id)
        for root in root_causes
        for obs_id in root.get("supporting_observations", [])
    }
    if not supporting_ids:
        return 0.75
    matched = len(source_ids & supporting_ids)
    return clamp_score(matched / len(supporting_ids))


def _engine_support_ratio(fused_observations: list[Any]) -> float:
    if not fused_observations:
        return 0.0
    multi_engine = sum(
        1
        for item in fused_observations
        if len(item.get("supporting_engines", [])) > 1
    )
    return clamp_score(multi_engine / len(fused_observations))


def _confidence_alignment(fused_observations: list[Any], fusion_confidence: float) -> float:
    if not fused_observations:
        return 0.0
    confidences = sorted(
        (float(item.get("confidence") or 0.0) for item in fused_observations),
        reverse=True,
    )
    top_confidences = confidences[: min(5, len(confidences))]
    expected = sum(top_confidences) / len(top_confidences)
    delta = abs(expected - fusion_confidence)
    return clamp_score(1.0 - min(delta, 1.0))


def _recommendation_root_cause_coverage(
    recommendations: list[Any],
    root_causes: list[Any],
) -> float:
    if not recommendations:
        return 1.0 if not root_causes else 0.5
    root_titles = {str(item.get("title") or "") for item in root_causes}
    linked = sum(
        1
        for item in recommendations
        if root_titles.intersection(set(item.get("supporting_root_causes", [])))
    )
    return clamp_score(linked / len(recommendations))


def _normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _keyword_set(text: str) -> set[str]:
    tokens = {
        token
        for token in _normalize_text(text).replace("-", " ").split()
        if len(token) >= 4
    }
    return tokens
