"""Validation and benchmarking orchestrator."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from validation_framework.case_validation.validator import validate_case, validation_result_to_dict
from validation_framework.datasets.loader import BenchmarkLoader
from validation_framework.failed_cases.store import FailedCaseStore
from validation_framework.reports.generator import generate_validation_report, report_summary_dict
from validation_framework.retraining.recommendations import generate_retraining_recommendations
from validation_framework.serializers.serializer import to_json_dict, to_json_string
from validation_framework.types import CaseStudy, ValidationReport


class ValidationEngine:
    """
    Validation and benchmarking framework for AstroGuruAI.

    Compares actual life outcomes against system predictions,
    computes accuracy metrics, stores failures, and generates retraining recommendations.
    Output is structured JSON only.
    """

    def __init__(
        self,
        *,
        benchmark_root: Path | str | None = None,
        failed_cases_path: Path | str | None = None,
    ) -> None:
        self._loader = BenchmarkLoader(benchmark_root)
        self._failed_store = FailedCaseStore(failed_cases_path)

    @property
    def failed_case_store(self) -> FailedCaseStore:
        return self._failed_store

    def validate_case(self, case: CaseStudy):
        return validate_case(case)

    def run_benchmark(
        self,
        *,
        categories: tuple[str, ...] | None = None,
    ) -> ValidationReport:
        cases = (
            self._loader.load_categories(categories)
            if categories
            else self._loader.load_all()
        )
        return self._run_cases(cases)

    def run_cases(self, cases: tuple[CaseStudy, ...]) -> ValidationReport:
        return self._run_cases(cases)

    def run_benchmark_json(
        self,
        *,
        categories: tuple[str, ...] | None = None,
    ) -> dict[str, Any]:
        return to_json_dict(self.run_benchmark(categories=categories))

    def validate_case_json(self, case: CaseStudy) -> dict[str, Any]:
        return validation_result_to_dict(validate_case(case))

    def run_benchmark_json_string(
        self,
        *,
        categories: tuple[str, ...] | None = None,
        indent: int | None = 2,
    ) -> str:
        return to_json_string(self.run_benchmark(categories=categories), indent=indent)

    def _run_cases(self, cases: tuple[CaseStudy, ...]) -> ValidationReport:
        results = []
        failed_records = []

        for case in cases:
            result = validate_case(case)
            results.append(result)
            if not result.passed:
                failed_records.append(
                    self._failed_store.record_failure(result, case_snapshot={
                        "case_id": case.case_id,
                        "title": case.title,
                        "category": case.category,
                        "problem_text": case.problem_text,
                        "source": case.source,
                    })
                )

        manifest = {}
        try:
            manifest = self._loader.load_manifest()
        except FileNotFoundError:
            manifest = {"version": "1.0"}

        recommendations = generate_retraining_recommendations(tuple(results), tuple(failed_records))

        return generate_validation_report(
            case_results=tuple(results),
            failed_records=tuple(failed_records),
            retraining_recommendations=recommendations,
            dataset_version=manifest.get("version", "1.0"),
        )
