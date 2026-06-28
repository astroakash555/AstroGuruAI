"""Tests for usage quota service."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.billing.usage import UsageService, current_period_start
from backend.app.core.config import get_settings
from backend.app.core.exceptions import QuotaExceededError
from backend.app.models.enums import SubscriptionPlan, UsageMetric


@pytest.mark.asyncio
async def test_check_quota_allows_within_limit(usage_service, mock_subscriptions, mock_quotas):
    user_id = uuid.uuid4()
    mock_subscriptions.get_active_for_user.return_value = MagicMock(plan=SubscriptionPlan.FREE)
    quota = MagicMock(used_count=2)
    mock_quotas.get_or_create.return_value = quota

    await usage_service.check_quota(user_id, UsageMetric.REPORTS)


@pytest.mark.asyncio
async def test_check_quota_blocks_when_limit_reached(usage_service, mock_subscriptions, mock_quotas):
    user_id = uuid.uuid4()
    mock_subscriptions.get_active_for_user.return_value = MagicMock(plan=SubscriptionPlan.FREE)
    quota = MagicMock(used_count=5)
    mock_quotas.get_or_create.return_value = quota

    with pytest.raises(QuotaExceededError):
        await usage_service.check_quota(user_id, UsageMetric.REPORTS)


@pytest.mark.asyncio
async def test_premium_plan_skips_quota(usage_service, mock_subscriptions):
    user_id = uuid.uuid4()
    mock_subscriptions.get_active_for_user.return_value = MagicMock(plan=SubscriptionPlan.PREMIUM)
    await usage_service.check_quota(user_id, UsageMetric.REPORTS)


@pytest.mark.asyncio
async def test_consume_increments_and_commits(usage_service, mock_subscriptions, mock_quotas, mock_session):
    user_id = uuid.uuid4()
    mock_subscriptions.get_active_for_user.return_value = MagicMock(plan=SubscriptionPlan.PRO)
    quota = MagicMock(used_count=1)
    mock_quotas.get_or_create.return_value = quota

    await usage_service.consume(user_id, UsageMetric.REPORTS)
    mock_quotas.increment.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


def test_current_period_start():
    moment = datetime(2026, 6, 15, tzinfo=UTC)
    assert current_period_start(moment) == date(2026, 6, 1)


@pytest.mark.asyncio
async def test_check_quota_bypassed_when_debug_enabled(
    usage_service,
    mock_subscriptions,
    mock_quotas,
    monkeypatch,
):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEBUG", "true")
    get_settings.cache_clear()

    user_id = uuid.uuid4()
    mock_subscriptions.get_active_for_user.return_value = MagicMock(plan=SubscriptionPlan.FREE)
    quota = MagicMock(used_count=999)
    mock_quotas.get_or_create.return_value = quota

    await usage_service.check_quota(user_id, UsageMetric.REPORTS)
    mock_quotas.get_or_create.assert_not_awaited()


@pytest.mark.asyncio
async def test_check_quota_bypassed_in_development_environment(
    usage_service,
    mock_subscriptions,
    mock_quotas,
    monkeypatch,
):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DEBUG", "false")
    get_settings.cache_clear()

    user_id = uuid.uuid4()
    mock_subscriptions.get_active_for_user.return_value = MagicMock(plan=SubscriptionPlan.FREE)
    quota = MagicMock(used_count=999)
    mock_quotas.get_or_create.return_value = quota

    await usage_service.check_quota(user_id, UsageMetric.REPORTS)
    mock_quotas.get_or_create.assert_not_awaited()


@pytest.mark.asyncio
async def test_consume_skipped_in_development_environment(
    usage_service,
    mock_subscriptions,
    mock_quotas,
    mock_session,
    monkeypatch,
):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DEBUG", "false")
    get_settings.cache_clear()

    await usage_service.consume(uuid.uuid4(), UsageMetric.REPORTS)
    mock_quotas.increment.assert_not_awaited()
    mock_session.commit.assert_not_awaited()
