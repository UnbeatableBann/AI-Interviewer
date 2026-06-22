import { create } from "zustand";

export interface UserProfile {
  id: string;
  email: string;
  role: "ADMIN" | "RECRUITER" | "CANDIDATE";
  tenant_id: string;
  scopes: string[];
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: UserProfile | null;
  tenantId: string | null;
  isAuthenticated: boolean;
  isAuthenticating: boolean;
  setAuth: (
    accessToken: string,
    refreshToken: string,
    user: UserProfile
  ) => void;
  clearAuth: () => void;
  setTenantId: (id: string | null) => void;
  setAuthenticating: (state: boolean) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  refreshToken: null,
  user: null,
  tenantId: null,
  isAuthenticated: false,
  isAuthenticating: false,
  setAuth: (accessToken, refreshToken, user) =>
    set({
      accessToken,
      refreshToken,
      user,
      tenantId: user.tenant_id,
      isAuthenticated: true,
      isAuthenticating: false,
    }),
  clearAuth: () =>
    set({
      accessToken: null,
      refreshToken: null,
      user: null,
      tenantId: null,
      isAuthenticated: false,
      isAuthenticating: false,
    }),
  setTenantId: (tenantId) => set({ tenantId }),
  setAuthenticating: (isAuthenticating) => set({ isAuthenticating }),
}));
