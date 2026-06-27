"""Tests for confidence calibration metrics."""

from __future__ import annotations

from backend.app.services.evaluation.confidence import compute_confidence_calibration


class TestConfidenceCalibration:
    def test_calibration_with_fusion_observations(
        self,
        sample_fusion,
        sample_observations_by_engine,
    ) -> None:
        metric = compute_confidence_calibration(sample_fusion, sample_observations_by_engine)
        assert metric.metric_id == "confidence_calibration"
        assert 0.0 <= metric.score <= 1.0
        assert metric.details["sample_count"] >= 1

    def test_calibration_falls_back_to_engine_observations(
        self,
        sample_observations_by_engine,
    ) -> None:
        metric = compute_confidence_calibration({}, sample_observations_by_engine)
        assert metric.details["sample_count"] == 3

    def test_calibration_empty_inputs(self) -> None:
        metric = compute_confidence_calibration({}, {})
        assert metric.score == 0.0
        assert metric.details["sample_count"] == 0

    def test_calibration_conflict_observation(self, sample_observations_by_engine) -> None:
        fusion = {
            "observations": [
                {
                    "fusion_id": "f1",
                    "confidence": 0.95,
                    "severity": 0.90,
                    "supporting_engines": ["vedic"],
                    "has_conflict": True,
                }
            ]
        }
        metric = compute_confidence_calibration(fusion, sample_observations_by_engine)
        assert metric.details["sample_count"] == 1
