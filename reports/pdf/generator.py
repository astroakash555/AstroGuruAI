"""PDF report generator using the premium PDF engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from backend.app.services.pdf_engine.pdf_builder import PremiumPDFBuilder
from backend.app.services.pdf_engine.types import PDFBuildInput


@dataclass(frozen=True)
class PDFGenerationResult:
    file_path: str
    file_name: str
    file_size_bytes: int
    generated_at: datetime


class PDFReportGenerator:
    """Generate downloadable premium PDF reports from professional report JSON."""

    def __init__(self, output_dir: str = "reports/generated") -> None:
        self._builder = PremiumPDFBuilder(output_dir=output_dir)

    def generate(
        self,
        *,
        client_report_json: dict[str, Any],
        unified_report_json: dict[str, Any] | None = None,
        file_prefix: str = "astroguru_report",
        report_id: str | None = None,
        client_name: str | None = None,
        online_report_url: str | None = None,
        ai_chat_url: str | None = None,
    ) -> PDFGenerationResult:
        result = self._builder.build(
            PDFBuildInput(
                client_report_json=client_report_json,
                unified_report_json=unified_report_json,
                file_prefix=file_prefix,
                report_id=report_id,
                client_name=client_name,
                online_report_url=online_report_url,
                ai_chat_url=ai_chat_url,
            )
        )
        return PDFGenerationResult(
            file_path=result.file_path,
            file_name=result.file_name,
            file_size_bytes=result.file_size_bytes,
            generated_at=result.generated_at,
        )
