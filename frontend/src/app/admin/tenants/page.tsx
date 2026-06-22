"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as zod from "zod";
import {
  Building,
  Plus,
  Ban,
  CheckCircle,
  Database,
  ArrowRight,
  ShieldAlert
} from "lucide-react";

// Form validation schema matching TenantCreate
const tenantSchema = zod.object({
  id: zod
    .string()
    .min(3, "Tenant ID must contain at least 3 characters.")
    .max(50)
    .regex(/^[a-z0-9\-]+$/, "ID slug can only contain lowercase letters, numbers, and hyphens."),
  name: zod.string().min(2, "Company name must contain at least 2 characters.").max(100),
  tier: zod.enum(["STANDARD", "ENTERPRISE", "DEDICATED"]),
});

type TenantFormValues = zod.infer<typeof tenantSchema>;

export default function TenantManagementPage() {
  const [tenants, setTenants] = useState([
    {
      id: "demo-tenant",
      name: "Acme Corporation Demo",
      tier: "STANDARD",
      status: "ACTIVE",
      created_at: "2026-06-20",
    },
    {
      id: "enterprise-a",
      name: "Global Tech Solutions Inc",
      tier: "ENTERPRISE",
      status: "ACTIVE",
      created_at: "2026-06-18",
    },
    {
      id: "standard-tenant-4",
      name: "Stark Industries Sandbox",
      tier: "STANDARD",
      status: "SUSPENDED",
      created_at: "2026-06-15",
    }
  ]);

  const [provisionOpen, setProvisionOpen] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TenantFormValues>({
    resolver: zodResolver(tenantSchema),
    defaultValues: {
      id: "",
      name: "",
      tier: "STANDARD",
    },
  });

  const handleCreateTenant = (values: TenantFormValues) => {
    const newTenant = {
      id: values.id,
      name: values.name,
      tier: values.tier,
      status: "ACTIVE",
      created_at: new Date().toISOString().split("T")[0],
    };
    setTenants([newTenant, ...tenants]);
    reset();
    setProvisionOpen(false);
  };

  const handleToggleStatus = (tenantId: string) => {
    setTenants(
      tenants.map((t) => {
        if (t.id === tenantId) {
          const nextStatus = t.status === "ACTIVE" ? "SUSPENDED" : "ACTIVE";
          return { ...t, status: nextStatus };
        }
        return t;
      })
    );
  };

  const tierOptions = [
    { label: "Standard Subscription Tier", value: "STANDARD" },
    { label: "Enterprise Isolated Tier", value: "ENTERPRISE" },
    { label: "Dedicated Database Cluster", value: "DEDICATED" }
  ];

  return (
    <div className="space-y-8 max-w-6xl font-sans selection:bg-primary selection:text-primary-foreground">
      {/* Header section */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Tenant Namespace Management</h1>
          <p className="text-xs text-muted-foreground mt-1 font-mono">
            Provision connection routing parameters & isolate database schemes.
          </p>
        </div>

        <Button size="sm" className="gap-1.5 text-xs font-mono" onClick={() => setProvisionOpen(true)}>
          <Plus className="h-4 w-4" />
          Provision Tenant
        </Button>
      </div>

      {/* Provision Drawer overlay */}
      {provisionOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-end bg-background/80 backdrop-blur-sm">
          <div className="w-[440px] bg-card border-l border-border h-full flex flex-col p-8 shadow-xl relative animate-in slide-in-from-right duration-200">
            <div className="flex items-center justify-between border-b border-border pb-4 mb-6">
              <h2 className="text-sm font-semibold tracking-tight">Provision Tenant Workspace</h2>
              <Button variant="ghost" size="sm" onClick={() => setProvisionOpen(false)} className="text-xs font-mono">
                Close
              </Button>
            </div>

            <form onSubmit={handleSubmit(handleCreateTenant)} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-muted-foreground mb-1 block">Tenant Slug ID URL</label>
                <Input
                  {...register("id")}
                  placeholder="e.g. acme-corp"
                  error={errors.id?.message}
                  className="font-mono text-xs"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-muted-foreground mb-1 block">Business Name</label>
                <Input
                  {...register("name")}
                  placeholder="Acme Corporation"
                  error={errors.name?.message}
                  className="font-mono text-xs"
                />
              </div>

              <div>
                <Select
                  label="Subscription Tier"
                  options={tierOptions}
                  {...register("tier")}
                  error={errors.tier?.message}
                  className="font-mono text-xs"
                />
              </div>

              <div className="pt-4">
                <Button type="submit" className="w-full text-xs font-mono">
                  ACTIVATE INSTANCE
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* List of tenants */}
      <div className="grid grid-cols-1 gap-4">
        {tenants.map((t) => (
          <div
            key={t.id}
            className="flex flex-col sm:flex-row sm:items-center justify-between p-6 rounded-lg border border-border bg-card hover:border-muted-foreground/30 transition-all gap-4"
          >
            <div className="space-y-1.5 flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold truncate">{t.name}</h3>
                <Badge variant="outline" className="text-[10px] font-mono">
                  Tier: {t.tier}
                </Badge>
                {t.status === "ACTIVE" ? (
                  <Badge variant="success" className="text-[10px] uppercase">
                    Active
                  </Badge>
                ) : (
                  <Badge variant="destructive" className="text-[10px] uppercase">
                    Suspended
                  </Badge>
                )}
              </div>
              <div className="flex gap-4 text-xs text-muted-foreground font-mono">
                <span>Slug ID: {t.id}</span>
                <span>Created: {t.created_at}</span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant={t.status === "ACTIVE" ? "destructive" : "default"}
                size="sm"
                className="h-8 gap-1.5 text-xs font-mono"
                onClick={() => handleToggleStatus(t.id)}
              >
                {t.status === "ACTIVE" ? (
                  <>
                    <Ban className="h-3.5 w-3.5" />
                    SUSPEND TENANT
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-3.5 w-3.5" />
                    ACTIVATE TENANT
                  </>
                )}
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
