"use client";

import React, { useState } from "react";
import { useParams } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Award,
  Sparkles,
  FileCheck2,
  TrendingUp,
  AlertOctagon,
  Quote,
  ArrowLeft,
  ArrowRight,
  BookOpen
} from "lucide-react";
import Link from "next/link";

export default function EvaluationReportPage() {
  const params = useParams();
  const sessionId = params.id as string;

  // Dummy mock evaluation report data matching EvaluationReportResponse schema
  const [report] = useState({
    id: "eval-report-uuid-001",
    session_id: sessionId,
    overall_score: 4.3,
    technical_accuracy_score: 4.5,
    communication_score: 4.2,
    depth_score: 4.0,
    problem_solving_score: 4.6,
    confidence_score: 4.1,
    completeness_score: 4.4,
    summary: "Candidate Jane Doe demonstrated excellent systems programming capability. Her answers around logical database partition layers, schema isolating procedures, and Postgres row-level security implementations reflect senior-level knowledge. She identified correct constraints when designing multi-tenant gateways. There is minor room for development in distributed locking consistency controls under split-brain network scenarios.",
    faithfulness_score: 4.8,
    hallucinations_detected: [
      {
        question_order: 3,
        evidence: "Mentioned that Redis cluster triggers fully synchronous Paxos consensus on all read operations.",
        critique: "Redis uses asynchronous replication; Sentinel/Raft configurations handle failover but do not require Paxos consensus on basic transactional write paths."
      }
    ],
    rubric_used: {
      role: "Senior Backend Engineer",
      standards: "ISO/IEC 25010 Systems Integrity and Scale Metrics"
    },
    extracted_evidence: [
      {
        skill: "Multi-Tenant Isolation",
        quote: "I configure app-level context vars to bind the validated tenant ID, which is then fed into row-level security policies inside PostgreSQL. This prevents tenant A from reading tenant B's database rows even if UUIDs collide.",
        rating: 4.8
      },
      {
        skill: "Distributed Cache Strategy",
        quote: "We set expiration lease values on lock hashes in Redis using SETNX to prevent deadlock states on worker crash events.",
        rating: 4.0
      }
    ]
  });

  return (
    <div className="space-y-8 max-w-5xl">
      {/* Back trigger */}
      <div>
        <Link href="/candidate/dashboard">
          <Button variant="ghost" size="sm" className="h-8 gap-1.5 text-xs font-mono pl-0 hover:bg-transparent">
            <ArrowLeft className="h-3 w-3" />
            Back to Dashboard
          </Button>
        </Link>
      </div>

      {/* Main Header bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-border pb-6 gap-6">
        <div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px]">
              Rubric Used: {report.rubric_used.role}
            </Badge>
            <Badge variant="success" className="text-[10px]">
              Evaluated
            </Badge>
          </div>
          <h1 className="text-xl font-semibold tracking-tight mt-2">Interview Evaluation Report</h1>
          <p className="text-xs text-muted-foreground mt-1 font-mono">
            Session: #{sessionId.slice(0, 8)}... | SSE-KMS Encrypted Metadata
          </p>
        </div>

        {/* Large Overall Score display */}
        <div className="flex items-center gap-4 bg-card border border-border p-4 rounded-lg shadow-sm">
          <div className="flex h-12 w-12 items-center justify-center rounded-md bg-accent text-primary border border-border">
            <Award className="h-6 w-6" />
          </div>
          <div>
            <p className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">Overall Rating</p>
            <div className="flex items-baseline gap-1 mt-0.5">
              <span className="text-xl font-bold tracking-tight">{report.overall_score}</span>
              <span className="text-xs text-muted-foreground">/ 5.0</span>
            </div>
          </div>
        </div>
      </div>

      {/* Grid structure */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Core summary and evidence lists (2/3 width) */}
        <div className="md:col-span-2 space-y-6">
          {/* Executive Summary Card */}
          <div className="rounded-lg border border-border bg-card p-6 shadow-sm space-y-3">
            <div className="flex items-center gap-2">
              <FileCheck2 className="h-4 w-4 text-muted-foreground" />
              <h2 className="text-sm font-semibold tracking-tight">Executive Summary</h2>
            </div>
            <p className="text-xs text-foreground leading-relaxed">
              {report.summary}
            </p>
          </div>

          {/* Transcript Evidence Card */}
          <div className="rounded-lg border border-border bg-card p-6 shadow-sm space-y-4">
            <div className="flex items-center gap-2 border-b border-border pb-3">
              <Quote className="h-4 w-4 text-muted-foreground" />
              <h2 className="text-sm font-semibold tracking-tight">Extracted Transcript Evidence</h2>
            </div>

            <div className="space-y-4">
              {report.extracted_evidence.map((ev, idx) => (
                <div key={idx} className="space-y-2 border-l-2 border-primary pl-4 py-1">
                  <div className="flex items-center justify-between text-[11px] font-mono">
                    <span className="font-bold text-foreground uppercase tracking-wider">{ev.skill}</span>
                    <span className="text-muted-foreground">Score: {ev.rating.toFixed(1)}/5.0</span>
                  </div>
                  <p className="text-xs text-muted-foreground italic leading-relaxed">
                    "{ev.quote}"
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Hallucinations Detected alert if any */}
          {report.hallucinations_detected && report.hallucinations_detected.length > 0 && (
            <div className="rounded-lg border border-destructive/20 bg-destructive/5 p-6 space-y-3">
              <div className="flex items-center gap-2 text-destructive">
                <AlertOctagon className="h-4 w-4" />
                <h2 className="text-sm font-semibold tracking-tight">Hallucinations / Logical Gaps Detected</h2>
              </div>
              <div className="space-y-3">
                {report.hallucinations_detected.map((hall, idx) => (
                  <div key={idx} className="text-xs font-mono space-y-1">
                    <p className="font-semibold text-destructive">Question Order #{hall.question_order} Statement:</p>
                    <p className="text-muted-foreground italic">"{hall.evidence}"</p>
                    <p className="text-foreground pt-1"><span className="font-bold">Evaluation Critique:</span> {hall.critique}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Competencies Breakdown sidebar (1/3 width) */}
        <div className="space-y-6">
          <div className="rounded-lg border border-border bg-card p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-4 border-b border-border pb-3">
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
              <h2 className="text-sm font-semibold tracking-tight">Dimensions Rating</h2>
            </div>

            <div className="space-y-4 font-mono text-xs">
              <div className="space-y-1">
                <div className="flex justify-between">
                  <span>Technical Accuracy</span>
                  <span className="font-bold">{report.technical_accuracy_score.toFixed(1)}/5.0</span>
                </div>
                <div className="h-1 bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-primary" style={{ width: `${(report.technical_accuracy_score / 5.0) * 100}%` }} />
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex justify-between">
                  <span>Problem Solving</span>
                  <span className="font-bold">{report.problem_solving_score.toFixed(1)}/5.0</span>
                </div>
                <div className="h-1 bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-primary" style={{ width: `${(report.problem_solving_score / 5.0) * 100}%` }} />
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex justify-between">
                  <span>Completeness</span>
                  <span className="font-bold">{report.completeness_score.toFixed(1)}/5.0</span>
                </div>
                <div className="h-1 bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-primary" style={{ width: `${(report.completeness_score / 5.0) * 100}%` }} />
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex justify-between">
                  <span>Communication</span>
                  <span className="font-bold">{report.communication_score.toFixed(1)}/5.0</span>
                </div>
                <div className="h-1 bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-primary" style={{ width: `${(report.communication_score / 5.0) * 100}%` }} />
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex justify-between">
                  <span>Depth of Knowledge</span>
                  <span className="font-bold">{report.depth_score.toFixed(1)}/5.0</span>
                </div>
                <div className="h-1 bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-primary" style={{ width: `${(report.depth_score / 5.0) * 100}%` }} />
                </div>
              </div>
            </div>
          </div>

          {/* Development Action Card */}
          <div className="rounded-lg border border-border bg-card p-6 shadow-sm bg-gradient-to-br from-accent/10 to-transparent">
            <div className="flex items-center gap-2 mb-3">
              <BookOpen className="h-4 w-4 text-muted-foreground" />
              <h2 className="text-sm font-semibold tracking-tight">Recommended Learning</h2>
            </div>
            <p className="text-xs text-muted-foreground leading-normal mb-4">
              Explore your detailed growth vectors, skill progression curves, and longitudinal timeline milestones inside your profile center.
            </p>
            <Link href="/candidate/profile">
              <Button size="sm" className="w-full gap-1 text-xs">
                Go to Profile Center
                <ArrowRight className="h-3.5 w-3.5" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
