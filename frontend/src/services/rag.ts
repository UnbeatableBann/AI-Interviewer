import apiClient from "@/lib/api-client";
import { APIResponse } from "./auth";

export interface KnowledgeDocument {
  id: string;
  tenant_id: string;
  title: string;
  source_type: "JOB_DESCRIPTION" | "COMPANY_RUBRIC" | "EXPECTED_ANSWER" | "INTERVIEW_PLAYBOOK" | "CANDIDATE_HISTORY";
  content: string;
  metadata_json?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Citation {
  document_id: string;
  title: string;
  source_type: string;
  chunk_index: number;
  content: string;
}

export interface RetrievalResult {
  chunk_id: string;
  score: number;
  content: string;
  citation: Citation;
}

export interface QueryResponse {
  query: string;
  results: RetrievalResult[];
}

export const ragService = {
  async ingestDocument(payload: {
    title: string;
    source_type: string;
    content: string;
    metadata_json?: Record<string, any>;
  }): Promise<APIResponse<KnowledgeDocument>> {
    const response = await apiClient.post<APIResponse<KnowledgeDocument>>("/rag/documents", payload);
    return response.data;
  },

  async queryContext(payload: {
    query: string;
    source_types?: string[];
    limit?: number;
  }): Promise<APIResponse<QueryResponse>> {
    const response = await apiClient.post<APIResponse<QueryResponse>>("/rag/query", payload);
    return response.data;
  },

  async deleteDocument(documentId: string): Promise<APIResponse<Record<string, string>>> {
    const response = await apiClient.delete<APIResponse<Record<string, string>>>(`/rag/documents/${documentId}`);
    return response.data;
  },
};
export default ragService;
