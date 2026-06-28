import { AnalyticsCard } from "@/components/admin/AnalyticsCard";
import { AnalyticsGrid } from "@/components/admin/AnalyticsGrid";
import { AnalyticsSection } from "@/components/admin/AnalyticsSection";
import { ErrorAnalytics } from "@/components/admin/ErrorAnalytics";
import { LoadingAnalytics } from "@/components/admin/LoadingAnalytics";
import { StatBadge } from "@/components/admin/StatBadge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAnalytics } from "@/hooks/useAnalytics";
import {
  formatDecimal,
  formatNumber,
  formatPaise,
  formatPercent,
  isAnalyticsEmpty,
  resolveSystemStatus,
} from "@/lib/analytics-format";
import type { AnalyticsBreakdownItem, AnalyticsRevenueBreakdownItem } from "@/types/analytics";

function BreakdownList({ items, valueKey = "count" }: { items: AnalyticsBreakdownItem[]; valueKey?: "count" }) {
  if (items.length === 0) {
    return null;
  }

  return (
    <ul className="space-y-2">
      {items.map((item) => (
        <li key={item.label} className="flex items-center justify-between rounded-md border border-border/60 px-3 py-2 text-sm">
          <span className="capitalize text-muted-foreground">{item.label.replaceAll("_", " ")}</span>
          <span className="font-medium">{formatNumber(item[valueKey])}</span>
        </li>
      ))}
    </ul>
  );
}

function RevenueBreakdownList({ items }: { items: AnalyticsRevenueBreakdownItem[] }) {
  if (items.length === 0) {
    return null;
  }

  return (
    <ul className="space-y-2">
      {items.map((item) => (
        <li key={item.plan} className="flex items-center justify-between rounded-md border border-border/60 px-3 py-2 text-sm">
          <span className="capitalize text-muted-foreground">{item.plan}</span>
          <span className="font-medium">{formatPaise(item.amount_paise)}</span>
        </li>
      ))}
    </ul>
  );
}

function MetricRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-md border border-border/60 px-3 py-2 text-sm">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}

export function AdminAnalyticsPage() {
  const { overview, users, revenue, reports, chat, system, ai, isLoading, firstError, refetchAll } = useAnalytics();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader />
        <LoadingAnalytics />
      </div>
    );
  }

  if (firstError) {
    return (
      <div className="space-y-6">
        <PageHeader />
        <ErrorAnalytics error={firstError} onRetry={() => void refetchAll()} />
      </div>
    );
  }

  if (!overview.data || !users.data || !revenue.data || !reports.data || !chat.data || !system.data || !ai.data) {
    return (
      <div className="space-y-6">
        <PageHeader />
        <ErrorAnalytics error={new Error("Analytics data is unavailable.")} onRetry={() => void refetchAll()} />
      </div>
    );
  }

  const systemStatus = resolveSystemStatus(system.data);
  const empty = isAnalyticsEmpty(overview.data);

  return (
    <div className="space-y-6">
      <PageHeader generatedAt={overview.data.generated_at} />

      {empty ? (
        <Card className="border-dashed">
          <CardHeader>
            <CardTitle>No analytics activity yet</CardTitle>
            <CardDescription>
              Metrics will appear here once users, reports, chat activity, and billing data are recorded.
            </CardDescription>
          </CardHeader>
          <CardContent />
        </Card>
      ) : null}

      <AnalyticsGrid columns={4}>
        <AnalyticsCard title="Total Users" value={formatNumber(overview.data.total_users)} description={`${formatNumber(overview.data.verified_users)} verified`} />
        <AnalyticsCard title="Active Users" value={formatNumber(overview.data.active_users)} description={`${formatNumber(overview.data.total_clients)} total clients`} />
        <AnalyticsCard title="Total Reports" value={formatNumber(overview.data.total_reports)} description={`${formatNumber(overview.data.captured_payments)} captured payments`} />
        <AnalyticsCard title="Monthly Revenue" value={formatPaise(revenue.data.revenue_this_period_paise)} description={`${formatPaise(revenue.data.total_revenue_paise)} lifetime revenue`} />
      </AnalyticsGrid>

      <AnalyticsGrid columns={4}>
        <AnalyticsCard title="AI Chats" value={formatNumber(overview.data.total_chat_queries)} description={`${formatNumber(chat.data.queries_this_period)} this billing period`} />
        <AnalyticsCard title="Active Subscriptions" value={formatNumber(overview.data.active_subscriptions)} description={`${formatNumber(revenue.data.paid_orders)} paid orders`} />
        <AnalyticsCard title="Reports This Period" value={formatNumber(reports.data.reports_this_period)} description={`${formatNumber(reports.data.reports_with_pdf)} with PDF`} />
        <AnalyticsCard
          title="System Status"
          value={systemStatus.label}
          description={`${formatNumber(system.data.active_sessions)} active sessions`}
          badge={<StatBadge label={systemStatus.label} tone={systemStatus.tone} />}
        />
      </AnalyticsGrid>

      <div className="grid gap-4 xl:grid-cols-2">
        <AnalyticsSection
          title="Revenue"
          description="Payment, order, and subscription revenue aggregates."
          empty={revenue.data.captured_payments === 0 && revenue.data.total_orders === 0}
        >
          <div className="space-y-2">
            <MetricRow label="Captured payments" value={formatNumber(revenue.data.captured_payments)} />
            <MetricRow label="Conversion rate" value={formatPercent(revenue.data.conversion_rate)} />
            <MetricRow label="Average order value" value={formatPaise(revenue.data.average_order_value_paise)} />
            <MetricRow label="Failed payments" value={formatNumber(revenue.data.failed_payments)} />
          </div>
          <div className="mt-4 space-y-4">
            <div>
              <p className="mb-2 text-sm font-medium">Revenue by plan</p>
              <RevenueBreakdownList items={revenue.data.revenue_by_plan} />
            </div>
            <div>
              <p className="mb-2 text-sm font-medium">Subscriptions by plan</p>
              <BreakdownList items={revenue.data.subscriptions_by_plan} />
            </div>
          </div>
        </AnalyticsSection>

        <AnalyticsSection
          title="Users"
          description="Growth, verification, and quota utilization."
          empty={users.data.total_users === 0}
        >
          <div className="space-y-2">
            <MetricRow label="New users this period" value={formatNumber(users.data.new_users_this_period)} />
            <MetricRow label="Inactive users" value={formatNumber(users.data.inactive_users)} />
            <MetricRow label="Unverified users" value={formatNumber(users.data.unverified_users)} />
            <MetricRow label="Average clients per user" value={formatDecimal(users.data.average_clients_per_user)} />
          </div>
          <div className="mt-4 space-y-4">
            <div>
              <p className="mb-2 text-sm font-medium">Users by role</p>
              <BreakdownList items={users.data.users_by_role} />
            </div>
            <div>
              <p className="mb-2 text-sm font-medium">Quota usage by metric</p>
              <BreakdownList items={users.data.quota_usage_by_metric} />
            </div>
          </div>
        </AnalyticsSection>

        <AnalyticsSection
          title="Reports"
          description="Report generation volume and PDF coverage."
          empty={reports.data.total_reports === 0}
        >
          <div className="space-y-2">
            <MetricRow label="Distinct owners" value={formatNumber(reports.data.distinct_owners)} />
            <MetricRow label="Distinct clients" value={formatNumber(reports.data.distinct_clients_with_reports)} />
            <MetricRow label="Average reports per owner" value={formatDecimal(reports.data.average_reports_per_owner)} />
          </div>
          <div className="mt-4 space-y-4">
            <div>
              <p className="mb-2 text-sm font-medium">Reports by version</p>
              <BreakdownList items={reports.data.reports_by_version} />
            </div>
            <div>
              <p className="mb-2 text-sm font-medium">PDF by status</p>
              <BreakdownList items={reports.data.pdf_by_status} />
            </div>
          </div>
        </AnalyticsSection>

        <AnalyticsSection
          title="Chat"
          description="Chat query volume, status, and token usage."
          empty={chat.data.total_queries === 0}
        >
          <div className="space-y-2">
            <MetricRow label="Answered queries" value={formatNumber(chat.data.answered_queries)} />
            <MetricRow label="Failed queries" value={formatNumber(chat.data.failed_queries)} />
            <MetricRow label="Processing queries" value={formatNumber(chat.data.processing_queries)} />
            <MetricRow label="Quota consumed this period" value={formatNumber(chat.data.quota_consumed_this_period)} />
            <MetricRow label="Average tokens per query" value={formatDecimal(chat.data.average_tokens_per_query)} />
          </div>
          <div className="mt-4 space-y-4">
            <div>
              <p className="mb-2 text-sm font-medium">Queries by type</p>
              <BreakdownList items={chat.data.queries_by_type} />
            </div>
            <div>
              <p className="mb-2 text-sm font-medium">Queries by model</p>
              <BreakdownList items={chat.data.queries_by_model} />
            </div>
          </div>
        </AnalyticsSection>

        <AnalyticsSection
          title="AI"
          description="AI invocation counts and token consumption."
          empty={ai.data.total_invocations === 0}
        >
          <div className="space-y-2">
            <MetricRow label="Successful invocations" value={formatNumber(ai.data.successful_invocations)} />
            <MetricRow label="Failed invocations" value={formatNumber(ai.data.failed_invocations)} />
            <MetricRow label="Invocations this period" value={formatNumber(ai.data.invocations_this_period)} />
            <MetricRow label="Total tokens" value={formatNumber(ai.data.total_tokens)} />
            <MetricRow label="Without token data" value={formatNumber(ai.data.invocations_without_token_data)} />
          </div>
          <div className="mt-4 space-y-4">
            <div>
              <p className="mb-2 text-sm font-medium">Invocations by model</p>
              <BreakdownList items={ai.data.invocations_by_model} />
            </div>
            <div>
              <p className="mb-2 text-sm font-medium">Invocations by query type</p>
              <BreakdownList items={ai.data.invocations_by_query_type} />
            </div>
          </div>
        </AnalyticsSection>

        <AnalyticsSection
          title="System"
          description="Operational health indicators."
          empty={system.data.active_sessions === 0 && system.data.failed_orders === 0 && system.data.failed_pdf_generations === 0}
        >
          <div className="space-y-2">
            <MetricRow label="Failed orders" value={formatNumber(system.data.failed_orders)} />
            <MetricRow label="Expired orders" value={formatNumber(system.data.expired_orders)} />
            <MetricRow label="Failed PDF generations" value={formatNumber(system.data.failed_pdf_generations)} />
            <MetricRow label="Inactive users" value={formatNumber(system.data.inactive_users)} />
            <MetricRow label="Chat error rate" value={formatPercent(system.data.chat_error_rate)} />
          </div>
        </AnalyticsSection>
      </div>
    </div>
  );
}

function PageHeader({ generatedAt }: { generatedAt?: string }) {
  return (
    <div>
      <h2 className="text-2xl font-semibold">Admin analytics</h2>
      <p className="text-muted-foreground">
        Platform metrics for users, revenue, reports, chat, AI usage, and system health.
        {generatedAt ? ` Last updated ${new Date(generatedAt).toLocaleString()}.` : null}
      </p>
    </div>
  );
}
