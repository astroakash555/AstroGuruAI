import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

import { getAuthUser, isAuthenticated, login as persistLogin, logout as persistLogout } from "@/lib/auth";
import type { AuthUser } from "@/types/api";

interface AuthContextValue {
  user: AuthUser | null;
  authenticated: boolean;
  login: (user: AuthUser) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => getAuthUser());

  const value = useMemo(
    () => ({
      user,
      authenticated: Boolean(user) && isAuthenticated(),
      login: (nextUser: AuthUser) => {
        persistLogin(nextUser);
        setUser(nextUser);
      },
      logout: () => {
        persistLogout();
        setUser(null);
      },
    }),
    [user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
