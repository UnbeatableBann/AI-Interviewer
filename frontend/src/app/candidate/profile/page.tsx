"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  FileUser,
  GitBranch,
  Network,
  Activity,
  History,
  TrendingUp,
  Map,
  Link as LinkIcon
} from "lucide-react";

export default function CandidateProfilePage() {
  // Mock Candidate Memory Response matching the API schema
  const [memory] = useState({
    profile: {
      resume_url: "cv_jane_doe_backend.pdf",
      experience_years: 8.5,
      summary: "Senior Systems and Backend Infrastructure engineer specializing in concurrent network pipelines, Postgres logical partitions, and high-performance caching layers. Core target alignment: Technical Lead / Principal architect contexts."
    },
    timeline: [
      {
        event_type: "INTERVIEW_ENDED",
        title: "Systems Design Evaluation Complete",
        timestamp: "2026-06-20T15:00:00Z",
        details: { score: 4.3, feedback: "Excellent logical partitioning design" }
      },
      {
        event_type: "EVALUATION_REPORT_GENERATED",
        title: "Primary Code Integrity Analysis Completed",
        timestamp: "2026-06-18T10:00:00Z",
        details: { score: 4.0 }
      },
      {
        event_type: "PROGRESS_SNAPSHOT_RECORDED",
        title: "Resume Ingested & Indexed",
        timestamp: "2026-06-15T09:00:00Z",
        details: { parsed_skills: ["Python", "FastAPI", "Postgres", "Redis"] }
      }
    ],
    knowledge_graph: {
      nodes: [
        { id: "cand", label: "Jane Doe (Candidate)", type: "CANDIDATE" },
        { id: "skill-py", label: "Python/FastAPI", type: "SKILL" },
        { id: "skill-db", label: "Postgres RLS", type: "SKILL" },
        { id: "skill-redis", label: "Redis Mutex", type: "SKILL" },
        { id: "job", label: "Tech Lead Role", type: "ROLE" }
      ],
      edges: [
        { source: "cand", target: "skill-py", relation: "EXPERT" },
        { source: "cand", target: "skill-db", relation: "PRACTITIONER" },
        { source: "cand", target: "skill-redis", relation: "DEVELOPING" },
        { source: "job", target: "skill-py", relation: "REQUIRED" },
        { source: "job", target: "skill-db", relation: "REQUIRED" }
      ]
    },
    skill_evolution: {
      "Python/FastAPI": [
        { date: "June 1", score: 4.0 },
        { date: "June 10", score: 4.2 },
        { date: "June 20", score: 4.5 }
      ],
      "Postgres RLS": [
        { date: "June 1", score: 3.2 },
        { date: "June 10", score: 3.8 },
        { date: "June 20", score: 4.2 }
      ],
      "Redis Mutex": [
        { date: "June 1", score: 3.0 },
        { date: "June 10", score: 3.0 },
        { date: "June 20", score: 2.8 }
      ]
    }
  });

  const [activeTab, setActiveTab] = useState<"graph" | "timeline" | "evolution">("graph");

  return (
    <div className="space-y-8 max-w-5xl">
      {/* Header section */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-border pb-6 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-muted-foreground">
              Candidate Profile
            </span>
            <Badge variant="success" className="text-[10px]">
              Active Memory Indexed
            </Badge>
          </div>
          <h1 className="text-xl font-semibold tracking-tight mt-2">Candidate Intelligence Center</h1>
          <p className="text-xs text-muted-foreground mt-1 font-mono">
            Chronological Timeline & Semantic Knowledge Graph Synthesis
          </p>
        </div>

        <Link href={`file:///C:/Users/Shadab/Downloads/Interviewer%20Intelligence%20Platform/frontend/public/resumes/${memory.profile.resume_url}`} target="_blank">
          <Button variant="outline" size="sm" className="h-8 gap-1.5 text-xs font-mono">
            <FileUser className="h-3.5 w-3.5" />
            Resume Profile: {memory.profile.resume_url}
          </Button>
        </Link>
      </div>

      {/* Summary statement card */}
      <div className="rounded-lg border border-border bg-card p-6 shadow-sm space-y-3">
        <span className="text-[10px] font-bold text-muted-foreground uppercase font-mono tracking-wider">
          Ingested CV Executive Summary
        </span>
        <p className="text-xs text-foreground leading-relaxed">
          {memory.profile.summary}
        </p>
        <div className="flex gap-4 pt-2 font-mono text-[11px] text-muted-foreground">
          <span>Target Job Level: Principal / Lead</span>
          <span>YOE: {memory.profile.experience_years} Years</span>
        </div>
      </div>

      {/* Interactive Tabs Header */}
      <div className="flex border-b border-border">
        <Button
          variant="ghost"
          className={`h-9 px-4 rounded-none border-b-2 text-xs font-semibold font-mono tracking-tight transition-all ${
            activeTab === "graph" ? "border-primary text-foreground bg-accent/20" : "border-transparent text-muted-foreground"
          }`}
          onClick={() => setActiveTab("graph")}
        >
          <Network className="h-3.5 w-3.5 mr-1.5" />
          Semantic Knowledge Graph
        </Button>
        <Button
          variant="ghost"
          className={`h-9 px-4 rounded-none border-b-2 text-xs font-semibold font-mono tracking-tight transition-all ${
            activeTab === "timeline" ? "border-primary text-foreground bg-accent/20" : "border-transparent text-muted-foreground"
          }`}
          onClick={() => setActiveTab("timeline")}
        >
          <History className="h-3.5 w-3.5 mr-1.5" />
          Milestones Timeline
        </Button>
        <Button
          variant="ghost"
          className={`h-9 px-4 rounded-none border-b-2 text-xs font-semibold font-mono tracking-tight transition-all ${
            activeTab === "evolution" ? "border-primary text-foreground bg-accent/20" : "border-transparent text-muted-foreground"
          }`}
          onClick={() => setActiveTab("evolution")}
        >
          <Activity className="h-3.5 w-3.5 mr-1.5" />
          Skill Evolution
        </Button>
      </div>

      {/* Dynamic Tab Body */}
      <div className="min-h-[360px]">
        {activeTab === "graph" && (
          <div className="rounded-lg border border-border bg-card p-6 shadow-sm space-y-6">
            <div>
              <h3 className="text-sm font-semibold tracking-tight">Semantic Knowledge Node Mapping</h3>
              <p className="text-[11px] text-muted-foreground mt-0.5">
                Displays identified capability relations compiled dynamically from parsed PDF resume sections and completed transcripts.
              </p>
            </div>

            {/* Interactive Graph mock (premium SVG rendering) */}
            <div className="h-72 w-full border border-border rounded bg-accent/5 relative overflow-hidden flex items-center justify-center">
              <svg className="absolute inset-0 h-full w-full pointer-events-none" xmlns="http://www.w3.org/2000/svg">
                {/* Edges line connections */}
                <line x1="120" y1="140" x2="320" y2="70" stroke="hsl(var(--border))" strokeWidth="1.5" />
                <line x1="120" y1="140" x2="320" y2="140" stroke="hsl(var(--border))" strokeWidth="1.5" />
                <line x1="120" y1="140" x2="320" y2="210" stroke="hsl(var(--border))" strokeWidth="1.5" />
                <line x1="520" y1="100" x2="320" y2="70" stroke="hsl(var(--border))" strokeWidth="1.5" strokeDasharray="3 3" />
                <line x1="520" y1="100" x2="320" y2="140" stroke="hsl(var(--border))" strokeWidth="1.5" strokeDasharray="3 3" />

                {/* Node Circles and Labels */}
                {/* Candidate Node */}
                <g className="cursor-pointer hover:opacity-85">
                  <circle cx="120" cy="140" r="16" fill="hsl(var(--primary))" stroke="hsl(var(--background))" strokeWidth="2" />
                  <text x="120" y="172" textAnchor="middle" className="text-[10px] font-mono font-bold fill-foreground">Jane Doe</text>
                </g>

                {/* Skill Nodes */}
                <g>
                  <circle cx="320" cy="70" r="12" fill="hsl(var(--success))" stroke="hsl(var(--background))" strokeWidth="2" />
                  <text x="340" y="74" className="text-[10px] font-mono fill-foreground">Python/FastAPI (Expert)</text>
                </g>
                <g>
                  <circle cx="320" cy="140" r="12" fill="hsl(var(--success))" stroke="hsl(var(--background))" strokeWidth="2" />
                  <text x="340" y="144" className="text-[10px] font-mono fill-foreground">Postgres RLS (Practitioner)</text>
                </g>
                <g>
                  <circle cx="320" cy="210" r="12" fill="hsl(var(--warning))" stroke="hsl(var(--background))" strokeWidth="2" />
                  <text x="340" y="214" className="text-[10px] font-mono fill-foreground">Redis Mutex (Developing)</text>
                </g>

                {/* Role Node */}
                <g>
                  <circle cx="520" cy="100" r="14" fill="hsl(var(--info))" stroke="hsl(var(--background))" strokeWidth="2" />
                  <text x="520" y="132" textAnchor="middle" className="text-[10px] font-mono font-bold fill-foreground">Tech Lead Target</text>
                </g>
              </svg>

              {/* Float helper absolute tags */}
              <div className="absolute top-4 right-4 flex flex-col gap-1.5 font-mono text-[9px]">
                <div className="flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-primary" /> Candidate profile
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-success" /> Validated Skills
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-warning" /> Developing Skills
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "timeline" && (
          <div className="rounded-lg border border-border bg-card p-6 shadow-sm space-y-6">
            <div>
              <h3 className="text-sm font-semibold tracking-tight">Chronological Journey Milestones</h3>
              <p className="text-[11px] text-muted-foreground mt-0.5">
                Reflects absolute chronological log transitions normalized to UTC dates context.
              </p>
            </div>

            <div className="space-y-6 relative pl-4 before:absolute before:left-[19px] before:top-2 before:bottom-2 before:w-[1px] before:bg-border">
              {memory.timeline.map((evt, idx) => (
                <div key={idx} className="flex gap-4 relative">
                  <span className="h-2.5 w-2.5 rounded-full bg-primary border-4 border-card outline outline-[1px] outline-primary relative top-1 z-10 shrink-0" />
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <h4 className="text-xs font-semibold text-foreground">{evt.title}</h4>
                      <Badge variant="outline" className="text-[9px] font-mono font-normal">
                        {evt.event_type}
                      </Badge>
                    </div>
                    <p className="text-[10px] text-muted-foreground font-mono">
                      {new Date(evt.timestamp).toUTCString()}
                    </p>
                    {evt.details && Object.keys(evt.details).length > 0 && (
                      <p className="text-[11px] text-muted-foreground pt-1">
                        {evt.details.feedback || evt.details.parsed_skills?.join(", ")}
                        {evt.details.score && ` (Evaluation Overall: ${evt.details.score}/5.0)`}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "evolution" && (
          <div className="rounded-lg border border-border bg-card p-6 shadow-sm space-y-6">
            <div>
              <h3 className="text-sm font-semibold tracking-tight">Competency Progression Curves</h3>
              <p className="text-[11px] text-muted-foreground mt-0.5">
                Displays changes in assessed skills over sequential session loops.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(memory.skill_evolution).map(([name, points], idx) => (
                <div key={idx} className="border border-border rounded p-4 space-y-3 bg-accent/5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold">{name}</span>
                    <span className="font-mono text-[10px] uppercase font-bold text-muted-foreground">
                      Trend: {points[points.length - 1].score >= points[0].score ? "Rising" : "Declining"}
                    </span>
                  </div>
                  <div className="flex items-end justify-between h-20 pt-4 px-2 border-b border-border">
                    {points.map((pt, pIdx) => (
                      <div key={pIdx} className="flex flex-col items-center flex-1 space-y-1">
                        <div 
                          className="w-4 bg-primary rounded-t"
                          style={{ height: `${(pt.score / 5.0) * 100}%` }}
                        />
                        <span className="text-[9px] text-muted-foreground font-mono truncate w-full text-center">
                          {pt.date}
                        </span>
                      </div>
                    ))}
                  </div>
                  <div className="flex justify-between font-mono text-[10px] text-muted-foreground">
                    <span>Initial: {points[0].score}</span>
                    <span>Current: {points[points.length - 1].score}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
