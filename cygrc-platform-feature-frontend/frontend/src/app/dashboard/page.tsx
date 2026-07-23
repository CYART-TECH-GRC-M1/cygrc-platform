"use client";
import React from "react";
import RequireAuth from "../../components/ui/RequireAuth";
import PageShell from "../../components/ui/PageShell";
import KpiGrid from "../../components/dashboard/KpiGrid";
import ComplianceChart from "../../components/dashboard/ComplianceChart";
import ActivityTable from "../../components/dashboard/ActivityTable";
import RoleDashboard from "../../components/dashboard/RoleDashboard";
import Link from "next/link";

export default function DashboardPage() {
  return (
    <RequireAuth>
      <PageShell
        title="Executive GRC Overview"
        subtitle="Operational visibility for compliance, risk, and control performance."
        action={
          <Link href="/risks/new" className="rounded-2xl bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-slate-200">
            New risk review
          </Link>
        }
      >
        <div className="space-y-6">
          <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-white">Program health snapshot</h2>
                <p className="mt-2 text-sm text-slate-400">A consolidated view of control status, remediation progress, and audit readiness.</p>
              </div>
              <div className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-sm text-emerald-300">
                94% on-track
              </div>
            </div>
          </section>

          <KpiGrid />

          <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
            <RoleDashboard />
            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
              <h3 className="text-lg font-semibold text-white">Priority actions</h3>
              <ul className="mt-4 space-y-3 text-sm text-slate-300">
                <li className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">Finalize remediation plans for 3 high-severity risks</li>
                <li className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">Review evidence uploads pending executive approval</li>
                <li className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">Prepare audit readiness report for Q3</li>
              </ul>
            </div>
          </div>

          <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
            <ComplianceChart />
            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
              <h3 className="text-lg font-semibold text-white">Role-based access</h3>
              <p className="mt-2 text-sm text-slate-400">Admins manage policies, analysts own mitigation, auditors review controls, and viewers stay informed.</p>
              <div className="mt-4 space-y-2 text-sm text-slate-300">
                <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">Admin: Full governance and remediation visibility</div>
                <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">Analyst: Incident and risk workflow ownership</div>
                <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">Auditor: Control assurance and evidence review</div>
              </div>
            </div>
          </div>

          <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
            <div>
              <h3 className="mb-4 text-sm font-semibold uppercase tracking-[0.28em] text-slate-400">Recent activity</h3>
              <ActivityTable />
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
              <h3 className="text-lg font-semibold text-white">Operational notes</h3>
              <p className="mt-2 text-sm text-slate-400">Security teams can keep executives informed with transparent statuses and next steps.</p>
            </div>
          </div>
        </div>
      </PageShell>
    </RequireAuth>
  );
}
