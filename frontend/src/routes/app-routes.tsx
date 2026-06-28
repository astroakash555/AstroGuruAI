import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "@/components/layout/app-layout";
import { BirthDetailsPage } from "@/pages/birth-details-page";
import { AdminAnalyticsPage } from "@/pages/admin/admin-analytics-page";
import { AdminBillingPage } from "@/pages/admin-billing-page";
import { BillingHistoryPage } from "@/pages/billing-history-page";
import { ChatPage } from "@/pages/chat-page";
import { ClientCreatePage, ClientDetailPage, ClientEditPage } from "@/pages/client-pages";
import { ClientsPage } from "@/pages/clients-page";
import { DashboardPage } from "@/pages/dashboard-page";
import { ForgotPasswordPage } from "@/pages/forgot-password-page";
import { GenerateReportPage } from "@/pages/generate-report-page";
import { LoginPage } from "@/pages/login-page";
import { PaymentFailurePage, PaymentSuccessPage } from "@/pages/payment-result-pages";
import { PdfViewerPage } from "@/pages/pdf-viewer-page";
import { PricingPage } from "@/pages/pricing-page";
import { ProfilePage } from "@/pages/profile-page";
import { ReportViewerPage } from "@/pages/report-viewer-page";
import { ResetPasswordPage } from "@/pages/reset-password-page";
import { SettingsPage } from "@/pages/settings-page";
import { SignupPage } from "@/pages/signup-page";
import { SubscriptionPage } from "@/pages/subscription-page";
import { UpgradePage } from "@/pages/upgrade-page";
import { VerifyEmailPage } from "@/pages/verify-email-page";
import { AdminRoute } from "@/routes/admin-route";
import { ProtectedRoute } from "@/routes/protected-route";

export function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/verify-email" element={<VerifyEmailPage />} />
        <Route path="/billing/success" element={<PaymentSuccessPage />} />
        <Route path="/billing/failure" element={<PaymentFailurePage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/upgrade" element={<UpgradePage />} />
          <Route element={<AppLayout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/clients" element={<ClientsPage />} />
            <Route path="/clients/new" element={<ClientCreatePage />} />
            <Route path="/clients/:clientId" element={<ClientDetailPage />} />
            <Route path="/clients/:clientId/edit" element={<ClientEditPage />} />
            <Route path="/birth-details" element={<BirthDetailsPage />} />
            <Route path="/reports/generate" element={<GenerateReportPage />} />
            <Route path="/reports/:reportId" element={<ReportViewerPage />} />
            <Route path="/reports/:reportId/pdf" element={<PdfViewerPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/billing/subscription" element={<SubscriptionPage />} />
            <Route path="/billing/history" element={<BillingHistoryPage />} />
            <Route element={<AdminRoute />}>
              <Route path="/admin/billing" element={<AdminBillingPage />} />
              <Route path="/admin/analytics" element={<AdminAnalyticsPage />} />
            </Route>
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
