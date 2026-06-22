"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as zod from "zod";
import {
  Users,
  Search,
  UserPlus,
  ArrowRight,
  FileUser,
  Trash2,
  Activity,
  Plus
} from "lucide-react";
import Link from "next/link";

// Zod Schema matching CandidateProfileCreate
const provisionSchema = zod.object({
  user_id: zod.string().uuid("Enter a valid user UUID link."),
  experience_years: zod.number().min(0, "Experience years cannot be negative."),
  resume_url: zod.string().url("Enter a valid PDF resume storage URL.").optional().or(zod.string().length(0)),
  summary: zod.string().min(10, "Summary must contain at least 10 characters.").optional().or(zod.string().length(0)),
});

type ProvisionFormValues = zod.infer<typeof provisionSchema>;

export default function CandidatesIndexPage() {
  const [candidates, setCandidates] = useState([
    {
      id: "cand-uuid-001",
      name: "Jane Doe",
      email: "jane.doe@candidate.io",
      experience_years: 8.5,
      resume_url: "cv_jane_doe_backend.pdf",
      summary: "Senior systems and backend engineer specialized in Postgres logical RLS partitions.",
    },
    {
      id: "cand-uuid-002",
      name: "Bob Smith",
      email: "bob.smith@fullstack.net",
      experience_years: 5.0,
      resume_url: "cv_bob_smith.pdf",
      summary: "Fullstack developer specializing in React and Node microservices configurations.",
    }
  ]);

  const [provisionOpen, setProvisionOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ProvisionFormValues>({
    resolver: zodResolver(provisionSchema),
    defaultValues: {
      user_id: "99999999-9999-9999-9999-999999999999",
      experience_years: 5,
      resume_url: "https://minio.iip-data/resumes/cv_candidate.pdf",
      summary: "Ingested profile with custom resume details.",
    },
  });

  const handleProvision = (values: ProvisionFormValues) => {
    // Scaffold insertion
    const newCand = {
      id: `cand-uuid-${Date.now()}`,
      name: `Candidate ${candidates.length + 1}`,
      email: `candidate-${candidates.length + 1}@organization.io`,
      experience_years: values.experience_years,
      resume_url: values.resume_url || "cv_uploaded.pdf",
      summary: values.summary || "No custom summary details provided.",
    };
    setCandidates([newCand, ...candidates]);
    reset();
    setProvisionOpen(false);
  };

  const filteredCandidates = candidates.filter(
    (c) =>
      c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.summary.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-8 max-w-6xl font-sans selection:bg-primary selection:text-primary-foreground">
      {/* Header section */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Candidates Center</h1>
          <p className="text-xs text-muted-foreground mt-1 font-mono">
            Provision candidate profiles under active tenant security bounds.
          </p>
        </div>

        <Button size="sm" className="gap-1.5 text-xs font-mono" onClick={() => setProvisionOpen(true)}>
          <Plus className="h-4 w-4" />
          Ingest Candidate Profile
        </Button>
      </div>

      {/* Action panel */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search candidates, skills, profiles..."
            className="pl-9 text-xs font-mono"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Provision Drawer overlay */}
      {provisionOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-end bg-background/80 backdrop-blur-sm">
          <div className="w-[480px] bg-card border-l border-border h-full flex flex-col p-8 shadow-xl relative animate-in slide-in-from-right duration-200">
            <div className="flex items-center justify-between border-b border-border pb-4 mb-6">
              <h2 className="text-sm font-semibold tracking-tight">Ingest Candidate CV Profile</h2>
              <Button variant="ghost" size="sm" onClick={() => setProvisionOpen(false)} className="text-xs font-mono">
                Close
              </Button>
            </div>

            <form onSubmit={handleSubmit(handleProvision)} className="space-y-4 flex-1 overflow-y-auto pr-1">
              <div>
                <label className="text-xs font-semibold text-muted-foreground mb-1 block">User UUID Bind Link</label>
                <Input {...register("user_id")} error={errors.user_id?.message} className="font-mono text-xs" />
              </div>

              <div>
                <label className="text-xs font-semibold text-muted-foreground mb-1 block">Years of Experience</label>
                <Input
                  type="number"
                  step="0.5"
                  {...register("experience_years", { valueAsNumber: true })}
                  error={errors.experience_years?.message}
                  className="font-mono text-xs"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-muted-foreground mb-1 block">Resume File URL (PDF)</label>
                <Input {...register("resume_url")} error={errors.resume_url?.message} className="font-mono text-xs" />
              </div>

              <div>
                <label className="text-xs font-semibold text-muted-foreground mb-1 block">Executive CV Summary</label>
                <textarea
                  {...register("summary")}
                  className="w-full min-h-[100px] p-3 rounded-md border border-input bg-background text-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono"
                  placeholder="Summarize candidate qualifications..."
                />
                {errors.summary?.message && (
                  <span className="text-[10px] text-destructive block mt-1 font-mono">{errors.summary.message}</span>
                )}
              </div>

              <div className="pt-4">
                <Button type="submit" className="w-full text-xs font-mono">
                  PROVISION PROFILE
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Grid: List of candidates */}
      <div className="grid grid-cols-1 gap-4">
        {filteredCandidates.map((c) => (
          <div
            key={c.id}
            className="rounded-lg border border-border bg-card p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:border-muted-foreground/30 transition-all"
          >
            <div className="space-y-1.5 flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold">{c.name}</h3>
                <Badge variant="secondary" className="text-[10px] font-mono">
                  YOE: {c.experience_years}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed truncate max-w-xl">
                {c.summary}
              </p>
              <div className="flex gap-4 text-[10px] text-muted-foreground font-mono">
                <span>ID: {c.id}</span>
                <span>Email: {c.email}</span>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <Link href={`/recruiter/candidates/${c.id}`}>
                <Button variant="outline" size="sm" className="h-8 gap-1 text-xs font-mono">
                  Intelligence Profile
                  <ArrowRight className="h-3.5 w-3.5" />
                </Button>
              </Link>
            </div>
          </div>
        ))}

        {filteredCandidates.length === 0 && (
          <div className="rounded-lg border border-dashed border-border p-12 text-center text-xs text-muted-foreground font-mono">
            No candidates matched search criteria.
          </div>
        )}
      </div>
    </div>
  );
}
