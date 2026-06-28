"""End-to-end birth data pipeline verification for a known Indian chart."""

from __future__ import annotations

import uuid
from datetime import date, datetime, time, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from zoneinfo import ZoneInfo

import pytest

from backend.app.models.birth_detail import BirthDetail
from backend.app.models.enums import RelationshipType
from backend.app.services.report_service import ReportService
from reports.builders import (
    build_birth_context_from_birth_detail,
    build_birth_data_from_context,
    build_birth_data_from_report,
)
from reports.orchestrator import ReportOrchestrator


REFERENCE = {
    "date_of_birth": date(1990, 1, 15),
    "birth_time": time(10, 30, 0),
    "birth_place": "New Delhi, India",
    "timezone": "Asia/Kolkata",
    "latitude": 28.6139,
    "longitude": 77.2090,
}


@pytest.fixture(scope="module")
def chart_expectations():
    """Compute expected sidereal outputs for the reference Indian birth chart."""
    pytest.importorskip("swisseph")
    from astrology_engine.engine import VedicAstrologyEngine

    birth_data = build_birth_data_from_report(
        date_of_birth=REFERENCE["date_of_birth"],
        birth_time=REFERENCE["birth_time"],
        latitude=REFERENCE["latitude"],
        longitude=REFERENCE["longitude"],
        timezone_name=REFERENCE["timezone"],
    )
    chart = VedicAstrologyEngine().compute_chart(birth_data)
    moon = next(planet for planet in chart.lagna_kundali.planets if planet.name == "Moon")

    return {
        "datetime_utc": birth_data.datetime_utc,
        "latitude": birth_data.latitude,
        "longitude": birth_data.longitude,
        "timezone": birth_data.timezone,
        "lagna_sign": chart.lagna_kundali.ascendant.sign.name_en,
        "moon_sign": moon.sign.name_en,
        "julian_day": chart.metadata.julian_day,
    }


def test_reference_birth_data_has_correct_utc_and_coordinates(chart_expectations) -> None:
    assert chart_expectations["datetime_utc"] == datetime(1990, 1, 15, 5, 0, tzinfo=timezone.utc)
    assert chart_expectations["latitude"] == pytest.approx(28.6139)
    assert chart_expectations["longitude"] == pytest.approx(77.2090)
    assert chart_expectations["timezone"] == "Asia/Kolkata"


def test_reference_chart_lagna_and_moon_match_engine(chart_expectations) -> None:
    pytest.importorskip("swisseph")
    from astrology_engine.engine import VedicAstrologyEngine

    birth_data = build_birth_data_from_report(
        date_of_birth=REFERENCE["date_of_birth"],
        birth_time=REFERENCE["birth_time"],
        latitude=REFERENCE["latitude"],
        longitude=REFERENCE["longitude"],
        timezone_name=REFERENCE["timezone"],
    )
    chart = VedicAstrologyEngine().compute_chart(birth_data)
    moon = next(planet for planet in chart.lagna_kundali.planets if planet.name == "Moon")

    assert chart.lagna_kundali.ascendant.sign.name_en == chart_expectations["lagna_sign"]
    assert moon.sign.name_en == chart_expectations["moon_sign"]
    assert chart.metadata.julian_day == chart_expectations["julian_day"]


def test_persisted_birth_detail_produces_same_birth_data(chart_expectations) -> None:
    localized = datetime.combine(
        REFERENCE["date_of_birth"],
        REFERENCE["birth_time"],
        tzinfo=ZoneInfo(REFERENCE["timezone"]),
    )
    birth_detail = BirthDetail(
        id=uuid.uuid4(),
        client_id=uuid.uuid4(),
        person_name="Reference Native",
        relationship_to_client=RelationshipType.SELF,
        birth_datetime=localized,
        birth_place_name=REFERENCE["birth_place"],
        latitude=Decimal(str(REFERENCE["latitude"])),
        longitude=Decimal(str(REFERENCE["longitude"])),
        timezone=REFERENCE["timezone"],
        is_primary=True,
    )

    birth_data = build_birth_data_from_context(build_birth_context_from_birth_detail(birth_detail))
    assert birth_data.datetime_utc == chart_expectations["datetime_utc"]
    assert birth_data.latitude == chart_expectations["latitude"]
    assert birth_data.longitude == chart_expectations["longitude"]


@pytest.mark.asyncio
async def test_report_service_uses_persisted_birth_detail_for_linked_client(
    chart_expectations,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("swisseph")

    localized = datetime.combine(
        REFERENCE["date_of_birth"],
        REFERENCE["birth_time"],
        tzinfo=ZoneInfo(REFERENCE["timezone"]),
    )
    birth_detail = BirthDetail(
        id=uuid.uuid4(),
        client_id=uuid.uuid4(),
        person_name="Reference Native",
        relationship_to_client=RelationshipType.SELF,
        birth_datetime=localized,
        birth_place_name=REFERENCE["birth_place"],
        latitude=Decimal(str(REFERENCE["latitude"])),
        longitude=Decimal(str(REFERENCE["longitude"])),
        timezone=REFERENCE["timezone"],
        is_primary=True,
    )

    async def _get_birth_detail_for_client(**_kwargs):
        return birth_detail

    monkeypatch.setattr(
        "backend.app.services.client_service.ClientService.get_birth_detail_for_client",
        _get_birth_detail_for_client,
    )

    service = ReportService(session=AsyncMock(), repository=AsyncMock())
    context, resolved_id = await service._resolve_birth_context(
        client_id=birth_detail.client_id,
        birth_detail_id=None,
        scoped_owner_id=uuid.uuid4(),
        date_of_birth=None,
        birth_time=None,
        birth_place="Wrong Place",
        birth_timezone="UTC",
        latitude=Decimal("0"),
        longitude=Decimal("0"),
    )

    assert resolved_id == birth_detail.id
    assert context.birth_place == REFERENCE["birth_place"]
    assert context.timezone_name == REFERENCE["timezone"]
    assert context.latitude == pytest.approx(REFERENCE["latitude"])
    assert context.longitude == pytest.approx(REFERENCE["longitude"])

    orchestrator = ReportOrchestrator()
    from reports.builders import build_birth_data_from_context
    from reports.types import ReportInput

    birth_data = build_birth_data_from_context(context)
    report_json = orchestrator.generate_json(
        ReportInput(birth_data=birth_data, birth_place=context.birth_place)
    )

    assert report_json["summary"]["lagna_sign"] == chart_expectations["lagna_sign"]
    assert report_json["summary"]["moon_sign"] == chart_expectations["moon_sign"]
    assert report_json["kundali"]["metadata"]["latitude"] == pytest.approx(REFERENCE["latitude"])
    assert report_json["kundali"]["metadata"]["longitude"] == pytest.approx(REFERENCE["longitude"])
