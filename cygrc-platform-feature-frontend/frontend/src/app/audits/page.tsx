"use client";
import React from "react";
import PageShell from "../../components/ui/PageShell";
import AuditTable from "../../components/audits/AuditTable";

export default function AuditsPage() {
  return (
    <PageShell
      title="Audits"
      subtitle="Manage audit programs, assign auditors, and track progress."
    >
      <div className="space-y-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
          <p className="text-sm text-slate-400">Audit planning and evidence collection are synchronized with the broader governance program.</p>
        </div>
        <AuditTable />
      </div>
    </PageShell>
  );
}
