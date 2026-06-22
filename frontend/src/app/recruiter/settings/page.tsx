"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as zod from "zod";
import {
  Database,
  Search,
  UploadCloud,
  FileCheck2,
  Trash2,
  ListFilter,
  Sparkles,
  ArrowRight,
  ShieldCheck
} from "lucide-react";

// Form validation schema matching KnowledgeDocumentCreate
const ingestSchema = zod.object({
  title: zod.string().min(3, "Title must contain at least 3 characters."),
  source_type: zod.enum(["JOB_DESCRIPTION", "COMPANY_RUBRIC", "EXPECTED_ANSWER", "INTERVIEW_PLAYBOOK", "CANDIDATE_HISTORY"]),
  content: zod.string().min(10, "Raw text content must contain at least 10 characters."),
});

type IngestFormValues = zod.infer<typeof ingestSchema>;

export default function RecruiterSettingsPage() {
  const [documents, setDocuments] = useState([
    {
      id: "doc-uuid-1",
      title: "Senior Backend Engineer Job Description",
      source_type: "JOB_DESCRIPTION",
      created_at: "2026-06-21",
    },
    {
      id: "doc-uuid-2",
      title: "ISO/IEC 25010 Systems Integrity Standard Rubric",
      source_type: "COMPANY_RUBRIC",
      created_at: "2026-06-20",
    }
  ]);

  const [queryText, setQueryText] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [querying, setQuerying] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<IngestFormValues>({
    resolver: zodResolver(ingestSchema),
    defaultValues: {
      title: "",
      source_type: "JOB_DESCRIPTION",
      content: "",
    },
  });

  const handleIngest = async (values: IngestFormValues) => {
    setUploading(true);
    setMessage(null);
    try {
      // Simulate API network latency
      await new Promise((resolve) => setTimeout(resolve, 1000));

      const newDoc = {
        id: `doc-uuid-${Date.now()}`,
        title: values.title,
        source_type: values.source_type,
        created_at: new Date().toISOString().split("T")[0],
      };
      
      setDocuments([newDoc, ...documents]);
      setMessage("Document ingested successfully. Chunks and embeddings vector-indexed.");
      reset();
    } catch (err: any) {
      setMessage("Ingestion failed. Check document configurations.");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId: string) => {
    setDocuments(documents.filter((d) => d.id !== docId));
    setMessage("Document successfully deleted from vector collections.");
  };

  const handleQuery = async () => {
    if (!queryText.trim()) return;
    setQuerying(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 800));
      
      // Mock citations retrieved matching retrieval models
      setSearchResults([
        {
          chunk_id: "chunk-1",
          score: 0.89,
          content: "...logical multi-tenancy configurations require filtering all SQL statements on the active tenant_id. We apply row-level security on PostgreSQL and partition vector collections inside Qdrant...",
          citation: {
            title: "ISO/IEC 25010 Systems Integrity Standard Rubric",
            source_type: "COMPANY_RUBRIC",
            chunk_index: 2
          }
        }
      ]);
    } catch (err) {
      console.error(err);
    } finally {
      setQuerying(false);
    }
  };

  const sourceOptions = [
    { label: "Job Description", value: "JOB_DESCRIPTION" },
    { label: "Company Rubric", value: "COMPANY_RUBRIC" },
    { label: "Expected Answer", value: "EXPECTED_ANSWER" },
    { label: "Interview Playbook", value: "INTERVIEW_PLAYBOOK" },
    { label: "Candidate History", value: "CANDIDATE_HISTORY" }
  ];

  return (
    <div className="space-y-8 max-w-6xl font-sans selection:bg-primary selection:text-primary-foreground">
      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold tracking-tight">RAG Context Control Center</h1>
        <p className="text-xs text-muted-foreground mt-1 font-mono">
          Upload evaluation rubrics, job descriptions, and query vector isolation.
        </p>
      </div>

      {message && (
        <div className="rounded-md bg-info/10 border border-info/20 p-3 text-xs text-info font-mono flex items-center gap-2">
          <ShieldCheck className="h-4 w-4" />
          {message}
        </div>
      )}

      {/* Split grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left pane: Ingestion form & search simulation */}
        <div className="space-y-6">
          {/* Document upload form */}
          <div className="rounded-lg border border-border bg-card p-6 shadow-sm space-y-4">
            <div className="flex items-center gap-2 border-b border-border pb-3">
              <UploadCloud className="h-4 w-4 text-muted-foreground" />
              <h2 className="text-sm font-semibold tracking-tight">Ingest Reference Document</h2>
            </div>

            <form onSubmit={handleSubmit(handleIngest)} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-muted-foreground mb-1 block">Document Title</label>
                <Input
                  {...register("title")}
                  placeholder="e.g. Technical Lead Role description"
                  error={errors.title?.message}
                  className="font-mono text-xs"
                />
              </div>

              <div>
                <Select
                  label="Document Source Type"
                  options={sourceOptions}
                  {...register("source_type")}
                  error={errors.source_type?.message}
                  className="font-mono text-xs"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-muted-foreground mb-1 block">Raw Content Text</label>
                <textarea
                  {...register("content")}
                  className="w-full min-h-[120px] p-3 rounded-md border border-input bg-background text-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono"
                  placeholder="Paste complete rubric instructions or job specification guidelines..."
                />
                {errors.content?.message && (
                  <span className="text-[10px] text-destructive block mt-1 font-mono">{errors.content.message}</span>
                )}
              </div>

              <Button type="submit" className="w-full text-xs font-mono" loading={uploading}>
                VECTORIZE & INDEX DOCUMENT
              </Button>
            </form>
          </div>

          {/* Query simulation widget */}
          <div className="rounded-lg border border-border bg-card p-6 shadow-sm space-y-4">
            <div className="flex items-center gap-2 border-b border-border pb-3">
              <Sparkles className="h-4 w-4 text-muted-foreground" />
              <h2 className="text-sm font-semibold tracking-tight">Retrieval Query Simulator</h2>
            </div>

            <div className="flex gap-2">
              <Input
                placeholder="Type query to test cosine alignment..."
                value={queryText}
                onChange={(e) => setQueryText(e.target.value)}
                className="font-mono text-xs"
              />
              <Button onClick={handleQuery} loading={querying} size="sm" className="font-mono text-xs">
                Query
              </Button>
            </div>

            {searchResults.map((res, idx) => (
              <div key={idx} className="border border-border rounded p-4 bg-accent/5 space-y-2">
                <div className="flex justify-between items-center text-[10px] font-mono">
                  <span className="font-bold text-foreground truncate max-w-[240px]">
                    Source: {res.citation.title}
                  </span>
                  <span className="text-muted-foreground">Cosine: {res.score}</span>
                </div>
                <p className="text-xs text-muted-foreground leading-normal italic font-mono">
                  {res.content}
                </p>
                <div className="flex gap-2 text-[9px] font-mono text-muted-foreground">
                  <span>Type: {res.citation.source_type}</span>
                  <span>Chunk Index: {res.citation.chunk_index}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right pane: Indexed reference documents listing */}
        <div className="rounded-lg border border-border bg-card p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-2 border-b border-border pb-3">
            <Database className="h-4 w-4 text-muted-foreground" />
            <h2 className="text-sm font-semibold tracking-tight">Active Context Index Map</h2>
          </div>

          <div className="divide-y divide-border">
            {documents.map((doc) => (
              <div key={doc.id} className="py-4 first:pt-0 last:pb-0 flex items-center justify-between gap-4">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="text-xs font-semibold truncate max-w-[220px]">{doc.title}</h3>
                    <Badge variant="outline" className="text-[9px] font-mono font-normal scale-90">
                      {doc.source_type}
                    </Badge>
                  </div>
                  <p className="text-[10px] text-muted-foreground font-mono mt-1">
                    Uploaded: {doc.created_at} • ID: {doc.id.slice(0, 8)}...
                  </p>
                </div>

                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10 shrink-0"
                  onClick={() => handleDelete(doc.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}

            {documents.length === 0 && (
              <div className="py-8 text-center text-xs text-muted-foreground font-mono">
                No active document context indexed.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
