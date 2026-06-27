"""Report generation service."""

from __future__ import annotations

import logging
import math
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ai_engine.interpreters.astro import AstroInterpretationEngine, AstroInterpretationInput
from ai_engine.interpreters.remedy import RemedyGenerationEngine, RemedyGenerationInput
from ai_engine.writers.client_report import ClientReportInput, ClientReportWriter
from consultation_layer import ConsultationEngine, consultation_input_from_unified_report
from reports.builders import build_birth_data_from_report
from reports.orchestrator import ReportOrchestrator
from reports.pdf import PDFReportGenerator
from reports.types import ReportInput

from backend.app.core.exceptions import NotFoundError
from backend.app.models.report import Report
from backend.app.repositories.report_repository import ReportRepository

logger = logging.getLogger(__name__)


class ReportService:
    """Orchestrate unified report, interpretation, remedies, client report, and PDF."""

    def __init__(
        self,
        *,
        reports_output_path: str = "reports/generated",
        session: AsyncSession | None = None,
        repository: ReportRepository | None = None,
    ) -> None:
        self._orchestrator = ReportOrchestrator()
        self._interpretation_engine = AstroInterpretationEngine()
        self._remedy_engine = RemedyGenerationEngine()
        self._client_writer = ClientReportWriter()
        self._pdf_output_dir = Path(reports_output_path)
        self._pdf_generator = PDFReportGenerator(output_dir=self._pdf_output_dir)
        self._consultation_engine = ConsultationEngine()
        self._session = session
        self._repository = repository or (ReportRepository(session) if session is not None else None)

    async def generate_report(
        self,
        *,
        date_of_birth: date,
        birth_time,
        birth_place: str,
        birth_timezone: str,
        latitude: Decimal | float,
        longitude: Decimal | float,
        problem_text: str | None = None,
        target_date: date | None = None,
        include_pdf: bool = False,
        client_id: uuid.UUID | None = None,
        birth_detail_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        if self._repository is None or self._session is None:
            raise RuntimeError("Report persistence is not configured for ReportService.")

        birth_data = build_birth_data_from_report(
            date_of_birth=date_of_birth,
            birth_time=birth_time,
            latitude=float(latitude),
            longitude=float(longitude),
            timezone_name=birth_timezone,
        )
        report_input = ReportInput(
            birth_data=birth_data,
            birth_place=birth_place,
            problem_text=problem_text,
            target_date=target_date,
        )
        unified_json = self._orchestrator.generate_json(report_input)

        interpretation = await self._interpretation_engine.interpret_json(
            AstroInterpretationInput(report_json=unified_json)
        )
        remedy_generation = await self._remedy_engine.generate_json(
            RemedyGenerationInput(report_json=unified_json)
        )
        client_report = self._client_writer.write_json(
            ClientReportInput(
                report_json=unified_json,
                interpretation_json=interpretation,
                remedy_generation_json=remedy_generation,
                problem_text=problem_text,
            )
        )

        consultation = self._consultation_engine.consult_json(
            consultation_input_from_unified_report(
                unified_json,
                problem_text=problem_text,
            )
        )

        pdf_payload = None
        pdf_path = None
        if include_pdf:
            pdf_payload, pdf_path = self._generate_pdf_payload(
                client_report_json=client_report,
                unified_report_json=unified_json,
            )

        generated_at = datetime.now(timezone.utc)
        version = unified_json.get("version", "unified_report_v2")

        persisted = await self._repository.create_report(
            client_id=client_id,
            birth_detail_id=birth_detail_id,
            version=version,
            problem_text=problem_text,
            unified_report_json=unified_json,
            interpretation_json=interpretation,
            remedy_json=remedy_generation,
            client_report_json=client_report,
            pdf_path=pdf_path,
            generated_at=generated_at,
        )
        await self._session.commit()

        return {
            "report_id": str(persisted.id),
            "version": version,
            "unified_report": unified_json,
            "interpretation": interpretation,
            "remedy_generation": remedy_generation,
            "client_report": client_report,
            "consultation": consultation,
            "pdf": pdf_payload,
            "generated_at": persisted.generated_at,
        }

    def _generate_pdf_payload(
        self,
        *,
        client_report_json: dict[str, Any],
        unified_report_json: dict[str, Any],
    ) -> tuple[dict[str, Any], str | None]:
        try:
            pdf_result = self._pdf_generator.generate(
                client_report_json=client_report_json,
                unified_report_json=unified_report_json,
            )
            return (
                {
                    "generated": True,
                    "filename": pdf_result.file_name,
                    "path": pdf_result.file_path,
                    "download_url": self._pdf_download_url(pdf_result.file_name),
                },
                pdf_result.file_path,
            )
        except Exception:
            logger.exception("PDF generation failed")
            return {"generated": False}, None

    @staticmethod
    def _pdf_download_url(filename: str) -> str:
        return f"/api/v1/dashboard/reports/pdf/{filename}"

    def generate_pdf_from_client_report(
        self,
        *,
        client_report_json: dict[str, Any],
        unified_report_json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        result = self._pdf_generator.generate(
            client_report_json=client_report_json,
            unified_report_json=unified_report_json,
        )
        return {
            "pdf_id": str(uuid.uuid4()),
            "file_name": result.file_name,
            "file_path": result.file_path,
            "file_size_bytes": result.file_size_bytes,
            "download_url": self._pdf_download_url(result.file_name),
            "generated_at": result.generated_at,
        }

    async def list_reports(
        self,
        *,
        client_id: uuid.UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        if self._repository is None:
            raise RuntimeError("Report persistence is not configured for ReportService.")

        reports, total = await self._repository.list_reports(
            client_id=client_id,
            page=page,
            page_size=page_size,
        )
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        pages = math.ceil(total / page_size) if total else 0

        return {
            "items": [self._report_to_summary(report) for report in reports],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        }

    async def get_report(self, report_id: uuid.UUID) -> dict[str, Any]:
        if self._repository is None:
            raise RuntimeError("Report persistence is not configured for ReportService.")

        report = await self._repository.get_report(report_id)
        if report is None:
            raise NotFoundError(f"Report with id '{report_id}' was not found.")
        return self._report_to_detail(report)

    async def delete_report(self, report_id: uuid.UUID) -> None:
        if self._repository is None or self._session is None:
            raise RuntimeError("Report persistence is not configured for ReportService.")

        deleted = await self._repository.delete_report(report_id)
        if not deleted:
            raise NotFoundError(f"Report with id '{report_id}' was not found.")
        await self._session.commit()

    @classmethod
    def _pdf_payload_from_path(cls, pdf_path: str | None) -> dict[str, Any] | None:
        if pdf_path is None:
            return None
        filename = Path(pdf_path).name
        return {
            "generated": True,
            "filename": filename,
            "path": pdf_path,
            "download_url": cls._pdf_download_url(filename),
        }

    @classmethod
    def _report_to_summary(cls, report: Report) -> dict[str, Any]:
        summary = report.unified_report_json.get("summary", {})
        return {
            "report_id": str(report.id),
            "client_id": report.client_id,
            "birth_detail_id": report.birth_detail_id,
            "version": report.version,
            "problem_text": report.problem_text,
            "lagna_sign": summary.get("lagna_sign"),
            "moon_sign": summary.get("moon_sign"),
            "generated_at": report.generated_at,
            "has_pdf": report.pdf_path is not None,
        }

    @classmethod
    def _report_to_detail(cls, report: Report) -> dict[str, Any]:
        return {
            "report_id": str(report.id),
            "client_id": report.client_id,
            "birth_detail_id": report.birth_detail_id,
            "version": report.version,
            "problem_text": report.problem_text,
            "unified_report": report.unified_report_json,
            "interpretation": report.interpretation_json,
            "remedy_generation": report.remedy_json,
            "client_report": report.client_report_json,
            "pdf": cls._pdf_payload_from_path(report.pdf_path),
            "generated_at": report.generated_at,
            "updated_at": report.updated_at,
        }
