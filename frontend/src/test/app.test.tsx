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
  it("stores demo session token", async () => {
    const { login, getAuthToken, logout } = await import("@/lib/auth");
    login({ email: "demo@test.com", name: "Demo" });
    expect(getAuthToken()).toBe("demo-token");
    logout();
    expect(getAuthToken()).toBeNull();
  });
});

describe("utils", () => {
  it("resolves relative download urls", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://localhost:8000/api/v1");
    const { resolveDownloadUrl } = await import("@/lib/utils");
    expect(resolveDownloadUrl("/api/v1/dashboard/reports/pdf/sample.pdf")).toContain("sample.pdf");
  });
});
