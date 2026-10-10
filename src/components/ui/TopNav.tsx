"use client";
import React from "react";
import Link from "next/link";
import { Bell, Search, Sparkles } from "lucide-react";
import ThemeToggle from "./ThemeToggle";

export default function TopNav() {
  return (
    <header className="sticky top-0 z-20 flex w-full items-center justify-between gap-4 rounded-[1.25rem] border border-[var(--border)] bg-[var(--surface)]/90 px-4 py-3 shadow-[0_8px_30px_rgba(15,23,42,0.06)] backdrop-blur">
      <div className="flex flex-1 items-center gap-3">
        <button className="rounded-full border border-[var(--border)] p-2 text-[var(--muted)] transition hover:bg-[var(--surface-strong)] hover:text-[var(--foreground)] md:hidden">Menu</button>
        <div className="flex hidden items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--surface-strong)] px-3 py-2 text-sm text-[var(--muted)] md:flex">
          <Search size={16} />
          <span>Search controls, risks, audits...</span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-2 text-sm font-medium text-blue-700 transition hover:bg-blue-100 dark:border-blue-900/40 dark:bg-blue-950/40 dark:text-blue-200">
          <Sparkles size={16} />
          AI Assist
        </button>
        <ThemeToggle />
        <button className="rounded-full border border-[var(--border)] p-2 text-[var(--muted)] transition hover:bg-[var(--surface-strong)] hover:text-[var(--foreground)]">
          <Bell size={16} />
        </button>
        <Link href="/connectors" className="hidden rounded-full border border-[var(--border)] px-3 py-2 text-sm font-medium text-[var(--foreground)] transition hover:bg-[var(--surface-strong)] sm:block">
          Connectors
        </Link>
        <div className="flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--surface-strong)] px-2 py-1">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-blue-600 to-cyan-500 text-sm font-semibold text-white">AM</div>
          <div className="hidden text-left sm:block">
            <p className="text-sm font-semibold text-[var(--foreground)]">Alex Morgan</p>
            <p className="text-xs text-[var(--muted)]">Admin</p>
          </div>
        </div>
      </div>
    </header>
  );
}
