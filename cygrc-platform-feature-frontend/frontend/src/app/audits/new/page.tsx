"use client";
import React from "react";
import Sidebar from "../../../components/ui/Sidebar";
import TopNav from "../../../components/ui/TopNav";
import AuditForm from "../../../components/audits/AuditForm";

export default function NewAuditPage() {
  return (
    <div className="min-h-screen bg-[var(--background)]">
      <div className="mx-auto max-w-7xl">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-[260px_1fr]">
          <Sidebar />
          <div className="flex flex-col gap-6">
            <TopNav />
            <main className="px-4 py-6">
              <h1 className="text-2xl font-semibold text-white">Create New Audit</h1>
              <p className="mt-2 text-sm text-slate-400">Provide audit details and assign an auditor.</p>

              <div className="mt-6 max-w-2xl">
                <AuditForm />
              </div>
            </main>
          </div>
        </div>
      </div>
    </div>
  );
}
