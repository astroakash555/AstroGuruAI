"""Font registration tests."""

from pathlib import Path

from backend.app.services.pdf_engine import fonts


def test_font_registration_falls_back_to_helvetica(monkeypatch, tmp_path):
    fonts.reset_font_registration_for_tests()
    fake_font = tmp_path / "fake.ttf"
    fake_font.write_bytes(b"not-a-font")
    monkeypatch.setattr(fonts, "_candidate_font_paths", lambda: [fake_font])
    regular, bold = fonts.register_pdf_fonts()
    assert regular == "Helvetica"
    assert bold == "Helvetica-Bold"
