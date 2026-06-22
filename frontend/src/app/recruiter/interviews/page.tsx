"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as zod from "zod";
import { Calendar, Plus, Play, Award, Trash2, ArrowRight } from "lucide-react";
import Link from "next/link";

// Zod Schema matching InterviewSessionCreate
const scheduleSchema = zod.object({
  candidate_id: zod.string().uuid("Enter a valid candidate UUID link."),
  type: zod.enum(["TECHNICAL", "HR", "SYSTEM_DESIGN"]),
});

type ScheduleFormValues = zod.infer<typeof scheduleSchema>;

export default function RecruiterInterviewsPage() {
  const [sessions, setSessions] = useState([
    {
      id: "session-uuid-101",
      candidate_name: "Jane Doe",
      type: "TECHNICAL",
      status: "CREATED",
      created_at: "2026-06-22T08:00:00Z",
    },
    {
      id: "session-uuid-102",
      candidate_name: "Jane Doe",
      type: "SYSTEM_DESIGN",
      status: "CREATED",
      created_at: "2026-06-22T09:30:00Z",
    },
    {
      id: "session-uuid-099",
      candidate_name: "Jane Doe",
      type: "HR",
      status: "COMPLETED",
      created_at: "2026-06-15T14:00:00Z",
    }
  ]);

  const [scheduleOpen, setScheduleOpen] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ScheduleFormValues>({
    resolver: zodResolver(scheduleSchema),
    defaultValues: {
      candidate_id: "cand-uuid-001",
      type: "TECHNICAL",
    },
  });

  const handleSchedule = (values: ScheduleFormValues) => {
    // Scaffold insertion
    const newSession = {
      id: `session-uuid-${Date.now()}`,
      candidate_name: "Jane Doe",
      type: values.type,
      status: "CREATED",
      created_at: new Date().toISOString(),
    };
    setSessions([newSession, ...sessions]);
    reset();
    setScheduleOpen(false);
  };

  const typeOptions = [
    { label: "Technical Coding", value: "TECHNICAL" },
    { label: "System Design", value: "SYSTEM_DESIGN" },
    { label: "HR / Behavioral", value: "HR" }
  ];

  return (
    <div className="space-y-8 max-w-6xl font-sans selection:bg-primary selection:text-primary-foreground">
      {/* Header section */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Interview Sessions</h1>
          <p className="text-xs text-muted-foreground mt-1 font-mono">
            Schedule and audit candidate evaluation sessions.
          </p>
        </div>

        <Button size="sm" className="gap-1.5 text-xs font-mono" onClick={() => setScheduleOpen(true)}>
          <Plus className="h-4 w-4" />
          Schedule Session
        </Button>
      </div>

      {/* Schedule Drawer overlay */}
      {scheduleOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-end bg-background/80 backdrop-blur-sm">
          <div className="w-[440px] bg-card border-l border-border h-full flex flex-col p-8 shadow-xl relative animate-in slide-in-from-right duration-200">
            <div className="flex items-center justify-between border-b border-border pb-4 mb-6">
              <h2 className="text-sm font-semibold tracking-tight">Schedule Assessment Session</h2>
              <Button variant="ghost" size="sm" onClick={() => setScheduleOpen(false)} className="text-xs font-mono">
                Close
              </Button>
            </div>

            <form onSubmit={handleSubmit(handleSchedule)} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-muted-foreground mb-1 block">Candidate Profile ID (UUID)</label>
                <Input {...register("candidate_id")} error={errors.candidate_id?.message} className="font-mono text-xs" />
              </div>

              <div>
                <Select
                  label="Assessment Category"
                  options={typeOptions}
                  {...register("type")}
                  error={errors.type?.message}
                  className="font-mono text-xs"
                />
              </div>

              <div className="pt-4">
                <Button type="submit" className="w-full text-xs font-mono">
                  CREATE SESSION
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* List of active sessions */}
      <div className="grid grid-cols-1 gap-4">
        {sessions.map((session) => (
          <div
            key={session.id}
            className="flex flex-col sm:flex-row sm:items-center justify-between p-6 rounded-lg border border-border bg-card hover:border-muted-foreground/30 transition-all gap-4"
          >
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold">Assessment Candidate: {session.candidate_name}</h3>
                <Badge variant="outline" className="text-[10px] font-mono">
                  {session.type}
                </Badge>
                {session.status === "CREATED" && (
                  <Badge variant="warning" className="text-[10px]">
                    Created
                  </Badge>
                )}
                {session.status === "COMPLETED" && (
                  <Badge variant="success" className="text-[10px]">
                    Completed
                  </Badge>
                )}
              </div>
              <div className="flex gap-4 text-xs text-muted-foreground font-mono">
                <span>Session ID: {session.id}</span>
                <span>Scheduled: {new Date(session.created_at).toLocaleDateString()}</span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {session.status === "CREATED" ? (
                <span className="text-xs font-mono text-muted-foreground italic">Pending candidate response...</span>
              ) : (
                <Link href={`/recruiter/candidates/cand-uuid-001`}>
                  <Button variant="outline" size="sm" className="h-8 gap-1.5 text-xs font-mono">
                    <Award className="h-3 w-3" />
                    Review Report
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
