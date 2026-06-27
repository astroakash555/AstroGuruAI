"""Root cause detection engine."""

from __future__ import annotations

from typing import Any

from reasoning_layer.constants import MALEFICS
from reasoning_layer.types import AuditEntry, ReasoningInput, RootCauseFinding, SystemSignal


def analyze_root_causes(
    reasoning_input: ReasoningInput,
    signals: dict[str, SystemSignal],
) -> tuple[RootCauseFinding, ...]:
    ranked_planets = _rank_planets(reasoning_input)
    dasha_influence = _extract_dasha_influence(reasoning_input)
    transit_influence = _extract_transit_influence(reasoning_input)

    triggering = ranked_planets[0] if ranked_planets else None
    supporting = _find_supporting_planet(reasoning_input, ranked_planets)

    findings: list[RootCauseFinding] = []

    if triggering:
        findings.append(
            RootCauseFinding(
                cause_type="actual",
                primary_factor=f"planet:{triggering}",
                triggering_planet=triggering,
                supporting_planet=supporting,
                dasha_influence=dasha_influence,
                transit_influence=transit_influence,
                severity=_planet_severity(reasoning_input, triggering),
                audit=_root_cause_audit(reasoning_input, triggering, "actual"),
            )
        )

    secondary = _secondary_cause(reasoning_input, ranked_planets, signals)
    if secondary:
        findings.append(secondary)

    hidden = _hidden_cause(reasoning_input, ranked_planets, signals)
    if hidden:
        findings.append(hidden)

    return tuple(findings)


def _rank_planets(reasoning_input: ReasoningInput) -> list[str]:
    scores: dict[str, float] = {}

    if reasoning_input.astro_intelligence:
        for planet in reasoning_input.astro_intelligence.get("root_cause_planets", []):
            scores[planet] = scores.get(planet, 0.0) + 0.5
        for item in reasoning_input.astro_intelligence.get("ranked_causes", []):
            scores[item["planet"]] = scores.get(item["planet"], 0.0) + item.get("severity", 0.3)

    if reasoning_input.problem_analysis:
        for planet in reasoning_input.problem_analysis.get("planets", {}).get("primary", []):
            scores[planet] = scores.get(planet, 0.0) + 0.35
        for planet in reasoning_input.problem_analysis.get("planets", {}).get("shadow", []):
            scores[planet] = scores.get(planet, 0.0) + 0.2

    for dosha in reasoning_input.doshas.get("present_doshas", []):
        for planet in dosha.get("planets_involved", []):
            scores[planet] = scores.get(planet, 0.0) + dosha.get("severity", 0.4)

    current = reasoning_input.dasha.get("current", {})
    for key in ("mahadasha", "antardasha"):
        period = current.get(key)
        if period and period.get("lord"):
            scores[period["lord"]] = scores.get(period["lord"], 0.0) + 0.25

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return [planet for planet, score in ranked if score >= 0.2]


def _find_supporting_planet(
    reasoning_input: ReasoningInput,
    ranked: list[str],
) -> str | None:
    supportive = ()
    if reasoning_input.astro_intelligence:
        supportive = tuple(reasoning_input.astro_intelligence.get("supportive_planets", []))
    for planet in supportive:
        if planet not in ranked[:1]:
            return planet
    for yoga in reasoning_input.yogas.get("present_yogas", []):
        for planet in yoga.get("planets_involved", []):
            if planet not in MALEFICS and planet not in ranked[:1]:
                return planet
    return None


def _extract_dasha_influence(reasoning_input: ReasoningInput) -> dict[str, Any]:
    current = reasoning_input.dasha.get("current", {})
    influence: dict[str, Any] = {"active_periods": [], "influence_type": "neutral"}
    for key in ("mahadasha", "antardasha", "pratyantar_dasha"):
        period = current.get(key)
        if not period:
            continue
        lord = period.get("lord")
        if not lord:
            continue
        period_type = "delay" if lord in MALEFICS else "support"
        influence["active_periods"].append(
            {"period": key, "lord": lord, "influence_type": period_type}
        )
    if influence["active_periods"]:
        delay_count = sum(
            1 for p in influence["active_periods"] if p["influence_type"] == "delay"
        )
        influence["influence_type"] = (
            "delay" if delay_count >= len(influence["active_periods"]) / 2 else "mixed"
        )
    return influence


def _extract_transit_influence(reasoning_input: ReasoningInput) -> dict[str, Any]:
    blocking: list[dict[str, Any]] = []
    supporting: list[dict[str, Any]] = []
    for key in ("saturn", "jupiter", "rahu", "ketu"):
        section = reasoning_input.transits.get(key, {})
        planet = section.get("planet", key.capitalize())
        for impact in section.get("natal_impacts", []):
            entry = {
                "planet": planet,
                "impact_type": impact.get("impact_type"),
                "strength": impact.get("strength", 0.0),
            }
            if impact.get("impact_type") in {"sade_sati_phase", "block", "delay", "affliction"}:
                blocking.append(entry)
            else:
                supporting.append(entry)
    influence_type = "block" if blocking and len(blocking) >= len(supporting) else "mixed"
    if not blocking and not supporting:
        influence_type = "neutral"
    return {
        "blocking_transits": blocking,
        "supporting_transits": supporting,
        "influence_type": influence_type,
    }


def _planet_severity(reasoning_input: ReasoningInput, planet: str) -> float:
    severity = 0.3
    for dosha in reasoning_input.doshas.get("present_doshas", []):
        if planet in dosha.get("planets_involved", []):
            severity = max(severity, dosha.get("severity", 0.5))
    if reasoning_input.problem_analysis:
        if planet in reasoning_input.problem_analysis.get("planets", {}).get("primary", []):
            severity = max(severity, 0.6)
    if planet in MALEFICS:
        severity = min(1.0, severity + 0.1)
    return round(severity, 3)


def _root_cause_audit(
    reasoning_input: ReasoningInput,
    planet: str,
    cause_type: str,
) -> tuple[AuditEntry, ...]:
    audit: list[AuditEntry] = []
    for dosha in reasoning_input.doshas.get("present_doshas", []):
        if planet in dosha.get("planets_involved", []):
            audit.append(
                AuditEntry(
                    rule_source="doshas_engine",
                    engine_source="root_cause_engine",
                    reason_used=f"{cause_type} cause: {planet} in dosha {dosha.get('dosha_id')}",
                    reference_id=dosha.get("dosha_id"),
                )
            )
    current = reasoning_input.dasha.get("current", {})
    for key in ("mahadasha", "antardasha"):
        period = current.get(key)
        if period and period.get("lord") == planet:
            audit.append(
                AuditEntry(
                    rule_source="dasha_engine",
                    engine_source="root_cause_engine",
                    reason_used=f"{cause_type} cause: active {key} lord {planet}",
                    reference_id=key,
                )
            )
    if not audit:
        audit.append(
            AuditEntry(
                rule_source="astro_intelligence",
                engine_source="root_cause_engine",
                reason_used=f"{cause_type} cause: ranked planet {planet}",
            )
        )
    return tuple(audit)


def _secondary_cause(
    reasoning_input: ReasoningInput,
    ranked: list[str],
    signals: dict[str, SystemSignal],
) -> RootCauseFinding | None:
    dasha_signal = signals.get("dasha")
    if not dasha_signal or dasha_signal.stance == "neutral":
        return None

    secondary_planet = ranked[1] if len(ranked) > 1 else None
    current = reasoning_input.dasha.get("current", {})
    maha = current.get("mahadasha", {})
    lord = maha.get("lord")

    return RootCauseFinding(
        cause_type="secondary",
        primary_factor=f"dasha:{dasha_signal.stance}",
        triggering_planet=lord or secondary_planet,
        supporting_planet=secondary_planet,
        dasha_influence=_extract_dasha_influence(reasoning_input),
        transit_influence={"influence_type": "neutral", "blocking_transits": [], "supporting_transits": []},
        severity=dasha_signal.strength,
        audit=dasha_signal.audit,
    )


def _hidden_cause(
    reasoning_input: ReasoningInput,
    ranked: list[str],
    signals: dict[str, SystemSignal],
) -> RootCauseFinding | None:
    lk = signals.get("lal_kitab")
    transit = signals.get("transit")
    hidden_planet = None

    if lk and lk.stance in {"block", "delay"} and reasoning_input.lal_kitab:
        for finding in reasoning_input.lal_kitab.get("dosh_findings", []):
            if finding.get("is_present"):
                planets = finding.get("planets_involved", [])
                hidden_planet = planets[0] if planets else None
                audit = lk.audit
                return RootCauseFinding(
                    cause_type="hidden",
                    primary_factor=f"lal_kitab:{finding.get('finding_id')}",
                    triggering_planet=hidden_planet,
                    supporting_planet=ranked[0] if ranked else None,
                    dasha_influence={"influence_type": "neutral", "active_periods": []},
                    transit_influence=_extract_transit_influence(reasoning_input),
                    severity=finding.get("strength", 0.5),
                    audit=audit,
                )

    if transit and transit.stance == "block":
        for key in ("saturn", "rahu"):
            section = reasoning_input.transits.get(key, {})
            if section.get("natal_impacts"):
                return RootCauseFinding(
                    cause_type="hidden",
                    primary_factor=f"transit:{key}",
                    triggering_planet=section.get("planet", key.capitalize()),
                    supporting_planet=ranked[0] if ranked else None,
                    dasha_influence={"influence_type": "neutral", "active_periods": []},
                    transit_influence=_extract_transit_influence(reasoning_input),
                    severity=transit.strength,
                    audit=transit.audit,
                )
    return None
