"use client";

import React, { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Activity,
  Database,
  Building,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  Server,
  Zap,
  ArrowRight
} from "lucide-react";
import Link from "next/link";

export default function AdminDashboard() {
  const [platformServices] = useState([
    { name: "PostgreSQL Database", status: "HEALTHY", delay: "2ms", type: "DB" },
    { name: "Qdrant Vector DB", status: "HEALTHY", delay: "8ms", type: "VECTOR" },
    { name: "Redis Cache / Locker", status: "HEALTHY", delay: "1ms", type: "CACHE" },
    { name: "Celery Workers Pool", status: "HEALTHY", delay: "Queue Empty", type: "WORKER" },
    { name: "MinIO S3 Storage", status: "HEALTHY", delay: "12ms", type: "STORAGE" }
  ]);

  const [alerts] = useState([
    {
      id: "alert-1",
      tenant: "standard-tenant-4",
      title: "API Limit Warning",
      description: "Tenant standard-tenant-4 has consumed 92% of monthly API limit bounds.",
      level: "WARNING",
    },
    {
      id: "alert-2",
      tenant: "demo-tenant",
      title: "Celery Task Retry Exceeded",
      description: "Audio stitching failed 3 times for session session-uuid-101. Out of memory check.",
      level: "CRITICAL",
    }
  ]);

  const [metrics] = useState({
    active_tenants: 8,
    total_interviews_run: 341,
    avg_latency: "142ms",
    cpu_utilization: "24%",
  });

  return (
    <div className="space-y-8 max-w-6xl font-sans selection:bg-primary selection:text-primary-foreground">
      {/* Header section */}
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Platform Operations Dashboard</h1>
        <p className="text-xs text-muted-foreground mt-1 font-mono">
          System telemetry metrics & cross-tenant cluster monitoring.
        </p>
      </div>

      {/* Metric panels */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-lg border border-border bg-card p-4 shadow-sm">
          <p className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">Active Tenancy Namespaces</p>
          <p className="text-xl font-bold tracking-tight mt-1">{metrics.active_tenants}</p>
          <div className="flex items-center gap-1 mt-1 text-[10px] text-success font-mono">
            <Building className="h-3 w-3" />
            <span>All schema isolated</span>
          </div>
        </div>

        <div className="rounded-lg border border-border bg-card p-4 shadow-sm">
          <p className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">Total Interviews Logged</p>
          <p className="text-xl font-bold tracking-tight mt-1">{metrics.total_interviews_run}</p>
          <div className="flex items-center gap-1 mt-1 text-[10px] text-success font-mono">
            <TrendingUp className="h-3 w-3" />
            <span>+18% growth month-over-month</span>
          </div>
        </div>

        <div className="rounded-lg border border-border bg-card p-4 shadow-sm">
          <p className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">Average Gateway Latency</p>
          <p className="text-xl font-bold tracking-tight mt-1">{metrics.avg_latency}</p>
          <div className="flex items-center gap-1 mt-1 text-[10px] text-success font-mono">
            <Zap className="h-3 w-3" />
            <span>Optimal latency targets</span>
          </div>
        </div>

        <div className="rounded-lg border border-border bg-card p-4 shadow-sm">
          <p className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">CPU Node Utilization</p>
          <p className="text-xl font-bold tracking-tight mt-1">{metrics.cpu_utilization}</p>
          <div className="flex items-center gap-1 mt-1 text-[10px] text-muted-foreground font-mono">
            <span>Server context normal</span>
          </div>
        </div>
      </div>

      {/* Grid: Health logs and System alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Services status list (2/3 width) */}
        <div className="lg:col-span-2 rounded-lg border border-border bg-card p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-2 border-b border-border pb-3">
            <Server className="h-4 w-4 text-muted-foreground" />
            <h2 className="text-sm font-semibold tracking-tight">Microservice Cluster Status</h2>
          </div>

          <div className="divide-y divide-border">
            {platformServices.map((service, idx) => (
              <div key={idx} className="py-3.5 first:pt-0 last:pb-0 flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="h-2 w-2 rounded-full bg-success" />
                  <div>
                    <h3 className="text-xs font-semibold">{service.name}</h3>
                    <p className="text-[10px] text-muted-foreground font-mono uppercase mt-0.5">Segment: {service.type}</p>
                  </div>
                </div>

                <div className="flex items-center gap-4 text-xs font-mono">
                  <span className="text-muted-foreground">Latency: {service.delay}</span>
                  <Badge variant="success" className="text-[9px] uppercase">
                    {service.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* System alerts widget (1/3 width) */}
        <div className="rounded-lg border border-border bg-card p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-2 border-b border-border pb-3">
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            <h2 className="text-sm font-semibold tracking-tight">Active Platform Alerts</h2>
          </div>

          <div className="space-y-4">
            {alerts.map((al) => (
              <div
                key={al.id}
                className={`border rounded p-4 space-y-2 text-xs font-mono ${
                  al.level === "CRITICAL"
                    ? "bg-destructive/5 border-destructive/20 text-destructive"
                    : "bg-warning/5 border-warning/20 text-warning"
                }`}
              >
                <div className="flex justify-between items-center">
                  <span className="font-bold uppercase text-[10px]">Level: {al.level}</span>
                  <span className="text-[9px] text-muted-foreground">Tenant: {al.tenant}</span>
                </div>
                <p className="font-bold text-foreground leading-snug">{al.title}</p>
                <p className="text-muted-foreground leading-normal">{al.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
