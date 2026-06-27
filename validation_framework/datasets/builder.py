"""Benchmark dataset builder with real astrology case study templates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from validation_framework.constants import BENCHMARK_CATEGORIES


CASE_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "marriage": [
        {
            "case_id": "marriage_001",
            "title": "Delayed marriage until age 38",
            "problem_text": "No marriage till age 38",
            "actual_outcome": {
                "event": "marriage",
                "outcome_type": "delay",
                "description": "Marriage occurred at age 38 during Venus antardasha.",
                "occurred_at_age": 38,
            },
            "ground_truth": {
                "planets": ["Saturn", "Mars", "Venus"],
                "houses": [7, 8],
                "dasha_lords": ["Saturn", "Venus"],
                "transit_indicators": ["sade_sati_phase"],
                "remedies": ["vedic_saturn_shani_mantra", "lk_remedy_saturn"],
                "consensus_outcome": "delayed_outcome",
            },
            "match_profile": "high",
        },
        {
            "case_id": "marriage_002",
            "title": "Early love marriage",
            "problem_text": "Love marriage at age 22",
            "actual_outcome": {
                "event": "marriage",
                "outcome_type": "early",
                "description": "Love marriage at age 22 with strong Venus support.",
                "occurred_at_age": 22,
            },
            "ground_truth": {
                "planets": ["Venus", "Moon"],
                "houses": [5, 7, 11],
                "dasha_lords": ["Venus", "Moon"],
                "transit_indicators": ["support"],
                "remedies": ["venus_strengthening"],
                "consensus_outcome": "strong_support",
            },
            "match_profile": "high",
        },
        {
            "case_id": "marriage_003",
            "title": "Denial of marriage indicators",
            "problem_text": "Repeated marriage proposals fail",
            "actual_outcome": {
                "event": "marriage",
                "outcome_type": "denial",
                "description": "Multiple proposals failed due to 7th lord affliction.",
            },
            "ground_truth": {
                "planets": ["Saturn", "Rahu", "Ketu"],
                "houses": [7, 12],
                "dasha_lords": ["Saturn", "Rahu"],
                "transit_indicators": ["block"],
                "remedies": ["rahu_remedy", "7th_lord_remedy"],
                "consensus_outcome": "blocked_outcome",
            },
            "match_profile": "medium",
        },
    ],
    "divorce": [
        {
            "case_id": "divorce_001",
            "title": "Divorce after 7th house affliction",
            "problem_text": "Marital separation after 8 years",
            "actual_outcome": {
                "event": "divorce",
                "outcome_type": "separation",
                "description": "Divorce during Rahu mahadasha with Mars in 7th.",
            },
            "ground_truth": {
                "planets": ["Mars", "Rahu", "Saturn"],
                "houses": [7, 8],
                "dasha_lords": ["Rahu", "Mars"],
                "transit_indicators": ["affliction"],
                "remedies": ["mars_remedy", "rahu_remedy"],
                "consensus_outcome": "blocked_outcome",
            },
            "match_profile": "high",
        },
        {
            "case_id": "divorce_002",
            "title": "Second marriage after divorce",
            "problem_text": "Second marriage after divorce",
            "actual_outcome": {
                "event": "second_marriage",
                "outcome_type": "recovery",
                "description": "Second marriage in Jupiter dasha after divorce.",
            },
            "ground_truth": {
                "planets": ["Jupiter", "Venus"],
                "houses": [2, 7, 11],
                "dasha_lords": ["Jupiter", "Venus"],
                "transit_indicators": ["support"],
                "remedies": ["jupiter_remedy"],
                "consensus_outcome": "moderate_support",
            },
            "match_profile": "medium",
        },
    ],
    "career": [
        {
            "case_id": "career_001",
            "title": "Job loss during Saturn dasha",
            "problem_text": "Lost private job during recession",
            "actual_outcome": {
                "event": "job_loss",
                "outcome_type": "unemployment",
                "description": "Unemployment period during Saturn antardasha.",
            },
            "ground_truth": {
                "planets": ["Saturn", "Rahu"],
                "houses": [6, 10],
                "dasha_lords": ["Saturn"],
                "transit_indicators": ["sade_sati_phase"],
                "remedies": ["saturn_remedy", "10th_lord_remedy"],
                "consensus_outcome": "delayed_outcome",
            },
            "match_profile": "high",
        },
        {
            "case_id": "career_002",
            "title": "Promotion in Jupiter period",
            "problem_text": "Promotion to senior role",
            "actual_outcome": {
                "event": "promotion",
                "outcome_type": "advancement",
                "description": "Promotion during Jupiter mahadasha.",
            },
            "ground_truth": {
                "planets": ["Jupiter", "Sun"],
                "houses": [10, 11],
                "dasha_lords": ["Jupiter", "Sun"],
                "transit_indicators": ["support"],
                "remedies": ["jupiter_remedy"],
                "consensus_outcome": "strong_support",
            },
            "match_profile": "high",
        },
    ],
    "government_job": [
        {
            "case_id": "government_job_001",
            "title": "IAS selection through Sun-Jupiter yoga",
            "problem_text": "Selected for government civil service",
            "actual_outcome": {
                "event": "government_selection",
                "outcome_type": "success",
                "description": "Civil service selection with Sun in 10th and Jupiter support.",
            },
            "ground_truth": {
                "planets": ["Sun", "Jupiter", "Saturn"],
                "houses": [6, 10, 11],
                "dasha_lords": ["Sun", "Jupiter"],
                "transit_indicators": ["support"],
                "remedies": ["sun_remedy", "jupiter_remedy"],
                "consensus_outcome": "strong_support",
            },
            "match_profile": "high",
        },
        {
            "case_id": "government_job_002",
            "title": "Repeated failure in government exams",
            "problem_text": "Failed government exam three times",
            "actual_outcome": {
                "event": "exam_failure",
                "outcome_type": "delay",
                "description": "Exam failures during afflicted 6th house period.",
            },
            "ground_truth": {
                "planets": ["Saturn", "Rahu"],
                "houses": [6, 12],
                "dasha_lords": ["Saturn", "Rahu"],
                "transit_indicators": ["block"],
                "remedies": ["saturn_remedy", "6th_lord_remedy"],
                "consensus_outcome": "delayed_outcome",
            },
            "match_profile": "medium",
        },
    ],
    "business": [
        {
            "case_id": "business_001",
            "title": "Business partnership failure",
            "problem_text": "Business partnership dissolved with loss",
            "actual_outcome": {
                "event": "partnership_loss",
                "outcome_type": "loss",
                "description": "Partnership break during Mercury-Saturn dasha.",
            },
            "ground_truth": {
                "planets": ["Mercury", "Saturn", "Rahu"],
                "houses": [7, 8, 11],
                "dasha_lords": ["Mercury", "Saturn"],
                "transit_indicators": ["affliction"],
                "remedies": ["mercury_remedy", "saturn_remedy"],
                "consensus_outcome": "blocked_outcome",
            },
            "match_profile": "high",
        },
        {
            "case_id": "business_002",
            "title": "Successful business expansion",
            "problem_text": "Business expanded to new city",
            "actual_outcome": {
                "event": "business_growth",
                "outcome_type": "success",
                "description": "Expansion during Jupiter-Venus dasha.",
            },
            "ground_truth": {
                "planets": ["Jupiter", "Venus", "Mercury"],
                "houses": [2, 10, 11],
                "dasha_lords": ["Jupiter", "Venus"],
                "transit_indicators": ["support"],
                "remedies": ["jupiter_remedy", "venus_remedy"],
                "consensus_outcome": "strong_support",
            },
            "match_profile": "high",
        },
    ],
    "health": [
        {
            "case_id": "health_001",
            "title": "Chronic illness during 6th lord dasha",
            "problem_text": "Chronic health issues for 5 years",
            "actual_outcome": {
                "event": "chronic_disease",
                "outcome_type": "illness",
                "description": "Chronic condition during afflicted 6th house dasha.",
            },
            "ground_truth": {
                "planets": ["Saturn", "Mars", "Rahu"],
                "houses": [6, 8, 12],
                "dasha_lords": ["Saturn", "Mars"],
                "transit_indicators": ["affliction"],
                "remedies": ["saturn_remedy", "mars_remedy"],
                "consensus_outcome": "blocked_outcome",
            },
            "match_profile": "high",
        },
        {
            "case_id": "health_002",
            "title": "Surgery during Mars transit",
            "problem_text": "Emergency surgery required",
            "actual_outcome": {
                "event": "surgery",
                "outcome_type": "medical_event",
                "description": "Surgery during Mars transit over natal 8th lord.",
            },
            "ground_truth": {
                "planets": ["Mars", "Saturn"],
                "houses": [6, 8],
                "dasha_lords": ["Mars"],
                "transit_indicators": ["affliction", "block"],
                "remedies": ["mars_remedy"],
                "consensus_outcome": "blocked_outcome",
            },
            "match_profile": "medium",
        },
    ],
    "court_case": [
        {
            "case_id": "court_case_001",
            "title": "Prolonged litigation",
            "problem_text": "Court case pending for 12 years",
            "actual_outcome": {
                "event": "litigation",
                "outcome_type": "delay",
                "description": "Case delayed with Saturn-Rahu influence on 6th and 12th.",
            },
            "ground_truth": {
                "planets": ["Saturn", "Rahu"],
                "houses": [6, 12],
                "dasha_lords": ["Saturn", "Rahu"],
                "transit_indicators": ["sade_sati_phase", "block"],
                "remedies": ["saturn_remedy", "rahu_remedy"],
                "consensus_outcome": "delayed_outcome",
            },
            "match_profile": "high",
        },
        {
            "case_id": "court_case_002",
            "title": "Favorable court verdict",
            "problem_text": "Won court case after long battle",
            "actual_outcome": {
                "event": "court_victory",
                "outcome_type": "success",
                "description": "Verdict in favor during Jupiter antardasha.",
            },
            "ground_truth": {
                "planets": ["Jupiter", "Sun"],
                "houses": [6, 9, 11],
                "dasha_lords": ["Jupiter", "Sun"],
                "transit_indicators": ["support"],
                "remedies": ["jupiter_remedy"],
                "consensus_outcome": "moderate_support",
            },
            "match_profile": "medium",
        },
    ],
    "foreign_settlement": [
        {
            "case_id": "foreign_settlement_001",
            "title": "Foreign settlement via 9th-12th linkage",
            "problem_text": "Moved abroad for work",
            "actual_outcome": {
                "event": "foreign_relocation",
                "outcome_type": "success",
                "description": "Settlement abroad during Rahu dasha with 9th lord support.",
            },
            "ground_truth": {
                "planets": ["Rahu", "Jupiter", "Moon"],
                "houses": [9, 12],
                "dasha_lords": ["Rahu", "Jupiter"],
                "transit_indicators": ["support"],
                "remedies": ["rahu_remedy", "9th_lord_remedy"],
                "consensus_outcome": "strong_support",
            },
            "match_profile": "high",
        },
        {
            "case_id": "foreign_settlement_002",
            "title": "Visa rejection repeated",
            "problem_text": "Visa rejected multiple times",
            "actual_outcome": {
                "event": "visa_rejection",
                "outcome_type": "denial",
                "description": "Visa denials during afflicted 12th house period.",
            },
            "ground_truth": {
                "planets": ["Saturn", "Ketu"],
                "houses": [9, 12],
                "dasha_lords": ["Saturn", "Ketu"],
                "transit_indicators": ["block"],
                "remedies": ["saturn_remedy", "ketu_remedy"],
                "consensus_outcome": "blocked_outcome",
            },
            "match_profile": "low",
        },
    ],
    "wealth": [
        {
            "case_id": "wealth_001",
            "title": "Sudden financial loss",
            "problem_text": "Major financial loss in business",
            "actual_outcome": {
                "event": "financial_loss",
                "outcome_type": "loss",
                "description": "Loss during 8th lord dasha with Rahu transit.",
            },
            "ground_truth": {
                "planets": ["Rahu", "Saturn", "Mars"],
                "houses": [2, 8, 11],
                "dasha_lords": ["Rahu", "Saturn"],
                "transit_indicators": ["affliction", "block"],
                "remedies": ["rahu_remedy", "saturn_remedy"],
                "consensus_outcome": "blocked_outcome",
            },
            "match_profile": "high",
        },
        {
            "case_id": "wealth_002",
            "title": "Inheritance received",
            "problem_text": "Received family inheritance",
            "actual_outcome": {
                "event": "inheritance",
                "outcome_type": "gain",
                "description": "Inheritance during Jupiter dasha with 8th house activation.",
            },
            "ground_truth": {
                "planets": ["Jupiter", "Venus"],
                "houses": [2, 8, 11],
                "dasha_lords": ["Jupiter"],
                "transit_indicators": ["support"],
                "remedies": ["jupiter_remedy"],
                "consensus_outcome": "strong_support",
            },
            "match_profile": "high",
        },
    ],
    "raj_yoga": [
        {
            "case_id": "raj_yoga_001",
            "title": "Gaj Kesari yoga activation",
            "problem_text": "Rise to leadership position",
            "actual_outcome": {
                "event": "leadership_rise",
                "outcome_type": "success",
                "description": "Leadership role during Gaj Kesari yoga activation.",
            },
            "ground_truth": {
                "planets": ["Moon", "Jupiter", "Sun"],
                "houses": [1, 9, 10],
                "dasha_lords": ["Jupiter", "Moon"],
                "transit_indicators": ["support"],
                "remedies": ["jupiter_remedy", "moon_remedy"],
                "consensus_outcome": "strong_support",
            },
            "match_profile": "high",
        },
        {
            "case_id": "raj_yoga_002",
            "title": "Raj yoga blocked by Saturn",
            "problem_text": "Leadership opportunity missed",
            "actual_outcome": {
                "event": "missed_opportunity",
                "outcome_type": "delay",
                "description": "Raj yoga present but Saturn dasha delayed results.",
            },
            "ground_truth": {
                "planets": ["Saturn", "Sun", "Jupiter"],
                "houses": [10, 11],
                "dasha_lords": ["Saturn", "Sun"],
                "transit_indicators": ["sade_sati_phase"],
                "remedies": ["saturn_remedy", "sun_remedy"],
                "consensus_outcome": "delayed_outcome",
            },
            "match_profile": "medium",
        },
    ],
}


def build_synthetic_unified_report(
    ground_truth: dict[str, Any],
    *,
    match_profile: str = "high",
) -> dict[str, Any]:
    """Build a synthetic unified report aligned to ground truth at varying match levels."""
    planets = list(ground_truth.get("planets", []))
    houses = list(ground_truth.get("houses", []))
    dasha_lords = list(ground_truth.get("dasha_lords", []))
    transit_indicators = list(ground_truth.get("transit_indicators", []))
    remedies = list(ground_truth.get("remedies", []))
    consensus = ground_truth.get("consensus_outcome")

    if match_profile == "medium":
        planets = planets[: max(1, len(planets) - 1)]
        houses = houses[: max(1, len(houses) - 1)]
        remedies = remedies[: max(0, len(remedies) - 1)]
    elif match_profile == "low":
        planets = ["Mercury"]
        houses = [3]
        dasha_lords = ["Mercury"]
        transit_indicators = []
        remedies = []
        consensus = "mixed_signals"

    current: dict[str, Any] = {}
    if dasha_lords:
        current["mahadasha"] = {"lord": dasha_lords[0]}
    if len(dasha_lords) > 1:
        current["antardasha"] = {"lord": dasha_lords[1]}

    natal_impacts = [{"impact_type": indicator, "strength": 0.7} for indicator in transit_indicators]

    return {
        "version": "unified_report_v2",
        "astro_intelligence": {
            "root_cause_planets": planets,
            "affected_houses": houses,
            "confidence_score": 0.75,
        },
        "problem_analysis": {
            "category": {"category": "unknown"},
            "planets": {"primary": planets[:2], "shadow": planets[2:]},
            "houses": {"primary": houses[:1], "secondary": houses[1:]},
        },
        "dasha": {"current": current},
        "transits": {
            "saturn": {"planet": "Saturn", "natal_impacts": natal_impacts},
        },
        "remedy_recommendations": {
            "matched_remedies": [
                {
                    "remedy": {"remedy_id": remedy_id, "astrology_system": "vedic"},
                    "match_score": 0.75,
                }
                for remedy_id in remedies
            ]
        },
        "reasoning": {
            "consensus": {"final_consensus": consensus},
            "confidence": {"overall_score": 72 if match_profile == "high" else 48},
        },
    }


def build_category_dataset(category: str) -> dict[str, Any]:
    templates = CASE_TEMPLATES.get(category, [])
    cases = []
    for template in templates:
        case = dict(template)
        case["category"] = category
        case["source"] = "astrology_case_study"
        case["unified_report"] = build_synthetic_unified_report(
            case["ground_truth"],
            match_profile=case.get("match_profile", "high"),
        )
        cases.append(case)
    return {
        "category": category,
        "version": "1.0",
        "count": len(cases),
        "cases": cases,
    }


def build_all_benchmarks(root: Path | str | None = None) -> dict[str, int]:
    root_path = Path(root or Path(__file__).resolve().parents[2] / "benchmarks")
    root_path.mkdir(parents=True, exist_ok=True)

    counts: dict[str, int] = {}
    total = 0
    for category in BENCHMARK_CATEGORIES:
        dataset = build_category_dataset(category)
        file_path = root_path / f"{category}.json"
        file_path.write_text(json.dumps(dataset, indent=2), encoding="utf-8")
        counts[f"{category}.json"] = dataset["count"]
        total += dataset["count"]

    manifest = {
        "version": "1.0",
        "name": "AstroGuruAI Benchmark Dataset",
        "categories": list(BENCHMARK_CATEGORIES),
        "files": counts,
        "total_cases": total,
    }
    (root_path / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    counts["manifest.json"] = 0
    return counts


if __name__ == "__main__":
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    result = build_all_benchmarks(target)
    print(json.dumps(result, indent=2))
