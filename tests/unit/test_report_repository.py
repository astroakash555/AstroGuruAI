"""Unit tests for ReportRepository."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.models.report import Report
from backend.app.repositories.report_repository import ReportRepository


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_create_report_persists_entity(mock_session):
    repository = ReportRepository(mock_session)
    client_id = uuid.uuid4()
    generated_at = datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc)

    created = await repository.create_report(
        client_id=client_id,
        birth_detail_id=None,
        version="unified_report_v2",
        problem_text="Marriage delay",
        unified_report_json={"version": "unified_report_v2", "summary": {"lagna_sign": "Aries"}},
        interpretation_json={"summary": "Interpretation"},
        remedy_json={"remedies": []},
        client_report_json={"problem_summary": "Marriage delay"},
        pdf_path=None,
        generated_at=generated_at,
    )

    mock_session.add.assert_called_once()
    added_report = mock_session.add.call_args[0][0]
    assert isinstance(added_report, Report)
    assert added_report.client_id == client_id
    assert added_report.version == "unified_report_v2"
    mock_session.flush.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(added_report)
    assert created is added_report


@pytest.mark.asyncio
async def test_get_report(mock_session):
    repository = ReportRepository(mock_session)
    report_id = uuid.uuid4()
    stored = Report(
        id=report_id,
        client_id=None,
        birth_detail_id=None,
        version="unified_report_v2",
        problem_text=None,
        unified_report_json={"summary": {}},
        interpretation_json={},
        remedy_json={},
        client_report_json={},
        pdf_path=None,
        generated_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    result = MagicMock()
    result.scalar_one_or_none.return_value = stored
    mock_session.execute.return_value = result

    fetched = await repository.get_report(report_id)
    assert fetched is stored
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_reports_by_client(mock_session):
    repository = ReportRepository(mock_session)
    client_id = uuid.uuid4()
    reports = [
        Report(
            id=uuid.uuid4(),
            client_id=client_id,
            birth_detail_id=None,
            version="unified_report_v2",
            problem_text=None,
            unified_report_json={},
            interpretation_json={},
            remedy_json={},
            client_report_json={},
            pdf_path=None,
            generated_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    ]
    repository.list_reports = AsyncMock(return_value=(reports, 1))

    fetched = await repository.get_reports_by_client(client_id)
    assert fetched == reports
    repository.list_reports.assert_awaited_once_with(client_id=client_id, page=1, page_size=100)


@pytest.mark.asyncio
async def test_list_reports_with_client_filter(mock_session):
    repository = ReportRepository(mock_session)
    client_id = uuid.uuid4()
    report = Report(
        id=uuid.uuid4(),
        client_id=client_id,
        birth_detail_id=None,
        version="unified_report_v2",
        problem_text="Career",
        unified_report_json={"summary": {"lagna_sign": "Aries"}},
        interpretation_json={},
        remedy_json={},
        client_report_json={},
        pdf_path=None,
        generated_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    count_result = MagicMock()
    count_result.scalar_one.return_value = 1
    list_result = MagicMock()
    list_result.scalars.return_value.all.return_value = [report]
    mock_session.execute = AsyncMock(side_effect=[count_result, list_result])

    reports, total = await repository.list_reports(client_id=client_id, page=1, page_size=20)
    assert total == 1
    assert len(reports) == 1
    assert reports[0].client_id == client_id
    assert mock_session.execute.await_count == 2


@pytest.mark.asyncio
async def test_delete_report(mock_session):
    repository = ReportRepository(mock_session)
    report_id = uuid.uuid4()
    stored = Report(
        id=report_id,
        client_id=None,
        birth_detail_id=None,
        version="unified_report_v2",
        problem_text=None,
        unified_report_json={},
        interpretation_json={},
        remedy_json={},
        client_report_json={},
        pdf_path=None,
        generated_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    get_result = MagicMock()
    get_result.scalar_one_or_none.return_value = stored
    mock_session.execute.return_value = get_result

    deleted = await repository.delete_report(report_id)
    assert deleted is True
    mock_session.delete.assert_awaited_once_with(stored)
    mock_session.flush.assert_awaited_once()

    get_result.scalar_one_or_none.return_value = None
    assert await repository.delete_report(uuid.uuid4()) is False
