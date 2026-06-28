"""Premium PDF builder integration tests."""

from pathlib import Path

from backend.app.services.pdf_engine.pdf_builder import PremiumPDFBuilder
from backend.app.services.pdf_engine.types import PDFBuildInput


def test_premium_pdf_builder_creates_print_ready_pdf(
    tmp_path,
    sample_client_report,
    sample_unified_report,
):
    builder = PremiumPDFBuilder(output_dir=tmp_path)
    result = builder.build(
        PDFBuildInput(
            client_report_json=sample_client_report,
            unified_report_json=sample_unified_report,
            report_id="report-123",
            client_name="Test Native",
            online_report_url="https://astroguru.ai/reports/report-123",
            ai_chat_url="https://astroguru.ai/chat/report-123",
        )
    )
    pdf_file = Path(result.file_path)
    assert pdf_file.exists()
    assert pdf_file.suffix == ".pdf"
    assert result.file_size_bytes > 5000
    assert result.section_pages


def test_legacy_pdf_generator_wrapper(tmp_path, sample_client_report, sample_unified_report):
    from reports.pdf import PDFReportGenerator

    generator = PDFReportGenerator(output_dir=tmp_path)
    result = generator.generate(
        client_report_json=sample_client_report,
        unified_report_json=sample_unified_report,
        report_id="report-456",
        client_name="Legacy Native",
    )
    assert Path(result.file_path).exists()
    assert result.file_size_bytes > 5000
