"use client";

import React, { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FileSpreadsheet, Eye, Plus, ArrowRight, BookOpen } from "lucide-react";

export default function TemplatesPage() {
  const [rubrics] = useState([
    {
      id: "rubric-1",
      title: "Senior Backend Engineer Rubric",
      target_skills: ["Python/FastAPI", "Postgres RLS", "System Design"],
      tier: "ENTERPRISE",
      min_years: 5,
    },
    {
      id: "rubric-2",
      title: "Security & Cloud Compliance Rubric",
      target_skills: ["Encryption", "SOC2 Controls", "Logical Isolation"],
      tier: "STANDARD",
      min_years: 3,
    }
  ]);

  return (
    <div className="space-y-8 max-w-5xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Assessment Rubrics</h1>
          <p className="text-xs text-muted-foreground mt-1 font-mono">
            Define target skill guidelines and evaluation matrices.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {rubrics.map((rub) => (
          <div key={rub.id} className="rounded-lg border border-border bg-card p-6 shadow-sm flex flex-col justify-between space-y-4 hover:border-muted-foreground/30 transition-all">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold">{rub.title}</h3>
                <Badge variant="outline" className="text-[9px] font-mono scale-90">
                  {rub.tier}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground font-mono">
                Min Experience: {rub.min_years} Years
              </p>
              
              <div className="pt-2">
                <label className="text-[10px] uppercase font-bold tracking-wide text-muted-foreground font-mono">Target Competencies</label>
                <div className="flex flex-wrap gap-1 mt-1">
                  {rub.target_skills.map((s, idx) => (
                    <Badge key={idx} variant="secondary" className="text-[9px] font-mono">
                      {s}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>

            <Button variant="outline" size="sm" className="w-full text-xs font-mono h-8 justify-between">
              <span>Inspect Rubric Details</span>
              <ArrowRight className="h-3 w-3" />
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
}
