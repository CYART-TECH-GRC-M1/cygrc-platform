import Link from "next/link";
import React from "react";
import Sidebar from "./Sidebar";
import TopNav from "./TopNav";

export default function PageShell({
  title,
  subtitle,
  children,
  action,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  action?: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[var(--background)]">
      <div className="mx-auto max-w-7xl px-2 py-2 sm:px-4 lg:px-6">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-[260px_1fr]">
          <Sidebar />
          <div className="flex flex-col gap-6">
            <TopNav />
            <main className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] px-4 py-6 shadow-[0_10px_40px_rgba(15,23,42,0.06)] sm:px-6 dark:shadow-none">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <h1 className="text-2xl font-semibold text-white">{title}</h1>
                  {subtitle ? <p className="mt-2 text-sm text-slate-400">{subtitle}</p> : null}
                </div>
                {action ? <div>{action}</div> : null}
              </div>
              <div className="mt-6">{children}</div>
            </main>
          </div>
        </div>
      </div>
    </div>
  );
}
