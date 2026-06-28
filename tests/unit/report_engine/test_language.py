"""Tests for report language helpers."""

from backend.app.services.report_engine.language import format_degree, localize
from backend.app.services.report_engine.types import ReportLanguage


def test_localize_hindi_default():
    assert localize(ReportLanguage.HINDI, "नमस्ते", "Hello") == "नमस्ते"


def test_localize_english():
    assert localize(ReportLanguage.ENGLISH, "नमस्ते", "Hello") == "Hello"


def test_format_degree_hinglish():
    text = format_degree(ReportLanguage.HINGLISH, 7.9)
    assert "7°" in text
