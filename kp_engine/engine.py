"""KP astrology analysis engine."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from astrology_engine.core.types import VedicChartBundle
from kp_engine.cusps.calculator import analyze_cusps
from kp_engine.event.framework import analyze_events
from kp_engine.serializers.serializer import to_json_dict, to_json_string
from kp_engine.significators.analyzer import analyze_significators
from kp_engine.star_lord.analyzer import analyze_star_lords
from kp_engine.sub_lord.analyzer import analyze_sub_lords
from kp_engine.types import KPAnalysisResult, KPAnalysisSummary


class KPEngine:
    """Production-grade KP astrology analysis engine."""

    def analyze(self, chart: VedicChartBundle) -> KPAnalysisResult:
        cusps = analyze_cusps(chart)
        significators = analyze_significators(chart)
        star_lords = analyze_star_lords(chart.lagna_kundali.planets)
        sub_lords = analyze_sub_lords(chart.lagna_kundali.planets)
        events = analyze_events(cusps, significators)

        supported = sum(1 for event in events if event.is_supported)
        summary = KPAnalysisSummary(
            total_cusps=len(cusps),
            total_significator_sets=len(significators),
            supported_events=supported,
            total_events=len(events),
        )

        return KPAnalysisResult(
            analyzed_at=datetime.now(timezone.utc),
            lagna_sign=chart.lagna_kundali.ascendant.sign.name_en,
            cusps=cusps,
            significators=significators,
            star_lords=star_lords,
            sub_lords=sub_lords,
            events=events,
            summary=summary,
            metadata={
                "engine": "kp_engine_v1",
                "ai_interpretation": False,
                "event_framework": "structured_v1",
            },
        )

    def analyze_json(self, chart: VedicChartBundle) -> dict[str, Any]:
        return to_json_dict(self.analyze(chart))

    def analyze_json_string(self, chart: VedicChartBundle, *, indent: int | None = 2) -> str:
        return to_json_string(self.analyze(chart), indent=indent)
