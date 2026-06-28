"""Monthly usage tracking and quota enforcement."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.billing.plans import get_limit, get_plan_definition
from backend.app.billing.repositories import SubscriptionRepository, UsageQuotaRepository
from backend.app.core.config import get_settings
from backend.app.core.exceptions import QuotaExceededError
from backend.app.models.enums import SubscriptionPlan, SubscriptionStatus, UsageMetric


def current_period_start(now: datetime | None = None) -> date:
    """Return the first day of the current UTC billing month."""
    moment = now or datetime.now(UTC)
    return date(moment.year, moment.month, 1)


def next_period_end(now: datetime | None = None) -> datetime:
    moment = now or datetime.now(UTC)
    if moment.month == 12:
        return datetime(moment.year + 1, 1, 1, tzinfo=UTC)
    return datetime(moment.year, moment.month + 1, 1, tzinfo=UTC)


class UsageService:
    """Track and enforce subscription usage limits."""

    def __init__(
        self,
        session: AsyncSession,
        *,
        subscriptions: SubscriptionRepository | None = None,
        quotas: UsageQuotaRepository | None = None,
    ) -> None:
        self._session = session
        self._subscriptions = subscriptions or SubscriptionRepository(session)
        self._quotas = quotas or UsageQuotaRepository(session)

    async def ensure_free_subscription(self, user_id: uuid.UUID) -> None:
        existing = await self._subscriptions.get_active_for_user(user_id)
        if existing is not None:
            return

        now = datetime.now(UTC)
        await self._subscriptions.create(
            user_id=user_id,
            plan=SubscriptionPlan.FREE,
            current_period_start=now,
            current_period_end=next_period_end(now),
            status=SubscriptionStatus.ACTIVE,
        )
        period = current_period_start(now)
        for metric in UsageMetric:
            await self._quotas.get_or_create(user_id=user_id, metric=metric, period_start=period)

    async def get_active_plan(self, user_id: uuid.UUID) -> SubscriptionPlan:
        await self.ensure_free_subscription(user_id)
        subscription = await self._subscriptions.get_active_for_user(user_id)
        if subscription is None:
            return SubscriptionPlan.FREE
        return subscription.plan

    async def get_usage_summary(self, user_id: uuid.UUID) -> dict:
        plan = await self.get_active_plan(user_id)
        period = current_period_start()
        quotas = await self._quotas.list_for_user_period(user_id, period)
        quota_map = {quota.metric: quota.used_count for quota in quotas}
        plan_def = get_plan_definition(plan)

        metrics = []
        for metric in UsageMetric:
            limit = plan_def.limits[metric]
            used = quota_map.get(metric, 0)
            metrics.append(
                {
                    "metric": metric.value,
                    "used": used,
                    "limit": limit,
                    "remaining": None if limit is None else max(limit - used, 0),
                }
            )

        return {
            "plan": plan.value,
            "period_start": period.isoformat(),
            "metrics": metrics,
        }

    async def check_quota(self, user_id: uuid.UUID, metric: UsageMetric) -> None:
        if not get_settings().quota_enforcement_enabled:
            return

        plan = await self.get_active_plan(user_id)
        limit = get_limit(plan, metric)
        if limit is None:
            return

        period = current_period_start()
        quota = await self._quotas.get_or_create(user_id=user_id, metric=metric, period_start=period)
        if quota.used_count >= limit:
            raise QuotaExceededError(
                f"Monthly {metric.value.replace('_', ' ')} limit reached for the {plan.value} plan."
            )

    async def consume(self, user_id: uuid.UUID, metric: UsageMetric, amount: int = 1) -> None:
        if not get_settings().quota_enforcement_enabled:
            return

        await self.check_quota(user_id, metric)
        period = current_period_start()
        quota = await self._quotas.get_or_create(user_id=user_id, metric=metric, period_start=period)
        await self._quotas.increment(quota, amount)
        await self._session.commit()

    async def reset_monthly_quotas(self, user_id: uuid.UUID) -> None:
        """Explicit monthly reset helper (also happens lazily via new period keys)."""
        period = current_period_start()
        for metric in UsageMetric:
            await self._quotas.get_or_create(user_id=user_id, metric=metric, period_start=period)
