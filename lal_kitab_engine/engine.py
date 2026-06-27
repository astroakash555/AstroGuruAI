"""Lal Kitab analysis engine."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from astrology_engine.core.types import LagnaKundali, VedicChartBundle
from lal_kitab_engine.analyzers.planet_house import analyze_planet_by_house
from lal_kitab_engine.context import build_lal_kitab_context
from lal_kitab_engine.registry import LalKitabRegistry
from lal_kitab_engine.rules import DEFAULT_LAL_KITAB_RULES, DOSH_RULES, RECOMMENDATION_RULES, RIN_RULES
from lal_kitab_engine.serializers.serializer import to_json_dict, to_json_string
from lal_kitab_engine.types import LalKitabAnalysisResult, LalKitabFinding, LalKitabSummary


class LalKitabEngine:
    """Production-grade Lal Kitab analysis engine with extensible rule registry."""

    def __init__(self, registry: LalKitabRegistry | None = None) -> None:
        self._registry = registry or LalKitabRegistry()
        if not self._registry.rules:
            for rule in DEFAULT_LAL_KITAB_RULES:
                self._registry.register(rule)

    @property
    def registry(self) -> LalKitabRegistry:
        return self._registry

    def analyze(self, chart: LagnaKundali | VedicChartBundle) -> LalKitabAnalysisResult:
        context = build_lal_kitab_context(chart)
        planet_by_house = analyze_planet_by_house(context)
        findings = self._registry.analyze_all(context)

        rin_findings = _filter_category(findings, "lal_kitab_rin")
        dosh_findings = _filter_category(findings, "lal_kitab_dosh")
        recommendations = _filter_category(findings, "lal_kitab_recommendation", present_only=True)

        present = tuple(item for item in findings if item.is_present)
        strengths = [item.strength for item in present]

        summary = LalKitabSummary(
            total_rules=len(findings),
            present_count=len(present),
            absent_count=len(findings) - len(present),
            average_strength=round(sum(strengths) / len(strengths), 3) if strengths else 0.0,
            rin_count=sum(1 for item in rin_findings if item.is_present),
            dosh_count=sum(1 for item in dosh_findings if item.is_present),
        )

        return LalKitabAnalysisResult(
            analyzed_at=datetime.now(timezone.utc),
            lagna_sign=context.lagna_sign,
            planet_by_house=planet_by_house,
            rin_findings=rin_findings,
            dosh_findings=dosh_findings,
            recommendations=recommendations,
            summary=summary,
            metadata={
                "engine": "lal_kitab_engine_v1",
                "ai_interpretation": False,
                "rule_ids": [rule.finding_id for rule in self._registry.rules],
            },
        )

    def analyze_json(self, chart: LagnaKundali | VedicChartBundle) -> dict[str, Any]:
        return to_json_dict(self.analyze(chart))

    def analyze_json_string(self, chart: LagnaKundali | VedicChartBundle, *, indent: int | None = 2) -> str:
        return to_json_string(self.analyze(chart), indent=indent)


def _filter_category(
    findings: tuple[LalKitabFinding, ...],
    category: str,
    *,
    present_only: bool = False,
) -> tuple[LalKitabFinding, ...]:
    return tuple(
        item
        for item in findings
        if item.category == category and (not present_only or item.is_present)
    )
