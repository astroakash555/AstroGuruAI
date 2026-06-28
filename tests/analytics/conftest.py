"""Analytics test fixtures."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from backend.app.services.analytics.analytics_service import AnalyticsService


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def analytics_service(mock_session):
    return AnalyticsService(mock_session)
