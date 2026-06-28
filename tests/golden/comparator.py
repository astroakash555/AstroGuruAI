"""Compare engine output against golden chart reference expectations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from astrology_engine.core.types import Ascendant, PlanetPosition, VedicChartBundle
from tests.golden.loader import GoldenChartCase, parse_reference_datetime

LONGITUDE_TOLERANCE = 0.01
DEGREE_IN_SIGN_TOLERANCE = 0.01

PLANET_NAMES = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Rahu",
    "Ketu",
)


@dataclass
class FieldMismatch:
    """Single field mismatch between engine and reference."""

    chart_id: str
    category: str
    field: str
    expected: Any
    actual: Any
    delta: float | None = None


@dataclass
class ChartComparisonResult:
    """Comparison outcome for one golden chart."""

    chart_id: str
    name: str
    source: str
    mismatches: list[FieldMismatch] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.mismatches


def _longitude_delta(expected: float, actual: float) -> float:
    delta = abs(expected - actual)
    return min(delta, 360.0 - delta)


def _compare_longitude(
    *,
    chart_id: str,
    category: str,
    field: str,
    expected: float,
    actual: float,
    mismatches: list[FieldMismatch],
) -> None:
    delta = _longitude_delta(expected, actual)
    if delta > LONGITUDE_TOLERANCE:
        mismatches.append(
            FieldMismatch(
                chart_id=chart_id,
                category=category,
                field=field,
                expected=expected,
                actual=actual,
                delta=delta,
            )
        )


def _compare_scalar(
    *,
    chart_id: str,
    category: str,
    field: str,
    expected: Any,
    actual: Any,
    mismatches: list[FieldMismatch],
) -> None:
    if expected != actual:
        mismatches.append(
            FieldMismatch(
                chart_id=chart_id,
                category=category,
                field=field,
                expected=expected,
                actual=actual,
            )
        )


def _compare_ascendant(
    chart_id: str,
    expected: dict[str, Any],
    actual: Ascendant,
    mismatches: list[FieldMismatch],
) -> None:
    _compare_longitude(
        chart_id=chart_id,
        category="ascendant",
        field="longitude",
        expected=float(expected["longitude"]),
        actual=actual.longitude,
        mismatches=mismatches,
    )
    _compare_scalar(
        chart_id=chart_id,
        category="ascendant",
        field="sign",
        expected=expected["sign"],
        actual=actual.sign.name_en,
        mismatches=mismatches,
    )
    if abs(float(expected["degree_in_sign"]) - actual.sign.degree_in_sign) > DEGREE_IN_SIGN_TOLERANCE:
        mismatches.append(
            FieldMismatch(
                chart_id=chart_id,
                category="ascendant",
                field="degree_in_sign",
                expected=expected["degree_in_sign"],
                actual=actual.sign.degree_in_sign,
                delta=abs(float(expected["degree_in_sign"]) - actual.sign.degree_in_sign),
            )
        )
    _compare_scalar(
        chart_id=chart_id,
        category="ascendant",
        field="nakshatra",
        expected=expected["nakshatra"],
        actual=actual.nakshatra.name,
        mismatches=mismatches,
    )
    _compare_scalar(
        chart_id=chart_id,
        category="ascendant",
        field="pada",
        expected=int(expected["pada"]),
        actual=actual.nakshatra.pada,
        mismatches=mismatches,
    )


def _compare_planet(
    chart_id: str,
    expected: dict[str, Any],
    actual: PlanetPosition,
    mismatches: list[FieldMismatch],
) -> None:
    category = f"planet:{actual.name}"
    _compare_longitude(
        chart_id=chart_id,
        category=category,
        field="longitude",
        expected=float(expected["longitude"]),
        actual=actual.longitude,
        mismatches=mismatches,
    )
    _compare_scalar(
        chart_id=chart_id,
        category=category,
        field="sign",
        expected=expected["sign"],
        actual=actual.sign.name_en,
        mismatches=mismatches,
    )
    _compare_scalar(
        chart_id=chart_id,
        category=category,
        field="house",
        expected=int(expected["house"]),
        actual=actual.house,
        mismatches=mismatches,
    )
    _compare_scalar(
        chart_id=chart_id,
        category=category,
        field="nakshatra",
        expected=expected["nakshatra"],
        actual=actual.nakshatra.name,
        mismatches=mismatches,
    )
    _compare_scalar(
        chart_id=chart_id,
        category=category,
        field="pada",
        expected=int(expected["pada"]),
        actual=actual.nakshatra.pada,
        mismatches=mismatches,
    )


def _normalize_instant(value: str) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _compare_dasha_periods(
    chart_id: str,
    category: str,
    expected_periods: list[dict[str, Any]],
    actual_periods: list[dict[str, Any]],
    mismatches: list[FieldMismatch],
) -> None:
    if len(expected_periods) != len(actual_periods):
        mismatches.append(
            FieldMismatch(
                chart_id=chart_id,
                category=category,
                field="count",
                expected=len(expected_periods),
                actual=len(actual_periods),
            )
        )
        return

    for index, (expected_period, actual_period) in enumerate(zip(expected_periods, actual_periods, strict=True)):
        prefix = f"{category}[{index}]"
        _compare_scalar(
            chart_id=chart_id,
            category=prefix,
            field="lord",
            expected=expected_period["lord"],
            actual=actual_period["lord"],
            mismatches=mismatches,
        )
        expected_start = _normalize_instant(expected_period["start"])
        actual_start = _normalize_instant(actual_period["start"])
        if expected_start != actual_start:
            mismatches.append(
                FieldMismatch(
                    chart_id=chart_id,
                    category=prefix,
                    field="start",
                    expected=expected_start,
                    actual=actual_start,
                )
            )
        expected_end = _normalize_instant(expected_period["end"])
        actual_end = _normalize_instant(actual_period["end"])
        if expected_end != actual_end:
            mismatches.append(
                FieldMismatch(
                    chart_id=chart_id,
                    category=prefix,
                    field="end",
                    expected=expected_end,
                    actual=actual_end,
                )
            )


def compare_chart(
    case: GoldenChartCase,
    bundle: VedicChartBundle,
    dasha_payload: dict[str, Any],
) -> ChartComparisonResult:
    """Compare computed chart and dasha output against golden reference."""
    mismatches: list[FieldMismatch] = []
    expected = case.expected

    _compare_ascendant(case.input.chart_id, expected["ascendant"], bundle.lagna_kundali.ascendant, mismatches)

    planets_by_name = {planet.name: planet for planet in bundle.lagna_kundali.planets}
    for planet_name in PLANET_NAMES:
        _compare_planet(
            case.input.chart_id,
            expected["planets"][planet_name],
            planets_by_name[planet_name],
            mismatches,
        )

    dasha_expected = expected["dasha"]
    _compare_scalar(
        chart_id=case.input.chart_id,
        category="dasha",
        field="balance_lord",
        expected=dasha_expected["balance_lord"],
        actual=dasha_payload["balance"]["lord"],
        mismatches=mismatches,
    )

    _compare_dasha_periods(
        case.input.chart_id,
        "dasha.mahadasha",
        dasha_expected["mahadashas"],
        dasha_payload["mahadashas"],
        mismatches,
    )

    for md_index, expected_md in enumerate(dasha_expected["mahadashas"]):
        actual_md = dasha_payload["mahadashas"][md_index]
        _compare_dasha_periods(
            case.input.chart_id,
            f"dasha.mahadasha[{md_index}].antardasha",
            expected_md.get("antardashas", []),
            actual_md.get("antardashas", []),
            mismatches,
        )

    current_expected = dasha_expected.get("current")
    if current_expected:
        reference_dt = parse_reference_datetime(dasha_expected.get("reference_datetime"))
        if reference_dt is not None:
            _compare_scalar(
                chart_id=case.input.chart_id,
                category="dasha.current",
                field="mahadasha",
                expected=current_expected["mahadasha"],
                actual=dasha_payload["current"]["mahadasha"]["lord"],
                mismatches=mismatches,
            )
            if "antardasha" in current_expected:
                _compare_scalar(
                    chart_id=case.input.chart_id,
                    category="dasha.current",
                    field="antardasha",
                    expected=current_expected["antardasha"],
                    actual=dasha_payload["current"]["antardasha"]["lord"],
                    mismatches=mismatches,
                )

    return ChartComparisonResult(
        chart_id=case.input.chart_id,
        name=case.input.name,
        source=case.input.source,
        mismatches=mismatches,
    )
