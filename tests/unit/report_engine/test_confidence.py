"""Tests for report engine confidence helpers."""

from backend.app.services.report_engine.confidence import fusion_confidence, section_confidence


def test_fusion_confidence_prefers_fusion_value():
    assert fusion_confidence({"fusion": {"confidence": 0.82}}) == 0.82


def test_fusion_confidence_uses_summary_scale():
    assert fusion_confidence({"summary": {"reasoning_confidence_score": 75}}) == 0.75


def test_section_confidence_reduces_when_no_data():
    report = {"fusion": {"confidence": 0.9}}
    assert section_confidence(report, has_data=False) <= 0.35
