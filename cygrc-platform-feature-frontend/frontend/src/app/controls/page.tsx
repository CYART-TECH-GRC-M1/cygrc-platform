"use client";
import React from "react";
import PageShell from "../../components/ui/PageShell";
import ControlTable from "../../components/controls/ControlTable";

export default function ControlsPage() {
  return (
    <PageShell
      title="Compliance Controls"
      subtitle="Manage controls across frameworks and assign owners."
    >
      <div className="space-y-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
          <p className="text-sm text-slate-400">Operational metrics, evidence linkage, and policy alignment are tracked here for each control family.</p>
        </div>
        <ControlTable />
      </div>
    </PageShell>
  );
}
