"use client";
import React from "react";
import { useAuth } from "../../context/AuthContext";

const roleContent: Record<string, { title: string; summary: string; focus: string[] }> = {
  admin: {
    title: "Executive oversight",
    summary: "You can monitor enterprise risk, control health, and remediation progress in one place.",
    focus: ["Approve policy exceptions", "Review top risks", "Track control attestations"],
  },
  auditor: {
    title: "Assurance workspace",
    summary: "You can review evidence, validate controls, and track audit readiness.",
    focus: ["Validate evidence", "Review audit findings", "Confirm completion status"],
  },
  analyst: {
    title: "Operations cockpit",
    summary: "You can manage remediation plans, incidents, and day-to-day risk treatment.",
    focus: ["Own issue resolution", "Coordinate owners", "Prioritize actions"],
  },
  viewer: {
    title: "Board-ready visibility",
    summary: "You can stay informed with concise summaries and current status indicators.",
    focus: ["Monitor trends", "Track key metrics", "Review critical updates"],
  },
};

export default function RoleDashboard() {
  const { user } = useAuth();
  const role = user?.role ?? "viewer";
  const content = roleContent[role] ?? roleContent.viewer;

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
      <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-400">Role view</p>
      <h3 className="mt-2 text-xl font-semibold text-white">{content.title}</h3>
      <p className="mt-3 text-sm text-slate-400">{content.summary}</p>
      <ul className="mt-4 space-y-2 text-sm text-slate-300">
        {content.focus.map((item) => (
          <li key={item} className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">{item}</li>
        ))}
      </ul>
    </div>
  );
}
