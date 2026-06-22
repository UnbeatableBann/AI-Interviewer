"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Calendar,
  ArrowRight,
  TrendingUp,
  BrainCircuit,
  Compass,
  AlertTriangle,
  CheckCircle2,
  Lock,
  ArrowUpRight
} from "lucide-react";
import Link from "next/link";

export default function CandidateDashboard() {
  const router = useRouter();
  
  // Dummy candidate dashboard metrics matching architecture spec
  const [upcomingInterviews] = useState([
    {
      id: "session-uuid-101",
      role: "Senior Backend Engineer",
      type: "TECHNICAL",
      status: "CREATED",
      duration: "45 mins",
      date: "Scheduled Today",
    },
    {
      id: "session-uuid-102",
      role: "Senior Backend Engineer",
      type: "SYSTEM_DESIGN",
      status: "CREATED",
      duration: "60 mins",
      date: "Scheduled tomorrow",
    }
  ]);

  const [strengths] = useState([
    { title: "Asynchronous APIs design", details: "Strong execution of FastAPI non-blocking async schemas and session isolation boundaries." },
    { title: "Logical database isolation", details: "Demonstrated clear knowledge of PostgreSQL RLS policies and connection parameters." }
  ]);

  const [weaknesses] = useState([
    { title: "Distributed Mutual Exclusion", details: "Identified gap in configuring Redis lock leases during peak concurrent transaction limits." }
  ]);

  const [skills] = useState([
    { name: "Python / FastAPI", level: 4.5, change: "+0.5", type: "up" },
    { name: "PostgreSQL Isolation", level: 4.2, change: "+0.8", type: "up" },
    { name: "System Design Topology", level: 3.5, change: "Flat", type: "flat" },
    { name: "Distributed Cache / Redis", level: 2.8, change: "-0.2", type: "down" }
  ]);

  return (
    <div className="space-y-8 max-w-6xl">
      {/* Header section */}
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Candidate Center</h1>
        <p className="text-xs text-muted-foreground mt-1 font-mono">
          Continuous Assessment Loop | Tracking Jane Doe
        </p>
      </div>

      {/* Grid container */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Column (2/3 width on desktop) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Upcoming Sessions Section */}
          <div className="rounded-lg border border-border bg-card p-6">
            <div className="flex items-center gap-2 mb-4">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <h2 className="text-sm font-semibold tracking-tight">Active Interview Sessions</h2>
            </div>
            
            <div className="divide-y divide-border">
              {upcomingInterviews.map((session) => (
                <div key={session.id} className="py-4 first:pt-0 last:pb-0 flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold">{session.role}</span>
                      <Badge variant="outline" className="text-[10px]">
                        {session.type}
                      </Badge>
                      <Badge variant="success" className="text-[10px]">
                        Ready
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1 font-mono">
                      {session.date} • {session.duration}
                    </p>
                  </div>
                  <Link href={`/candidate/interviews`}>
                    <Button variant="outline" size="sm" className="h-8 gap-1.5 text-xs">
                      Enter Room
                      <ArrowRight className="h-3 w-3" />
                    </Button>
                  </Link>
                </div>
              ))}
            </div>
          </div>

          {/* Skill gaps & growth areas */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Strengths Card */}
            <div className="rounded-lg border border-border bg-card p-6">
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle2 className="h-4 w-4 text-success" />
                <h3 className="text-sm font-semibold tracking-tight">Identified Strengths</h3>
              </div>
              <div className="space-y-3">
                {strengths.map((str, idx) => (
                  <div key={idx} className="text-xs">
                    <p className="font-semibold text-foreground">{str.title}</p>
                    <p className="text-muted-foreground mt-1 leading-normal">{str.details}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Weaknesses Card */}
            <div className="rounded-lg border border-border bg-card p-6">
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle className="h-4 w-4 text-warning" />
                <h3 className="text-sm font-semibold tracking-tight">Development Gaps</h3>
              </div>
              <div className="space-y-3">
                {weaknesses.map((weak, idx) => (
                  <div key={idx} className="text-xs">
                    <p className="font-semibold text-foreground">{weak.title}</p>
                    <p className="text-muted-foreground mt-1 leading-normal">{weak.details}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar Column (1/3 width on desktop) */}
        <div className="space-y-6">
          {/* Skill Matrix Summary */}
          <div className="rounded-lg border border-border bg-card p-6">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
              <h2 className="text-sm font-semibold tracking-tight">Skills Capability</h2>
            </div>
            
            <div className="space-y-4">
              {skills.map((skill, idx) => (
                <div key={idx} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="truncate">{skill.name}</span>
                    <span className="flex items-center gap-1.5 font-bold">
                      {skill.level.toFixed(1)}/5.0
                      <span className={
                        skill.type === "up" ? "text-success" : 
                        skill.type === "down" ? "text-destructive" : 
                        "text-muted-foreground"
                      }>
                        ({skill.change})
                      </span>
                    </span>
                  </div>
                  {/* Progress Line */}
                  <div className="h-1.5 w-full bg-secondary rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary rounded-full"
                      style={{ width: `${(skill.level / 5.0) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recommended Roadmap */}
          <div className="rounded-lg border border-border bg-card p-6">
            <div className="flex items-center gap-2 mb-3">
              <Compass className="h-4 w-4 text-muted-foreground" />
              <h2 className="text-sm font-semibold tracking-tight">Growth Recommendations</h2>
            </div>
            <p className="text-xs text-muted-foreground leading-normal mb-4">
              Based on your evaluation in Session #291, you should study cache synchronization patterns and lock leases.
            </p>
            <div className="space-y-2">
              <Link href="https://redis.io/docs/manual/patterns/distributed-locks/" target="_blank">
                <Button variant="outline" size="sm" className="w-full text-xs h-8 justify-between font-mono">
                  Redis Distributed Locks
                  <ArrowUpRight className="h-3 w-3" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
