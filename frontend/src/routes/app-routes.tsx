import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "@/components/layout/app-layout";
import { BirthDetailsPage } from "@/pages/birth-details-page";
import { ChatPage } from "@/pages/chat-page";
import { ClientCreatePage, ClientDetailPage, ClientEditPage } from "@/pages/client-pages";
import { ClientsPage } from "@/pages/clients-page";
import { DashboardPage } from "@/pages/dashboard-page";
import { ForgotPasswordPage } from "@/pages/forgot-password-page";
import { GenerateReportPage } from "@/pages/generate-report-page";
import { LoginPage } from "@/pages/login-page";
import { PdfViewerPage } from "@/pages/pdf-viewer-page";
import { ProfilePage } from "@/pages/profile-page";
import { ReportViewerPage } from "@/pages/report-viewer-page";
import { ResetPasswordPage } from "@/pages/reset-password-page";
import { SettingsPage } from "@/pages/settings-page";
import { SignupPage } from "@/pages/signup-page";
import { VerifyEmailPage } from "@/pages/verify-email-page";
import { ProtectedRoute } from "@/routes/protected-route";

export function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/verify-email" element={<VerifyEmailPage />} />
        <Route element={<ProtectedRoute />}>
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
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
