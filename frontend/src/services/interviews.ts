import apiClient from "@/lib/api-client";
import { APIResponse } from "./auth";
import { Question, ResponseItem, SessionStatus } from "@/stores/interview-store";

export interface InterviewSession {
  id: string;
  tenant_id: string;
  candidate_id: string;
  type: "TECHNICAL" | "HR" | "SYSTEM_DESIGN";
  status: SessionStatus;
  memory_summary?: string;
  adaptive_state?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface InterviewSessionDetail extends InterviewSession {
  questions: Question[];
  responses: ResponseItem[];
}

export const interviewService = {
  async createSession(payload: {
    candidate_id: string;
    type: "TECHNICAL" | "HR" | "SYSTEM_DESIGN";
  }): Promise<APIResponse<InterviewSession>> {
    const response = await apiClient.post<APIResponse<InterviewSession>>("/interviews", payload);
    return response.data;
  },

  async getSession(sessionId: string): Promise<APIResponse<InterviewSessionDetail>> {
    const response = await apiClient.get<APIResponse<InterviewSessionDetail>>(`/interviews/${sessionId}`);
    return response.data;
  },

  async startSession(sessionId: string): Promise<APIResponse<InterviewSessionDetail>> {
    const response = await apiClient.post<APIResponse<InterviewSessionDetail>>(`/interviews/${sessionId}/start`);
    return response.data;
  },

  async pauseSession(sessionId: string): Promise<APIResponse<InterviewSession>> {
    const response = await apiClient.post<APIResponse<InterviewSession>>(`/interviews/${sessionId}/pause`);
    return response.data;
  },

  async resumeSession(sessionId: string): Promise<APIResponse<InterviewSession>> {
    const response = await apiClient.post<APIResponse<InterviewSession>>(`/interviews/${sessionId}/resume`);
    return response.data;
  },

  async completeSession(sessionId: string): Promise<APIResponse<InterviewSession>> {
    const response = await apiClient.post<APIResponse<InterviewSession>>(`/interviews/${sessionId}/complete`);
    return response.data;
  },

  async submitResponse(
    sessionId: string,
    payload: { response_text: string; audio_url?: string }
  ): Promise<APIResponse<ResponseItem>> {
    const response = await apiClient.post<APIResponse<ResponseItem>>(`/interviews/${sessionId}/response`, payload);
    return response.data;
  },
};
export default interviewService;
