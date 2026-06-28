"""Tests for subscription plan definitions."""

from backend.app.billing.plans import PLAN_DEFINITIONS, get_limit, get_plan_definition
from backend.app.models.enums import SubscriptionPlan, UsageMetric


def test_plan_definitions_cover_all_plans():
    assert set(PLAN_DEFINITIONS) == set(SubscriptionPlan)


def test_free_plan_has_limits():
    plan = get_plan_definition(SubscriptionPlan.FREE)
    assert plan.price_paise == 0
    assert get_limit(SubscriptionPlan.FREE, UsageMetric.REPORTS) == 5


def test_premium_plan_is_unlimited():
    assert get_limit(SubscriptionPlan.PREMIUM, UsageMetric.REPORTS) is None
