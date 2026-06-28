import { useQueries } from "@tanstack/react-query";

import { analyticsApi } from "@/api/analytics";

export const analyticsQueryKeys = {
  overview: ["admin", "analytics", "overview"] as const,
  users: ["admin", "analytics", "users"] as const,
  revenue: ["admin", "analytics", "revenue"] as const,
  reports: ["admin", "analytics", "reports"] as const,
  chat: ["admin", "analytics", "chat"] as const,
  system: ["admin", "analytics", "system"] as const,
  ai: ["admin", "analytics", "ai"] as const,
};

const analyticsQueries = [
  { queryKey: analyticsQueryKeys.overview, queryFn: analyticsApi.getOverview },
  { queryKey: analyticsQueryKeys.users, queryFn: analyticsApi.getUsers },
  { queryKey: analyticsQueryKeys.revenue, queryFn: analyticsApi.getRevenue },
  { queryKey: analyticsQueryKeys.reports, queryFn: analyticsApi.getReports },
  { queryKey: analyticsQueryKeys.chat, queryFn: analyticsApi.getChat },
  { queryKey: analyticsQueryKeys.system, queryFn: analyticsApi.getSystem },
  { queryKey: analyticsQueryKeys.ai, queryFn: analyticsApi.getAi },
] as const;

export function useAnalytics() {
  const results = useQueries({ queries: analyticsQueries });

  const [overview, users, revenue, reports, chat, system, ai] = results;

  const isLoading = results.some((result) => result.isLoading);
  const isFetching = results.some((result) => result.isFetching);
  const firstError = results.find((result) => result.error)?.error ?? null;

  const refetchAll = async () => {
    await Promise.all(results.map((result) => result.refetch()));
  };

  return {
    overview,
    users,
    revenue,
    reports,
    chat,
    system,
    ai,
    isLoading,
    isFetching,
    firstError,
    refetchAll,
  };
}
