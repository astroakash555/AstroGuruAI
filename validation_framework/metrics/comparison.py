"""Extract system predictions from unified report output."""

from __future__ import annotations

from typing import Any

from validation_framework.types import SystemPrediction


def extract_system_prediction(unified_report: dict[str, Any]) -> SystemPrediction:
    intelligence = unified_report.get("astro_intelligence", {})
    problem = unified_report.get("problem_analysis") or {}
    dasha = unified_report.get("dasha", {})
    transits = unified_report.get("transits", {})
    remedies = unified_report.get("remedy_recommendations", {})
    reasoning = unified_report.get("reasoning", {})
    consultation = unified_report.get("consultation", {})

    planets: set[str] = set(intelligence.get("root_cause_planets", []))
    for planet in problem.get("planets", {}).get("primary", []):
        planets.add(planet)
    for planet in problem.get("planets", {}).get("shadow", []):
        planets.add(planet)

    houses: set[int] = set(intelligence.get("affected_houses", []))
    for house in problem.get("houses", {}).get("primary", []):
        houses.add(house)
    for house in problem.get("houses", {}).get("secondary", []):
        houses.add(house)

    dasha_lords: list[str] = []
    current = dasha.get("current", {})
    for key in ("mahadasha", "antardasha", "pratyantar_dasha"):
        period = current.get(key)
        if period and period.get("lord"):
            dasha_lords.append(period["lord"])

    transit_indicators: list[str] = []
    for key in ("saturn", "jupiter", "rahu", "ketu"):
        section = transits.get(key, {})
        for impact in section.get("natal_impacts", []):
            impact_type = impact.get("impact_type")
            if impact_type:
                transit_indicators.append(impact_type)

    remedy_ids: list[str] = []
    for match in remedies.get("matched_remedies", []):
        remedy_id = match.get("remedy", {}).get("remedy_id")
        if remedy_id:
            remedy_ids.append(remedy_id)

    guru_remedies = consultation.get("senior_guru", {}).get("strongest_remedies", [])
    for remedy in guru_remedies:
        remedy_id = remedy.get("remedy_id")
        if remedy_id:
            remedy_ids.append(remedy_id)

    consensus = None
    if reasoning:
        consensus = reasoning.get("consensus", {}).get("final_consensus")
    elif consultation:
        consensus = consultation.get("senior_guru", {}).get("final_conclusion", {}).get(
            "consensus_outcome"
        )

    confidence = None
    if reasoning:
        confidence = reasoning.get("confidence", {}).get("overall_score")

    return SystemPrediction(
        planets=tuple(sorted(planets)),
        houses=tuple(sorted(houses)),
        dasha_lords=tuple(dasha_lords),
        transit_indicators=tuple(dict.fromkeys(transit_indicators)),
        remedies=tuple(dict.fromkeys(remedy_ids)),
        consensus_outcome=consensus,
        confidence_score=confidence,
    )


def prediction_to_dict(prediction: SystemPrediction) -> dict[str, Any]:
    return {
        "planets": list(prediction.planets),
        "houses": list(prediction.houses),
        "dasha_lords": list(prediction.dasha_lords),
        "transit_indicators": list(prediction.transit_indicators),
        "remedies": list(prediction.remedies),
        "consensus_outcome": prediction.consensus_outcome,
        "confidence_score": prediction.confidence_score,
    }
