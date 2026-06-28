import api from "@/lib/api";
import type {
  AIMetrics,
  ChatMetrics,
  DashboardOverviewMetrics,
  ReportMetrics,
  RevenueMetrics,
  SystemMetrics,
  UserMetrics,
} from "@/types/analytics";

export const analyticsApi = {
  getOverview: () =>
    api.get<DashboardOverviewMetrics>("/admin/analytics/overview").then((response) => response.data),
  getUsers: () => api.get<UserMetrics>("/admin/analytics/users").then((response) => response.data),
  getRevenue: () => api.get<RevenueMetrics>("/admin/analytics/revenue").then((response) => response.data),
  getReports: () => api.get<ReportMetrics>("/admin/analytics/reports").then((response) => response.data),
  getChat: () => api.get<ChatMetrics>("/admin/analytics/chat").then((response) => response.data),
  getSystem: () => api.get<SystemMetrics>("/admin/analytics/system").then((response) => response.data),
  getAi: () => api.get<AIMetrics>("/admin/analytics/ai").then((response) => response.data),
};
