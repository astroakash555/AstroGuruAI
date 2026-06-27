"""Contradiction detection engine."""

from __future__ import annotations

from typing import Any

from reasoning_layer.types import AuditEntry, ContradictionFinding, SystemSignal


def analyze_contradictions(
    signals: dict[str, SystemSignal],
    problem_domain: str | None,
) -> tuple[ContradictionFinding, ...]:
    contradictions: list[ContradictionFinding] = []
    topic = problem_domain or "general_outcome"

    vedic = signals.get("vedic")
    kp = signals.get("kp")
    transit = signals.get("transit")
    lk = signals.get("lal_kitab")
    kb = signals.get("knowledge_brain")

    if vedic and kp and _is_contradictory(vedic.stance, kp.stance):
        contradictions.append(
            _build_contradiction(
                topic=f"{topic}:vedic_vs_kp",
                supporting=_evidence_from_signal(vedic, "support"),
                opposing=_evidence_from_signal(kp, "opposing"),
                audit=vedic.audit + kp.audit,
            )
        )

    if kb and kp and _is_contradictory(kb.stance, kp.stance):
        contradictions.append(
            _build_contradiction(
                topic=f"{topic}:knowledge_vs_kp",
                supporting=_evidence_from_signal(kb, "support"),
                opposing=_evidence_from_signal(kp, "opposing"),
                audit=kb.audit + kp.audit,
            )
        )

    if vedic and transit and _is_contradictory(vedic.stance, transit.stance):
        contradictions.append(
            _build_contradiction(
                topic=f"{topic}:vedic_vs_transit",
                supporting=_evidence_from_signal(vedic, "support"),
                opposing=_evidence_from_signal(transit, "opposing"),
                audit=vedic.audit + transit.audit,
            )
        )

    if lk and vedic and _is_contradictory(lk.stance, vedic.stance):
        contradictions.append(
            _build_contradiction(
                topic=f"{topic}:lal_kitab_vs_vedic",
                supporting=_evidence_from_signal(lk, "opposing"),
                opposing=_evidence_from_signal(vedic, "support"),
                audit=lk.audit + vedic.audit,
            )
        )

    return tuple(contradictions)


def _is_contradictory(stance_a: str, stance_b: str) -> bool:
    if stance_a == "neutral" or stance_b == "neutral":
        return False
    if stance_a == stance_b:
        return False
    return True


def _evidence_from_signal(signal: SystemSignal, role: str) -> list[dict[str, Any]]:
    return [
        {
            "system": signal.system,
            "stance": signal.stance,
            "strength": signal.strength,
            "factors": list(signal.factors),
            "role": role,
        }
    ]


def _build_contradiction(
    *,
    topic: str,
    supporting: list[dict[str, Any]],
    opposing: list[dict[str, Any]],
    audit: tuple[AuditEntry, ...],
) -> ContradictionFinding:
    support_strength = max((item["strength"] for item in supporting), default=0.0)
    oppose_strength = max((item["strength"] for item in opposing), default=0.0)
    total = support_strength + oppose_strength
    confidence = round((max(support_strength, oppose_strength) / total) * 100, 1) if total else 50.0

    contradiction_audit = audit + (
        AuditEntry(
            rule_source="contradiction_engine",
            engine_source="contradiction_engine",
            reason_used=f"Detected opposing stances for topic {topic}",
        ),
    )

    return ContradictionFinding(
        topic=topic,
        supporting_evidence=tuple(supporting),
        opposing_evidence=tuple(opposing),
        confidence_score=confidence,
        audit=contradiction_audit,
    )
