"use client";

import React from "react";
import {
FileText,
BarChart3,
Download,
ArrowUpRight,
} from "lucide-react";

export default function ReportsPage() {
return ( <div className="space-y-6">
{/* =====================================================
PAGE HEADER
====================================================== */}

  <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
    <div>
      <div className="mb-2 flex items-center gap-2">
        <div className="h-1 w-8 rounded-full bg-orange-500" />

        <span className="font-mono text-[9px] font-semibold tracking-[0.2em] text-orange-400">
          CYGRC / REPORTS
        </span>
      </div>

      <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
        Reports
      </h1>

      <p className="mt-2 text-sm text-zinc-500">
        Executive summaries, compliance snapshots, and
        scheduled reporting views.
      </p>
    </div>
  </div>

  {/* =====================================================
      REPORT OVERVIEW
  ====================================================== */}

  <div className="grid gap-4 lg:grid-cols-2">
    {/* Executive Reporting */}

    <div className="group relative overflow-hidden rounded-2xl border border-orange-500/20 bg-[#080807] p-6 transition-all duration-300 hover:border-orange-500/50 hover:shadow-[0_0_30px_rgba(249,115,22,0.08)]">
      <div className="pointer-events-none absolute right-0 top-0 h-16 w-16 border-r border-t border-orange-500/20" />

      <div className="flex items-start justify-between">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-orange-500/30 bg-orange-500/[0.08] text-orange-400 transition group-hover:bg-orange-500/15">
          <FileText
            size={21}
            strokeWidth={1.5}
          />
        </div>

        <span className="font-mono text-[8px] tracking-[0.2em] text-zinc-700">
          REPORT_01
        </span>
      </div>

      <h2 className="mt-6 text-lg font-semibold tracking-wide text-white">
        Executive reporting
      </h2>

      <p className="mt-2 text-sm leading-6 text-zinc-500">
        Board-ready summaries tailored for security
        leaders and compliance stakeholders.
      </p>

      <div className="mt-6 flex items-center justify-between border-t border-orange-500/10 pt-4">
        <span className="font-mono text-[9px] tracking-[0.18em] text-emerald-500">
          BOARD_READY
        </span>

        <button
          type="button"
          className="flex items-center gap-2 font-mono text-[9px] tracking-widest text-orange-400 transition hover:text-orange-300"
        >
          VIEW REPORT
          <ArrowUpRight size={13} />
        </button>
      </div>
    </div>

    {/* Analytics Snapshots */}

    <div className="group relative overflow-hidden rounded-2xl border border-emerald-500/20 bg-[#080807] p-6 transition-all duration-300 hover:border-emerald-500/50 hover:shadow-[0_0_30px_rgba(16,185,129,0.08)]">
      <div className="pointer-events-none absolute right-0 top-0 h-16 w-16 border-r border-t border-emerald-500/20" />

      <div className="flex items-start justify-between">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-emerald-500/30 bg-emerald-500/[0.08] text-emerald-400 transition group-hover:bg-emerald-500/15">
          <BarChart3
            size={21}
            strokeWidth={1.5}
          />
        </div>

        <span className="font-mono text-[8px] tracking-[0.2em] text-zinc-700">
          REPORT_02
        </span>
      </div>

      <h2 className="mt-6 text-lg font-semibold tracking-wide text-white">
        Analytics snapshots
      </h2>

      <p className="mt-2 text-sm leading-6 text-zinc-500">
        Track trend lines, control health, and
        remediation execution across teams.
      </p>

      <div className="mt-6 flex items-center justify-between border-t border-emerald-500/10 pt-4">
        <span className="font-mono text-[9px] tracking-[0.18em] text-emerald-500">
          LIVE_ANALYTICS
        </span>

        <button
          type="button"
          className="flex items-center gap-2 font-mono text-[9px] tracking-widest text-emerald-400 transition hover:text-emerald-300"
        >
          VIEW ANALYTICS
          <ArrowUpRight size={13} />
        </button>
      </div>
    </div>
  </div>

  {/* =====================================================
      REPORT STATUS
  ====================================================== */}

  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
    <ReportMetric
      label="GENERATED REPORTS"
      value="128"
      status="+12%"
      color="orange"
    />

    <ReportMetric
      label="SCHEDULED"
      value="24"
      status="ACTIVE"
      color="green"
    />

    <ReportMetric
      label="COMPLIANCE SNAPSHOTS"
      value="86"
      status="+8%"
      color="orange"
    />

    <ReportMetric
      label="LAST GENERATED"
      value="2h"
      status="RECENT"
      color="green"
    />
  </div>

  {/* =====================================================
      REPORT GENERATOR
  ====================================================== */}

  <div className="relative overflow-hidden rounded-2xl border border-orange-500/15 bg-[#080807]">
    <div className="pointer-events-none absolute inset-0 opacity-20">
      <div className="cyber-report-grid absolute inset-0" />
    </div>

    <div className="relative p-6">
      <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-orange-500/30 bg-orange-500/[0.08] text-orange-400">
              <Download size={19} />
            </div>

            <div>
              <p className="font-mono text-[8px] tracking-[0.25em] text-orange-500">
                REPORT_GENERATOR
              </p>

              <h3 className="mt-1 text-lg font-semibold text-white">
                Generate a new report
              </h3>
            </div>
          </div>

          <p className="mt-3 max-w-2xl text-sm leading-6 text-zinc-500">
            Create executive summaries, compliance
            reports, risk snapshots, and security
            analytics for your organization.
          </p>
        </div>

        <button
          type="button"
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-orange-500/40 bg-orange-500 px-5 py-3 font-mono text-[10px] font-bold tracking-[0.15em] text-black transition hover:bg-orange-400 hover:shadow-[0_0_25px_rgba(249,115,22,0.2)]"
        >
          GENERATE REPORT
          <ArrowUpRight size={14} />
        </button>
      </div>
    </div>
  </div>

  {/* =====================================================
      REPORT TYPES
  ====================================================== */}

  <div>
    <div className="mb-4">
      <p className="font-mono text-[8px] tracking-[0.3em] text-orange-500">
        AVAILABLE_REPORTS
      </p>

      <h2 className="mt-2 text-xl font-semibold text-white">
        Security intelligence
      </h2>
    </div>

    <div className="grid gap-3 md:grid-cols-3">
      <ReportType
        title="Compliance Report"
        description="Framework posture, controls, evidence and compliance status."
        color="orange"
      />

      <ReportType
        title="Risk Report"
        description="Risk exposure, critical findings and remediation progress."
        color="green"
      />

      <ReportType
        title="Audit Report"
        description="Audit findings, observations, evidence and action items."
        color="orange"
      />
    </div>
  </div>

  {/* =====================================================
      LOCAL STYLES
  ====================================================== */}

  <style jsx>{`
    .cyber-report-grid {
      background-image:
        linear-gradient(
          rgba(249, 115, 22, 0.035) 1px,
          transparent 1px
        ),
        linear-gradient(
          90deg,
          rgba(249, 115, 22, 0.035) 1px,
          transparent 1px
        );
      background-size: 40px 40px;
    }
  `}</style>
</div>


);
}

/* =========================================================
REPORT METRIC
========================================================= */

function ReportMetric({
label,
value,
status,
color,
}: {
label: string;
value: string;
status: string;
color: "orange" | "green";
}) {
const isOrange = color === "orange";

return (
<div
className={`rounded-2xl border bg-[#080807] p-5 transition-all duration-300 ${
        isOrange
          ? "border-orange-500/15 hover:border-orange-500/40"
          : "border-emerald-500/15 hover:border-emerald-500/40"
      }`}
> <p className="font-mono text-[8px] tracking-[0.2em] text-zinc-600">
{label} </p>


  <div className="mt-3 flex items-end justify-between">
    <span className="text-3xl font-semibold tracking-tight text-white">
      {value}
    </span>

    <span
      className={`font-mono text-[8px] tracking-widest ${
        isOrange
          ? "text-orange-400"
          : "text-emerald-400"
      }`}
    >
      {status}
    </span>
  </div>

  <div className="mt-4 h-px bg-zinc-900">
    <div
      className={`h-px transition-all duration-700 ${
        isOrange
          ? "w-3/4 bg-orange-500"
          : "w-4/5 bg-emerald-500"
      }`}
    />
  </div>
</div>


);
}

/* =========================================================
REPORT TYPE
========================================================= */

function ReportType({
title,
description,
color,
}: {
title: string;
description: string;
color: "orange" | "green";
}) {
const isOrange = color === "orange";

return (
<div
className={`group rounded-2xl border bg-[#080807] p-5 transition-all duration-300 ${
        isOrange
          ? "border-orange-500/15 hover:border-orange-500/40"
          : "border-emerald-500/15 hover:border-emerald-500/40"
      }`}
>
<div
className={`mb-4 h-1 w-10 rounded-full ${
          isOrange
            ? "bg-orange-500"
            : "bg-emerald-500"
        }`}
/>


  <h3 className="text-sm font-semibold tracking-wide text-white">
    {title}
  </h3>

  <p className="mt-2 text-xs leading-5 text-zinc-600">
    {description}
  </p>

  <div
    className={`mt-5 font-mono text-[8px] tracking-widest transition ${
      isOrange
        ? "text-orange-500 group-hover:text-orange-400"
        : "text-emerald-500 group-hover:text-emerald-400"
    }`}
  >
    OPEN REPORT →
  </div>
</div>


);
}
