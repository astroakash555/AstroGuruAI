"""Conflict resolution engine for consultation brain evidence bundles."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from backend.app.services.consultation_brain.constants import CONFLICT_CONFIDENCE_PENALTY, EvidenceSource
from backend.app.services.consultation_brain.models import (
    ConsultationConflict,
    ConsultationConflictResolution,
    ConsultationEvidence,
    ConsultationEvidenceBundle,
)
from backend.app.services.consultation_brain.rules import CONFLICT_ELIGIBLE_SOURCES, ConflictType, detect_conflict_type
from backend.app.services.consultation_brain.weights import (
    CONFLICT_RESOLUTION_WEIGHTS,
    get_conflict_weight,
    weighted_evidence_score,
)


@dataclass(frozen=True)
class ConflictEngineResult:
    """Output of conflict detection and weighted resolution."""

    resolutions: tuple[ConsultationConflictResolution, ...]
    resolved_evidence: tuple[ConsultationEvidence, ...]
    legacy_conflicts: tuple[ConsultationConflict, ...]


class ConflictEngine:
    """Detects contradictory evidence and resolves it using architectural weights."""

    def __init__(self, *, weights: Mapping[EvidenceSource, float] | None = None) -> None:
        self._weights = weights or CONFLICT_RESOLUTION_WEIGHTS

    @property
    def weights(self) -> Mapping[EvidenceSource, float]:
        return self._weights

    def resolve(self, bundle: ConsultationEvidenceBundle) -> ConflictEngineResult:
        """Resolve conflicts in a normalized evidence bundle."""
        eligible = tuple(item for item in bundle.all_evidence if item.source in CONFLICT_ELIGIBLE_SOURCES)
        sorted_items = _sort_evidence(eligible)
        resolutions: list[ConsultationConflictResolution] = []
        loser_penalties: dict[str, float] = {}

        for left_index in range(len(sorted_items)):
            left_item = sorted_items[left_index]
            for right_item in sorted_items[left_index + 1 :]:
                conflict_type = detect_conflict_type(left_item, right_item)
                if conflict_type is None:
                    continue
                winner, loser = _pick_winner(left_item, right_item, weights=self._weights)
                resolution_id = _resolution_id(conflict_type, left_item.evidence_id, right_item.evidence_id)
                resolutions.append(
                    ConsultationConflictResolution(
                        resolution_id=resolution_id,
                        conflict_type=conflict_type.value,
                        resolved_signal=_mark_winner(winner, conflict_type=conflict_type, resolution_id=resolution_id),
                        winning_sources=(winner.source,),
                        losing_sources=(loser.source,),
                        resolution_reason=_resolution_reason(
                            conflict_type=conflict_type,
                            winner=winner,
                            loser=loser,
                            weights=self._weights,
                        ),
                        confidence=round(weighted_evidence_score(winner, weights=self._weights), 4),
                        evidence_ids=tuple(sorted((left_item.evidence_id, right_item.evidence_id))),
                    )
                )
                loser_penalties[loser.evidence_id] = max(
                    loser_penalties.get(loser.evidence_id, 0.0),
                    CONFLICT_CONFIDENCE_PENALTY,
                )

        deduped_resolutions = _dedupe_resolutions(resolutions)
        resolved_evidence = _apply_penalties(bundle.all_evidence, loser_penalties, deduped_resolutions)
        legacy_conflicts = tuple(_to_legacy_conflict(resolution) for resolution in deduped_resolutions)
        return ConflictEngineResult(
            resolutions=deduped_resolutions,
            resolved_evidence=resolved_evidence,
            legacy_conflicts=legacy_conflicts,
        )


def bundle_from_evidence(evidence: Sequence[ConsultationEvidence]) -> ConsultationEvidenceBundle:
    """Build a bundle from flat evidence for adapter compatibility."""
    grouped: dict[EvidenceSource, list[ConsultationEvidence]] = {source: [] for source in EvidenceSource}
    for item in evidence:
        grouped[item.source].append(item)
    return ConsultationEvidenceBundle(
        yogas=tuple(grouped[EvidenceSource.YOGAS]),
        dasha=tuple(grouped[EvidenceSource.DASHA]),
        transit=tuple(grouped[EvidenceSource.TRANSIT]),
        kp=tuple(grouped[EvidenceSource.KP]),
        lal_kitab=tuple(grouped[EvidenceSource.LAL_KITAB]),
        rule_studio=tuple(grouped[EvidenceSource.RULE_STUDIO]),
        case_learning=tuple(grouped[EvidenceSource.CASE_LEARNING]),
        fusion=tuple(grouped[EvidenceSource.FUSION]),
        golden_dataset=tuple(grouped[EvidenceSource.GOLDEN_DATASET]),
        professional_report=tuple(grouped[EvidenceSource.PROFESSIONAL_REPORT]),
    )


def _sort_evidence(evidence: Sequence[ConsultationEvidence]) -> tuple[ConsultationEvidence, ...]:
    return tuple(sorted(evidence, key=lambda item: (item.source.value, item.evidence_id)))


def _pick_winner(
    left: ConsultationEvidence,
    right: ConsultationEvidence,
    *,
    weights: Mapping[EvidenceSource, float],
) -> tuple[ConsultationEvidence, ConsultationEvidence]:
    left_score = weighted_evidence_score(left, weights=weights)
    right_score = weighted_evidence_score(right, weights=weights)
    if left_score > right_score:
        return left, right
    if right_score > left_score:
        return right, left
    left_weight = get_conflict_weight(left.source, weights=weights)
    right_weight = get_conflict_weight(right.source, weights=weights)
    if left_weight > right_weight:
        return left, right
    if right_weight > left_weight:
        return right, left
    if left.evidence_id <= right.evidence_id:
        return left, right
    return right, left


def _resolution_id(conflict_type: ConflictType, left_id: str, right_id: str) -> str:
    return f"{conflict_type.value}-{'-'.join(sorted((left_id, right_id)))}"


def _resolution_reason(
    *,
    conflict_type: ConflictType,
    winner: ConsultationEvidence,
    loser: ConsultationEvidence,
    weights: Mapping[EvidenceSource, float],
) -> str:
    winner_weight = get_conflict_weight(winner.source, weights=weights)
    loser_weight = get_conflict_weight(loser.source, weights=weights)
    return (
        f"Weighted resolution for {conflict_type.value}: "
        f"{winner.source.value} ({winner_weight:.2f}) outranked "
        f"{loser.source.value} ({loser_weight:.2f})."
    )


def _mark_winner(
    winner: ConsultationEvidence,
    *,
    conflict_type: ConflictType,
    resolution_id: str,
) -> ConsultationEvidence:
    return ConsultationEvidence(
        evidence_id=winner.evidence_id,
        source=winner.source,
        category=winner.category,
        title=winner.title,
        summary=winner.summary,
        weight=winner.weight,
        confidence=winner.confidence,
        raw_reference=winner.raw_reference,
        tags=winner.tags,
        metadata={
            **winner.metadata,
            "conflict_resolution_id": resolution_id,
            "conflict_type": conflict_type.value,
            "conflict_winner": True,
        },
    )


def _dedupe_resolutions(
    resolutions: Sequence[ConsultationConflictResolution],
) -> tuple[ConsultationConflictResolution, ...]:
    seen: set[str] = set()
    unique: list[ConsultationConflictResolution] = []
    for resolution in sorted(resolutions, key=lambda item: item.resolution_id):
        if resolution.resolution_id in seen:
            continue
        seen.add(resolution.resolution_id)
        unique.append(resolution)
    return tuple(unique)


def _apply_penalties(
    evidence: Sequence[ConsultationEvidence],
    loser_penalties: Mapping[str, float],
    resolutions: Sequence[ConsultationConflictResolution],
) -> tuple[ConsultationEvidence, ...]:
    resolution_by_evidence: dict[str, str] = {}
    for resolution in resolutions:
        for evidence_id in resolution.evidence_ids:
            if evidence_id not in resolution_by_evidence:
                resolution_by_evidence[evidence_id] = resolution.resolution_id

    adjusted: list[ConsultationEvidence] = []
    for item in evidence:
        penalty = loser_penalties.get(item.evidence_id, 0.0)
        if penalty <= 0.0:
            adjusted.append(item)
            continue
        adjusted.append(
            ConsultationEvidence(
                evidence_id=item.evidence_id,
                source=item.source,
                category=item.category,
                title=item.title,
                summary=item.summary,
                weight=item.weight,
                confidence=max(0.0, item.confidence - penalty),
                raw_reference=item.raw_reference,
                tags=item.tags,
                metadata={
                    **item.metadata,
                    "conflict_id": resolution_by_evidence.get(item.evidence_id, ""),
                    "conflict_loser": True,
                },
            )
        )
    return tuple(adjusted)


def _to_legacy_conflict(resolution: ConsultationConflictResolution) -> ConsultationConflict:
    return ConsultationConflict(
        conflict_id=resolution.resolution_id,
        evidence_ids=resolution.evidence_ids,
        description=f"Conflict type: {resolution.conflict_type}",
        resolution=resolution.resolution_reason,
        resolved_confidence=resolution.confidence,
    )
