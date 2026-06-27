"""Validation framework unit tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from validation_framework import ValidationEngine, build_all_benchmarks
from validation_framework.case_validation.validator import case_from_dict, validate_case
from validation_framework.datasets.loader import BenchmarkLoader
from validation_framework.metrics.accuracy import compute_accuracy_metrics
from validation_framework.metrics.comparison import extract_system_prediction
from validation_framework.types import GroundTruth


@pytest.fixture(scope="module")
def benchmark_root(tmp_path_factory):
    root = tmp_path_factory.mktemp("benchmarks")
    build_all_benchmarks(root)
    return root


def test_build_benchmark_datasets(benchmark_root):
    manifest = json.loads((benchmark_root / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["total_cases"] >= 20
    assert len(manifest["categories"]) == 10
    assert (benchmark_root / "marriage.json").exists()
    assert (benchmark_root / "raj_yoga.json").exists()


def test_case_validation_match_percentage(benchmark_root):
    loader = BenchmarkLoader(benchmark_root)
    case = loader.load_category("marriage")[0]
    result = validate_case(case)

    assert result.case_id
    assert result.actual_outcome
    assert result.system_prediction
    assert 0 <= result.match_percentage <= 100
    assert result.accuracy_metrics.planet_accuracy >= 0
    assert result.comparison_details["planets"]["matched"]


def test_accuracy_metrics_computation():
    ground_truth = GroundTruth(
        planets=("Saturn", "Mars", "Venus"),
        houses=(7, 8),
        dasha_lords=("Saturn", "Venus"),
        transit_indicators=("sade_sati_phase",),
        remedies=("vedic_saturn_shani_mantra",),
        consensus_outcome="delayed_outcome",
    )
    prediction = extract_system_prediction(
        {
            "astro_intelligence": {"root_cause_planets": ["Saturn", "Mars"], "affected_houses": [7]},
            "problem_analysis": {"planets": {"primary": ["Venus"]}, "houses": {"secondary": [8]}},
            "dasha": {"current": {"mahadasha": {"lord": "Saturn"}, "antardasha": {"lord": "Venus"}}},
            "transits": {"saturn": {"natal_impacts": [{"impact_type": "sade_sati_phase"}]}},
            "remedy_recommendations": {
                "matched_remedies": [
                    {"remedy": {"remedy_id": "vedic_saturn_shani_mantra"}, "match_score": 0.8}
                ]
            },
            "reasoning": {
                "consensus": {"final_consensus": "delayed_outcome"},
                "confidence": {"overall_score": 70},
            },
        }
    )
    metrics = compute_accuracy_metrics(ground_truth, prediction)
    assert metrics.planet_accuracy == 1.0
    assert metrics.house_accuracy == 1.0
    assert metrics.overall_match_percentage >= 80


def test_run_benchmark_report(benchmark_root, tmp_path):
    engine = ValidationEngine(
        benchmark_root=benchmark_root,
        failed_cases_path=tmp_path / "failed_cases.json",
    )
    payload = engine.run_benchmark_json()

    assert payload["total_cases"] >= 20
    assert payload["aggregate_metrics"]["overall_match_percentage"] >= 0
    assert "case_results" in payload
    assert payload["metadata"]["ai_prediction"] is False
    assert json.dumps(payload)


def test_failed_cases_stored(benchmark_root, tmp_path):
    engine = ValidationEngine(
        benchmark_root=benchmark_root,
        failed_cases_path=tmp_path / "failed.json",
    )
    report = engine.run_benchmark()
    if report.failed_cases:
        assert engine.failed_case_store.all_failures()
        assert (tmp_path / "failed.json").exists()


def test_retraining_recommendations_generated(benchmark_root):
    payload = ValidationEngine(benchmark_root=benchmark_root).run_benchmark_json()
    assert isinstance(payload["retraining_recommendations"], list)
    if payload["failed_cases"] > 0:
        assert payload["retraining_recommendations"]


def test_validation_json_contract(benchmark_root):
    payload = ValidationEngine(benchmark_root=benchmark_root).run_benchmark_json()
    required = {
        "report_id",
        "generated_at",
        "total_cases",
        "passed_cases",
        "failed_cases",
        "aggregate_metrics",
        "case_results",
        "failed_case_records",
        "retraining_recommendations",
        "metadata",
    }
    assert required.issubset(payload.keys())
