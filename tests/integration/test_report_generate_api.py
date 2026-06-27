"""Integration tests for POST /api/v1/dashboard/reports/generate."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.api.v1.endpoints.dashboard import get_report_service
from backend.app.main import create_app
from backend.app.schemas.dashboard import ReportGenerateResponse
from tests.helpers import override_current_user

GENERATE_URL = "/api/v1/dashboard/reports/generate"


def _valid_payload(**overrides) -> dict:
    payload = {
        "date_of_birth": "1990-01-15",
        "birth_time": "05:00:00",
        "birth_place": "New Delhi, India",
        "timezone": "Asia/Kolkata",
        "latitude": "28.6139",
        "longitude": "77.2090",
        "problem_text": "Marriage delay",
    }
    payload.update(overrides)
    return payload


def _service_response(include_pdf: bool = False) -> dict:
    generated_at = datetime.now(timezone.utc)
    pdf_payload = None
    if include_pdf:
        pdf_payload = {
            "generated": True,
            "filename": "client_report_1990.pdf",
            "path": "reports/generated/client_report_1990.pdf",
            "download_url": "/api/v1/dashboard/reports/pdf/client_report_1990.pdf",
        }

    return {
        "report_id": str(uuid.uuid4()),
        "version": "unified_report_v2",
        "unified_report": {
            "version": "unified_report_v2",
            "summary": {
                "lagna_sign": "Taurus",
                "moon_sign": "Cancer",
                "moon_nakshatra": "Pushya",
                "present_yogas_count": 2,
                "present_doshas_count": 1,
            },
            "kundali": {"chart_type": "d1_lagna", "ascendant": {"sign": {"name_en": "Taurus"}}},
            "metadata": {"orchestrator": "report_orchestrator_v2"},
        },
        "interpretation": {"summary": "Saturn influences the 7th house."},
        "remedy_generation": {"remedies": [{"remedy_id": "vedic_saturn_mantra"}]},
        "client_report": {"problem_summary": "Marriage delay", "sections": []},
        "pdf": pdf_payload,
        "generated_at": generated_at,
    }


@pytest.fixture
def mock_report_service():
    service = AsyncMock()
    service.generate_report.return_value = _service_response()
    return service


@pytest.fixture
async def report_generate_client(mock_report_service, test_user):
    app = create_app()
    app.dependency_overrides[get_report_service] = lambda: mock_report_service
    override_current_user(app, test_user)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_generate_report_success_returns_200(report_generate_client, mock_report_service):
    response = await report_generate_client.post(GENERATE_URL, json=_valid_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["version"] == "unified_report_v2"
    assert body["unified_report"]["summary"]["lagna_sign"] == "Taurus"
    assert body["interpretation"]["summary"]
    assert body["client_report"]["problem_summary"] == "Marriage delay"
    assert body["pdf"] is None
    mock_report_service.generate_report.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_report_response_matches_schema(report_generate_client):
    response = await report_generate_client.post(GENERATE_URL, json=_valid_payload())

    assert response.status_code == 200
    parsed = ReportGenerateResponse.model_validate(response.json())
    assert parsed.report_id
    assert parsed.version == "unified_report_v2"
    assert isinstance(parsed.unified_report, dict)
    assert isinstance(parsed.generated_at, datetime)


@pytest.mark.asyncio
async def test_generate_report_passes_birth_timezone_to_service(report_generate_client, mock_report_service):
    await report_generate_client.post(
        GENERATE_URL,
        json=_valid_payload(timezone="Asia/Kolkata"),
    )

    call_kwargs = mock_report_service.generate_report.await_args.kwargs
    assert call_kwargs["birth_timezone"] == "Asia/Kolkata"
    assert call_kwargs["birth_place"] == "New Delhi, India"
    assert str(call_kwargs["latitude"]) == "28.6139"
    assert str(call_kwargs["longitude"]) == "77.2090"


@pytest.mark.asyncio
async def test_generate_report_accepts_optional_valid_uuids(report_generate_client):
    client_id = str(uuid.uuid4())
    birth_detail_id = str(uuid.uuid4())
    response = await report_generate_client.post(
        GENERATE_URL,
        json=_valid_payload(client_id=client_id, birth_detail_id=birth_detail_id),
    )

    assert response.status_code == 200
    ReportGenerateResponse.model_validate(response.json())


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("client_id", "not-a-valid-uuid"),
        ("client_id", "00000000-0000-0000-0000-000000000000-extra"),
        ("birth_detail_id", "invalid-uuid"),
        ("birth_detail_id", ""),
    ],
)
async def test_generate_report_rejects_invalid_uuid_fields(report_generate_client, field, value):
    response = await report_generate_client.post(
        GENERATE_URL,
        json=_valid_payload(**{field: value}),
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert any(item["loc"][-1] == field for item in detail)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("latitude", "91.0"),
        ("latitude", "-90.1"),
        ("longitude", "180.1"),
        ("longitude", "-180.1"),
    ],
)
async def test_generate_report_rejects_invalid_coordinates(report_generate_client, field, value):
    response = await report_generate_client.post(
        GENERATE_URL,
        json=_valid_payload(**{field: value}),
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert any(item["loc"][-1] == field for item in detail)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "missing_field",
    ["date_of_birth", "birth_time", "birth_place", "latitude", "longitude"],
)
async def test_generate_report_rejects_missing_required_fields(
    report_generate_client,
    mock_report_service,
    missing_field,
):
    payload = _valid_payload()
    if missing_field in ("latitude", "longitude"):
        payload[missing_field] = None
    else:
        payload.pop(missing_field, None)

    response = await report_generate_client.post(GENERATE_URL, json=payload)

    assert response.status_code == 422
    mock_report_service.generate_report.assert_not_awaited()


@pytest.mark.asyncio
async def test_generate_report_missing_birth_fields_returns_endpoint_message(report_generate_client):
    response = await report_generate_client.post(
        GENERATE_URL,
        json={
            "timezone": "Asia/Kolkata",
            "latitude": "28.6139",
            "longitude": "77.2090",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "date_of_birth, birth_time, and birth_place are required."
    )


@pytest.mark.asyncio
async def test_generate_report_missing_coordinates_returns_endpoint_message(report_generate_client):
    response = await report_generate_client.post(
        GENERATE_URL,
        json={
            "date_of_birth": "1990-01-15",
            "birth_time": "05:00:00",
            "birth_place": "New Delhi, India",
            "timezone": "Asia/Kolkata",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "latitude and longitude are required for report generation."
    )


@pytest.mark.asyncio
async def test_generate_report_rejects_invalid_birth_time_format(report_generate_client):
    response = await report_generate_client.post(
        GENERATE_URL,
        json=_valid_payload(birth_time="25:99:00"),
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert any(item["loc"][-1] == "birth_time" for item in detail)


@pytest.mark.asyncio
async def test_generate_report_rejects_invalid_date_of_birth_format(report_generate_client):
    response = await report_generate_client.post(
        GENERATE_URL,
        json=_valid_payload(date_of_birth="1990-13-40"),
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert any(item["loc"][-1] == "date_of_birth" for item in detail)


@pytest.mark.asyncio
async def test_generate_report_with_pdf_flag(report_generate_client, mock_report_service):
    mock_report_service.generate_report.return_value = _service_response(include_pdf=True)

    response = await report_generate_client.post(
        GENERATE_URL,
        json=_valid_payload(include_pdf=True),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["pdf"] is not None
    assert body["pdf"]["generated"] is True
    assert body["pdf"]["filename"] == "client_report_1990.pdf"
    assert body["pdf"]["download_url"] == "/api/v1/dashboard/reports/pdf/client_report_1990.pdf"

    call_kwargs = mock_report_service.generate_report.await_args.kwargs
    assert call_kwargs["include_pdf"] is True

    parsed = ReportGenerateResponse.model_validate(body)
    assert parsed.pdf is not None
    assert parsed.pdf.generated is True
    assert parsed.pdf.filename == "client_report_1990.pdf"


@pytest.mark.asyncio
async def test_generate_report_without_pdf_flag(report_generate_client, mock_report_service):
    response = await report_generate_client.post(
        GENERATE_URL,
        json=_valid_payload(include_pdf=False),
    )

    assert response.status_code == 200
    assert response.json()["pdf"] is None

    call_kwargs = mock_report_service.generate_report.await_args.kwargs
    assert call_kwargs["include_pdf"] is False


@pytest.mark.asyncio
async def test_generate_report_empty_body_returns_422(report_generate_client, mock_report_service):
    response = await report_generate_client.post(GENERATE_URL, json={})

    assert response.status_code == 422
    mock_report_service.generate_report.assert_not_awaited()
