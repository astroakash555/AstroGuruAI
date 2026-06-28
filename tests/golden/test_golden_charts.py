"""Golden chart regression tests — Phase 16 astrology accuracy lockdown."""

from __future__ import annotations

import pytest

pytest.importorskip("swisseph")

from astrology_engine import VedicAstrologyEngine
from astrology_engine.dasha.serializer import to_json_dict
from tests.golden.helpers import build_birth_data, build_dasha_input_from_bundle
from tests.golden.comparator import (
    LONGITUDE_TOLERANCE,
    ChartComparisonResult,
    compare_chart,
)
from tests.golden.loader import (
    GoldenChartCase,
    list_golden_chart_ids,
    load_all_golden_charts,
    load_golden_chart,
    parse_reference_datetime,
)


@pytest.fixture(scope="module")
def engine() -> VedicAstrologyEngine:
    return VedicAstrologyEngine()


def _run_comparison(case: GoldenChartCase, engine: VedicAstrologyEngine) -> ChartComparisonResult:
    birth_data = build_birth_data(
        date_of_birth=case.input.date_of_birth,
        birth_time=case.input.birth_time,
        latitude=case.input.latitude,
        longitude=case.input.longitude,
        timezone_name=case.input.timezone,
    )
    bundle = engine.compute_chart(birth_data)
    dasha_input = build_dasha_input_from_bundle(
        bundle,
        birth_place=case.input.place,
        timezone=case.input.timezone,
    )
    reference_dt = parse_reference_datetime(case.expected["dasha"].get("reference_datetime"))
    dasha_result = engine.compute_vimshottari_dasha(dasha_input, reference_datetime=reference_dt)
    dasha_payload = to_json_dict(dasha_result)
    return compare_chart(case, bundle, dasha_payload)


def _format_failure(result: ChartComparisonResult) -> str:
    lines = [f"{result.chart_id} ({result.name}) mismatches:"]
    for mismatch in result.mismatches:
        delta = f", delta={mismatch.delta:.6f}" if mismatch.delta is not None else ""
        lines.append(
            f"  - [{mismatch.category}] {mismatch.field}: expected={mismatch.expected!r}, "
            f"actual={mismatch.actual!r}{delta}"
        )
    return "\n".join(lines)


@pytest.fixture(scope="module")
def golden_cases() -> list[GoldenChartCase]:
    cases = load_all_golden_charts()
    assert len(cases) >= 20, "Golden dataset must contain at least 20 charts"
    return cases


@pytest.mark.parametrize("chart_id", list_golden_chart_ids())
def test_golden_chart_matches_reference(chart_id: str, engine: VedicAstrologyEngine) -> None:
    """Every golden chart must match reference within strict tolerances."""
    case = load_golden_chart(chart_id)
    result = _run_comparison(case, engine)
    assert result.passed, _format_failure(result)


def test_golden_dataset_has_minimum_chart_count(golden_cases: list[GoldenChartCase]) -> None:
    assert len(golden_cases) >= 20


def test_golden_manifest_tolerances() -> None:
    from tests.golden.loader import load_manifest

    manifest = load_manifest()
    assert manifest["tolerances"]["longitude_degrees"] == LONGITUDE_TOLERANCE
    assert manifest["tolerances"]["ascendant_degrees"] == LONGITUDE_TOLERANCE
    assert manifest["tolerances"]["dasha_dates"] == "exact"


def test_poorvi_sharma_astrosage_verified(engine: VedicAstrologyEngine) -> None:
    """Poorvi Sharma is the externally verified AstroSage reference chart."""
    case = load_golden_chart("poorvi_sharma_2016")
    assert case.input.source == "astrosage"
    result = _run_comparison(case, engine)
    assert result.passed, _format_failure(result)

    asc = case.expected["ascendant"]
    assert asc["sign"] == "Libra"
    assert 187.0 <= asc["longitude"] <= 188.5
    assert case.expected["planets"]["Moon"]["nakshatra"] == "Hasta"
    assert case.expected["planets"]["Moon"]["pada"] == 4
    assert case.expected["dasha"]["current"]["mahadasha"] == "Rahu"
