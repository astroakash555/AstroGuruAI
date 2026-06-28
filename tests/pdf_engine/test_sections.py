"""Unit tests for PDF section modules."""

from backend.app.services.pdf_engine.birth_details_section import build_birth_details_section
from backend.app.services.pdf_engine.cover_page import build_cover_page
from backend.app.services.pdf_engine.dasha_section import build_dasha_section
from backend.app.services.pdf_engine.fonts import register_pdf_fonts, reset_font_registration_for_tests
from backend.app.services.pdf_engine.house_section import build_house_section
from backend.app.services.pdf_engine.kundali_section import build_kundali_section
from backend.app.services.pdf_engine.planet_section import build_planet_section
from backend.app.services.pdf_engine.problem_section import build_problem_section
from backend.app.services.pdf_engine.remedy_section import build_remedy_section
from backend.app.services.pdf_engine.renderer import escape_text
from backend.app.services.pdf_engine.summary_section import build_qr_page, build_summary_section
from backend.app.services.pdf_engine.table_of_contents import build_table_of_contents
from backend.app.services.pdf_engine.theme import THEME, build_styles
from backend.app.services.pdf_engine.transit_section import build_transit_section
from backend.app.services.pdf_engine.yoga_section import build_yoga_section
from backend.app.services.pdf_engine.charts import build_chart_flowables, _moon_chart_from_lagna
from backend.app.services.pdf_engine.tables import build_table
from datetime import datetime, timezone


def _styles():
    regular, bold = register_pdf_fonts()
    return build_styles(regular, bold)


def test_escape_text_escapes_markup():
    assert escape_text("<A & B>") == "&lt;A &amp; B&gt;"


def test_theme_colors_are_professional():
    from reportlab.lib import colors

    assert THEME.dark_blue == colors.HexColor("#0B1F3A")
    assert THEME.gold == colors.HexColor("#C9A227")


def test_cover_page_flowables():
    flowables = build_cover_page(
        styles=_styles(),
        client_name="Native",
        report_id="abc",
        language="hi",
        generated_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    assert len(flowables) >= 5


def test_table_of_contents_includes_page_numbers():
    flowables = build_table_of_contents(
        styles=_styles(),
        entries=[("birth_details", "Birth Details", 3)],
    )
    assert flowables


def test_section_builders_return_flowables(sample_client_report, sample_unified_report):
    styles = _styles()
    assert build_birth_details_section(
        styles=styles,
        client_report=sample_client_report,
        unified_report=sample_unified_report,
        client_name="Native",
    )
    assert build_kundali_section(styles=styles, unified_report=sample_unified_report)
    assert build_planet_section(
        styles=styles,
        client_report=sample_client_report,
        unified_report=sample_unified_report,
    )
    assert build_house_section(styles=styles, client_report=sample_client_report)
    assert build_yoga_section(
        styles=styles,
        client_report=sample_client_report,
        unified_report=sample_unified_report,
    )
    assert build_dasha_section(styles=styles, client_report=sample_client_report)
    assert build_transit_section(styles=styles, client_report=sample_client_report)
    assert build_problem_section(
        styles=styles,
        client_report=sample_client_report,
        unified_report=sample_unified_report,
    )
    assert build_remedy_section(styles=styles, client_report=sample_client_report)
    assert build_summary_section(
        styles=styles,
        client_report=sample_client_report,
        unified_report=sample_unified_report,
    )
    assert build_qr_page(
        styles=styles,
        online_report_url="https://example.com/report",
        ai_chat_url="https://example.com/chat",
    )


def test_chart_helpers_rotate_moon_reference(sample_unified_report):
    kundali = sample_unified_report["kundali"]
    rotated = _moon_chart_from_lagna(kundali)
    assert rotated[1]


def test_build_table_creates_themed_table():
    table = build_table([["A", "B"], ["1", "2"]], col_widths=[100, 100])
    assert table


def test_font_registration_reset():
    reset_font_registration_for_tests()
    regular, bold = register_pdf_fonts()
    assert regular
    assert bold


def test_chart_flowables_from_kundali(sample_unified_report):
    flowables = build_chart_flowables(
        title="Lagna",
        chart=sample_unified_report["kundali"],
        styles=_styles(),
    )
    assert len(flowables) >= 3
