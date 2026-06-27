"""Multi-system consensus engine."""

from __future__ import annotations

from reasoning_layer.types import AuditEntry, ConsensusResult, SystemSignal


def analyze_consensus(signals: dict[str, SystemSignal]) -> ConsensusResult:
    core_systems = ("vedic", "kp", "lal_kitab")
    system_stances = {name: signals[name].stance for name in core_systems if name in signals}

    agreement_areas: list[str] = []
    disagreement_areas: list[str] = []
    audit: list[AuditEntry] = []

    stances = list(system_stances.values())
    if stances and len(set(stances)) == 1:
        agreement_areas.append(f"all_core_systems:{stances[0]}")
    else:
        for name, signal in signals.items():
            if name not in core_systems:
                continue
            audit.extend(signal.audit)
            matched = [
                other
                for other, other_signal in signals.items()
                if other in core_systems
                and other != name
                and other_signal.stance == signal.stance
            ]
            if matched:
                agreement_areas.append(f"{name}_with_{'_'.join(matched)}:{signal.stance}")
            else:
                disagreement_areas.append(f"{name}_stance:{signal.stance}")

    dasha_stance = signals.get("dasha")
    transit_stance = signals.get("transit")
    if dasha_stance and transit_stance:
        if dasha_stance.stance == transit_stance.stance:
            agreement_areas.append(f"timing_layers:{dasha_stance.stance}")
        else:
            disagreement_areas.append(
                f"timing_conflict:dasha_{dasha_stance.stance}_transit_{transit_stance.stance}"
            )

    final_consensus = _resolve_consensus(system_stances, signals)
    audit.append(
        AuditEntry(
            rule_source="consensus_engine",
            engine_source="consensus_engine",
            reason_used=f"Resolved consensus to {final_consensus}",
        )
    )

    return ConsensusResult(
        agreement_areas=tuple(dict.fromkeys(agreement_areas)),
        disagreement_areas=tuple(dict.fromkeys(disagreement_areas)),
        final_consensus=final_consensus,
        system_stances=system_stances,
        audit=tuple(audit),
    )


def _resolve_consensus(
    core_stances: dict[str, str],
    signals: dict[str, SystemSignal],
) -> str:
    if not core_stances:
        return "insufficient_data"

    stance_counts: dict[str, int] = {}
    for stance in core_stances.values():
        stance_counts[stance] = stance_counts.get(stance, 0) + 1

    dominant_stance = max(stance_counts, key=stance_counts.get)
    dominant_count = stance_counts[dominant_stance]
    total = len(core_stances)

    if dominant_count == total:
        if dominant_stance == "support":
            return "strong_support"
        if dominant_stance == "block":
            return "blocked_outcome"
        if dominant_stance == "delay":
            return "delayed_outcome"
        return "mixed_signals"

    if dominant_count >= total / 2:
        if dominant_stance == "support":
            return "moderate_support"
        if dominant_stance in {"block", "delay"}:
            return "delayed_outcome" if dominant_stance == "delay" else "blocked_outcome"

    transit = signals.get("transit")
    if transit and transit.stance == "block":
        return "blocked_outcome"

    return "mixed_signals"
