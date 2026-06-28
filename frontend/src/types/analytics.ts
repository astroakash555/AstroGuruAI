export interface AnalyticsBreakdownItem {
  label: string;
  count: number;
}

export interface AnalyticsRevenueBreakdownItem {
  plan: string;
  amount_paise: number;
}

export interface DashboardOverviewMetrics {
  total_users: number;
  active_users: number;
  verified_users: number;
  total_clients: number;
  active_clients: number;
  total_reports: number;
  total_chat_queries: number;
  total_revenue_paise: number;
  active_subscriptions: number;
  captured_payments: number;
  generated_at: string;
}

export interface RevenueMetrics {
  total_revenue_paise: number;
  revenue_this_period_paise: number;
  captured_payments: number;
  failed_payments: number;
  pending_payments: number;
  refunded_payments: number;
  total_orders: number;
  paid_orders: number;
  failed_orders: number;
  pending_orders: number;
  conversion_rate: number;
  average_order_value_paise: number;
  revenue_by_plan: AnalyticsRevenueBreakdownItem[];
  subscriptions_by_plan: AnalyticsBreakdownItem[];
  period_start: string;
  generated_at: string;
}

export interface UserMetrics {
  total_users: number;
  active_users: number;
  verified_users: number;
  inactive_users: number;
  unverified_users: number;
  new_users_this_period: number;
  users_by_role: AnalyticsBreakdownItem[];
  active_subscriptions_by_plan: AnalyticsBreakdownItem[];
  total_clients: number;
  average_clients_per_user: number;
  quota_usage_by_metric: AnalyticsBreakdownItem[];
  period_start: string;
  generated_at: string;
}

export interface ReportMetrics {
  total_reports: number;
  reports_this_period: number;
  reports_with_pdf: number;
  distinct_clients_with_reports: number;
  distinct_owners: number;
  average_reports_per_owner: number;
  reports_by_version: AnalyticsBreakdownItem[];
  pdf_by_status: AnalyticsBreakdownItem[];
  period_start: string;
  generated_at: string;
}

export interface ChatMetrics {
  total_queries: number;
  queries_this_period: number;
  answered_queries: number;
  failed_queries: number;
  processing_queries: number;
  queries_by_type: AnalyticsBreakdownItem[];
  queries_by_status: AnalyticsBreakdownItem[];
  total_prompt_tokens: number;
  total_completion_tokens: number;
  total_tokens: number;
  average_tokens_per_query: number;
  queries_by_model: AnalyticsBreakdownItem[];
  quota_consumed_this_period: number;
  period_start: string;
  generated_at: string;
}

export interface SystemMetrics {
  active_sessions: number;
  failed_orders: number;
  expired_orders: number;
  failed_pdf_generations: number;
  inactive_users: number;
  unverified_users: number;
  chat_error_rate: number;
  generated_at: string;
}

export interface AIMetrics {
  total_invocations: number;
  successful_invocations: number;
  failed_invocations: number;
  invocations_this_period: number;
  total_prompt_tokens: number;
  total_completion_tokens: number;
  total_tokens: number;
  average_tokens_per_success: number;
  invocations_by_model: AnalyticsBreakdownItem[];
  invocations_by_query_type: AnalyticsBreakdownItem[];
  invocations_without_token_data: number;
  period_start: string;
  generated_at: string;
}
