"""Language templates for report narration (no astrology inference)."""

from __future__ import annotations

from backend.app.services.report_engine.types import ReportLanguage


def localize(language: ReportLanguage, hi: str, en: str, hinglish: str | None = None) -> str:
    """Pick localized text for the requested report language."""
    if language == ReportLanguage.ENGLISH:
        return en
    if language == ReportLanguage.HINGLISH:
        return hinglish or f"{hi} ({en})"
    return hi


def format_degree(language: ReportLanguage, value: float) -> str:
    degrees = int(value)
    minutes = int(round((value - degrees) * 60))
    if language == ReportLanguage.ENGLISH:
        return f"{degrees}°{minutes:02d}'"
    if language == ReportLanguage.HINGLISH:
        return f"{degrees}°{minutes:02d}' ({degrees} ansh {minutes} kala)"
    return f"{degrees}°{minutes:02d}'"
