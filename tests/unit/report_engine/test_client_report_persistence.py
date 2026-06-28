"""Unit tests for client report persistence validation."""

from __future__ import annotations

import logging

import pytest

from backend.app.core.exceptions import ValidationError
from backend.app.services.report_engine.client_report_persistence import (
    log_client_report_section_fact_types,
    prepare_client_report_for_persistence,
    validate_client_report_sections_for_persistence,
)


def _valid_section(section_id: str = "birth_details") -> dict:
    return {
        "section_id": section_id,
        "title": "Title",
        "narrative": "Narrative",
        "facts": ["Fact line"],
        "confidence": 0.8,
        "confidence_label": "80%",
    }


def test_validate_allows_legacy_payload_without_sections():
    validate_client_report_sections_for_persistence({"problem_summary": "Marriage delay"})


def test_validate_accepts_string_array_facts():
    payload = {"sections": [_valid_section()]}
    validate_client_report_sections_for_persistence(payload)


def test_validate_rejects_dict_facts():
    section = _valid_section()
    section["facts"] = {"birth_place": "Delhi"}
    with pytest.raises(ValidationError, match="must be a list"):
        validate_client_report_sections_for_persistence({"sections": [section]})


def test_validate_rejects_string_facts():
    section = _valid_section()
    section["facts"] = "single string"
    with pytest.raises(ValidationError, match="must be a list"):
        validate_client_report_sections_for_persistence({"sections": [section]})


def test_validate_rejects_null_facts():
    section = _valid_section()
    section["facts"] = None
    with pytest.raises(ValidationError, match="must be a list"):
        validate_client_report_sections_for_persistence({"sections": [section]})


def test_validate_rejects_non_string_fact_items():
    section = _valid_section()
    section["facts"] = ["ok", {"bad": "object"}]
    with pytest.raises(ValidationError, match="only strings"):
        validate_client_report_sections_for_persistence({"sections": [section]})


def test_prepare_logs_fact_types(caplog):
    payload = {"sections": [_valid_section("moon_analysis")]}
    with caplog.at_level(logging.INFO):
        prepare_client_report_for_persistence(payload)
    assert "facts_type=list" in caplog.text
    assert "moon_analysis" in caplog.text


def test_log_client_report_section_fact_types_logs_dict_type(caplog):
    payload = {"sections": [{"section_id": "x", "facts": {"raw": "dict"}}]}
    with caplog.at_level(logging.INFO):
        log_client_report_section_fact_types(payload)
    assert "facts_type=dict" in caplog.text
