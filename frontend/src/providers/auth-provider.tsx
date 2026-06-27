import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

import { authApi } from "@/lib/api";
import { getAuthUser, isAuthenticated, logout as clearSession, setAuthSession, getRefreshToken } from "@/lib/auth";
import type { AuthSession, AuthUser } from "@/types/api";

interface AuthContextValue {
  user: AuthUser | null;
  authenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (payload: { email: string; password: string; full_name: string }) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => getAuthUser());

  const applySession = useCallback((session: AuthSession) => {
    setAuthSession(session);
    setUser(session.user);
  }, []);

  const value = useMemo(
    () => ({
      user,
      authenticated: Boolean(user) && isAuthenticated(),
      login: async (email: string, password: string) => {
        const session = await authApi.login({ email, password });
        applySession(session);
      },
      signup: async (payload: { email: string; password: string; full_name: string }) => {
        const session = await authApi.signup(payload);
        applySession(session);
      },
      logout: async () => {
        const refreshToken = getRefreshToken();
        clearSession();
        setUser(null);
        if (refreshToken) {
          try {
            await authApi.logout(refreshToken);
          } catch {
            // Local session is already cleared.
          }
        }
      },
      refreshProfile: async () => {
        const profile = await authApi.me();
        setUser(profile);
        const existing = getAuthUser();
        if (existing) {
          setAuthSession({
            user: profile,
            tokens: {
              access_token: localStorage.getItem("astroguruai.auth.access") ?? "",
              refresh_token: localStorage.getItem("astroguruai.auth.refresh") ?? "",
              token_type: "bearer",
              expires_in: 0,
            },
          });
        }
      },
    }),
    [applySession, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
