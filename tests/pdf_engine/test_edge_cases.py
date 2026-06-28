"""Additional edge-case tests for PDF engine coverage."""

from backend.app.services.pdf_engine.fonts import register_pdf_fonts
from backend.app.services.pdf_engine.house_section import build_house_section
from backend.app.services.pdf_engine.kundali_section import build_kundali_section
from backend.app.services.pdf_engine.planet_section import build_planet_section
from backend.app.services.pdf_engine.remedy_section import build_remedy_section
from backend.app.services.pdf_engine.summary_section import build_qr_page
from backend.app.services.pdf_engine.theme import build_styles
from backend.app.services.pdf_engine.yoga_section import build_yoga_section


def _styles():
    regular, bold = register_pdf_fonts()
    return build_styles(regular, bold)


def test_planet_section_falls_back_to_unified_report(sample_unified_report):
    flowables = build_planet_section(
        styles=_styles(),
        client_report={"sections": []},
        unified_report=sample_unified_report,
    )
    assert flowables


def test_house_section_without_houses():
    flowables = build_house_section(
        styles=_styles(),
        client_report={"sections": [{"section_id": "house_wise_interpretation", "facts": {"houses": []}}]},
    )
    assert flowables


def test_kundali_section_without_unified_report():
    flowables = build_kundali_section(styles=_styles(), unified_report=None)
    assert flowables


def test_yoga_section_without_present_yogas():
    flowables = build_yoga_section(
        styles=_styles(),
        client_report={"sections": [{"section_id": "yoga_analysis", "facts": {"yogas": []}}]},
        unified_report={"yogas": {"present_yogas": []}},
    )
    assert flowables


def test_remedy_section_without_remedies():
    flowables = build_remedy_section(
        styles=_styles(),
        client_report={"sections": [{"section_id": "personalized_remedies"}], "remedies": []},
    )
    assert flowables


def test_qr_page_without_urls():
    flowables = build_qr_page(styles=_styles(), online_report_url=None, ai_chat_url=None)
    assert flowables


def test_qr_page_handles_qr_failure(monkeypatch):
    import qrcode

    def _fail(_url):
        raise RuntimeError("qr failed")

    monkeypatch.setattr(qrcode, "make", _fail)
    flowables = build_qr_page(
        styles=_styles(),
        online_report_url="https://example.com/report",
        ai_chat_url=None,
    )
    assert flowables
