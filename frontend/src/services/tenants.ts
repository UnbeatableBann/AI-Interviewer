import apiClient from "@/lib/api-client";
import { APIResponse } from "./auth";

export interface Tenant {
  id: string;
  name: string;
  tier: "STANDARD" | "ENTERPRISE" | "DEDICATED";
  status: "ACTIVE" | "SUSPENDED";
  created_at: string;
}

export const tenantService = {
  async provisionTenant(payload: {
    id: string;
    name: string;
    tier?: "STANDARD" | "ENTERPRISE" | "DEDICATED";
  }): Promise<APIResponse<Tenant>> {
    const response = await apiClient.post<APIResponse<Tenant>>("/tenants", payload);
    return response.data;
  },

  async getTenant(id: string): Promise<APIResponse<Tenant>> {
    const response = await apiClient.get<APIResponse<Tenant>>(`/tenants/${id}`);
    return response.data;
  },

  async suspendTenant(id: string): Promise<APIResponse<Tenant>> {
    const response = await apiClient.post<APIResponse<Tenant>>(`/tenants/${id}/suspend`);
    return response.data;
  },

  async activateTenant(id: string): Promise<APIResponse<Tenant>> {
    const response = await apiClient.post<APIResponse<Tenant>>(`/tenants/${id}/activate`);
    return response.data;
  },
};
export default tenantService;
