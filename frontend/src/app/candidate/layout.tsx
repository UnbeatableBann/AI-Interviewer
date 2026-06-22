"use client";

import React, { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/button";
import {
  LayoutDashboard,
  Calendar,
  History,
  FileUser,
  Settings,
  LogOut,
  Shield,
  User,
  Menu,
  X
} from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

export default function CandidateLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isAuthenticated, clearAuth } = useAuthStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    // Redirect if not authenticated or not a candidate
    if (!isAuthenticated || !user) {
      router.push("/auth/login");
      return;
    }
    if (user.role !== "CANDIDATE" && user.role !== "ADMIN") {
      router.push("/auth/login");
    }
  }, [isAuthenticated, user, router]);

  if (!isAuthenticated || !user) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-background text-muted-foreground font-mono text-xs">
        Verifying secure candidate session...
      </div>
    );
  }

  const navItems = [
    { label: "Dashboard", href: "/candidate/dashboard", icon: LayoutDashboard },
    { label: "Interview Sessions", href: "/candidate/interviews", icon: Calendar },
    { label: "Skill Intelligence Profile", href: "/candidate/profile", icon: FileUser },
    { label: "Settings", href: "/candidate/settings", icon: Settings },
  ];

  const handleLogout = () => {
    clearAuth();
    router.push("/auth/login");
  };

  return (
    <div className="flex min-h-screen bg-background font-sans">
      {/* Sidebar for Desktop */}
      <aside className="hidden md:flex w-64 flex-col border-r border-border bg-card">
        <div className="flex h-14 items-center gap-2 px-6 border-b border-border">
          <Shield className="h-5 w-5 text-primary" />
          <span className="font-semibold tracking-tight text-sm">IIP Candidate Portal</span>
        </div>

        <nav className="flex-1 space-y-1 px-4 py-6">
          {navItems.map((item) => {
            const isActive = pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                )}
              >
                <Icon className="h-4 w-4 shrink-0" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Footer profile info */}
        <div className="p-4 border-t border-border bg-accent/20">
          <div className="flex items-center gap-3 mb-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent text-foreground border border-border">
              <User className="h-4 w-4" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold truncate text-foreground">{user.email}</p>
              <p className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground font-mono">
                {user.role} ({user.tenant_id})
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="w-full text-xs text-muted-foreground hover:text-destructive hover:bg-destructive/10 justify-start gap-2 h-8"
            onClick={handleLogout}
          >
            <LogOut className="h-3.5 w-3.5" />
            Sign Out
          </Button>
        </div>
      </aside>

      {/* Main Body */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header bar */}
        <header className="flex h-14 items-center justify-between px-6 border-b border-border bg-card">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden h-8 w-8"
              onClick={() => setMobileMenuOpen(true)}
            >
              <Menu className="h-4 w-4" />
            </Button>
            <span className="text-xs font-mono text-muted-foreground uppercase tracking-wider">
              Secure Channel | RLS active
            </span>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-[11px] font-mono border border-border px-2 py-0.5 rounded bg-accent">
              Workspace: {user.tenant_id}
            </span>
          </div>
        </header>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="fixed inset-0 z-50 flex md:hidden bg-background/80 backdrop-blur-sm">
            <div className="w-64 bg-card border-r border-border h-full flex flex-col p-6 shadow-xl relative animate-in slide-in-from-left duration-200">
              <Button
                variant="ghost"
                size="icon"
                className="absolute right-4 top-4 h-8 w-8"
                onClick={() => setMobileMenuOpen(false)}
              >
                <X className="h-4 w-4" />
              </Button>
              <div className="flex items-center gap-2 pb-6 border-b border-border mb-6">
                <Shield className="h-5 w-5" />
                <span className="font-semibold text-sm">IIP Portal</span>
              </div>
              <nav className="flex-1 space-y-1">
                {navItems.map((item) => {
                  const isActive = pathname.startsWith(item.href);
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                        isActive
                          ? "bg-primary text-primary-foreground"
                          : "text-muted-foreground hover:bg-accent hover:text-foreground"
                      )}
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      <Icon className="h-4 w-4" />
                      {item.label}
                    </Link>
                  );
                })}
              </nav>
              <div className="pt-6 border-t border-border mt-6">
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full text-xs text-muted-foreground hover:text-destructive justify-start gap-2 h-8"
                  onClick={handleLogout}
                >
                  <LogOut className="h-3.5 w-3.5" />
                  Sign Out
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Page children container */}
        <main className="flex-1 overflow-y-auto p-8">{children}</main>
      </div>
    </div>
  );
}
