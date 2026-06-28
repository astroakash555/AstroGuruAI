"""Subscription plan definitions and monthly limits."""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.models.enums import SubscriptionPlan, UsageMetric


@dataclass(frozen=True)
class PlanDefinition:
    plan: SubscriptionPlan
    name: str
    description: str
    price_paise: int
    currency: str
    limits: dict[UsageMetric, int | None]
    features: tuple[str, ...]


UNLIMITED: int | None = None


PLAN_DEFINITIONS: dict[SubscriptionPlan, PlanDefinition] = {
    SubscriptionPlan.FREE: PlanDefinition(
        plan=SubscriptionPlan.FREE,
        name="Free",
        description="Get started with core astrology tools.",
        price_paise=0,
        currency="INR",
        limits={
            UsageMetric.REPORTS: 5,
            UsageMetric.CHAT_MESSAGES: 20,
            UsageMetric.CLIENTS: 10,
        },
        features=(
            "5 reports per month",
            "20 chat messages per month",
            "Up to 10 clients",
        ),
    ),
    SubscriptionPlan.PRO: PlanDefinition(
        plan=SubscriptionPlan.PRO,
        name="Pro",
        description="For active practitioners managing a growing practice.",
        price_paise=99900,
        currency="INR",
        limits={
            UsageMetric.REPORTS: 50,
            UsageMetric.CHAT_MESSAGES: 500,
            UsageMetric.CLIENTS: 100,
        },
        features=(
            "50 reports per month",
            "500 chat messages per month",
            "Up to 100 clients",
            "Priority support",
        ),
    ),
    SubscriptionPlan.PREMIUM: PlanDefinition(
        plan=SubscriptionPlan.PREMIUM,
        name="Premium",
        description="Unlimited access for high-volume professionals.",
        price_paise=249900,
        currency="INR",
        limits={
            UsageMetric.REPORTS: UNLIMITED,
            UsageMetric.CHAT_MESSAGES: UNLIMITED,
            UsageMetric.CLIENTS: UNLIMITED,
        },
        features=(
            "Unlimited reports",
            "Unlimited chat",
            "Unlimited clients",
            "Dedicated support",
        ),
    ),
}


def get_plan_definition(plan: SubscriptionPlan) -> PlanDefinition:
    return PLAN_DEFINITIONS[plan]


def get_limit(plan: SubscriptionPlan, metric: UsageMetric) -> int | None:
    return PLAN_DEFINITIONS[plan].limits[metric]
