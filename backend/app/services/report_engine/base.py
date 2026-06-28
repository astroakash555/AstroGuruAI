"""Shared helpers for report section builders."""

from __future__ import annotations

from typing import Any

from backend.app.services.report_engine.types import ReportLanguage, ReportSection


def planet_lookup(kundali: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Index kundali planets by name."""
    return {planet["name"]: planet for planet in kundali.get("planets", [])}


def moon_planet(kundali: dict[str, Any]) -> dict[str, Any] | None:
    planets = planet_lookup(kundali)
    return planets.get("Moon")


def section(
    *,
    section_id: str,
    title: str,
    narrative: str,
    facts: dict[str, Any],
    confidence: float,
) -> ReportSection:
    return ReportSection(
        section_id=section_id,
        title=title,
        narrative=narrative,
        facts=facts,
        confidence=round(max(0.0, min(1.0, confidence)), 4),
    )


def join_lines(lines: list[str]) -> str:
    return "\n".join(line for line in lines if line)
