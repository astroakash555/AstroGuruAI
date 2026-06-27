"""Serialize KP analysis to JSON."""

from __future__ import annotations

from typing import Any

from kp_engine.serializers.schemas import KPAnalysisJSON
from kp_engine.types import (
    CuspalPoint,
    EventAnalysis,
    KPAnalysisResult,
    SignificatorSet,
    StarLordAnalysis,
    SubLordAnalysis,
)


def _cusp_dict(item: CuspalPoint) -> dict[str, Any]:
    return {
        "house": item.house,
        "longitude": item.longitude,
        "sign": item.sign,
        "star_lord": item.star_lord,
        "sub_lord": item.sub_lord,
    }


def _significator_dict(item: SignificatorSet) -> dict[str, Any]:
    return {
        "house": item.house,
        "level_a": list(item.level_a),
        "level_b": list(item.level_b),
        "level_c": list(item.level_c),
        "level_d": list(item.level_d),
        "combined": list(item.combined),
    }


def _star_lord_dict(item: StarLordAnalysis) -> dict[str, Any]:
    return {
        "planet": item.planet,
        "longitude": item.longitude,
        "nakshatra": item.nakshatra,
        "star_lord": item.star_lord,
        "house": item.house,
    }


def _sub_lord_dict(item: SubLordAnalysis) -> dict[str, Any]:
    return {
        "planet": item.planet,
        "longitude": item.longitude,
        "nakshatra": item.nakshatra,
        "star_lord": item.star_lord,
        "sub_lord": item.sub_lord,
        "house": item.house,
    }


def _event_dict(item: EventAnalysis) -> dict[str, Any]:
    return {
        "event_id": item.event_id,
        "event_type": item.event_type,
        "target_houses": list(item.target_houses),
        "is_supported": item.is_supported,
        "support_score": item.support_score,
        "significators_matched": list(item.significators_matched),
        "cusp_sub_lords_matched": list(item.cusp_sub_lords_matched),
        "evidence": list(item.evidence),
    }


def to_json_dict(result: KPAnalysisResult) -> dict[str, Any]:
    payload = KPAnalysisJSON(
        analyzed_at=result.analyzed_at,
        lagna_sign=result.lagna_sign,
        cusps=[_cusp_dict(item) for item in result.cusps],
        significators=[_significator_dict(item) for item in result.significators],
        star_lords=[_star_lord_dict(item) for item in result.star_lords],
        sub_lords=[_sub_lord_dict(item) for item in result.sub_lords],
        events=[_event_dict(item) for item in result.events],
        summary={
            "total_cusps": result.summary.total_cusps,
            "total_significator_sets": result.summary.total_significator_sets,
            "supported_events": result.summary.supported_events,
            "total_events": result.summary.total_events,
        },
        metadata=dict(result.metadata),
    )
    return payload.model_dump(mode="json")


def to_json_string(result: KPAnalysisResult, *, indent: int | None = 2) -> str:
    import json

    return json.dumps(to_json_dict(result), indent=indent, ensure_ascii=False)
