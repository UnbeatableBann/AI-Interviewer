"use client";

import React, { useState } from "react";
import { useParams } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Award,
  Sparkles,
  TrendingUp,
  History,
  AlertTriangle,
  CheckCircle2,
  FileText,
  Network,
  ArrowLeft,
  ChevronRight,
  Plus,
  Compass
} from "lucide-react";
import Link from "next/link";

export default function CandidateIntelligenceDetails() {
  const params = useParams();
  const candId = params.id as string;

  // Mock aggregated CandidateIntelligenceReport payload
  const [report, setReport] = useState({
    profile: {
      id: candId,
      name: "Jane Doe",
      email: "jane.doe@candidate.io",
      experience_years: 8.5,
      summary: "Senior systems and backend infrastructure engineer. Strong architecture compliance record, logical partition expert.",
      resume_url: "cv_jane_doe_backend.pdf"
    },
    skills: [
      { id: "s-1", name: "Python / FastAPI", category: "TECHNICAL", level: 4.5, confidence: 0.9, evaluations_count: 3 },
      { id: "s-2", name: "PostgreSQL Isolation", category: "TECHNICAL", level: 4.2, confidence: 0.85, evaluations_count: 3 },
      { id: "s-3", name: "System Design Topology", category: "SYSTEM_DESIGN", level: 3.8, confidence: 0.8, evaluations_count: 2 },
      { id: "s-4", name: "Distributed Lock/Redis", category: "TECHNICAL", level: 2.8, confidence: 0.7, evaluations_count: 1 }
    ],
    strengths: [
      {
        id: "str-1",
        title: "Asynchronous APIs design",
        description: "Excellent layout execution of non-blocking asyncio procedures, preventing worker thread blocks.",
        context_source: "Interview Session #101"
      },
      {
        id: "str-2",
        title: "Logical multi-tenant isolation",
        description: "Successfully configured tenant routing middleware context filters and mapped connections isolates.",
        context_source: "Interview Session #101"
      }
    ],
    weaknesses: [
      {
        id: "weak-1",
        title: "Distributed Lock Synchronization lease locks",
        description: "Incurred timing locks overlap on concurrent API worker tests during Sentinel master transitions.",
        context_source: "Interview Session #102"
      }
    ],
    insights: [
      {
        id: "ins-1",
        session_id: "session-uuid-101",
        communication_score: 4.5,
        confidence_score: 4.0,
        technical_rating: 4.4,
        key_takeaways: "Jane is extremely articulate when describing database replication bounds. Excellent grasp of async-await concurrency primitives in Python."
      }
    ]
  });

  const [strengthOpen, setStrengthOpen] = useState(false);
  const [newStrengthTitle, setNewStrengthTitle] = useState("");
  const [newStrengthDesc, setNewStrengthDesc] = useState("");

  const handleAddStrength = () => {
    if (!newStrengthTitle.trim() || !newStrengthDesc.trim()) return;
    const newStr = {
      id: `str-${Date.now()}`,
      title: newStrengthTitle,
      description: newStrengthDesc,
      context_source: "Manual Recruiter Review Entry"
    };
    setReport({
      ...report,
      strengths: [...report.strengths, newStr]
    });
    setNewStrengthTitle("");
    setNewStrengthDesc("");
    setStrengthOpen(false);
  };

  return (
    <div className="space-y-8 max-w-6xl font-sans selection:bg-primary selection:text-primary-foreground">
      {/* Back button */}
      <div>
        <Link href="/recruiter/candidates">
          <Button variant="ghost" size="sm" className="h-8 gap-1.5 text-xs font-mono pl-0 hover:bg-transparent">
            <ArrowLeft className="h-3.5 w-3.5" />
            Back to Candidates Index
          </Button>
        </Link>
      </div>

      {/* Main Header bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-border pb-6 gap-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-muted-foreground">
              Candidate Intelligence Report
            </span>
            <Badge variant="success" className="text-[10px]">
              Continuous Sync Active
            </Badge>
          </div>
          <h1 className="text-xl font-semibold tracking-tight mt-2">{report.profile.name}</h1>
          <p className="text-xs text-muted-foreground mt-1 font-mono">
            Candidate ID: {candId.slice(0, 8)}... | Email: {report.profile.email}
          </p>
        </div>

        <Link href={`file:///C:/Users/Shadab/Downloads/Interviewer%20Intelligence%20Platform/frontend/public/resumes/${report.profile.resume_url}`} target="_blank">
          <Button variant="outline" size="sm" className="h-8 gap-1.5 text-xs font-mono">
            <FileText className="h-3.5 w-3.5" />
            Ingested CV: {report.profile.resume_url}
          </Button>
        </Link>
      </div>

      {/* Layout Split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Strengths, gaps, insights (2/3 width) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Executive Summary */}
          <div className="rounded-lg border border-border bg-card p-6 shadow-sm space-y-3">
            <span className="text-[10px] font-bold text-muted-foreground uppercase font-mono tracking-wider block">
              Candidate Summary Overview
            </span>
            <p className="text-xs text-foreground leading-relaxed">
              {report.profile.summary}
            </p>
          </div>

          {/* Strengths Grid */}
          <div className="rounded-lg border border-border bg-card p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-success" />
                <h2 className="text-sm font-semibold tracking-tight">Competency Strengths Highlights</h2>
              </div>
              <Button variant="outline" size="sm" className="h-7 text-xs font-mono gap-1" onClick={() => setStrengthOpen(true)}>
                <Plus className="h-3 w-3" /> Add Highlight
              </Button>
            </div>

            {/* Custom Input strength modal mockup */}
            {strengthOpen && (
              <div className="bg-accent/10 border border-border rounded-lg p-4 space-y-3">
                <Input
                  placeholder="Strength Title (e.g. Concurrency)"
                  value={newStrengthTitle}
                  onChange={(e) => setNewStrengthTitle(e.target.value)}
                  className="text-xs font-mono h-8"
                />
                <textarea
                  placeholder="Enter detailed evaluation evidence quote..."
                  value={newStrengthDesc}
                  onChange={(e) => setNewStrengthDesc(e.target.value)}
                  className="w-full min-h-[60px] p-2 text-xs font-mono rounded border border-input bg-background focus:outline-none"
                />
                <div className="flex justify-end gap-2">
                  <Button variant="ghost" size="sm" className="h-7 text-[10px]" onClick={() => setStrengthOpen(false)}>Cancel</Button>
                  <Button size="sm" className="h-7 text-[10px]" onClick={handleAddStrength}>Save Strength</Button>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {report.strengths.map((str) => (
                <div key={str.id} className="border border-border rounded p-4 space-y-2 bg-success/5 hover:border-success/30 transition-all">
                  <div className="flex justify-between items-start gap-2">
                    <h4 className="text-xs font-semibold text-foreground">{str.title}</h4>
                    <Badge variant="success" className="text-[9px] scale-90">Strength</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">{str.description}</p>
                  <p className="text-[10px] text-muted-foreground font-mono pt-1">Source: {str.context_source}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Development Gaps Grid */}
          <div className="rounded-lg border border-border bg-card p-6 shadow-sm space-y-4">
            <div className="flex items-center gap-2 border-b border-border pb-3">
              <AlertTriangle className="h-4 w-4 text-warning" />
              <h2 className="text-sm font-semibold tracking-tight">Identified Skill Gaps & Development Areas</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {report.weaknesses.map((weak) => (
                <div key={weak.id} className="border border-border rounded p-4 space-y-2 bg-warning/5 hover:border-warning/30 transition-all">
                  <div className="flex justify-between items-start gap-2">
                    <h4 className="text-xs font-semibold text-foreground">{weak.title}</h4>
                    <Badge variant="warning" className="text-[9px] scale-90">Gap</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">{weak.description}</p>
                  <p className="text-[10px] text-muted-foreground font-mono pt-1">Source: {weak.context_source}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Interview Insights */}
          <div className="rounded-lg border border-border bg-card p-6 shadow-sm space-y-4">
            <div className="flex items-center gap-2 border-b border-border pb-3">
              <Compass className="h-4 w-4 text-muted-foreground" />
              <h2 className="text-sm font-semibold tracking-tight">Structured Interviewer Insights</h2>
            </div>

            <div className="divide-y divide-border">
              {report.insights.map((ins) => (
                <div key={ins.id} className="py-4 first:pt-0 last:pb-0 space-y-3">
                  <div className="grid grid-cols-3 gap-4 font-mono text-[10px] text-center">
                    <div className="bg-accent/30 p-2 rounded">
                      <p className="text-muted-foreground uppercase">Tech Rating</p>
                      <p className="text-sm font-bold text-foreground mt-1">{ins.technical_rating} / 5.0</p>
                    </div>
                    <div className="bg-accent/30 p-2 rounded">
                      <p className="text-muted-foreground uppercase">Comm Score</p>
                      <p className="text-sm font-bold text-foreground mt-1">{ins.communication_score} / 5.0</p>
                    </div>
                    <div className="bg-accent/30 p-2 rounded">
                      <p className="text-muted-foreground uppercase">Confidence</p>
                      <p className="text-sm font-bold text-foreground mt-1">{ins.confidence_score} / 5.0</p>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    <span className="font-bold text-foreground">Synthesis Takeaways:</span> {ins.key_takeaways}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Evolving skills matrix, Semantic Knowledge Graph (1/3 width) */}
        <div className="space-y-6">
          {/* Evolving Skills list */}
          <div className="rounded-lg border border-border bg-card p-6 shadow-sm space-y-4">
            <div className="flex items-center gap-2 border-b border-border pb-3">
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
              <h2 className="text-sm font-semibold tracking-tight">Evolving Skills Taxonomy</h2>
            </div>

            <div className="space-y-4">
              {report.skills.map((skill) => (
                <div key={skill.id} className="space-y-1.5 text-xs">
                  <div className="flex justify-between font-mono">
                    <span className="truncate">{skill.name}</span>
                    <span className="font-bold">{skill.level.toFixed(1)} / 5.0</span>
                  </div>
                  <div className="h-1.5 w-full bg-secondary rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary"
                      style={{ width: `${(skill.level / 5.0) * 100}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-[9px] text-muted-foreground font-mono">
                    <span>Confidence: {(skill.confidence * 100).toFixed(0)}%</span>
                    <span>Evaluations Count: {skill.evaluations_count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Interactive Knowledge Graph SVG Node map */}
          <div className="rounded-lg border border-border bg-card p-6 shadow-sm space-y-4">
            <div className="flex items-center gap-2 border-b border-border pb-3">
              <Network className="h-4 w-4 text-muted-foreground" />
              <h2 className="text-sm font-semibold tracking-tight">Semantic Entity Connections</h2>
            </div>

            {/* SVG Visual graph mock */}
            <div className="h-48 border border-border rounded bg-accent/5 relative overflow-hidden flex items-center justify-center">
              <svg className="absolute inset-0 h-full w-full pointer-events-none" xmlns="http://www.w3.org/2000/svg">
                {/* Connecting lines */}
                <line x1="80" y1="90" x2="200" y2="50" stroke="hsl(var(--border))" strokeWidth="1.5" />
                <line x1="80" y1="90" x2="200" y2="130" stroke="hsl(var(--border))" strokeWidth="1.5" />

                {/* Candidate node */}
                <circle cx="80" cy="90" r="12" fill="hsl(var(--primary))" stroke="hsl(var(--background))" strokeWidth="1.5" />
                <text x="80" y="114" textAnchor="middle" className="text-[9px] font-mono fill-foreground">Jane Doe</text>

                {/* Skill node expert */}
                <circle cx="200" cy="50" r="10" fill="hsl(var(--success))" stroke="hsl(var(--background))" strokeWidth="1.5" />
                <text x="215" y="53" className="text-[8px] font-mono fill-foreground">FastAPI (Expert)</text>

                {/* Skill node practitioner */}
                <circle cx="200" cy="130" r="10" fill="hsl(var(--success))" stroke="hsl(var(--background))" strokeWidth="1.5" />
                <text x="215" y="133" className="text-[8px] font-mono fill-foreground">Postgres RLS</text>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
