"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Calendar, History, ArrowRight, Play, Award, CheckCircle2 } from "lucide-react";
import Link from "next/link";

export default function CandidateInterviewsPage() {
  const router = useRouter();
  const { user } = useAuthStore();

  const [sessions] = useState([
    {
      id: "session-uuid-101",
      type: "TECHNICAL",
      status: "CREATED",
      created_at: "2026-06-22T08:00:00Z",
      title: "Core Backend Systems Assessment",
    },
    {
      id: "session-uuid-102",
      type: "SYSTEM_DESIGN",
      status: "CREATED",
      created_at: "2026-06-22T09:30:00Z",
      title: "Scalable Data Storage Architecture",
    },
    {
      id: "session-uuid-099",
      type: "HR",
      status: "COMPLETED",
      created_at: "2026-06-15T14:00:00Z",
      title: "Behavioral & Cultural Alignment",
    }
  ]);

  return (
    <div className="space-y-8 max-w-5xl">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Interview Sessions</h1>
        <p className="text-xs text-muted-foreground mt-1 font-mono">
          Authorized User ID: {user?.id} | Row-Level Security Enforced
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {sessions.map((session) => (
          <div
            key={session.id}
            className="flex flex-col sm:flex-row sm:items-center justify-between p-6 rounded-lg border border-border bg-card hover:border-muted-foreground/30 transition-all gap-4"
          >
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold">{session.title}</h3>
                <Badge variant="outline" className="text-[10px] font-mono">
                  {session.type}
                </Badge>
                {session.status === "CREATED" && (
                  <Badge variant="warning" className="text-[10px]">
                    Pending Start
                  </Badge>
                )}
                {session.status === "COMPLETED" && (
                  <Badge variant="success" className="text-[10px]">
                    Completed
                  </Badge>
                )}
              </div>
              <div className="flex gap-4 text-xs text-muted-foreground font-mono">
                <span>Session ID: {session.id.slice(0, 8)}...</span>
                <span>Scheduled: {new Date(session.created_at).toLocaleDateString()}</span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {session.status === "CREATED" ? (
                <Link href={`/candidate/interviews/${session.id}`} className="w-full sm:w-auto">
                  <Button size="sm" className="w-full gap-1.5 text-xs font-mono">
                    <Play className="h-3 w-3" />
                    START ASSESSMENT
                  </Button>
                </Link>
              ) : (
                <Link href={`/candidate/reports/${session.id}`} className="w-full sm:w-auto">
                  <Button variant="outline" size="sm" className="w-full gap-1.5 text-xs font-mono">
                    <Award className="h-3 w-3" />
                    VIEW REPORT
                  </Button>
                </Link>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
