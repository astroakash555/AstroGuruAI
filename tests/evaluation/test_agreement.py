"""Tests for cross-engine agreement metrics."""

from __future__ import annotations

from backend.app.services.evaluation.agreement import (
    compute_cross_engine_agreement,
    focus_signature,
    normalize_title,
)
from backend.app.services.evaluation.models import observation_from_dict


class TestCrossEngineAgreement:
    def test_agreement_detects_shared_focus(self, sample_observations_by_engine) -> None:
        metric = compute_cross_engine_agreement(sample_observations_by_engine)
        assert metric.metric_id == "cross_engine_agreement"
        assert metric.score > 0.0
        assert metric.details["multi_engine_clusters"] >= 1

    def test_agreement_empty_observations(self) -> None:
        metric = compute_cross_engine_agreement({})
        assert metric.score == 0.0
        assert metric.details["cluster_count"] == 0

    def test_agreement_single_engine_only(self) -> None:
        metric = compute_cross_engine_agreement(
            {
                "vedic": (
                    observation_from_dict(
                        "vedic",
                        {
                            "observation_id": "v1",
                            "title": "Unique Observation",
                            "category": "test",
                            "affected_planets": ["Sun"],
                            "affected_houses": [5],
                            "severity": 0.7,
                            "confidence": 0.8,
                        },
                    ),
                )
            }
        )
        assert metric.score == 0.0

    def test_focus_signature_and_title_normalizer(self) -> None:
        snapshot = observation_from_dict(
            "vedic",
            {
                "observation_id": "v1",
                "title": "Strong Mars in Lagna!",
                "category": "test",
                "affected_planets": ["Mars"],
                "affected_houses": [1],
            },
        )
        assert focus_signature(snapshot)[2] == normalize_title("Strong Mars in Lagna")
