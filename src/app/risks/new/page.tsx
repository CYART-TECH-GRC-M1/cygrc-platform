"use client";
import React from "react";
import Sidebar from "../../../components/ui/Sidebar";
import TopNav from "../../../components/ui/TopNav";
import RiskForm from "../../../components/risks/RiskForm";

export default function NewRiskPage() {
  return (
    <div className="min-h-screen bg-[var(--background)]">
      <div className="mx-auto max-w-7xl">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-[260px_1fr]">
          <Sidebar />
          <div className="flex flex-col gap-6">
            <TopNav />
            <main className="px-4 py-6">
              <h1 className="text-2xl font-semibold text-white">Add Risk</h1>
              <p className="mt-2 text-sm text-slate-400">Create a new risk and assign an owner.</p>

              <div className="mt-6 max-w-2xl">
                <RiskForm />
              </div>
            </main>
          </div>
        </div>
      </div>
    </div>
  );
}
