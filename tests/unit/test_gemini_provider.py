"""Gemini provider tests."""

from __future__ import annotations

import json

import pytest

from ai_engine.providers.gemini.config import GeminiConfig
from ai_engine.providers.gemini.cost_tracker import CostTracker
from ai_engine.providers.gemini.structured import extract_json_object, validate_required_keys


def test_gemini_config_from_env(monkeypatch):
    monkeypatch.setenv("GEMINI_ENABLED", "true")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    config = GeminiConfig.from_env()
    assert config.enabled is True
    assert config.api_key == "test-key"


def test_cost_tracker_accumulates_usage():
    tracker = CostTracker()
    first = tracker.record_usage(model="gemini-2.0-flash", prompt_tokens=100, completion_tokens=50)
    second = tracker.record_usage(model="gemini-2.0-flash", prompt_tokens=200, completion_tokens=100)
    assert first.total_tokens == 150
    assert tracker.total_tokens == 450
    assert tracker.total_estimated_cost_usd > 0


def test_extract_json_object_from_fenced_block():
    payload = extract_json_object('```json\n{"summary": "ok"}\n```')
    assert payload["summary"] == "ok"


def test_validate_required_keys_raises():
    with pytest.raises(ValueError):
        validate_required_keys({"a": 1}, ("a", "b"))
