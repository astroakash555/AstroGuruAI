"""Persistence layer for unified reports."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.report import Report


class ReportRepository:
    """CRUD operations for persisted unified reports."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_report(
        self,
        *,
        client_id: uuid.UUID | None,
        birth_detail_id: uuid.UUID | None,
        version: str,
        problem_text: str | None,
        unified_report_json: dict,
        interpretation_json: dict,
        remedy_json: dict,
        client_report_json: dict,
        pdf_path: str | None,
        generated_at,
    ) -> Report:
        report = Report(
            client_id=client_id,
            birth_detail_id=birth_detail_id,
            version=version,
            problem_text=problem_text,
            unified_report_json=unified_report_json,
            interpretation_json=interpretation_json,
            remedy_json=remedy_json,
            client_report_json=client_report_json,
            pdf_path=pdf_path,
            generated_at=generated_at,
        )
        self._session.add(report)
        await self._session.flush()
        await self._session.refresh(report)
        return report

    async def get_report(self, report_id: uuid.UUID) -> Report | None:
        result = await self._session.execute(select(Report).where(Report.id == report_id))
        return result.scalar_one_or_none()

    async def list_reports(
        self,
        *,
        client_id: uuid.UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Report], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        offset = (page - 1) * page_size

        filters = []
        if client_id is not None:
            filters.append(Report.client_id == client_id)

        count_stmt = select(func.count()).select_from(Report)
        if filters:
            count_stmt = count_stmt.where(*filters)
        total = int((await self._session.execute(count_stmt)).scalar_one())

        stmt = (
            select(Report)
            .order_by(Report.generated_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        if filters:
            stmt = stmt.where(*filters)

        result = await self._session.execute(stmt)
        return list(result.scalars().all()), total

    async def get_reports_by_client(self, client_id: uuid.UUID) -> list[Report]:
        reports, _ = await self.list_reports(client_id=client_id, page=1, page_size=100)
        return reports

    async def delete_report(self, report_id: uuid.UUID) -> bool:
        report = await self.get_report(report_id)
        if report is None:
            return False
        await self._session.delete(report)
        await self._session.flush()
        return True
