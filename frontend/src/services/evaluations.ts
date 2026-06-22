import apiClient from "@/lib/api-client";
import { APIResponse, UserResponse } from "./auth";
import { Skill } from "./candidates";

export interface EvaluationReport {
  id: string;
  tenant_id: string;
  session_id: string;
  overall_score: number;
  technical_accuracy_score: number;
  communication_score: number;
  depth_score: number;
  problem_solving_score: number;
  confidence_score: number;
  completeness_score: number;
  summary: string;
  hallucinations_detected?: Array<Record<string, any>>;
  faithfulness_score: number;
  rubric_used: Record<string, any>;
  extracted_evidence: Array<Record<string, any>>;
  created_at: string;
}

export interface SkillGapReport {
  id: string;
  tenant_id: string;
  candidate_id: string;
  skill_id: string;
  skill: Skill;
  current_level: number;
  required_level: number;
  gap: number;
  recommendations: string;
  created_at: string;
}

export const evaluationService = {
  async evaluateSession(
    sessionId: string,
    requiredSkillLevels?: Record<string, number>
  ): Promise<APIResponse<EvaluationReport>> {
    const payload = {
      session_id: sessionId,
      required_skill_levels: requiredSkillLevels,
    };
    const response = await apiClient.post<APIResponse<EvaluationReport>>("/evaluations", payload);
    return response.data;
  },

  async getEvaluationReport(sessionId: string): Promise<APIResponse<EvaluationReport>> {
    const response = await apiClient.get<APIResponse<EvaluationReport>>(`/evaluations/reports/${sessionId}`);
    return response.data;
  },

  async getSkillGaps(candidateId: string): Promise<APIResponse<SkillGapReport[]>> {
    const response = await apiClient.get<APIResponse<SkillGapReport[]>>(`/evaluations/gaps/${candidateId}`);
    return response.data;
  },
};
export default evaluationService;
