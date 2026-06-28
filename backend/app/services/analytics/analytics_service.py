"""Analytics aggregation service."""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from backend.app.billing.usage import current_period_start
from backend.app.models.client import Client
from backend.app.models.enums import (
    OrderStatus,
    PaymentStatus,
    PDFGenerationStatus,
    QueryStatus,
    SubscriptionStatus,
    UsageMetric,
)
from backend.app.models.generated_pdf import GeneratedPDF
from backend.app.models.order import Order
from backend.app.models.payment import Payment
from backend.app.models.refresh_token import RefreshToken
from backend.app.models.report import Report
from backend.app.models.subscription import Subscription
from backend.app.models.usage_quota import UsageQuota
from backend.app.models.user import User
from backend.app.models.user_query import UserQuery
from backend.app.services.analytics.constants import (
    DEFAULT_AMOUNT_PAISE,
    DEFAULT_COUNT,
    enum_value_label,
    period_start_datetime,
    safe_average,
    safe_rate,
    utc_now,
)
from backend.app.services.analytics.models import (
    AIMetrics,
    AnalyticsResponse,
    ChatMetrics,
    DashboardOverview,
    ReportMetrics,
    RevenueMetrics,
    SystemMetrics,
    UserMetrics,
)


class AnalyticsService:
    """Aggregate platform metrics from existing persistence tables."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_dashboard_overview(self) -> DashboardOverview:
        """Return a high-level snapshot of platform activity."""
        generated_at = utc_now()
        total_revenue_paise = await self._sum_column(
            Payment,
            Payment.amount_paise,
            Payment.status == PaymentStatus.CAPTURED,
        )

        return DashboardOverview(
            total_users=await self._count_rows(User),
            active_users=await self._count_rows(User, User.is_active.is_(True)),
            verified_users=await self._count_rows(User, User.is_verified.is_(True)),
            total_clients=await self._count_rows(Client),
            active_clients=await self._count_rows(Client, Client.is_active.is_(True)),
            total_reports=await self._count_rows(Report),
            total_chat_queries=await self._count_rows(UserQuery),
            total_revenue_paise=total_revenue_paise,
            active_subscriptions=await self._count_rows(
                Subscription,
                Subscription.status == SubscriptionStatus.ACTIVE,
            ),
            captured_payments=await self._count_rows(
                Payment,
                Payment.status == PaymentStatus.CAPTURED,
            ),
            generated_at=generated_at,
        )

    async def get_revenue_metrics(self) -> RevenueMetrics:
        """Return billing and subscription revenue aggregates."""
        generated_at = utc_now()
        period_start = current_period_start(generated_at)
        period_start_dt = period_start_datetime(period_start)

        captured_payments = await self._count_rows(Payment, Payment.status == PaymentStatus.CAPTURED)
        paid_orders = await self._count_rows(Order, Order.status == OrderStatus.PAID)
        total_orders = await self._count_rows(Order)
        total_revenue_paise = await self._sum_column(
            Payment,
            Payment.amount_paise,
            Payment.status == PaymentStatus.CAPTURED,
        )
        revenue_this_period_paise = await self._sum_column(
            Payment,
            Payment.amount_paise,
            Payment.status == PaymentStatus.CAPTURED,
            Payment.paid_at.is_not(None),
            Payment.paid_at >= period_start_dt,
        )

        return RevenueMetrics(
            total_revenue_paise=total_revenue_paise,
            revenue_this_period_paise=revenue_this_period_paise,
            captured_payments=captured_payments,
            failed_payments=await self._count_rows(Payment, Payment.status == PaymentStatus.FAILED),
            pending_payments=await self._count_rows(Payment, Payment.status == PaymentStatus.PENDING),
            refunded_payments=await self._count_rows(Payment, Payment.status == PaymentStatus.REFUNDED),
            total_orders=total_orders,
            paid_orders=paid_orders,
            failed_orders=await self._count_rows(Order, Order.status == OrderStatus.FAILED),
            pending_orders=await self._count_rows(Order, Order.status == OrderStatus.CREATED),
            conversion_rate=safe_rate(paid_orders, total_orders),
            average_order_value_paise=int(
                safe_average(total_revenue_paise, captured_payments)
            ),
            revenue_by_plan=await self._revenue_by_plan(),
            subscriptions_by_plan=await self._group_count(
                Subscription.plan,
                Subscription,
                Subscription.status == SubscriptionStatus.ACTIVE,
            ),
            period_start=period_start,
            generated_at=generated_at,
        )

    async def get_user_metrics(self) -> UserMetrics:
        """Return user growth and quota utilization metrics."""
        generated_at = utc_now()
        period_start = current_period_start(generated_at)
        period_start_dt = period_start_datetime(period_start)

        total_users = await self._count_rows(User)
        active_users = await self._count_rows(User, User.is_active.is_(True))
        verified_users = await self._count_rows(User, User.is_verified.is_(True))
        total_clients = await self._count_rows(Client)

        return UserMetrics(
            total_users=total_users,
            active_users=active_users,
            verified_users=verified_users,
            inactive_users=await self._count_rows(User, User.is_active.is_(False)),
            unverified_users=await self._count_rows(User, User.is_verified.is_(False)),
            new_users_this_period=await self._count_rows(User, User.created_at >= period_start_dt),
            users_by_role=await self._group_count(User.role, User),
            active_subscriptions_by_plan=await self._group_count(
                Subscription.plan,
                Subscription,
                Subscription.status == SubscriptionStatus.ACTIVE,
            ),
            total_clients=total_clients,
            average_clients_per_user=safe_average(total_clients, total_users),
            quota_usage_by_metric=await self._quota_usage_by_metric(period_start),
            period_start=period_start,
            generated_at=generated_at,
        )

    async def get_report_metrics(self) -> ReportMetrics:
        """Return report generation and PDF artifact metrics."""
        generated_at = utc_now()
        period_start = current_period_start(generated_at)
        period_start_dt = period_start_datetime(period_start)

        total_reports = await self._count_rows(Report)
        distinct_owners = await self._count_distinct(Report, Report.owner_id, Report.owner_id.is_not(None))

        return ReportMetrics(
            total_reports=total_reports,
            reports_this_period=await self._count_rows(Report, Report.generated_at >= period_start_dt),
            reports_with_pdf=await self._count_rows(Report, Report.pdf_path.is_not(None)),
            distinct_clients_with_reports=await self._count_distinct(
                Report,
                Report.client_id,
                Report.client_id.is_not(None),
            ),
            distinct_owners=distinct_owners,
            average_reports_per_owner=safe_average(total_reports, distinct_owners),
            reports_by_version=await self._group_count(Report.version, Report),
            pdf_by_status=await self._group_count(GeneratedPDF.status, GeneratedPDF),
            period_start=period_start,
            generated_at=generated_at,
        )

    async def get_chat_metrics(self) -> ChatMetrics:
        """Return chat query volume and token usage metrics."""
        generated_at = utc_now()
        period_start = current_period_start(generated_at)
        period_start_dt = period_start_datetime(period_start)

        total_queries = await self._count_rows(UserQuery)
        total_tokens = await self._sum_column(
            UserQuery,
            UserQuery.total_tokens,
            UserQuery.total_tokens.is_not(None),
        )

        return ChatMetrics(
            total_queries=total_queries,
            queries_this_period=await self._count_rows(UserQuery, UserQuery.created_at >= period_start_dt),
            answered_queries=await self._count_rows(UserQuery, UserQuery.status == QueryStatus.ANSWERED),
            failed_queries=await self._count_rows(UserQuery, UserQuery.status == QueryStatus.FAILED),
            processing_queries=await self._count_rows(UserQuery, UserQuery.status == QueryStatus.PROCESSING),
            queries_by_type=await self._group_count(UserQuery.query_type, UserQuery),
            queries_by_status=await self._group_count(UserQuery.status, UserQuery),
            total_prompt_tokens=await self._sum_column(
                UserQuery,
                UserQuery.prompt_tokens,
                UserQuery.prompt_tokens.is_not(None),
            ),
            total_completion_tokens=await self._sum_column(
                UserQuery,
                UserQuery.completion_tokens,
                UserQuery.completion_tokens.is_not(None),
            ),
            total_tokens=total_tokens,
            average_tokens_per_query=safe_average(
                total_tokens,
                await self._count_rows(UserQuery, UserQuery.total_tokens.is_not(None)),
            ),
            queries_by_model=await self._group_count(UserQuery.ai_model, UserQuery),
            quota_consumed_this_period=await self._quota_total_for_metric(
                UsageMetric.CHAT_MESSAGES,
                period_start,
            ),
            period_start=period_start,
            generated_at=generated_at,
        )

    async def get_system_metrics(self) -> SystemMetrics:
        """Return operational health indicators."""
        generated_at = utc_now()
        total_queries = await self._count_rows(UserQuery)
        failed_queries = await self._count_rows(UserQuery, UserQuery.status == QueryStatus.FAILED)

        return SystemMetrics(
            active_sessions=await self._count_rows(
                RefreshToken,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > generated_at,
            ),
            failed_orders=await self._count_rows(Order, Order.status == OrderStatus.FAILED),
            expired_orders=await self._count_rows(Order, Order.status == OrderStatus.EXPIRED),
            failed_pdf_generations=await self._count_rows(
                GeneratedPDF,
                GeneratedPDF.status == PDFGenerationStatus.FAILED,
            ),
            inactive_users=await self._count_rows(User, User.is_active.is_(False)),
            unverified_users=await self._count_rows(User, User.is_verified.is_(False)),
            chat_error_rate=safe_rate(failed_queries, total_queries),
            generated_at=generated_at,
        )

    async def get_ai_metrics(self) -> AIMetrics:
        """Return AI invocation and token consumption metrics."""
        generated_at = utc_now()
        period_start = current_period_start(generated_at)
        period_start_dt = period_start_datetime(period_start)

        successful_invocations = await self._count_rows(UserQuery, UserQuery.status == QueryStatus.ANSWERED)
        total_prompt_tokens = await self._sum_column(
            UserQuery,
            UserQuery.prompt_tokens,
            UserQuery.prompt_tokens.is_not(None),
        )
        total_completion_tokens = await self._sum_column(
            UserQuery,
            UserQuery.completion_tokens,
            UserQuery.completion_tokens.is_not(None),
        )
        total_tokens = await self._sum_column(UserQuery, UserQuery.total_tokens, UserQuery.total_tokens.is_not(None))

        return AIMetrics(
            total_invocations=await self._count_rows(UserQuery),
            successful_invocations=successful_invocations,
            failed_invocations=await self._count_rows(UserQuery, UserQuery.status == QueryStatus.FAILED),
            invocations_this_period=await self._count_rows(UserQuery, UserQuery.created_at >= period_start_dt),
            total_prompt_tokens=total_prompt_tokens,
            total_completion_tokens=total_completion_tokens,
            total_tokens=total_tokens,
            average_tokens_per_success=safe_average(total_tokens, successful_invocations),
            invocations_by_model=await self._group_count(UserQuery.ai_model, UserQuery),
            invocations_by_query_type=await self._group_count(UserQuery.query_type, UserQuery),
            invocations_without_token_data=await self._count_rows(UserQuery, UserQuery.total_tokens.is_(None)),
            period_start=period_start,
            generated_at=generated_at,
        )

    async def get_analytics_response(self) -> AnalyticsResponse:
        """Compose all analytics metric groups into a single response."""
        generated_at = utc_now()
        return AnalyticsResponse(
            overview=await self.get_dashboard_overview(),
            revenue=await self.get_revenue_metrics(),
            users=await self.get_user_metrics(),
            reports=await self.get_report_metrics(),
            chat=await self.get_chat_metrics(),
            system=await self.get_system_metrics(),
            ai=await self.get_ai_metrics(),
            generated_at=generated_at,
        )

    async def _count_rows(self, model: type[object], *filters: ColumnElement[bool]) -> int:
        stmt = select(func.count()).select_from(model)
        if filters:
            stmt = stmt.where(*filters)
        return await self._scalar_int(stmt)

    async def _count_distinct(
        self,
        model: type[object],
        column: object,
        *filters: ColumnElement[bool],
    ) -> int:
        stmt = select(func.count(func.distinct(column))).select_from(model)
        if filters:
            stmt = stmt.where(*filters)
        return await self._scalar_int(stmt)

    async def _sum_column(
        self,
        model: type[object],
        column: object,
        *filters: ColumnElement[bool],
    ) -> int:
        stmt = select(func.coalesce(func.sum(column), DEFAULT_AMOUNT_PAISE)).select_from(model)
        if filters:
            stmt = stmt.where(*filters)
        return await self._scalar_int(stmt)

    async def _group_count(
        self,
        column: object,
        model: type[object],
        *filters: ColumnElement[bool],
    ) -> tuple[tuple[str, int], ...]:
        stmt = select(column, func.count()).select_from(model).group_by(column)
        if filters:
            stmt = stmt.where(*filters)
        result = await self._session.execute(stmt)
        rows = sorted(
            ((enum_value_label(row[0]), int(row[1] or DEFAULT_COUNT)) for row in result.all()),
            key=lambda item: item[0],
        )
        return tuple(rows)

    async def _revenue_by_plan(self) -> tuple[tuple[str, int], ...]:
        stmt = (
            select(Order.plan, func.coalesce(func.sum(Payment.amount_paise), DEFAULT_AMOUNT_PAISE))
            .select_from(Payment)
            .join(Order, Payment.order_id == Order.id)
            .where(Payment.status == PaymentStatus.CAPTURED)
            .group_by(Order.plan)
        )
        result = await self._session.execute(stmt)
        rows = sorted(
            ((enum_value_label(row[0]), int(row[1] or DEFAULT_AMOUNT_PAISE)) for row in result.all()),
            key=lambda item: item[0],
        )
        return tuple(rows)

    async def _quota_usage_by_metric(self, period_start: date) -> tuple[tuple[str, int], ...]:
        stmt = (
            select(UsageQuota.metric, func.coalesce(func.sum(UsageQuota.used_count), DEFAULT_COUNT))
            .select_from(UsageQuota)
            .where(UsageQuota.period_start == period_start)
            .group_by(UsageQuota.metric)
        )
        result = await self._session.execute(stmt)
        rows = sorted(
            ((enum_value_label(row[0]), int(row[1] or DEFAULT_COUNT)) for row in result.all()),
            key=lambda item: item[0],
        )
        return tuple(rows)

    async def _quota_total_for_metric(self, metric: UsageMetric, period_start: date) -> int:
        stmt = (
            select(func.coalesce(func.sum(UsageQuota.used_count), DEFAULT_COUNT))
            .select_from(UsageQuota)
            .where(
                UsageQuota.metric == metric,
                UsageQuota.period_start == period_start,
            )
        )
        return await self._scalar_int(stmt)

    async def _scalar_int(self, stmt: object) -> int:
        result = await self._session.execute(stmt)  # type: ignore[arg-type]
        value = result.scalar_one()
        return int(value or DEFAULT_COUNT)
