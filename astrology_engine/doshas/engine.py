"""Dosha Detection Engine orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from astrology_engine.core.types import LagnaKundali, VedicChartBundle
from astrology_engine.doshas.base import DoshaRule
from astrology_engine.doshas.registry import DoshaRegistry
from astrology_engine.doshas.rules import DEFAULT_DOSHA_RULES
from astrology_engine.doshas.serializer import to_json_dict, to_json_string
from astrology_engine.doshas.types import DoshaDetectionResult, DoshaDetectionSummary
from astrology_engine.yogas.context import build_chart_context


class DoshaDetectionEngine:
    """
    Pluggable dosha detection engine.

    Register custom `DoshaRule` implementations to extend detection beyond defaults.
    """

    def __init__(self, registry: DoshaRegistry | None = None) -> None:
        self._registry = registry or DoshaRegistry()
        if not self._registry.rules():
            for rule in DEFAULT_DOSHA_RULES:
                self._registry.register(rule)

    @property
    def registry(self) -> DoshaRegistry:
        return self._registry

    def register_rule(self, rule: DoshaRule) -> None:
        """Register an additional dosha rule at runtime."""
        self._registry.register(rule)

    def detect(self, chart: LagnaKundali | VedicChartBundle) -> DoshaDetectionResult:
        """Run all registered dosha rules against a computed chart."""
        context = build_chart_context(chart)
        detections = self._registry.detect_all(context)
        present = tuple(dosha for dosha in detections if dosha.is_present)

        severities = [dosha.severity for dosha in present]
        summary = DoshaDetectionSummary(
            total_rules=len(detections),
            present_count=len(present),
            absent_count=len(detections) - len(present),
            average_severity=round(sum(severities) / len(severities), 3) if severities else 0.0,
            highest_severity=max(severities) if severities else 0.0,
        )

        moon = context.get_planet("Moon")
        return DoshaDetectionResult(
            detected_at=datetime.now(timezone.utc),
            lagna_sign=context.ascendant.sign.name_en,
            moon_sign=moon.sign.name_en,
            doshas=detections,
            present_doshas=present,
            summary=summary,
            metadata={
                "engine": "dosha_detection_v1",
                "rules_evaluated": len(detections),
                "expandable": True,
                "remedies_generated": False,
            },
        )

    def detect_json(self, chart: LagnaKundali | VedicChartBundle) -> dict[str, Any]:
        """Detect doshas and return structured JSON dictionary."""
        return to_json_dict(self.detect(chart))

    def detect_json_string(
        self,
        chart: LagnaKundali | VedicChartBundle,
        *,
        indent: int | None = 2,
    ) -> str:
        """Detect doshas and return formatted JSON string."""
        return to_json_string(self.detect(chart), indent=indent)
