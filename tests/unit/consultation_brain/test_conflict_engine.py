"""Tests for ConflictEngine and conflict rules."""

from backend.app.services.consultation_brain.conflict_engine import (
    ConflictEngine,
    _dedupe_resolutions,
    _pick_winner,
    bundle_from_evidence,
)
from backend.app.services.consultation_brain.models import ConsultationConflictResolution
from backend.app.services.consultation_brain.constants import EvidenceCategory, EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationEvidence, ConsultationEvidenceBundle
from backend.app.services.consultation_brain.rules import ConflictType, detect_conflict_type, extract_signals


def _evidence(
    *,
    evidence_id: str,
    source: EvidenceSource,
    category: EvidenceCategory,
    confidence: float,
    metadata: dict | None = None,
    tags: tuple[str, ...] = (),
) -> ConsultationEvidence:
    return ConsultationEvidence(
        evidence_id=evidence_id,
        source=source,
        category=category,
        title=evidence_id,
        summary="summary",
        weight=0.5,
        confidence=confidence,
        metadata=metadata or {},
        tags=tags,
    )


def test_extract_signals_reads_supported_metadata():
    negative = _evidence(
        evidence_id="kp-1",
        source=EvidenceSource.KP,
        category=EvidenceCategory.RELATIONSHIP,
        confidence=0.35,
        metadata={"is_supported": False},
    )
    signals = extract_signals(negative)
    assert signals.polarity == "negative"


def test_detect_positive_vs_negative_conflict():
    positive = _evidence(
        evidence_id="fusion-1",
        source=EvidenceSource.FUSION,
        category=EvidenceCategory.RELATIONSHIP,
        confidence=0.8,
        metadata={"is_supported": True},
    )
    negative = _evidence(
        evidence_id="kp-1",
        source=EvidenceSource.KP,
        category=EvidenceCategory.RELATIONSHIP,
        confidence=0.35,
        metadata={"is_supported": False},
    )
    assert detect_conflict_type(positive, negative) == ConflictType.POSITIVE_VS_NEGATIVE


def test_detect_rare_yoga_vs_general_transit():
    yoga = _evidence(
        evidence_id="yoga-1",
        source=EvidenceSource.YOGAS,
        category=EvidenceCategory.GENERAL,
        confidence=0.82,
    )
    transit = _evidence(
        evidence_id="transit-1",
        source=EvidenceSource.TRANSIT,
        category=EvidenceCategory.TIMING,
        confidence=0.55,
    )
    assert detect_conflict_type(yoga, transit) == ConflictType.RARE_YOGA_VS_GENERAL_TRANSIT


def test_conflict_engine_resolves_with_higher_weight_source():
    bundle = ConsultationEvidenceBundle(
        rule_studio=(
            _evidence(
                evidence_id="rule-1",
                source=EvidenceSource.RULE_STUDIO,
                category=EvidenceCategory.RELATIONSHIP,
                confidence=0.7,
                metadata={"is_supported": True},
            ),
        ),
        lal_kitab=(
            _evidence(
                evidence_id="lk-1",
                source=EvidenceSource.LAL_KITAB,
                category=EvidenceCategory.RELATIONSHIP,
                confidence=0.9,
                metadata={"is_supported": False},
            ),
        ),
    )
    result = ConflictEngine().resolve(bundle)
    assert len(result.resolutions) == 1
    resolution = result.resolutions[0]
    assert resolution.winning_sources == (EvidenceSource.RULE_STUDIO,)
    assert resolution.losing_sources == (EvidenceSource.LAL_KITAB,)
    assert resolution.resolved_signal.source == EvidenceSource.RULE_STUDIO
    assert "Weighted resolution" in resolution.resolution_reason


def test_conflict_engine_is_deterministic():
    bundle = ConsultationEvidenceBundle(
        fusion=(
            _evidence(
                evidence_id="fusion-1",
                source=EvidenceSource.FUSION,
                category=EvidenceCategory.CAREER,
                confidence=0.7,
                metadata={"is_supported": True},
            ),
        ),
        case_learning=(
            _evidence(
                evidence_id="case-1",
                source=EvidenceSource.CASE_LEARNING,
                category=EvidenceCategory.CAREER,
                confidence=0.75,
                metadata={"is_supported": False},
            ),
        ),
    )
    first = ConflictEngine().resolve(bundle)
    second = ConflictEngine().resolve(bundle)
    assert first.resolutions == second.resolutions
    assert first.resolved_evidence == second.resolved_evidence


def test_conflict_engine_penalizes_losing_evidence():
    bundle = ConsultationEvidenceBundle(
        dasha=(
            _evidence(
                evidence_id="dasha-1",
                source=EvidenceSource.DASHA,
                category=EvidenceCategory.TIMING,
                confidence=0.7,
                metadata={"is_supported": True},
            ),
        ),
        transit=(
            _evidence(
                evidence_id="transit-1",
                source=EvidenceSource.TRANSIT,
                category=EvidenceCategory.GENERAL,
                confidence=0.4,
                metadata={"is_supported": False},
            ),
        ),
    )
    result = ConflictEngine().resolve(bundle)
    loser = next(item for item in result.resolved_evidence if item.evidence_id == "transit-1")
    assert loser.metadata.get("conflict_loser") is True
    assert loser.confidence < 0.4


def test_bundle_from_evidence_groups_by_source():
    items = (
        _evidence(
            evidence_id="yoga-1",
            source=EvidenceSource.YOGAS,
            category=EvidenceCategory.GENERAL,
            confidence=0.5,
        ),
        _evidence(
            evidence_id="dasha-1",
            source=EvidenceSource.DASHA,
            category=EvidenceCategory.TIMING,
            confidence=0.5,
        ),
    )
    bundle = bundle_from_evidence(items)
    assert len(bundle.yogas) == 1
    assert len(bundle.dasha) == 1


def test_no_conflicts_when_only_one_eligible_source():
    bundle = ConsultationEvidenceBundle(
        yogas=(
            _evidence(
                evidence_id="yoga-1",
                source=EvidenceSource.YOGAS,
                category=EvidenceCategory.GENERAL,
                confidence=0.8,
            ),
            _evidence(
                evidence_id="yoga-2",
                source=EvidenceSource.YOGAS,
                category=EvidenceCategory.GENERAL,
                confidence=0.7,
            ),
        )
    )
    result = ConflictEngine().resolve(bundle)
    assert result.resolutions == ()


def test_detect_rule_based_vs_learned_conflict():
    rule = _evidence(
        evidence_id="rule-1",
        source=EvidenceSource.RULE_STUDIO,
        category=EvidenceCategory.CAREER,
        confidence=0.55,
        metadata={"is_supported": True},
    )
    learned = _evidence(
        evidence_id="case-1",
        source=EvidenceSource.CASE_LEARNING,
        category=EvidenceCategory.CAREER,
        confidence=0.55,
        metadata={"is_supported": True},
    )
    assert detect_conflict_type(rule, learned) == ConflictType.RULE_BASED_VS_LEARNED


def test_detect_time_sensitive_vs_permanent_conflict():
    dasha = _evidence(
        evidence_id="dasha-1",
        source=EvidenceSource.DASHA,
        category=EvidenceCategory.TIMING,
        confidence=0.55,
        metadata={"is_supported": True},
    )
    fusion = _evidence(
        evidence_id="fusion-1",
        source=EvidenceSource.FUSION,
        category=EvidenceCategory.GENERAL,
        confidence=0.55,
        metadata={"is_supported": True},
    )
    assert detect_conflict_type(dasha, fusion) == ConflictType.TIME_SENSITIVE_VS_PERMANENT


def test_detect_strong_vs_weak_conflict():
    strong = _evidence(
        evidence_id="fusion-1",
        source=EvidenceSource.FUSION,
        category=EvidenceCategory.HEALTH,
        confidence=0.8,
        metadata={"is_supported": True},
    )
    weak = _evidence(
        evidence_id="kp-1",
        source=EvidenceSource.KP,
        category=EvidenceCategory.HEALTH,
        confidence=0.4,
        metadata={"is_supported": True},
    )
    assert detect_conflict_type(strong, weak) == ConflictType.STRONG_VS_WEAK


def test_same_source_pairs_are_ignored():
    left = _evidence(
        evidence_id="kp-1",
        source=EvidenceSource.KP,
        category=EvidenceCategory.GENERAL,
        confidence=0.4,
        metadata={"is_supported": False},
    )
    right = _evidence(
        evidence_id="kp-2",
        source=EvidenceSource.KP,
        category=EvidenceCategory.GENERAL,
        confidence=0.8,
        metadata={"is_supported": True},
    )
    assert detect_conflict_type(left, right) is None


def test_conflict_engine_exposes_injected_weights():
    custom_weights = {EvidenceSource.KP: 0.99}
    engine = ConflictEngine(weights=custom_weights)
    assert engine.weights[EvidenceSource.KP] == 0.99


def test_conflict_engine_breaks_equal_scores_by_source_weight():
    bundle = ConsultationEvidenceBundle(
        kp=(
            _evidence(
                evidence_id="kp-1",
                source=EvidenceSource.KP,
                category=EvidenceCategory.GENERAL,
                confidence=0.5,
                metadata={"is_supported": True},
            ),
        ),
        lal_kitab=(
            _evidence(
                evidence_id="lk-1",
                source=EvidenceSource.LAL_KITAB,
                category=EvidenceCategory.GENERAL,
                confidence=0.5,
                metadata={"is_supported": False},
            ),
        ),
    )
    result = ConflictEngine().resolve(bundle)
    assert result.resolutions[0].winning_sources == (EvidenceSource.KP,)


def test_extract_signals_uses_tag_polarity():
    evidence = _evidence(
        evidence_id="fusion-1",
        source=EvidenceSource.FUSION,
        category=EvidenceCategory.GENERAL,
        confidence=0.2,
        tags=("supported",),
    )
    assert extract_signals(evidence).polarity == "positive"


def test_extract_signals_marks_negative_tags():
    evidence = _evidence(
        evidence_id="fusion-1",
        source=EvidenceSource.FUSION,
        category=EvidenceCategory.GENERAL,
        confidence=0.8,
        tags=("negative",),
    )
    assert extract_signals(evidence).polarity == "negative"


def test_pick_winner_prefers_higher_score_and_weight_ties():
    winner, loser = _pick_winner(
        _evidence(
            evidence_id="kp-1",
            source=EvidenceSource.KP,
            category=EvidenceCategory.GENERAL,
            confidence=0.9,
        ),
        _evidence(
            evidence_id="fusion-1",
            source=EvidenceSource.FUSION,
            category=EvidenceCategory.GENERAL,
            confidence=0.4,
            metadata={"is_supported": False},
        ),
        weights=ConflictEngine().weights,
    )
    assert winner.source == EvidenceSource.KP
    assert loser.source == EvidenceSource.FUSION


def test_pick_winner_breaks_full_ties_by_evidence_id():
    left = _evidence(
        evidence_id="b-id",
        source=EvidenceSource.DASHA,
        category=EvidenceCategory.GENERAL,
        confidence=0.5,
    )
    right = _evidence(
        evidence_id="a-id",
        source=EvidenceSource.TRANSIT,
        category=EvidenceCategory.GENERAL,
        confidence=0.5,
    )
    winner, loser = _pick_winner(left, right, weights={EvidenceSource.DASHA: 0.5, EvidenceSource.TRANSIT: 0.5})
    assert winner.evidence_id == "a-id"
    assert loser.evidence_id == "b-id"


def test_dedupe_resolutions_skips_duplicate_ids():
    resolution = ConsultationConflictResolution(
        resolution_id="conflict-1",
        conflict_type=ConflictType.POSITIVE_VS_NEGATIVE.value,
        resolved_signal=_evidence(
            evidence_id="fusion-1",
            source=EvidenceSource.FUSION,
            category=EvidenceCategory.GENERAL,
            confidence=0.8,
        ),
        winning_sources=(EvidenceSource.FUSION,),
        losing_sources=(EvidenceSource.KP,),
        resolution_reason="reason",
        confidence=0.8,
        evidence_ids=("fusion-1", "kp-1"),
    )
    deduped = _dedupe_resolutions((resolution, resolution))
    assert deduped == (resolution,)


