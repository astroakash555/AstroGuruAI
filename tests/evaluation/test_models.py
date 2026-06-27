"""Tests for intelligence evaluation models and helpers."""

from __future__ import annotations

import pytest

from backend.app.services.evaluation.models import (
    clamp_score,
    extract_engine_observations,
    observation_from_dict,
    resolve_fusion_payload,
)


class TestModelHelpers:
    def test_clamp_score_bounds(self) -> None:
        assert clamp_score(1.5) == 1.0
        assert clamp_score(-0.2) == 0.0
        assert clamp_score(0.4567) == 0.4567

    def test_observation_from_dict(self) -> None:
        payload = {
            "observation_id": "obs-1",
            "title": "Sample",
            "category": "test",
            "affected_planets": ["Mars"],
            "affected_houses": [1],
            "severity": 0.8,
            "confidence": 0.9,
        }
        snapshot = observation_from_dict("vedic", payload)
        assert snapshot.engine == "vedic"
        assert snapshot.observation_id == "obs-1"
        assert snapshot.affected_planets == ("Mars",)

    def test_observation_from_dict_uses_fusion_id(self) -> None:
        snapshot = observation_from_dict(
            "fusion",
            {"fusion_id": "fusion-1", "title": "Fused", "category": "fusion:test"},
        )
        assert snapshot.observation_id == "fusion-1"

    def test_extract_engine_observations(self, sample_unified_report) -> None:
        extracted = extract_engine_observations(sample_unified_report)
        assert set(extracted.keys()) == {"vedic", "kp", "lal_kitab"}
        assert len(extracted["vedic"]) == 1

    def test_resolve_fusion_payload_prefers_explicit(self, sample_unified_report, sample_fusion) -> None:
        explicit = {"confidence": 0.11}
        resolved = resolve_fusion_payload(sample_unified_report, explicit)
        assert resolved["confidence"] == 0.11

    def test_resolve_fusion_payload_from_report(self, sample_unified_report) -> None:
        resolved = resolve_fusion_payload(sample_unified_report, None)
        assert resolved["confidence"] == 0.86

    def test_resolve_fusion_payload_empty(self) -> None:
        assert resolve_fusion_payload({}, None) == {}

    def test_extract_engine_observations_skips_invalid_items(self) -> None:
        report = {
            "vedic": {"observations": ["invalid", {"observation_id": "ok", "title": "Ok"}]},
        }
        extracted = extract_engine_observations(report)
        assert len(extracted["vedic"]) == 1

    def test_observation_from_dict_defaults(self) -> None:
        snapshot = observation_from_dict("vedic", {})
        assert snapshot.observation_id == ""
        assert snapshot.severity == 0.0
