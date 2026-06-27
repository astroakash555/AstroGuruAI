"""Confidence scoring engine."""

from __future__ import annotations

from reasoning_layer.types import ConfidenceBreakdown, ContradictionFinding, SystemSignal


def compute_confidence(
    signals: dict[str, SystemSignal],
    contradictions: tuple[ContradictionFinding, ...],
) -> ConfidenceBreakdown:
    vedic = _agreement_score(signals.get("vedic"))
    kp = _agreement_score(signals.get("kp"))
    lal_kitab = _agreement_score(signals.get("lal_kitab"))
    dasha = _agreement_score(signals.get("dasha"))
    transit = _agreement_score(signals.get("transit"))

    weights = {
        "vedic": 0.25,
        "kp": 0.2,
        "lal_kitab": 0.15,
        "dasha": 0.2,
        "transit": 0.2,
    }
    weighted = (
        vedic * weights["vedic"]
        + kp * weights["kp"]
        + lal_kitab * weights["lal_kitab"]
        + dasha * weights["dasha"]
        + transit * weights["transit"]
    )

    contradiction_penalty = min(0.35, len(contradictions) * 0.08)
    consensus_bonus = _consensus_bonus(signals)
    overall = int(round(max(0, min(100, (weighted - contradiction_penalty + consensus_bonus) * 100))))

    return ConfidenceBreakdown(
        vedic_agreement=round(vedic, 3),
        kp_agreement=round(kp, 3),
        lal_kitab_agreement=round(lal_kitab, 3),
        dasha_agreement=round(dasha, 3),
        transit_agreement=round(transit, 3),
        overall_score=overall,
    )


def _agreement_score(signal: SystemSignal | None) -> float:
    if not signal:
        return 0.0
    if signal.stance == "neutral":
        return 0.35
    return min(1.0, 0.5 + signal.strength * 0.5)


def _consensus_bonus(signals: dict[str, SystemSignal]) -> float:
    stances = [signal.stance for signal in signals.values() if signal.stance != "neutral"]
    if not stances:
        return 0.0
    dominant = max(set(stances), key=stances.count)
    agreement_ratio = stances.count(dominant) / len(stances)
    return agreement_ratio * 0.15
