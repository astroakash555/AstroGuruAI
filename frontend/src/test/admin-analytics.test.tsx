import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axios from "axios";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { analyticsApi } from "@/api/analytics";
import { AnalyticsCard } from "@/components/admin/AnalyticsCard";
import { AnalyticsGrid } from "@/components/admin/AnalyticsGrid";
import { AnalyticsSection } from "@/components/admin/AnalyticsSection";
import { ErrorAnalytics, resolveAnalyticsError } from "@/components/admin/ErrorAnalytics";
import { LoadingAnalytics } from "@/components/admin/LoadingAnalytics";
import { StatBadge } from "@/components/admin/StatBadge";
import { useAnalytics } from "@/hooks/useAnalytics";
import {
  formatDecimal,
  formatNumber,
  formatPaise,
  formatPercent,
  isAnalyticsEmpty,
  resolveSystemStatus,
} from "@/lib/analytics-format";
import { AdminAnalyticsPage } from "@/pages/admin/admin-analytics-page";
import type {
  AIMetrics,
  ChatMetrics,
  DashboardOverviewMetrics,
  ReportMetrics,
  RevenueMetrics,
  SystemMetrics,
  UserMetrics,
} from "@/types/analytics";

const timestamp = "2026-06-15T12:00:00.000Z";
const periodStart = "2026-06-01";

const overview: DashboardOverviewMetrics = {
  total_users: 10,
  active_users: 8,
  verified_users: 7,
  total_clients: 20,
  active_clients: 18,
  total_reports: 5,
  total_chat_queries: 30,
  total_revenue_paise: 99900,
  active_subscriptions: 4,
  captured_payments: 2,
  generated_at: timestamp,
};

const revenue: RevenueMetrics = {
  total_revenue_paise: 99900,
  revenue_this_period_paise: 49900,
  captured_payments: 2,
  failed_payments: 0,
  pending_payments: 0,
  refunded_payments: 0,
  total_orders: 2,
  paid_orders: 2,
  failed_orders: 0,
  pending_orders: 0,
  conversion_rate: 1,
  average_order_value_paise: 49950,
  revenue_by_plan: [{ plan: "pro", amount_paise: 99900 }],
  subscriptions_by_plan: [{ label: "pro", count: 2 }],
  period_start: periodStart,
  generated_at: timestamp,
};

const users: UserMetrics = {
  total_users: 10,
  active_users: 8,
  verified_users: 7,
  inactive_users: 2,
  unverified_users: 3,
  new_users_this_period: 1,
  users_by_role: [{ label: "user", count: 9 }],
  active_subscriptions_by_plan: [{ label: "free", count: 8 }],
  total_clients: 20,
  average_clients_per_user: 2,
  quota_usage_by_metric: [{ label: "reports", count: 5 }],
  period_start: periodStart,
  generated_at: timestamp,
};

const reports: ReportMetrics = {
  total_reports: 5,
  reports_this_period: 2,
  reports_with_pdf: 3,
  distinct_clients_with_reports: 4,
  distinct_owners: 2,
  average_reports_per_owner: 2.5,
  reports_by_version: [{ label: "1.0", count: 5 }],
  pdf_by_status: [{ label: "completed", count: 3 }],
  period_start: periodStart,
  generated_at: timestamp,
};

const chat: ChatMetrics = {
  total_queries: 30,
  queries_this_period: 10,
  answered_queries: 25,
  failed_queries: 3,
  processing_queries: 2,
  queries_by_type: [{ label: "kundali", count: 30 }],
  queries_by_status: [{ label: "answered", count: 25 }],
  total_prompt_tokens: 100,
  total_completion_tokens: 200,
  total_tokens: 300,
  average_tokens_per_query: 12,
  queries_by_model: [{ label: "gemini", count: 20 }],
  quota_consumed_this_period: 10,
  period_start: periodStart,
  generated_at: timestamp,
};

const system: SystemMetrics = {
  active_sessions: 5,
  failed_orders: 0,
  expired_orders: 0,
  failed_pdf_generations: 0,
  inactive_users: 2,
  unverified_users: 3,
  chat_error_rate: 0.02,
  generated_at: timestamp,
};

const ai: AIMetrics = {
  total_invocations: 30,
  successful_invocations: 25,
  failed_invocations: 3,
  invocations_this_period: 10,
  total_prompt_tokens: 100,
  total_completion_tokens: 200,
  total_tokens: 300,
  average_tokens_per_success: 12,
  invocations_by_model: [{ label: "gemini", count: 20 }],
  invocations_by_query_type: [{ label: "kundali", count: 30 }],
  invocations_without_token_data: 5,
  period_start: periodStart,
  generated_at: timestamp,
};

vi.mock("@/api/analytics", () => ({
  analyticsApi: {
    getOverview: vi.fn(),
    getUsers: vi.fn(),
    getRevenue: vi.fn(),
    getReports: vi.fn(),
    getChat: vi.fn(),
    getSystem: vi.fn(),
    getAi: vi.fn(),
  },
}));

function mockAnalyticsSuccess() {
  vi.mocked(analyticsApi.getOverview).mockResolvedValue(overview);
  vi.mocked(analyticsApi.getUsers).mockResolvedValue(users);
  vi.mocked(analyticsApi.getRevenue).mockResolvedValue(revenue);
  vi.mocked(analyticsApi.getReports).mockResolvedValue(reports);
  vi.mocked(analyticsApi.getChat).mockResolvedValue(chat);
  vi.mocked(analyticsApi.getSystem).mockResolvedValue(system);
  vi.mocked(analyticsApi.getAi).mockResolvedValue(ai);
}

function renderWithQuery(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

describe("analytics format helpers", () => {
  it("formats currency, percent, and numbers", () => {
    expect(formatPaise(99900)).toBe("₹999");
    expect(formatPercent(0.25)).toBe("25.0%");
    expect(formatNumber(1200)).toBe("1,200");
    expect(formatDecimal(2.456)).toBe("2.5");
  });

  it("resolves system status tones", () => {
    expect(resolveSystemStatus({ chat_error_rate: 0.02, failed_orders: 0, failed_pdf_generations: 0 }).tone).toBe(
      "success",
    );
    expect(resolveSystemStatus({ chat_error_rate: 0.12, failed_orders: 1, failed_pdf_generations: 0 }).tone).toBe(
      "warning",
    );
    expect(resolveSystemStatus({ chat_error_rate: 0.4, failed_orders: 6, failed_pdf_generations: 1 }).tone).toBe(
      "danger",
    );
  });

  it("detects empty analytics overview", () => {
    expect(isAnalyticsEmpty({ total_users: 0, total_reports: 0, total_chat_queries: 0, total_revenue_paise: 0 })).toBe(
      true,
    );
    expect(isAnalyticsEmpty({ total_users: 1, total_reports: 0, total_chat_queries: 0, total_revenue_paise: 0 })).toBe(
      false,
    );
  });
});

describe("resolveAnalyticsError", () => {
  it("handles network, auth, forbidden, and server failures", () => {
    expect(resolveAnalyticsError(new axios.AxiosError("network", undefined, undefined, undefined, undefined)).title).toBe(
      "Network failure",
    );
    expect(
      resolveAnalyticsError(
        new axios.AxiosError("unauthorized", undefined, undefined, undefined, {
          status: 401,
          statusText: "Unauthorized",
          headers: {},
          config: { headers: new axios.AxiosHeaders() },
          data: { detail: "Authentication required." },
        }),
      ).title,
    ).toBe("Unauthorized");
    expect(
      resolveAnalyticsError(
        new axios.AxiosError("forbidden", undefined, undefined, undefined, {
          status: 403,
          statusText: "Forbidden",
          headers: {},
          config: { headers: new axios.AxiosHeaders() },
          data: { detail: "Forbidden" },
        }),
      ).canRetry,
    ).toBe(false);
    expect(
      resolveAnalyticsError(
        new axios.AxiosError("server", undefined, undefined, undefined, {
          status: 500,
          statusText: "Server Error",
          headers: {},
          config: { headers: new axios.AxiosHeaders() },
          data: { detail: "Unable to load analytics data." },
        }),
      ).canRetry,
    ).toBe(true);
  });

  it("falls back to generic error messaging", () => {
    expect(resolveAnalyticsError(new Error("Unexpected failure")).message).toBe("Unexpected failure");
  });
});

describe("admin analytics components", () => {
  it("renders analytics card and badge", () => {
    render(
      <>
        <AnalyticsCard title="Total Users" value="10" description="7 verified" badge={<StatBadge label="Healthy" tone="success" />} />
        <StatBadge label="Attention" tone="warning" />
      </>,
    );
    expect(screen.getByText("Total Users")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument();
    expect(screen.getByText("Healthy")).toBeInTheDocument();
    expect(screen.getByText("Attention")).toBeInTheDocument();
  });

  it("renders grid, section, loading, and error states", async () => {
    const onRetry = vi.fn();
    render(
      <>
        <AnalyticsGrid columns={2}>
          <div>Metric A</div>
          <div>Metric B</div>
        </AnalyticsGrid>
        <AnalyticsSection title="Revenue" description="Revenue metrics" empty emptyMessage="No revenue yet.">
          hidden
        </AnalyticsSection>
        <LoadingAnalytics statCards={2} sections={1} />
        <ErrorAnalytics error={new Error("Failed")} onRetry={onRetry} />
      </>,
    );

    expect(screen.getByText("Metric A")).toBeInTheDocument();
    expect(screen.getByText("No revenue yet.")).toBeInTheDocument();
    expect(screen.getByText("Unable to load analytics")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /retry/i }));
    expect(onRetry).toHaveBeenCalledOnce();
  });

  it("hides retry for unauthorized errors", () => {
    render(
      <ErrorAnalytics
        error={
          new axios.AxiosError("unauthorized", undefined, undefined, undefined, {
            status: 401,
            statusText: "Unauthorized",
            headers: {},
            config: { headers: new axios.AxiosHeaders() },
            data: { detail: "Authentication required." },
          })
        }
        onRetry={vi.fn()}
      />,
    );
    expect(screen.queryByRole("button", { name: /retry/i })).not.toBeInTheDocument();
  });
});

describe("analytics api", () => {
  it("calls admin analytics endpoints", async () => {
    const { analyticsApi: realAnalyticsApi } = await vi.importActual<typeof import("@/api/analytics")>(
      "@/api/analytics",
    );
    const libApi = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
    const get = vi.spyOn(libApi.default, "get").mockResolvedValue({ data: overview });

    await realAnalyticsApi.getOverview();
    await realAnalyticsApi.getUsers();
    await realAnalyticsApi.getRevenue();
    await realAnalyticsApi.getReports();
    await realAnalyticsApi.getChat();
    await realAnalyticsApi.getSystem();
    await realAnalyticsApi.getAi();

    expect(get).toHaveBeenCalledWith("/admin/analytics/overview");
    expect(get).toHaveBeenCalledWith("/admin/analytics/ai");
  });
});

describe("useAnalytics", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAnalyticsSuccess();
  });

  it("loads all analytics queries", async () => {
    function Probe() {
      const analytics = useAnalytics();
      if (analytics.isLoading) {
        return <div>loading</div>;
      }
      return <div>{analytics.overview.data?.total_users ?? 0}</div>;
    }

    renderWithQuery(<Probe />);
    expect(screen.getByText("loading")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("10")).toBeInTheDocument());
    expect(analyticsApi.getOverview).toHaveBeenCalledOnce();
    expect(analyticsApi.getAi).toHaveBeenCalledOnce();
  });
});

describe("AdminAnalyticsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows loading skeletons while fetching", () => {
    vi.mocked(analyticsApi.getOverview).mockReturnValue(new Promise(() => undefined));
    renderWithQuery(<AdminAnalyticsPage />);
    expect(screen.getByLabelText("Loading analytics")).toBeInTheDocument();
  });

  it("renders populated analytics dashboard", async () => {
    mockAnalyticsSuccess();
    renderWithQuery(<AdminAnalyticsPage />);
    await waitFor(() => expect(screen.getByText("Monthly Revenue")).toBeInTheDocument());
    expect(screen.getByText("₹499")).toBeInTheDocument();
    expect(screen.getByText("Revenue by plan")).toBeInTheDocument();
    expect(screen.getByText("Invocations by model")).toBeInTheDocument();
  });

  it("shows empty platform banner when all overview totals are zero", async () => {
    mockAnalyticsSuccess();
    vi.mocked(analyticsApi.getOverview).mockResolvedValue({
      ...overview,
      total_users: 0,
      total_reports: 0,
      total_chat_queries: 0,
      total_revenue_paise: 0,
    });
    renderWithQuery(<AdminAnalyticsPage />);
    await waitFor(() => expect(screen.getByText("No analytics activity yet")).toBeInTheDocument());
  });

  it("shows retryable server error state", async () => {
    vi.mocked(analyticsApi.getOverview).mockRejectedValue(
      new axios.AxiosError("server", undefined, undefined, undefined, {
        status: 500,
        statusText: "Server Error",
        headers: {},
        config: { headers: new axios.AxiosHeaders() },
        data: { detail: "Unable to load analytics data." },
      }),
    );
    vi.mocked(analyticsApi.getUsers).mockResolvedValue(users);
    vi.mocked(analyticsApi.getRevenue).mockResolvedValue(revenue);
    vi.mocked(analyticsApi.getReports).mockResolvedValue(reports);
    vi.mocked(analyticsApi.getChat).mockResolvedValue(chat);
    vi.mocked(analyticsApi.getSystem).mockResolvedValue(system);
    vi.mocked(analyticsApi.getAi).mockResolvedValue(ai);

    renderWithQuery(<AdminAnalyticsPage />);
    await waitFor(() => expect(screen.getByText("Server error")).toBeInTheDocument());
    mockAnalyticsSuccess();
    await userEvent.click(screen.getByRole("button", { name: /retry/i }));
    await waitFor(() => expect(screen.getByText("Monthly Revenue")).toBeInTheDocument());
  });

  it("shows forbidden error without retry", async () => {
    vi.mocked(analyticsApi.getOverview).mockRejectedValue(
      new axios.AxiosError("forbidden", undefined, undefined, undefined, {
        status: 403,
        statusText: "Forbidden",
        headers: {},
        config: { headers: new axios.AxiosHeaders() },
        data: { detail: "Forbidden" },
      }),
    );
    vi.mocked(analyticsApi.getUsers).mockResolvedValue(users);
    vi.mocked(analyticsApi.getRevenue).mockResolvedValue(revenue);
    vi.mocked(analyticsApi.getReports).mockResolvedValue(reports);
    vi.mocked(analyticsApi.getChat).mockResolvedValue(chat);
    vi.mocked(analyticsApi.getSystem).mockResolvedValue(system);
    vi.mocked(analyticsApi.getAi).mockResolvedValue(ai);

    renderWithQuery(<AdminAnalyticsPage />);
    await waitFor(() => expect(screen.getByText("Access denied")).toBeInTheDocument());
    expect(screen.queryByRole("button", { name: /retry/i })).not.toBeInTheDocument();
  });
});
