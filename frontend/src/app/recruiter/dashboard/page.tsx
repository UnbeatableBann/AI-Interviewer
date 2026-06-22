"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Users,
  Calendar,
  AlertCircle,
  FileCheck2,
  TrendingUp,
  TrendingDown,
  UserPlus,
  ArrowRight,
  TrendingDown as AlertTrend,
  CheckCircle2,
  Network
} from "lucide-react";
import Link from "next/link";

export default function RecruiterDashboard() {
  const [candidatesReview] = useState([
    {
      id: "cand-uuid-001",
      name: "Jane Doe",
      role: "Senior Backend Engineer",
      overall_score: 4.3,
      evaluated_at: "2026-06-20",
      status: "REQUIRES_REVIEW",
    },
    {
      id: "cand-uuid-002",
      name: "Bob Smith",
      role: "Senior Full Stack Dev",
      overall_score: 3.5,
      evaluated_at: "2026-06-19",
      status: "REQUIRES_REVIEW",
    }
  ]);

  const [funnelMetrics] = useState({
    active_interviews: 12,
    completion_rate: "89%",
    avg_quality_score: "3.9 / 5.0",
    total_candidates: 48,
  });

  return (
    <div className="space-y-8 max-w-6xl">
      {/* Header section */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Recruiter Dashboard</h1>
          <p className="text-xs text-muted-foreground mt-1 font-mono">
            Hiring Funnel Health & Continuous Assessment Sync
          </p>
        </div>
        
        <Link href="/recruiter/candidates">
          <Button size="sm" className="gap-1.5 text-xs font-mono">
            <UserPlus className="h-4 w-4" />
            Provision Candidate Profile
          </Button>
        </Link>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-lg border border-border bg-card p-4 shadow-sm">
          <p className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">Active Interviews</p>
          <p className="text-xl font-bold tracking-tight mt-1">{funnelMetrics.active_interviews}</p>
          <div className="flex items-center gap-1 mt-1 text-[10px] text-success font-mono">
            <TrendingUp className="h-3 w-3" />
            <span>+3 this week</span>
          </div>
        </div>

        <div className="rounded-lg border border-border bg-card p-4 shadow-sm">
          <p className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">Completion Rate</p>
          <p className="text-xl font-bold tracking-tight mt-1">{funnelMetrics.completion_rate}</p>
          <div className="flex items-center gap-1 mt-1 text-[10px] text-success font-mono">
            <CheckCircle2 className="h-3 w-3" />
            <span>Optimal latency</span>
          </div>
        </div>

        <div className="rounded-lg border border-border bg-card p-4 shadow-sm">
          <p className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">Avg Candidate Quality</p>
          <p className="text-xl font-bold tracking-tight mt-1">{funnelMetrics.avg_quality_score}</p>
          <div className="flex items-center gap-1 mt-1 text-[10px] text-success font-mono">
            <TrendingUp className="h-3 w-3" />
            <span>+0.2 pts change</span>
          </div>
        </div>

        <div className="rounded-lg border border-border bg-card p-4 shadow-sm">
          <p className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">Total Ingested Profiles</p>
          <p className="text-xl font-bold tracking-tight mt-1">{funnelMetrics.total_candidates}</p>
          <div className="flex items-center gap-1 mt-1 text-[10px] text-muted-foreground font-mono">
            <span>RAG context indexed</span>
          </div>
        </div>
      </div>

      {/* Grid: Review list and Funnel chart mockup */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Review list (2/3 width) */}
        <div className="lg:col-span-2 rounded-lg border border-border bg-card p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-muted-foreground" />
              <h2 className="text-sm font-semibold tracking-tight">Candidates Requiring Review</h2>
            </div>
            <span className="text-[11px] font-mono text-muted-foreground">Action required</span>
          </div>

          <div className="divide-y divide-border">
            {candidatesReview.map((cand) => (
              <div key={cand.id} className="py-4 first:pt-0 last:pb-0 flex items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold">{cand.name}</span>
                    <Badge variant="outline" className="text-[10px] font-mono font-normal">
                      {cand.role}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1 font-mono">
                    Completed: {cand.evaluated_at} • Evaluation overall score: {cand.overall_score}/5.0
                  </p>
                </div>
                <Link href={`/recruiter/candidates/${cand.id}`}>
                  <Button variant="outline" size="sm" className="h-8 gap-1 text-xs font-mono">
                    Review Intel
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </div>

        {/* Funnel Health widget (1/3 width) */}
        <div className="rounded-lg border border-border bg-card p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-2 border-b border-border pb-3">
            <Network className="h-4 w-4 text-muted-foreground" />
            <h2 className="text-sm font-semibold tracking-tight">Hiring Pipeline Funnel</h2>
          </div>

          <div className="space-y-4">
            <div className="space-y-1">
              <div className="flex justify-between text-xs font-mono">
                <span>1. CV Ingestion</span>
                <span className="font-bold">48 candidates</span>
              </div>
              <div className="h-2 bg-secondary rounded-full overflow-hidden">
                <div className="h-full bg-primary" style={{ width: "100%" }} />
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-xs font-mono">
                <span>2. Interview Completed</span>
                <span className="font-bold">24 candidates</span>
              </div>
              <div className="h-2 bg-secondary rounded-full overflow-hidden">
                <div className="h-full bg-primary" style={{ width: "50%" }} />
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-xs font-mono">
                <span>3. Evaluation Reviewed</span>
                <span className="font-bold">8 candidates</span>
              </div>
              <div className="h-2 bg-secondary rounded-full overflow-hidden">
                <div className="h-full bg-primary" style={{ width: "16%" }} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
