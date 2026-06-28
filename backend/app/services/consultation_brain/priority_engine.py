"""Priority intelligence engine for consultation brain."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from backend.app.services.consultation_brain.conflict_engine import ConflictEngineResult
from backend.app.services.consultation_brain.constants import EvidenceSource, MAX_PRIORITIES
from backend.app.services.consultation_brain.models import ConsultationEvidence, ConsultationPriority
from backend.app.services.consultation_brain.priority_models import (
    ALL_PRIORITY_DOMAINS,
    ConsultationPriorityResult,
    DomainPriority,
    PriorityDomain,
)
from backend.app.services.consultation_brain.priority_rules import (
    SECONDARY_PRIORITY_COUNT,
    SUPPRESSION_THRESHOLD,
    compute_domain_confidence,
    compute_importance,
    compute_priority_score,
    compute_urgency,
    empty_domain_set,
    filter_active_evidence,
    is_suppressed,
    map_evidence_to_domains,
    sort_domain_priorities,
    supporting_sources,
)
from backend.app.services.consultation_brain.weights import CONFLICT_RESOLUTION_WEIGHTS


class PriorityEngine:
    """Ranks consultation domains from conflict-resolved evidence."""

    def __init__(
        self,
        *,
        weights: Mapping | None = None,
        suppression_threshold: float = SUPPRESSION_THRESHOLD,
        secondary_count: int = SECONDARY_PRIORITY_COUNT,
    ) -> None:
        self._weights = weights or CONFLICT_RESOLUTION_WEIGHTS
        self._suppression_threshold = suppression_threshold
        self._secondary_count = secondary_count

    @property
    def weights(self) -> Mapping:
        return self._weights

    def rank(
        self,
        conflict_result: ConflictEngineResult,
        evidence: Sequence[ConsultationEvidence] | None = None,
    ) -> ConsultationPriorityResult:
        """Rank consultation domains using conflict output and evidence signals."""
        source_evidence = tuple(evidence if evidence is not None else conflict_result.resolved_evidence)
        active_evidence = filter_active_evidence(source_evidence)
        domain_groups = empty_domain_set()
        for item in active_evidence:
            for domain in map_evidence_to_domains(item):
                domain_groups[domain].append(item)

        scored: list[tuple[PriorityDomain, dict[str, float | int | tuple]]] = []
        for domain, items in domain_groups.items():
            if not items:
                continue
            urgency = compute_urgency(items)
            importance = compute_importance(items, weights=self._weights)
            confidence = compute_domain_confidence(items)
            sources = supporting_sources(items)
            priority_score = compute_priority_score(
                urgency=urgency,
                importance=importance,
                evidence_count=len(items),
                confidence=confidence,
                supporting_source_count=len(sources),
            )
            scored.append(
                (
                    domain,
                    {
                        "priority_score": priority_score,
                        "urgency": urgency,
                        "importance": importance,
                        "evidence_count": len(items),
                        "confidence": confidence,
                        "supporting_sources": sources,
                        "evidence_ids": tuple(sorted(item.evidence_id for item in items)),
                    },
                )
            )

        ranked = sort_domain_priorities(scored)
        active_domains: list[DomainPriority] = []
        suppressed: list[PriorityDomain] = []
        for domain in ALL_PRIORITY_DOMAINS:
            payload = next((entry for entry in ranked if entry[0] == domain), None)
            if payload is None:
                suppressed.append(domain)
                continue
            _, metrics = payload
            priority_score = float(metrics["priority_score"])
            evidence_count = int(metrics["evidence_count"])
            if priority_score < self._suppression_threshold or is_suppressed(
                priority_score=priority_score,
                evidence_count=evidence_count,
            ):
                suppressed.append(domain)
                continue
            active_domains.append(
                DomainPriority(
                    domain=domain,
                    rank=0,
                    priority_score=priority_score,
                    urgency=float(metrics["urgency"]),
                    importance=float(metrics["importance"]),
                    evidence_count=evidence_count,
                    confidence=float(metrics["confidence"]),
                    supporting_sources=tuple(metrics["supporting_sources"]),  # type: ignore[arg-type]
                    evidence_ids=tuple(metrics["evidence_ids"]),  # type: ignore[arg-type]
                )
            )

        active_domains.sort(
            key=lambda item: (-item.priority_score, -item.confidence, item.domain.value),
        )
        ranked_priorities = tuple(
            DomainPriority(
                domain=item.domain,
                rank=index,
                priority_score=item.priority_score,
                urgency=item.urgency,
                importance=item.importance,
                evidence_count=item.evidence_count,
                confidence=item.confidence,
                supporting_sources=item.supporting_sources,
                evidence_ids=item.evidence_ids,
                metadata={"conflict_resolution_count": len(conflict_result.resolutions)},
            )
            for index, item in enumerate(active_domains, start=1)
        )

        highest = ranked_priorities[0] if ranked_priorities else None
        secondary = ranked_priorities[1 : 1 + self._secondary_count]
        return ConsultationPriorityResult(
            priorities=ranked_priorities,
            highest_priority=highest,
            secondary_priorities=secondary,
            suppressed_topics=tuple(sorted(set(suppressed), key=lambda item: item.value)),
            metadata={
                "ranked_domain_count": len(ranked_priorities),
                "suppressed_domain_count": len(suppressed),
                "conflict_resolution_count": len(conflict_result.resolutions),
                "active_evidence_count": len(active_evidence),
            },
        )


def to_legacy_priorities(result: ConsultationPriorityResult) -> tuple[ConsultationPriority, ...]:
    """Convert priority intelligence output to legacy consultation priorities."""
    legacy: list[ConsultationPriority] = []
    for item in result.priorities[:MAX_PRIORITIES]:
        legacy.append(
            ConsultationPriority(
                rank=item.rank,
                domain=item.domain.value,
                title=item.domain.value.replace("_", " ").title(),
                rationale=(
                    f"Priority score {item.priority_score:.2f}; "
                    f"urgency {item.urgency:.2f}; importance {item.importance:.2f}"
                ),
                confidence=item.confidence,
                evidence_ids=item.evidence_ids,
            )
        )
    return tuple(legacy)
