"""Validation and logging for persisted client report JSON."""

from __future__ import annotations

import logging
from typing import Any

from backend.app.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


def validate_client_report_sections_for_persistence(client_report: dict[str, Any]) -> None:
    """Ensure every persisted section exposes facts as a string array."""
    sections = client_report.get("sections")
    if not sections:
        return

    if not isinstance(sections, list):
        raise ValidationError("client_report.sections must be a list when present.")

    for section in sections:
        if not isinstance(section, dict):
            raise ValidationError("Each client_report section must be an object.")
        section_id = str(section.get("section_id") or "<unknown>")
        facts = section.get("facts")
        if not isinstance(facts, list):
            raise ValidationError(
                f"Section '{section_id}' facts must be a list of strings before persistence, "
                f"got {type(facts).__name__}."
            )
        if any(not isinstance(line, str) for line in facts):
            raise ValidationError(
                f"Section '{section_id}' facts must contain only strings before persistence."
            )


def log_client_report_section_fact_types(client_report: dict[str, Any]) -> None:
    """Log Python types for section facts immediately before database persistence."""
    for section in client_report.get("sections") or []:
        if not isinstance(section, dict):
            continue
        facts = section.get("facts")
        logger.info(
            "Persisting client_report section facts: section_id=%s facts_type=%s",
            section.get("section_id"),
            type(facts).__name__,
        )


def prepare_client_report_for_persistence(client_report: dict[str, Any]) -> None:
    """Log and validate client report payload before it is written to the database."""
    log_client_report_section_fact_types(client_report)
    validate_client_report_sections_for_persistence(client_report)
