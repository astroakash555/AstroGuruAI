"""Tests for regression comparison between report JSON payloads."""

from __future__ import annotations

import copy

from backend.app.services.evaluation.regression import compare_reports


class TestRegressionComparison:
    def test_no_regression_for_identical_reports(
        self,
        sample_unified_report,
        baseline_unified_report,
    ) -> None:
        report = compare_reports(baseline_unified_report, sample_unified_report)
        assert report.regression_score == 1.0
        assert report.has_regression is False
        assert report.regressions == ()

    def test_regression_detected_on_confidence_drop(
        self,
        sample_unified_report,
        baseline_unified_report,
    ) -> None:
        candidate = copy.deepcopy(sample_unified_report)
        candidate["fusion"]["confidence"] = 0.20
        candidate["summary"]["reasoning_confidence_score"] = 20

        report = compare_reports(baseline_unified_report, candidate)
        assert report.has_regression is True
        assert report.regression_score < 1.0
        assert len(report.regressions) >= 1

    def test_regression_detected_on_observation_loss(
        self,
        sample_unified_report,
        baseline_unified_report,
    ) -> None:
        candidate = copy.deepcopy(sample_unified_report)
        candidate["vedic"]["observations"] = []
        candidate["kp"]["observations"] = []

        report = compare_reports(baseline_unified_report, candidate, regression_tolerance=0.01)
        assert report.has_regression is True

    def test_improvements_recorded(
        self,
        sample_unified_report,
        baseline_unified_report,
    ) -> None:
        candidate = copy.deepcopy(sample_unified_report)
        candidate["fusion"]["confidence"] = 0.95
        candidate["fusion"]["observations"].append(
            {
                "fusion_id": "fusion-0002",
                "title": "Extra",
                "confidence": 0.9,
                "severity": 0.8,
                "supporting_engines": ["vedic"],
            }
        )

        report = compare_reports(baseline_unified_report, candidate)
        assert len(report.improvements) >= 1

    def test_conflict_regression(self, sample_unified_report, baseline_unified_report) -> None:
        candidate = copy.deepcopy(sample_unified_report)
        candidate["fusion"]["conflicts"] = [{"conflict_id": "c1"}, {"conflict_id": "c2"}]

        report = compare_reports(baseline_unified_report, candidate)
        conflict_regressions = [item for item in report.regressions if item["field"] == "conflicts"]
        assert len(conflict_regressions) == 1

    def test_regression_summary_field_lookup(self) -> None:
        report = compare_reports(
            {"summary": {"reasoning_confidence_score": 80}},
            {"summary": {"reasoning_confidence_score": 40}},
            regression_tolerance=0.01,
        )
        assert report.has_regression is True

    def test_extract_metric_handles_invalid_sections(self) -> None:
        report = compare_reports(
            {"vedic": "invalid", "summary": "invalid"},
            {"vedic": {"observations": []}, "summary": {}},
        )
        assert report.regression_score <= 1.0
