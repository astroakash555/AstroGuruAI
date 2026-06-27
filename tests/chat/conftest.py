"""Shared fixtures for chat tests."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from backend.app.models.enums import QueryStatus, QueryType
from backend.app.services.chat.models import ChatMessage


@pytest.fixture
def report_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def client_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def sample_unified_report() -> dict:
    return {
        "version": "unified_report_v2",
        "generated_at": datetime(2026, 6, 15, 12, 0, tzinfo=timezone.utc).isoformat(),
        "subject": {"birth_place": "Delhi", "timezone": "Asia/Kolkata", "client_id": None},
        "summary": {
            "lagna_sign": "Aries",
            "moon_sign": "Cancer",
            "current_mahadasha": "Saturn",
            "current_antardasha": "Mercury",
        },
        "problem_analysis": {
            "category": {"category": "marriage"},
            "severity": {"level": "high"},
        },
        "consultation_brain": {
            "executive_summary": "Marriage delay is the dominant theme.",
            "overall_confidence": 0.8,
            "sections": [
                {
                    "section_id": "marriage",
                    "title": "Marriage",
                    "current_situation": "Venus pressure is delaying marriage.",
                    "root_cause": "Afflicted 7th lord.",
                    "positive_factors": ["Jupiter aspect support"],
                    "challenges": ["Saturn delay"],
                    "timeline": "Improvement after Venus antardasha.",
                    "actionable_advice": ["Perform Venus pacification on Fridays."],
                    "confidence": 0.82,
                },
                {
                    "section_id": "career",
                    "title": "Career",
                    "current_situation": "Steady professional growth.",
                    "root_cause": "Strong 10th house support.",
                    "positive_factors": ["Saturn discipline"],
                    "challenges": ["Slow promotion cycle"],
                    "timeline": "Better gains during Mercury antardasha.",
                    "actionable_advice": ["Avoid impulsive job changes."],
                    "confidence": 0.75,
                },
            ],
            "priorities": [{"rank": 1, "title": "Marriage focus", "explanation": "Priority", "domain": "marriage", "confidence": 0.8}],
            "strengths": [],
            "risks": [],
        },
        "fusion": {
            "confidence": 0.79,
            "observations": [
                {
                    "title": "Venus relationship pressure",
                    "explanation": "Venus affliction affects partnership timing.",
                    "category": "vedic:relationship",
                    "affected_planets": ["Venus"],
                    "affected_houses": [7],
                    "severity": 0.7,
                    "confidence": 0.8,
                }
            ],
            "root_causes": [{"title": "Venus pressure", "explanation": "Primary marriage delay factor.", "confidence": 0.8}],
            "conflicts": [],
            "recommendations": [
                {
                    "title": "Strengthen Venus",
                    "explanation": "Use Venus remedies during the current dasha window.",
                    "priority": "high",
                    "confidence": 0.84,
                }
            ],
        },
        "vedic": {
            "metadata": {"engine": "vedic_intelligence_v1"},
            "observations": [
                {
                    "title": "7th house pressure",
                    "explanation": "Marriage houses under stress.",
                    "category": "vedic:relationship",
                    "affected_planets": ["Venus"],
                    "affected_houses": [7],
                    "severity": 0.72,
                    "confidence": 0.81,
                }
            ],
        },
        "kp": {
            "metadata": {"engine": "kp_intelligence_v1"},
            "observations": [],
            "event_timing": [{"event": "Marriage", "support_level": "moderate"}],
        },
        "lal_kitab_intelligence": {
            "metadata": {"engine": "lal_kitab_intelligence_v1"},
            "observations": [],
            "remedies": [{"title": "Donate white items on Friday"}],
        },
        "dasha": {
            "system": "vimshottari",
            "moon": {"nakshatra": "Pushya"},
            "current": {
                "mahadasha": {"lord": "Saturn"},
                "antardasha": {"lord": "Mercury"},
            },
            "summary": {"active_level": "antardasha"},
        },
        "transits": {
            "metadata": {"engine": "transit_engine_v1", "reference_date": "2026-06-15", "planets_analyzed": ["Saturn", "Jupiter"]},
            "summary": {"headline": "Saturn transiting 7th house"},
            "significant_transits": [{"planet": "Saturn", "effect": "relationship pressure"}],
        },
    }


@pytest.fixture
def sample_report(report_id, client_id, sample_unified_report):
    return SimpleNamespace(
        id=report_id,
        client_id=client_id,
        birth_detail_id=uuid.uuid4(),
        version="unified_report_v2",
        unified_report_json=sample_unified_report,
    )


@pytest.fixture
def mock_report_repository(sample_report):
    repository = AsyncMock()
    repository.get_report.return_value = sample_report
    return repository


@pytest.fixture
def mock_user_query_repository():
    repository = AsyncMock()
    query = SimpleNamespace(id=uuid.uuid4())
    repository.create_query.return_value = query
    repository.mark_answered.return_value = query
    return repository


@pytest.fixture
def mock_llm_provider():
    provider = AsyncMock()
    provider.is_available = True
    provider.generate_answer.return_value = SimpleNamespace(
        content="Marriage timing improves after Venus support strengthens.",
        model="gemini-2.0-flash",
        metadata={
            "provider": "gemini",
            "prompt_tokens": 120,
            "completion_tokens": 45,
            "total_tokens": 165,
        },
    )
    return provider


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    return session
