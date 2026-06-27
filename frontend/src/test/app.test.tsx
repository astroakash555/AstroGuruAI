import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import { AuthProvider } from "@/providers/auth-provider";
import { LoginPage } from "@/pages/login-page";

describe("LoginPage", () => {
  it("renders sign-in form", () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </MemoryRouter>,
    );

    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  });
});

describe("auth helpers", () => {
  it("stores access and refresh tokens", async () => {
    const { setAuthSession, getAccessToken, getRefreshToken, logout } = await import("@/lib/auth");
    setAuthSession({
      user: {
        id: "1",
        email: "demo@test.com",
        full_name: "Demo",
        role: "user",
        is_active: true,
        is_verified: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      tokens: {
        access_token: "access-token",
        refresh_token: "refresh-token",
        token_type: "bearer",
        expires_in: 1800,
      },
    });
    expect(getAccessToken()).toBe("access-token");
    expect(getRefreshToken()).toBe("refresh-token");
    logout();
    expect(getAccessToken()).toBeNull();
  });
});

describe("utils", () => {
  it("resolves relative download urls", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://localhost:8000/api/v1");
    const { resolveDownloadUrl } = await import("@/lib/utils");
    expect(resolveDownloadUrl("/api/v1/dashboard/reports/pdf/sample.pdf")).toContain("sample.pdf");
  });
});
