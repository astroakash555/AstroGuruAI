"""Extract normalized signals from each astrology system."""

from __future__ import annotations

from typing import Any

from reasoning_layer.constants import DOMAIN_HOUSE_MAP, MALEFICS
from reasoning_layer.types import AuditEntry, ReasoningInput, SystemSignal


def extract_system_signals(reasoning_input: ReasoningInput) -> dict[str, SystemSignal]:
    domain = _resolve_domain(reasoning_input)
    return {
        "vedic": _vedic_signal(reasoning_input, domain),
        "kp": _kp_signal(reasoning_input, domain),
        "lal_kitab": _lal_kitab_signal(reasoning_input),
        "dasha": _dasha_signal(reasoning_input, domain),
        "transit": _transit_signal(reasoning_input, domain),
        "knowledge_brain": _knowledge_signal(reasoning_input),
    }


def _resolve_domain(reasoning_input: ReasoningInput) -> str | None:
    if reasoning_input.problem_analysis:
        category = reasoning_input.problem_analysis.get("category", {}).get("category")
        if category and category != "unknown":
            return category
    if reasoning_input.knowledge_search:
        inferred = reasoning_input.knowledge_search.get("summary", {}).get("inferred_domain")
        if inferred:
            return inferred
    return None


def _vedic_signal(reasoning_input: ReasoningInput, domain: str | None) -> SystemSignal:
    factors: list[str] = []
    audit: list[AuditEntry] = []
    support_score = 0.0
    block_score = 0.0

    for yoga in reasoning_input.yogas.get("present_yogas", []):
        strength = yoga.get("strength", 0.5)
        support_score += strength * 0.3
        factors.append(f"yoga:{yoga.get('yoga_id')}")
        audit.append(
            AuditEntry(
                rule_source="yogas_engine",
                engine_source="vedic",
                reason_used=f"Present yoga {yoga.get('yoga_id')} strength {strength}",
                reference_id=yoga.get("yoga_id"),
            )
        )

    for dosha in reasoning_input.doshas.get("present_doshas", []):
        severity = dosha.get("severity", 0.5)
        block_score += severity * 0.35
        factors.append(f"dosha:{dosha.get('dosha_id')}")
        audit.append(
            AuditEntry(
                rule_source="doshas_engine",
                engine_source="vedic",
                reason_used=f"Present dosha {dosha.get('dosha_id')} severity {severity}",
                reference_id=dosha.get("dosha_id"),
            )
        )

    if reasoning_input.problem_analysis:
        severity = reasoning_input.problem_analysis.get("severity", {}).get("score", 0.5)
        block_score += severity * 0.25
        factors.append("problem_severity")
        audit.append(
            AuditEntry(
                rule_source="problem_analyzer",
                engine_source="vedic",
                reason_used=f"Problem severity score {severity}",
            )
        )

    if domain:
        domain_houses = DOMAIN_HOUSE_MAP.get(domain, ())
        for planet in reasoning_input.kundali.get("planets", []):
            if planet.get("house") in domain_houses and planet.get("name") in MALEFICS:
                block_score += 0.15
                factors.append(f"malefic_in_domain_house:{planet['name']}_h{planet['house']}")
                audit.append(
                    AuditEntry(
                        rule_source="kundali_chart",
                        engine_source="vedic",
                        reason_used=(
                            f"Malefic {planet['name']} in domain house {planet['house']}"
                        ),
                    )
                )

    stance, strength = _score_to_stance(support_score, block_score)
    return SystemSignal(
        system="vedic",
        stance=stance,
        strength=round(strength, 3),
        factors=tuple(factors),
        audit=tuple(audit),
    )


def _kp_signal(reasoning_input: ReasoningInput, domain: str | None) -> SystemSignal:
    factors: list[str] = []
    audit: list[AuditEntry] = []
    support_score = 0.0
    block_score = 0.0

    kp = reasoning_input.kp_analysis or {}
    events = kp.get("events", [])
    for event in events:
        score = event.get("support_score", 0.0)
        if event.get("is_supported"):
            support_score += score * 0.4
            factors.append(f"event_supported:{event.get('event_id')}")
            audit.append(
                AuditEntry(
                    rule_source="kp_event_rules",
                    engine_source="kp",
                    reason_used=f"Event {event.get('event_id')} supported score {score}",
                    reference_id=event.get("event_id"),
                )
            )
        else:
            block_score += (1.0 - score) * 0.4
            factors.append(f"event_unsupported:{event.get('event_id')}")
            audit.append(
                AuditEntry(
                    rule_source="kp_event_rules",
                    engine_source="kp",
                    reason_used=f"Event {event.get('event_id')} not supported score {score}",
                    reference_id=event.get("event_id"),
                )
            )

    summary = kp.get("summary", {})
    if summary.get("supported_events", 0) == 0 and events:
        block_score += 0.2
        factors.append("no_supported_events")
        audit.append(
            AuditEntry(
                rule_source="kp_summary",
                engine_source="kp",
                reason_used="No KP events currently supported",
            )
        )

    if domain and not events:
        block_score += 0.1
        factors.append("missing_domain_events")

    stance, strength = _score_to_stance(support_score, block_score)
    if block_score > support_score and block_score > 0.3:
        stance = "delay"
    return SystemSignal(
        system="kp",
        stance=stance,
        strength=round(strength, 3),
        factors=tuple(factors),
        audit=tuple(audit),
    )


def _lal_kitab_signal(reasoning_input: ReasoningInput) -> SystemSignal:
    factors: list[str] = []
    audit: list[AuditEntry] = []
    support_score = 0.0
    block_score = 0.0

    lk = reasoning_input.lal_kitab or {}
    for finding in lk.get("dosh_findings", []):
        if not finding.get("is_present"):
            continue
        strength = finding.get("strength", 0.5)
        block_score += strength * 0.35
        factors.append(f"dosh:{finding.get('finding_id')}")
        audit.append(
            AuditEntry(
                rule_source="lal_kitab_dosh",
                engine_source="lal_kitab",
                reason_used=f"Dosh {finding.get('finding_id')} present strength {strength}",
                reference_id=finding.get("finding_id"),
            )
        )

    for finding in lk.get("rin_findings", []):
        if not finding.get("is_present"):
            continue
        strength = finding.get("strength", 0.4)
        block_score += strength * 0.25
        factors.append(f"rin:{finding.get('finding_id')}")
        audit.append(
            AuditEntry(
                rule_source="lal_kitab_rin",
                engine_source="lal_kitab",
                reason_used=f"Rin {finding.get('finding_id')} present strength {strength}",
                reference_id=finding.get("finding_id"),
            )
        )

    summary = lk.get("summary", {})
    if summary.get("present_count", 0) == 0:
        support_score += 0.15
        factors.append("no_lk_findings")

    stance, strength = _score_to_stance(support_score, block_score)
    return SystemSignal(
        system="lal_kitab",
        stance=stance,
        strength=round(strength, 3),
        factors=tuple(factors),
        audit=tuple(audit),
    )


def _dasha_signal(reasoning_input: ReasoningInput, domain: str | None) -> SystemSignal:
    factors: list[str] = []
    audit: list[AuditEntry] = []
    support_score = 0.0
    block_score = 0.0

    current = reasoning_input.dasha.get("current", {})
    for key in ("mahadasha", "antardasha", "pratyantar_dasha"):
        period = current.get(key)
        if not period:
            continue
        lord = period.get("lord")
        if not lord:
            continue
        if lord in MALEFICS:
            block_score += 0.25
            factors.append(f"{key}_malefic:{lord}")
        else:
            support_score += 0.2
            factors.append(f"{key}_benefic:{lord}")
        audit.append(
            AuditEntry(
                rule_source="dasha_engine",
                engine_source="dasha",
                reason_used=f"Active {key} lord {lord}",
                reference_id=key,
            )
        )

    stance, strength = _score_to_stance(support_score, block_score)
    if block_score > support_score:
        stance = "delay"
    return SystemSignal(
        system="dasha",
        stance=stance,
        strength=round(strength, 3),
        factors=tuple(factors),
        audit=tuple(audit),
    )


def _transit_signal(reasoning_input: ReasoningInput, domain: str | None) -> SystemSignal:
    factors: list[str] = []
    audit: list[AuditEntry] = []
    support_score = 0.0
    block_score = 0.0

    for key in ("saturn", "jupiter", "rahu", "ketu"):
        section = reasoning_input.transits.get(key, {})
        for impact in section.get("natal_impacts", []):
            strength = impact.get("strength", 0.3)
            impact_type = impact.get("impact_type", "general")
            if impact_type in {"sade_sati_phase", "block", "delay", "affliction"}:
                block_score += strength * 0.35
                factors.append(f"{key}:{impact_type}")
            else:
                support_score += strength * 0.25
                factors.append(f"{key}:{impact_type}")
            audit.append(
                AuditEntry(
                    rule_source="transit_engine",
                    engine_source="transit",
                    reason_used=f"{section.get('planet', key)} impact {impact_type} strength {strength}",
                    reference_id=impact_type,
                )
            )

        current = section.get("current", {})
        house = current.get("house_from_lagna")
        if house in (6, 8, 12):
            block_score += 0.1
            factors.append(f"{key}_transit_dusthana:{house}")

    stance, strength = _score_to_stance(support_score, block_score)
    if block_score > support_score and block_score >= 0.25:
        stance = "block"
    return SystemSignal(
        system="transit",
        stance=stance,
        strength=round(strength, 3),
        factors=tuple(factors),
        audit=tuple(audit),
    )


def _knowledge_signal(reasoning_input: ReasoningInput) -> SystemSignal:
    factors: list[str] = []
    audit: list[AuditEntry] = []
    support_score = 0.0
    block_score = 0.0

    kb = reasoning_input.knowledge_search or {}
    for ranked in kb.get("ranked_rules", [])[:10]:
        category = ranked.get("category", "")
        score = ranked.get("score", 0.0)
        rule_id = ranked.get("rule_id", "")
        delay_keywords = ("delay", "denial", "block", "divorce", "unemployment", "debt", "loss")
        support_keywords = ("early", "promotion", "wealth", "recovery", "government")

        if any(kw in category for kw in delay_keywords):
            block_score += score * 0.15
            factors.append(f"kb_block:{rule_id}")
        elif any(kw in category for kw in support_keywords):
            support_score += score * 0.15
            factors.append(f"kb_support:{rule_id}")
        else:
            support_score += score * 0.08
            factors.append(f"kb_neutral:{rule_id}")

        audit.append(
            AuditEntry(
                rule_source="knowledge_brain",
                engine_source="knowledge_brain",
                reason_used=f"Rule {rule_id} category {category} score {score}",
                reference_id=rule_id,
            )
        )

    stance, strength = _score_to_stance(support_score, block_score)
    return SystemSignal(
        system="knowledge_brain",
        stance=stance,
        strength=round(strength, 3),
        factors=tuple(factors),
        audit=tuple(audit),
    )


def _score_to_stance(support_score: float, block_score: float) -> tuple[str, float]:
    if support_score == 0.0 and block_score == 0.0:
        return "neutral", 0.0
    if block_score > support_score * 1.2:
        return "block", min(1.0, block_score)
    if support_score > block_score * 1.2:
        return "support", min(1.0, support_score)
    if abs(block_score - support_score) <= 0.1:
        return "delay", min(1.0, max(support_score, block_score))
    return "neutral", min(1.0, max(support_score, block_score))
