"use client";

import React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Shield, BrainCircuit, Activity, Network, ArrowRight } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-background font-sans selection:bg-primary selection:text-primary-foreground">
      {/* Navigation header */}
      <header className="flex h-16 items-center justify-between px-8 border-b border-border bg-card">
        <div className="flex items-center gap-2">
          <Shield className="h-5 w-5 text-primary" />
          <span className="font-semibold tracking-tight text-sm">Interviewer Intelligence Platform</span>
        </div>
        <div>
          <Link href="/auth/login">
            <Button variant="outline" size="sm" className="font-mono text-xs">
              Go to Workspace
            </Button>
          </Link>
        </div>
      </header>

      {/* Main hero section */}
      <main className="flex-1 flex flex-col items-center justify-center text-center px-4 max-w-4xl mx-auto space-y-8">
        <div className="space-y-4">
          <div className="inline-flex items-center gap-2 rounded-full border border-border bg-accent/30 px-3 py-1 text-xs font-mono text-muted-foreground">
            <span className="h-1.5 w-1.5 rounded-full bg-success" />
            Adaptive Evaluation Engine Active
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-foreground leading-tight">
            Enterprise Interview Intelligence
          </h1>
          <p className="text-sm md:text-base text-muted-foreground max-w-xl mx-auto leading-relaxed">
            Conduct adaptive AI-driven technical assessments, generate semantic candidate capability maps, and isolate evaluations under row-level security.
          </p>
        </div>

        {/* Feature widgets */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 w-full max-w-3xl pt-6">
          <div className="rounded-lg border border-border bg-card p-6 text-left space-y-3">
            <div className="h-8 w-8 rounded bg-accent/20 border border-border flex items-center justify-center text-primary">
              <BrainCircuit className="h-4 w-4" />
            </div>
            <h3 className="text-xs font-bold font-mono text-foreground uppercase tracking-wider">Adaptive Loops</h3>
            <p className="text-xs text-muted-foreground leading-normal">
              Questions adapt in difficulty and target skill category sequentially based on transcript analysis.
            </p>
          </div>

          <div className="rounded-lg border border-border bg-card p-6 text-left space-y-3">
            <div className="h-8 w-8 rounded bg-accent/20 border border-border flex items-center justify-center text-primary">
              <Network className="h-4 w-4" />
            </div>
            <h3 className="text-xs font-bold font-mono text-foreground uppercase tracking-wider">Memory Graph</h3>
            <p className="text-xs text-muted-foreground leading-normal">
              Chronological milestone logging and semantic entity connection graphs show long-term growth.
            </p>
          </div>

          <div className="rounded-lg border border-border bg-card p-6 text-left space-y-3">
            <div className="h-8 w-8 rounded bg-accent/20 border border-border flex items-center justify-center text-primary">
              <Shield className="h-4 w-4" />
            </div>
            <h3 className="text-xs font-bold font-mono text-foreground uppercase tracking-wider">Data Boundaries</h3>
            <p className="text-xs text-muted-foreground leading-normal">
              Logical schema multi-tenant context separation maps credentials safely inside Postgres RLS.
            </p>
          </div>
        </div>

        <div className="pt-8">
          <Link href="/auth/login">
            <Button size="lg" className="gap-2 font-mono text-xs px-8">
              ENTER SYSTEM WORKSPACE
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="h-14 border-t border-border bg-card flex items-center justify-between px-8 text-[11px] font-mono text-muted-foreground">
        <span>Logical separation: verified-isolation</span>
        <span>Secure Protocol: TLS 1.3 SSE-KMS</span>
      </footer>
    </div>
  );
}
