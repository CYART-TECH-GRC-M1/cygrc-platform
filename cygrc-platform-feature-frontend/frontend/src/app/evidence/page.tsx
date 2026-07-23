"use client";
import React from "react";
import Sidebar from "../../components/ui/Sidebar";
import TopNav from "../../components/ui/TopNav";
import EvidenceUpload from "../../components/evidence/EvidenceUpload";
import EvidenceTable from "../../components/evidence/EvidenceTable";

export default function EvidencePage() {
  return (
    <div className="min-h-screen bg-[var(--background)]">
      <div className="mx-auto max-w-7xl">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-[260px_1fr]">
          <Sidebar />
          <div className="flex flex-col gap-6">
            <TopNav />
            <main className="px-4 py-6">
              <h1 className="text-2xl font-semibold text-white">Evidence Management</h1>
              <p className="mt-2 text-sm text-slate-400">Upload, preview, and manage evidence files.</p>

              <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
                <div className="col-span-2">
                  <EvidenceUpload onComplete={() => { /* refresh handled in table via search or reload */ }} />
                </div>
                <div className="col-span-1">
                  <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
                    <h4 className="text-sm font-semibold text-white">Upload Tips</h4>
                    <ul className="mt-3 text-sm text-slate-300">
                      <li>Supported types: images, PDF, archives</li>
                      <li>Max file size: depends on backend (demo: unlimited)</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="mt-6">
                <EvidenceTable />
              </div>
            </main>
          </div>
        </div>
      </div>
    </div>
  );
}
