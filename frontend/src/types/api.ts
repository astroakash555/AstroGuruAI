export type Gender = "male" | "female" | "other" | "unspecified";

export interface BirthDetail {
  id: string;
  date_of_birth: string;
  birth_time: string;
  birth_place: string;
  birth_datetime: string;
  timezone: string;
  latitude: string;
  longitude: string;
  country?: string | null;
  state?: string | null;
  place_id?: string | null;
  is_primary: boolean;
}

export interface Client {
  id: string;
  name: string;
  gender: Gender;
  email: string | null;
  phone: string | null;
  preferred_language: string;
  timezone: string;
  notes: string | null;
  is_active: boolean;
  birth_detail: BirthDetail | null;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ClientCreatePayload {
  name: string;
  gender: Gender;
  date_of_birth: string;
  birth_time: string;
  birth_place: string;
  email?: string;
  phone?: string;
  timezone?: string;
  latitude?: string;
  longitude?: string;
  place_id?: string;
  country?: string;
  state?: string;
  preferred_language?: string;
  notes?: string;
}

export type ClientUpdatePayload = Partial<ClientCreatePayload> & { is_active?: boolean };

export interface ReportPdfMeta {
  generated: boolean;
  filename?: string;
  path?: string;
  download_url?: string;
}

export interface ReportSummary {
  report_id: string;
  client_id?: string;
  birth_detail_id?: string;
  version: string;
  problem_text?: string;
  lagna_sign?: string;
  moon_sign?: string;
  generated_at: string;
  has_pdf: boolean;
}

export interface ReportDetail {
  report_id: string;
  client_id?: string;
  birth_detail_id?: string;
  version: string;
  problem_text?: string;
  unified_report: Record<string, unknown>;
  interpretation: Record<string, unknown>;
  remedy_generation: Record<string, unknown>;
  client_report: Record<string, unknown>;
  pdf?: ReportPdfMeta | null;
  generated_at: string;
  updated_at: string;
}

export interface ReportGeneratePayload {
  client_id?: string;
  birth_detail_id?: string;
  date_of_birth?: string;
  birth_time?: string;
  birth_place?: string;
  timezone?: string;
  latitude?: string | number;
  longitude?: string | number;
  problem_text?: string;
  target_date?: string;
  include_pdf?: boolean;
}

export interface ReportGenerateResponse {
  report_id: string;
  version: string;
  unified_report: Record<string, unknown>;
  interpretation: Record<string, unknown>;
  remedy_generation: Record<string, unknown>;
  client_report: Record<string, unknown>;
  pdf?: ReportPdfMeta | null;
  generated_at: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  report_id: string;
  user_message: string;
  conversation_history?: ChatMessage[];
}

export interface ChatResponse {
  report_id: string;
  answer: string;
  conversation_history: ChatMessage[];
  model: string;
  source: string;
  token_usage: {
    prompt_tokens?: number;
    completion_tokens?: number;
    total_tokens?: number;
  };
  generated_at: string;
  query_id?: string;
  metadata: Record<string, unknown>;
}

export interface HealthResponse {
  status: string;
  app_name: string;
  environment: string;
}

export interface AuthUser {
  id: string;
  email: string;
  full_name: string;
  role: "admin" | "user";
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthSession {
  user: AuthUser;
  tokens: AuthTokens;
}

export interface MessageResponse {
  message: string;
}

export type SubscriptionPlan = "free" | "pro" | "premium";

export interface PlanDefinition {
  plan: SubscriptionPlan;
  name: string;
  description: string;
  price_paise: number;
  currency: string;
  features: string[];
  limits: Record<string, number | null>;
}

export interface UsageMetricSummary {
  metric: string;
  used: number;
  limit: number | null;
  remaining: number | null;
}

export interface UsageSummary {
  plan: SubscriptionPlan;
  period_start: string;
  metrics: UsageMetricSummary[];
}

export interface SubscriptionInfo {
  subscription_id: string;
  plan: SubscriptionPlan;
  status: string;
  current_period_start: string;
  current_period_end: string;
  usage: UsageSummary;
}

export interface CheckoutOrder {
  order_id: string;
  razorpay_order_id: string;
  amount_paise: number;
  currency: string;
  key_id: string;
  plan: SubscriptionPlan;
  receipt: string;
}

export interface PaymentHistoryItem {
  payment_id: string;
  user_id: string;
  order_id: string | null;
  subscription_id: string | null;
  amount_paise: number;
  currency: string;
  status: string;
  razorpay_payment_id: string;
  razorpay_order_id: string;
  method: string | null;
  paid_at: string | null;
  created_at: string;
}

export interface AdminSubscriptionItem {
  subscription_id: string;
  user_id: string;
  plan: SubscriptionPlan;
  status: string;
  current_period_start: string;
  current_period_end: string;
  cancelled_at: string | null;
  created_at: string;
}
