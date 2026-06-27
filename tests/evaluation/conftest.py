"""Shared fixtures for intelligence evaluation tests."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

GENERATED_AT = datetime(2026, 6, 20, 12, 0, 0, tzinfo=timezone.utc)


def observation(
    *,
    observation_id: str,
    title: str,
    category: str,
    planets: tuple[str, ...],
    houses: tuple[int, ...],
    severity: float,
    confidence: float,
) -> dict:
    return {
        "observation_id": observation_id,
        "category": category,
        "title": title,
        "explanation": f"{title} explanation.",
        "affected_planets": list(planets),
        "affected_houses": list(houses),
        "severity": severity,
        "confidence": confidence,
        "metadata": {},
    }


def fused_observation(
    *,
    fusion_id: str,
    title: str,
    planets: tuple[str, ...],
    houses: tuple[int, ...],
    severity: float,
    confidence: float,
    engines: tuple[str, ...],
    has_conflict: bool = False,
) -> dict:
    return {
        "fusion_id": fusion_id,
        "title": title,
        "explanation": f"{title} fused explanation.",
        "category": "fusion:multi_engine",
        "affected_planets": list(planets),
        "affected_houses": list(houses),
        "severity": severity,
        "confidence": confidence,
        "supporting_engines": list(engines),
        "rank_score": 0.82,
        "has_conflict": has_conflict,
    }


@pytest.fixture
def sample_observations_by_engine() -> dict[str, tuple]:
    from backend.app.services.evaluation.models import observation_from_dict

    payloads = {
        "vedic": (
            observation(
                observation_id="vedic-mars-1",
                title="Strong Mars in Lagna",
                category="strength",
                planets=("Mars",),
                houses=(1,),
                severity=0.82,
                confidence=0.91,
            ),
        ),
        "kp": (
            observation(
                observation_id="kp-mars-1",
                title="Strong Mars in Lagna",
                category="significator",
                planets=("Mars",),
                houses=(1,),
                severity=0.78,
                confidence=0.88,
            ),
        ),
        "lal_kitab": (
            observation(
                observation_id="lk-venus-1",
                title="Venus Debt Indicator",
                category="rin",
                planets=("Venus",),
                houses=(7,),
                severity=0.70,
                confidence=0.85,
            ),
        ),
    }
    return {
        engine: tuple(observation_from_dict(engine, item) for item in items)
        for engine, items in payloads.items()
    }


@pytest.fixture
def sample_fusion() -> dict:
    return {
        "analyzed_at": GENERATED_AT.isoformat(),
        "confidence": 0.86,
        "root_causes": [
            {
                "title": "Mars Lagna Influence",
                "explanation": "Mars dominates the chart lagna.",
                "supporting_observations": ("fusion-0001-strongmarsinlagna",),
                "supporting_engines": ["vedic", "kp"],
                "confidence": 0.89,
            }
        ],
        "conflicts": [],
        "recommendations": [
            {
                "recommendation_id": "rec-1",
                "title": "Strengthen Mars Remedies",
                "explanation": "Apply Mars balancing remedies.",
                "priority": "high",
                "supporting_root_causes": ("Mars Lagna Influence",),
                "confidence": 0.87,
            }
        ],
        "observations": [
            fused_observation(
                fusion_id="fusion-0001-strongmarsinlagna",
                title="Strong Mars in Lagna",
                planets=("Mars",),
                houses=(1,),
                severity=0.80,
                confidence=0.90,
                engines=("vedic", "kp"),
            )
        ],
        "metadata": {"engine": "intelligence_fusion_v1"},
    }


@pytest.fixture
def sample_unified_report(sample_fusion) -> dict:
    return {
        "generated_at": GENERATED_AT.isoformat(),
        "version": "unified_report_v2",
        "vedic": {
            "metadata": {"engine": "vedic_intelligence_v1"},
            "observations": [
                observation(
                    observation_id="vedic-mars-1",
                    title="Strong Mars in Lagna",
                    category="strength",
                    planets=("Mars",),
                    houses=(1,),
                    severity=0.82,
                    confidence=0.91,
                )
            ],
        },
        "kp": {
            "metadata": {"engine": "kp_intelligence_v1"},
            "observations": [
                observation(
                    observation_id="kp-mars-1",
                    title="Strong Mars in Lagna",
                    category="significator",
                    planets=("Mars",),
                    houses=(1,),
                    severity=0.78,
                    confidence=0.88,
                )
            ],
            "event_timing": [],
        },
        "lal_kitab_intelligence": {
            "metadata": {"engine": "lal_kitab_intelligence_v1"},
            "observations": [
                observation(
                    observation_id="lk-venus-1",
                    title="Venus Debt Indicator",
                    category="rin",
                    planets=("Venus",),
                    houses=(7,),
                    severity=0.70,
                    confidence=0.85,
                )
            ],
            "remedies": [],
        },
        "fusion": sample_fusion,
        "astro_intelligence": {
            "severity_score": 0.72,
            "confidence_score": 0.86,
            "recommended_remedies": [
                {
                    "remedy_id": "vedic_mars_hanuman_worship",
                    "title": "Hanuman Worship for Mars",
                    "explanation": "Balance Mars through Hanuman worship.",
                }
            ],
        },
        "remedy_recommendations": {
            "matched_remedies": [
                {
                    "remedy": {"remedy_id": "vedic_mars_hanuman_worship"},
                    "match_score": 0.84,
                }
            ],
            "metadata": {"engine": "remedy_engine_v1"},
        },
        "summary": {
            "reasoning_confidence_score": 86,
            "intelligence_severity_score": 0.72,
        },
    }


@pytest.fixture
def baseline_unified_report(sample_unified_report) -> dict:
    return sample_unified_report
