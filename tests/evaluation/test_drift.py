"""Tests for historical output drift detection."""

from __future__ import annotations

import copy

from backend.app.services.evaluation.drift import detect_output_drift


class TestOutputDrift:
    def test_no_drift_for_identical_reports(
        self,
        sample_unified_report,
        baseline_unified_report,
    ) -> None:
        drift = detect_output_drift(sample_unified_report, baseline_unified_report)
        assert drift.drift_score == 0.0
        assert drift.is_drift_detected is False
        assert drift.changed_sections == ()

    def test_drift_detected_on_large_change(
        self,
        sample_unified_report,
        baseline_unified_report,
    ) -> None:
        current = copy.deepcopy(sample_unified_report)
        current["fusion"]["confidence"] = 0.10
        current["fusion"]["observations"] = []
        current["vedic"]["observations"] = []
        current["summary"]["reasoning_confidence_score"] = 20

        drift = detect_output_drift(current, baseline_unified_report, drift_threshold=0.10)
        assert drift.drift_score > 0.0
        assert drift.is_drift_detected is True
        assert len(drift.changed_sections) >= 1

    def test_drift_handles_missing_sections(self) -> None:
        drift = detect_output_drift({"fusion": {}}, {"fusion": {}})
        assert drift.drift_score == 0.0

    def test_drift_skips_invalid_observation_items(self) -> None:
        drift = detect_output_drift(
            {"vedic": {"observations": ["bad", {"category": "x"}]}},
            {"vedic": {"observations": []}},
        )
        assert "vedic" in drift.details["section_details"]

    def test_drift_relative_delta_from_zero_baseline(self) -> None:
        drift = detect_output_drift(
            {"vedic": {"observations": [{"category": "a"}]}},
            {"vedic": {"observations": []}},
        )
        assert drift.details["section_details"]["vedic"]["observation_delta"] == 1.0

    def test_drift_summary_confidence_normalization(self) -> None:
        drift = detect_output_drift(
            {"summary": {"reasoning_confidence_score": 50}},
            {"summary": {"reasoning_confidence_score": 90}},
        )
        assert drift.details["section_details"]["summary"]["confidence_delta"] > 0

    def test_drift_skips_non_dict_sections(self) -> None:
        drift = detect_output_drift({"vedic": "invalid"}, {"vedic": {}})
        assert "vedic" not in drift.details["section_details"]

    def test_normalize_summary_confidence_helpers(self) -> None:
        from backend.app.services.evaluation.drift import _normalize_summary_confidence

        assert _normalize_summary_confidence(None) == 0.0
        assert _normalize_summary_confidence(85) == 0.85
        assert _normalize_summary_confidence(0.75) == 0.75

    def test_drift_category_distribution_change(
        self,
        sample_unified_report,
        baseline_unified_report,
    ) -> None:
        current = copy.deepcopy(sample_unified_report)
        current["vedic"]["observations"] = [
            {
                "observation_id": "v2",
                "title": "Different",
                "category": "yoga",
                "affected_planets": [],
                "affected_houses": [],
                "severity": 0.5,
                "confidence": 0.5,
            }
        ]
        drift = detect_output_drift(current, baseline_unified_report)
        assert drift.details["section_details"]["vedic"]["category_delta"] > 0
