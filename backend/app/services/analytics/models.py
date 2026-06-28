"""Immutable analytics domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class DashboardOverview:
    """High-level platform snapshot for admin dashboards."""

    total_users: int
    active_users: int
    verified_users: int
    total_clients: int
    active_clients: int
    total_reports: int
    total_chat_queries: int
    total_revenue_paise: int
    active_subscriptions: int
    captured_payments: int
    generated_at: datetime


@dataclass(frozen=True)
class RevenueMetrics:
    """Billing and subscription revenue aggregates."""

    total_revenue_paise: int
    revenue_this_period_paise: int
    captured_payments: int
    failed_payments: int
    pending_payments: int
    refunded_payments: int
    total_orders: int
    paid_orders: int
    failed_orders: int
    pending_orders: int
    conversion_rate: float
    average_order_value_paise: int
    revenue_by_plan: tuple[tuple[str, int], ...]
    subscriptions_by_plan: tuple[tuple[str, int], ...]
    period_start: date
    generated_at: datetime


@dataclass(frozen=True)
class UserMetrics:
    """User growth, verification, and quota utilization metrics."""

    total_users: int
    active_users: int
    verified_users: int
    inactive_users: int
    unverified_users: int
    new_users_this_period: int
    users_by_role: tuple[tuple[str, int], ...]
    active_subscriptions_by_plan: tuple[tuple[str, int], ...]
    total_clients: int
    average_clients_per_user: float
    quota_usage_by_metric: tuple[tuple[str, int], ...]
    period_start: date
    generated_at: datetime


@dataclass(frozen=True)
class ReportMetrics:
    """Report generation and PDF artifact metrics."""

    total_reports: int
    reports_this_period: int
    reports_with_pdf: int
    distinct_clients_with_reports: int
    distinct_owners: int
    average_reports_per_owner: float
    reports_by_version: tuple[tuple[str, int], ...]
    pdf_by_status: tuple[tuple[str, int], ...]
    period_start: date
    generated_at: datetime


@dataclass(frozen=True)
class ChatMetrics:
    """Chat query volume, status, and token usage metrics."""

    total_queries: int
    queries_this_period: int
    answered_queries: int
    failed_queries: int
    processing_queries: int
    queries_by_type: tuple[tuple[str, int], ...]
    queries_by_status: tuple[tuple[str, int], ...]
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    average_tokens_per_query: float
    queries_by_model: tuple[tuple[str, int], ...]
    quota_consumed_this_period: int
    period_start: date
    generated_at: datetime


@dataclass(frozen=True)
class SystemMetrics:
    """Operational health indicators derived from persisted records."""

    active_sessions: int
    failed_orders: int
    expired_orders: int
    failed_pdf_generations: int
    inactive_users: int
    unverified_users: int
    chat_error_rate: float
    generated_at: datetime


@dataclass(frozen=True)
class AIMetrics:
    """AI invocation, token consumption, and model breakdown metrics."""

    total_invocations: int
    successful_invocations: int
    failed_invocations: int
    invocations_this_period: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    average_tokens_per_success: float
    invocations_by_model: tuple[tuple[str, int], ...]
    invocations_by_query_type: tuple[tuple[str, int], ...]
    invocations_without_token_data: int
    period_start: date
    generated_at: datetime


@dataclass(frozen=True)
class AnalyticsResponse:
    """Complete analytics payload composed from all metric groups."""

    overview: DashboardOverview
    revenue: RevenueMetrics
    users: UserMetrics
    reports: ReportMetrics
    chat: ChatMetrics
    system: SystemMetrics
    ai: AIMetrics
    generated_at: datetime
