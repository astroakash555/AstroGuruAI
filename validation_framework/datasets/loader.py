"""Benchmark dataset loader."""

from __future__ import annotations

import json
from pathlib import Path

from validation_framework.case_validation.validator import case_from_dict
from validation_framework.constants import BENCHMARK_CATEGORIES
from validation_framework.types import CaseStudy


class BenchmarkLoader:
    """Load benchmark case studies from JSON datasets."""

    def __init__(self, root: Path | str | None = None) -> None:
        self._root = Path(root or Path(__file__).resolve().parents[2] / "benchmarks")

    @property
    def root(self) -> Path:
        return self._root

    def load_manifest(self) -> dict:
        path = self._root / "manifest.json"
        if not path.exists():
            raise FileNotFoundError(f"Benchmark manifest not found at {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def load_category(self, category: str) -> tuple[CaseStudy, ...]:
        if category not in BENCHMARK_CATEGORIES:
            raise ValueError(f"Unknown benchmark category: {category}")
        path = self._root / f"{category}.json"
        if not path.exists():
            raise FileNotFoundError(f"Benchmark file not found: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        return tuple(case_from_dict(item) for item in payload.get("cases", []))

    def load_all(self) -> tuple[CaseStudy, ...]:
        cases: list[CaseStudy] = []
        for category in BENCHMARK_CATEGORIES:
            path = self._root / f"{category}.json"
            if not path.exists():
                continue
            cases.extend(self.load_category(category))
        return tuple(cases)

    def load_categories(self, categories: tuple[str, ...]) -> tuple[CaseStudy, ...]:
        cases: list[CaseStudy] = []
        for category in categories:
            cases.extend(self.load_category(category))
        return tuple(cases)
