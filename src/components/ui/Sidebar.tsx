"use client";
import Link from "next/link";
import React, { useState } from "react";
import { Home, ShieldCheck, Grid, AlertCircle, Folder, FileText, Users, Settings, Menu } from "lucide-react";

const items = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
  { href: "/compliance", label: "Compliance", icon: ShieldCheck },
  { href: "/controls", label: "Controls", icon: Grid },
  { href: "/risks", label: "Risks", icon: AlertCircle },
  { href: "/audits", label: "Audits", icon: FileText },
  { href: "/evidence", label: "Evidence", icon: Folder },
  { href: "/reports", label: "Reports", icon: FileText },
  { href: "/users", label: "Users", icon: Users },
  { href: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside className={`${collapsed ? "w-20" : "w-64"} hidden md:flex flex-col gap-4 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-3 shadow-[0_8px_30px_rgba(15,23,42,0.05)] transition-all` }>
      <div className="flex items-center justify-between px-2">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-900 text-sm font-bold text-white dark:bg-slate-100 dark:text-slate-900">C</div>
          {!collapsed && (
            <div>
              <h4 className="text-sm font-semibold text-white">CYGRC</h4>
              <p className="text-xs text-slate-400">Governance</p>
            </div>
          )}
        </div>
        <button aria-label="Toggle sidebar" onClick={() => setCollapsed((c) => !c)} className="rounded p-2 text-slate-500 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800">
          <Menu size={16} />
        </button>
      </div>

      <nav className="mt-4 flex flex-col gap-1">
        {items.map((it) => {
          const Icon = it.icon;
          return (
            <Link key={it.href} href={it.href} className={`flex items-center gap-3 rounded-xl px-3 py-2 text-sm text-slate-600 transition hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white ${collapsed ? "justify-center" : ""}`}>
              <Icon size={18} className="text-slate-500 dark:text-slate-300" />
              {!collapsed && <span>{it.label}</span>}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto px-2">
        {!collapsed && <div className="mb-2 text-xs text-slate-500">© {new Date().getFullYear()} CYGRC</div>}
        <div className="flex items-center gap-2">
          <img src="/avatar-placeholder.png" alt="avatar" className="h-8 w-8 rounded-full bg-slate-200 dark:bg-slate-800" />
          {!collapsed && <div className="text-sm text-slate-200">security@corp.com</div>}
        </div>
      </div>
    </aside>
  );
}
