import apiClient from "@/lib/api-client";
import { APIResponse } from "./auth";

export interface Skill {
  id: string;
  name: string;
  category: string;
  description?: string;
}

export interface CandidateSkill {
  id: string;
  skill: Skill;
  level: number;
  confidence: number;
  evaluations_count: number;
  last_evaluated: string;
}

export interface CandidateProfile {
  id: string;
  tenant_id: string;
  user_id: string;
  resume_url?: string;
  experience_years?: number;
  summary?: string;
  created_at: string;
}

export interface Strength {
  id: string;
  title: string;
  description: string;
  context_source?: string;
  created_at: string;
}

export interface Weakness {
  id: string;
  title: string;
  description: string;
  context_source?: string;
  created_at: string;
}

export interface InterviewInsight {
  id: string;
  session_id: string;
  communication_score: number;
  confidence_score: number;
  technical_rating: number;
  key_takeaways: string;
  created_at: string;
}

export interface ProgressSnapshot {
  id: string;
  snapshot_date: string;
  overall_score: number;
  skills_matrix: string; // JSON payload string
  created_at: string;
}

export interface CandidateIntelligenceReport {
  profile: CandidateProfile;
  skills: CandidateSkill[];
  strengths: Strength[];
  weaknesses: Weakness[];
  insights: InterviewInsight[];
  progress_snapshots: ProgressSnapshot[];
}

export interface TimelineEvent {
  event_type: "INTERVIEW" | "EVALUATION" | "INSIGHT" | "SNAPSHOT";
  title: string;
  timestamp: string;
  details: Record<string, any>;
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  properties: Record<string, any>;
}

export interface GraphEdge {
  source: string;
  target: string;
  relation: string;
  properties: Record<string, any>;
}

export interface KnowledgeGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface CandidateMemory {
  timeline: TimelineEvent[];
  knowledge_graph: KnowledgeGraph;
  skill_evolution: Record<string, Array<{ date: string; score: number }>>;
  interviews: any[];
  evaluations: any[];
  insights: InterviewInsight[];
}

export const candidateService = {
  async provisionProfile(payload: {
    user_id: string;
    resume_url?: string;
    experience_years?: number;
    summary?: string;
  }): Promise<APIResponse<CandidateProfile>> {
    const response = await apiClient.post<APIResponse<CandidateProfile>>("/candidates", payload);
    return response.data;
  },

  async updateProfile(
    candidateId: string,
    payload: {
      resume_url?: string;
      experience_years?: number;
      summary?: string;
    }
  ): Promise<APIResponse<CandidateProfile>> {
    const response = await apiClient.put<APIResponse<CandidateProfile>>(`/candidates/${candidateId}`, payload);
    return response.data;
  },

  async getIntelligenceReport(candidateId: string): Promise<APIResponse<CandidateIntelligenceReport>> {
    const response = await apiClient.get<APIResponse<CandidateIntelligenceReport>>(
      `/candidates/${candidateId}/intelligence`
    );
    return response.data;
  },

  async getCandidateMemory(candidateId: string): Promise<APIResponse<CandidateMemory>> {
    const response = await apiClient.get<APIResponse<CandidateMemory>>(`/candidates/${candidateId}/memory`);
    return response.data;
  },

  async evaluateCandidateSkill(
    candidateId: string,
    skillId: string,
    score: number,
    confidence: number
  ): Promise<APIResponse<CandidateSkill>> {
    const response = await apiClient.post<APIResponse<CandidateSkill>>(
      `/candidates/${candidateId}/skills/${skillId}`,
      null,
      { params: { score, confidence } }
    );
    return response.data;
  },

  async addStrength(
    candidateId: string,
    payload: { title: string; description: string; context_source?: string }
  ): Promise<APIResponse<Strength>> {
    const response = await apiClient.post<APIResponse<Strength>>(`/candidates/${candidateId}/strengths`, payload);
    return response.data;
  },

  async addWeakness(
    candidateId: string,
    payload: { title: string; description: string; context_source?: string }
  ): Promise<APIResponse<Weakness>> {
    const response = await apiClient.post<APIResponse<Weakness>>(`/candidates/${candidateId}/weaknesses`, payload);
    return response.data;
  },

  async recordInsight(
    candidateId: string,
    payload: {
      session_id: string;
      communication_score: number;
      confidence_score: number;
      technical_rating: number;
      key_takeaways: string;
    }
  ): Promise<APIResponse<InterviewInsight>> {
    const response = await apiClient.post<APIResponse<InterviewInsight>>(
      `/candidates/${candidateId}/insights`,
      payload
    );
    return response.data;
  },
};
export default candidateService;
