"""Tests for PDF section utilities."""

from backend.app.services.pdf_engine.fonts import register_pdf_fonts
from backend.app.services.pdf_engine.section_utils import append_section_content, find_section
from backend.app.services.pdf_engine.theme import build_styles


def _styles():
    regular, bold = register_pdf_fonts()
    return build_styles(regular, bold)


def test_find_section_returns_match_or_empty():
    report = {"sections": [{"section_id": "current_dasha", "title": "Dasha"}]}
    assert find_section(report, "current_dasha")["title"] == "Dasha"
    assert find_section(report, "missing") == {}


def test_append_section_content_adds_narrative_and_facts():
    flowables = []
    styles = _styles()
    section = {
        "narrative": "Current dasha period.",
        "facts": ["Saturn mahadasha", "Venus antardasha"],
    }
    append_section_content(flowables, section, styles)
    assert len(flowables) >= 5
