"use client";
import React from "react";
import PageShell from "../../components/ui/PageShell";
import RiskTable from "../../components/risks/RiskTable";
import RequirementList from "../../components/risks/RequirementList";

export default function RisksPage() {
  return (
    <PageShell
      title="Risk Management"
      subtitle="Track and manage organizational risks with enterprise-grade oversight."
    >
      <div className="space-y-6">
        <RequirementList />
        <RiskTable />
      </div>
    </PageShell>
  );
}
