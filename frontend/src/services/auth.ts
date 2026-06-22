import apiClient from "@/lib/api-client";
import { useAuthStore } from "@/stores/auth-store";

export interface APIResponse<T> {
  success: boolean;
  data: T | null;
  error: {
    code: string;
    message: string;
    details: any;
  } | null;
  meta: any;
}

export interface UserResponse {
  id: string;
  email: string;
  role: "ADMIN" | "RECRUITER" | "CANDIDATE";
  tenant_id: string;
  scopes: string[];
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export const authService = {
  async register(payload: any): Promise<APIResponse<UserResponse>> {
    const response = await apiClient.post<APIResponse<UserResponse>>("/auth/register", payload);
    return response.data;
  },

  async login(payload: any): Promise<APIResponse<TokenResponse>> {
    const response = await apiClient.post<APIResponse<TokenResponse>>("/auth/login", payload);
    if (response.data.success && response.data.data) {
      const tokens = response.data.data;
      
      // Decrypt or parse payload token directly to obtain user profile
      const decodedUser = authService.decodeToken(tokens.access_token);
      if (decodedUser) {
        useAuthStore.getState().setAuth(tokens.access_token, tokens.refresh_token, decodedUser);
      }
    }
    return response.data;
  },

  async verifyEmail(payload: { token: string }): Promise<APIResponse<boolean>> {
    const response = await apiClient.post<APIResponse<boolean>>("/auth/verify-email", payload);
    return response.data;
  },

  async requestPasswordReset(payload: { email: string }): Promise<APIResponse<boolean>> {
    const response = await apiClient.post<APIResponse<boolean>>("/auth/password-reset/request", payload);
    return response.data;
  },

  async confirmPasswordReset(payload: any): Promise<APIResponse<boolean>> {
    const response = await apiClient.post<APIResponse<boolean>>("/auth/password-reset/confirm", payload);
    return response.data;
  },

  decodeToken(token: string): any {
    try {
      const base64Url = token.split(".")[1];
      const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split("")
          .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
          .join("")
      );
      const parsed = JSON.parse(jsonPayload);
      
      // Map JWT payload to AuthUser shape
      return {
        id: parsed.sub || parsed.id,
        email: parsed.email,
        role: parsed.role,
        tenant_id: parsed.tenant_id,
        scopes: parsed.scopes || [],
      };
    } catch (e) {
      console.error("JWT token decoding failed:", e);
      return null;
    }
  },
};
export default authService;
