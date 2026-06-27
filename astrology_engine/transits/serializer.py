"""Serialize transit analysis to JSON."""

from __future__ import annotations

from typing import Any

from astrology_engine.transits.schemas import TransitAnalysisJSON
from astrology_engine.transits.types import (
    DailyTransitResult,
    MonthlyTransitResult,
    TransitAnalysisResult,
    TransitPlanetAnalysis,
    TransitPlanetSnapshot,
    YearlyTransitResult,
)


def _snapshot_dict(snapshot: TransitPlanetSnapshot) -> dict[str, Any]:
    return {
        "planet": snapshot.planet,
        "datetime": snapshot.datetime,
        "longitude": snapshot.longitude,
        "sign": {
            "index": snapshot.sign.index,
            "name_en": snapshot.sign.name_en,
            "name_sa": snapshot.sign.name_sa,
            "lord": snapshot.sign.lord,
            "degree_in_sign": snapshot.sign.degree_in_sign,
        },
        "house_from_lagna": snapshot.house_from_lagna,
        "house_from_moon": snapshot.house_from_moon,
        "is_retrograde": snapshot.is_retrograde,
        "nakshatra": {
            "index": snapshot.nakshatra.index,
            "name": snapshot.nakshatra.name,
            "lord": snapshot.nakshatra.lord,
            "pada": snapshot.nakshatra.pada,
        },
        "speed": snapshot.speed,
    }


def _analysis_dict(analysis: TransitPlanetAnalysis) -> dict[str, Any]:
    return {
        "planet": analysis.planet,
        "theme": analysis.theme,
        "current": _snapshot_dict(analysis.current) if analysis.current else None,
        "sign_changes": [
            {
                "planet": event.planet,
                "datetime": event.datetime,
                "from_sign": event.from_sign,
                "to_sign": event.to_sign,
                "from_house_lagna": event.from_house_lagna,
                "to_house_lagna": event.to_house_lagna,
            }
            for event in analysis.sign_changes
        ],
        "natal_impacts": [
            {
                "impact_type": impact.impact_type,
                "description": impact.description,
                "strength": impact.strength,
                "target": impact.target,
                "house_from_lagna": impact.house_from_lagna,
                "house_from_moon": impact.house_from_moon,
            }
            for impact in analysis.natal_impacts
        ],
        "highlights": list(analysis.highlights),
    }


def _daily_dict(daily: DailyTransitResult) -> dict[str, Any]:
    return {
        "date": daily.date,
        "snapshots": [_snapshot_dict(item) for item in daily.snapshots],
        "analyses": [_analysis_dict(item) for item in daily.analyses],
    }


def _monthly_dict(monthly: MonthlyTransitResult) -> dict[str, Any]:
    return {
        "year": monthly.year,
        "month": monthly.month,
        "period_start": monthly.period_start,
        "period_end": monthly.period_end,
        "sign_changes": [
            {
                "planet": event.planet,
                "datetime": event.datetime,
                "from_sign": event.from_sign,
                "to_sign": event.to_sign,
                "from_house_lagna": event.from_house_lagna,
                "to_house_lagna": event.to_house_lagna,
            }
            for event in monthly.sign_changes
        ],
        "analyses": [_analysis_dict(item) for item in monthly.analyses],
        "highlights": list(monthly.highlights),
    }


def _yearly_dict(yearly: YearlyTransitResult) -> dict[str, Any]:
    return {
        "year": yearly.year,
        "period_start": yearly.period_start,
        "period_end": yearly.period_end,
        "sign_changes": [
            {
                "planet": event.planet,
                "datetime": event.datetime,
                "from_sign": event.from_sign,
                "to_sign": event.to_sign,
                "from_house_lagna": event.from_house_lagna,
                "to_house_lagna": event.to_house_lagna,
            }
            for event in yearly.sign_changes
        ],
        "monthly_highlights": list(yearly.monthly_highlights),
        "analyses": [_analysis_dict(item) for item in yearly.analyses],
        "highlights": list(yearly.highlights),
    }


def to_json_dict(result: TransitAnalysisResult) -> dict[str, Any]:
    payload = TransitAnalysisJSON(
        computed_at=result.computed_at,
        natal_lagna_sign=result.natal_lagna_sign,
        natal_moon_sign=result.natal_moon_sign,
        daily=_daily_dict(result.daily) if result.daily else None,
        monthly=_monthly_dict(result.monthly) if result.monthly else None,
        yearly=_yearly_dict(result.yearly) if result.yearly else None,
        saturn=_analysis_dict(result.saturn),
        jupiter=_analysis_dict(result.jupiter),
        rahu=_analysis_dict(result.rahu),
        ketu=_analysis_dict(result.ketu),
        metadata=dict(result.metadata),
    )
    return payload.model_dump(mode="json")


def to_json_string(result: TransitAnalysisResult, *, indent: int | None = 2) -> str:
    import json

    return json.dumps(to_json_dict(result), indent=indent, ensure_ascii=False)
