"""Load golden chart fixtures for regression testing."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, time
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from astrology_engine.core.base import BirthData
from astrology_engine.dasha.types import DashaBirthInput
from tests.golden.helpers import build_birth_data as make_birth_data
from tests.golden.helpers import build_dasha_input_from_bundle

GOLDEN_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "golden_charts"
MANIFEST_PATH = GOLDEN_DIR / "manifest.json"


@dataclass(frozen=True)
class GoldenChartInput:
    """Birth inputs for a golden chart case."""

    chart_id: str
    name: str
    date_of_birth: date
    birth_time: time
    timezone: str
    latitude: float
    longitude: float
    place: str
    source: str
    notes: str = ""


@dataclass(frozen=True)
class GoldenChartCase:
    """Full golden chart fixture including reference expectations."""

    input: GoldenChartInput
    expected: dict[str, Any]
    reference_settings: dict[str, str]


def load_manifest() -> dict[str, Any]:
    """Load the golden chart manifest."""
    with MANIFEST_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def list_golden_chart_ids() -> list[str]:
    """Return ordered golden chart identifiers."""
    manifest = load_manifest()
    return [item["id"] for item in manifest["charts"]]


def load_golden_chart(chart_id: str) -> GoldenChartCase:
    """Load a single golden chart case by identifier."""
    manifest = load_manifest()
    chart_meta = next(item for item in manifest["charts"] if item["id"] == chart_id)
    chart_path = GOLDEN_DIR / chart_meta["file"]
    with chart_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    birth = payload["birth"]
    chart_input = GoldenChartInput(
        chart_id=payload["id"],
        name=payload["name"],
        date_of_birth=date.fromisoformat(birth["date"]),
        birth_time=time.fromisoformat(birth["time"]),
        timezone=birth["timezone"],
        latitude=float(birth["latitude"]),
        longitude=float(birth["longitude"]),
        place=birth["place"],
        source=payload.get("source", "engine_locked"),
        notes=payload.get("notes", ""),
    )
    return GoldenChartCase(
        input=chart_input,
        expected=payload["expected"],
        reference_settings=payload.get("reference_settings", {}),
    )


def load_all_golden_charts() -> list[GoldenChartCase]:
    """Load every golden chart case."""
    return [load_golden_chart(chart_id) for chart_id in list_golden_chart_ids()]


def build_birth_data_for_case(case: GoldenChartCase) -> BirthData:
    """Build BirthData for engine computation."""
    return make_birth_data(
        date_of_birth=case.input.date_of_birth,
        birth_time=case.input.birth_time,
        latitude=case.input.latitude,
        longitude=case.input.longitude,
        timezone_name=case.input.timezone,
    )


def build_dasha_input(case: GoldenChartCase, moon_nakshatra: str, moon_longitude: float) -> DashaBirthInput:
    """Build dasha input aligned with computed chart moon position."""
    return DashaBirthInput(
        date_of_birth=case.input.date_of_birth,
        birth_time=case.input.birth_time,
        birth_place=case.input.place,
        timezone=case.input.timezone,
        moon_nakshatra=moon_nakshatra,
        latitude=case.input.latitude,
        longitude=case.input.longitude,
        moon_longitude=moon_longitude,
    )


def parse_reference_datetime(value: str | None) -> datetime | None:
    """Parse ISO reference datetime for dasha current-period lookup."""
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=ZoneInfo("UTC"))
    return parsed
