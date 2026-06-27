"""Yoga Detection Engine orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from astrology_engine.core.types import LagnaKundali, VedicChartBundle
from astrology_engine.yogas.base import YogaRule
from astrology_engine.yogas.context import build_chart_context
from astrology_engine.yogas.registry import YogaRegistry
from astrology_engine.yogas.rules import DEFAULT_YOGA_RULES
from astrology_engine.yogas.serializer import to_json_dict, to_json_string
from astrology_engine.yogas.types import YogaDetectionResult, YogaDetectionSummary


class YogaDetectionEngine:
    """
    Pluggable yoga detection engine.

    Register custom `YogaRule` implementations to extend detection beyond defaults.
    """

    def __init__(self, registry: YogaRegistry | None = None) -> None:
        self._registry = registry or YogaRegistry()
        if not self._registry.rules():
            for rule in DEFAULT_YOGA_RULES:
                self._registry.register(rule)

    @property
    def registry(self) -> YogaRegistry:
        return self._registry

    def register_rule(self, rule: YogaRule) -> None:
        """Register an additional yoga rule at runtime."""
        self._registry.register(rule)

    def detect(self, chart: LagnaKundali | VedicChartBundle) -> YogaDetectionResult:
        """Run all registered yoga rules against a computed chart."""
        context = build_chart_context(chart)
        detections = self._registry.detect_all(context)
        present = tuple(yoga for yoga in detections if yoga.is_present)

        strengths = [yoga.strength for yoga in present]
        summary = YogaDetectionSummary(
            total_rules=len(detections),
            present_count=len(present),
            absent_count=len(detections) - len(present),
            average_strength=round(sum(strengths) / len(strengths), 3) if strengths else 0.0,
        )

        moon = context.get_planet("Moon")
        return YogaDetectionResult(
            detected_at=datetime.now(timezone.utc),
            lagna_sign=context.ascendant.sign.name_en,
            moon_sign=moon.sign.name_en,
            yogas=detections,
            present_yogas=present,
            summary=summary,
            metadata={
                "engine": "yoga_detection_v1",
                "rules_evaluated": len(detections),
                "expandable": True,
            },
        )

    def detect_json(self, chart: LagnaKundali | VedicChartBundle) -> dict[str, Any]:
        """Detect yogas and return structured JSON dictionary."""
        return to_json_dict(self.detect(chart))

    def detect_json_string(
        self,
        chart: LagnaKundali | VedicChartBundle,
        *,
        indent: int | None = 2,
    ) -> str:
        """Detect yogas and return formatted JSON string."""
        return to_json_string(self.detect(chart), indent=indent)
