"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as zod from "zod";
import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Shield, Key, Mail, Building, Globe } from "lucide-react";

// Form validation schema
const loginSchema = zod.object({
  email: zod.string().email("Enter a valid organizational email address."),
  password: zod.string().min(6, "Password must contain at least 6 characters."),
  tenant_id: zod.string().min(3, "Tenant ID must consist of lowercase alphanumeric letters and hyphens."),
});

type LoginFormValues = zod.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
      tenant_id: "default-tenant",
    },
  });

  const onSubmit = async (values: LoginFormValues) => {
    setLoading(true);
    setError(null);
    try {
      // Direct demo sign in
      let mockRole: "CANDIDATE" | "RECRUITER" | "ADMIN" = "CANDIDATE";
      let scopes: string[] = ["candidate:read", "candidate:write"];
      
      if (values.email.includes("recruiter")) {
        mockRole = "RECRUITER";
        scopes = ["recruiter:read", "recruiter:write"];
      } else if (values.email.includes("admin")) {
        mockRole = "ADMIN";
        scopes = ["system:admin", "recruiter:read", "recruiter:write"];
      }

      // Generate a mock JWT for development containing the credentials
      const header = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }));
      const payload = btoa(
        JSON.stringify({
          sub: "user-uuid-9999",
          email: values.email,
          role: mockRole,
          tenant_id: values.tenant_id,
          scopes: scopes,
          exp: Math.floor(Date.now() / 1000) + 3600,
        })
      );
      const mockAccessToken = `${header}.${payload}.signature_hash`;
      const mockRefreshToken = `refresh_token_dev_${Date.now()}`;

      // Simulate network request
      await new Promise((resolve) => setTimeout(resolve, 800));

      setAuth(mockAccessToken, mockRefreshToken, {
        id: "user-uuid-9999",
        email: values.email,
        role: mockRole,
        tenant_id: values.tenant_id,
        scopes: scopes,
      });

      // Route based on role
      if (mockRole === "ADMIN") {
        router.push("/admin/dashboard");
      } else if (mockRole === "RECRUITER") {
        router.push("/recruiter/dashboard");
      } else {
        router.push("/candidate/dashboard");
      }
    } catch (err: any) {
      setError(err.message || "Authentication failed. Verify credentials.");
    } finally {
      setLoading(false);
    }
  };

  const loadDemoProfile = (profile: "candidate" | "recruiter" | "admin") => {
    if (profile === "candidate") {
      setValue("email", "jane.doe@candidate.io");
      setValue("password", "candidatePass123");
      setValue("tenant_id", "demo-tenant");
    } else if (profile === "recruiter") {
      setValue("email", "sarah.connor@recruiter.com");
      setValue("password", "recruiterPass999");
      setValue("tenant_id", "demo-tenant");
    } else if (profile === "admin") {
      setValue("email", "john.doe@admin.platform");
      setValue("password", "adminSecurePass");
      setValue("tenant_id", "system-root");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-12 font-sans selection:bg-primary selection:text-primary-foreground">
      <div className="w-full max-w-[420px] rounded-lg border border-border bg-card p-8 shadow-sm transition-all">
        <div className="flex flex-col items-center mb-8">
          <div className="flex h-10 w-10 items-center justify-center rounded-md border border-border bg-accent text-foreground mb-4">
            <Shield className="h-5 w-5" />
          </div>
          <h1 className="text-xl font-semibold tracking-tight">Interviewer Intelligence</h1>
          <p className="text-sm text-muted-foreground mt-1.5 text-center">
            Conduct adaptive interviews and track performance.
          </p>
        </div>

        {error && (
          <div className="mb-4 rounded-md bg-destructive/10 border border-destructive/20 p-3 text-xs text-destructive font-mono">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-semibold text-muted-foreground">Tenant Workspace</label>
            </div>
            <div className="relative">
              <Building className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                {...register("tenant_id")}
                placeholder="company-workspace-id"
                className="pl-9 font-mono"
                error={errors.tenant_id?.message}
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-semibold text-muted-foreground">Email Address</label>
            </div>
            <div className="relative">
              <Mail className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                {...register("email")}
                type="email"
                placeholder="name@organization.com"
                className="pl-9 font-mono"
                error={errors.email?.message}
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-semibold text-muted-foreground">Password</label>
            </div>
            <div className="relative">
              <Key className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                {...register("password")}
                type="password"
                placeholder="••••••••"
                className="pl-9 font-mono"
                error={errors.password?.message}
              />
            </div>
          </div>

          <Button type="submit" className="w-full mt-2" loading={loading}>
            Sign In to Workspace
          </Button>
        </form>

        <div className="mt-8 pt-6 border-t border-border">
          <label className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground block mb-3 text-center">
            Demo Sandbox Accounts
          </label>
          <div className="grid grid-cols-3 gap-2">
            <Button
              variant="outline"
              size="sm"
              className="text-[11px] h-8 px-1"
              onClick={() => loadDemoProfile("candidate")}
            >
              Candidate
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="text-[11px] h-8 px-1"
              onClick={() => loadDemoProfile("recruiter")}
            >
              Recruiter
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="text-[11px] h-8 px-1"
              onClick={() => loadDemoProfile("admin")}
            >
              Admin
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
