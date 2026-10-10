"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FileText,
  BarChart3,
  Download,
  ArrowUpRight,
  X,
  CheckCircle2,
  Calendar,
  Layers,
  ShieldCheck,
  TrendingUp,
  FileCheck,
} from "lucide-react";

export default function ReportsPage() {
  // Generator Modal State
  const [isGeneratorOpen, setIsGeneratorOpen] = useState(false);
  const [selectedReportType, setSelectedReportType] = useState("Executive Summary");
  const [selectedFramework, setSelectedFramework] = useState("ISO 27001");
  const [selectedFormat, setSelectedFormat] = useState("CSV");
  const [selectedPeriod, setSelectedPeriod] = useState("Last 30 Days");
  const [generateSuccess, setGenerateSuccess] = useState(false);

  // Executive Preview Modal State
  const [isExecutivePreviewOpen, setIsExecutivePreviewOpen] = useState(false);

  // Analytics Preview Modal State
  const [isAnalyticsPreviewOpen, setIsAnalyticsPreviewOpen] = useState(false);

  const handleDownloadReport = () => {
    const reportData = [
      "CyGRC Security & Compliance Report",
      `Report Type,${selectedReportType}`,
      `Framework Scope,${selectedFramework}`,
      `Period,${selectedPeriod}`,
      `Format,${selectedFormat}`,
      `Generated At,${new Date().toISOString()}`,
      "--------------------------------------------------",
      "Section,Metric,Value,Status",
      "Compliance Posture,Readiness Score,87%,Healthy",
      "Controls Health,Active Controls,1204,Operational",
      "Risk Exposure,Total Risks,142,Managed (-8% MoM)",
      "Evidence Health,Evidence Artifacts,4521,Verified",
      "Audits Pipeline,Scheduled Reviews,24,On Track",
      "Incident Response,Resolved Incidents,89,Satisfactory",
    ].join("\n");

    const blob = new Blob([reportData], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute(
      "download",
      `cygrc_${selectedReportType.toLowerCase().replace(/\s+/g, "_")}_${Date.now()}.csv`
    );
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    setGenerateSuccess(true);
    setTimeout(() => {
      setGenerateSuccess(false);
      setIsGeneratorOpen(false);
    }, 1500);
  };

  const openGeneratorForType = (title: string) => {
    setSelectedReportType(title);
    setIsGeneratorOpen(true);
  };

  return (
    <div className="space-y-6">
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
            Executive summaries, compliance snapshots, and scheduled reporting views.
          </p>
        </div>

        <button
          type="button"
          onClick={() => {
            setSelectedReportType("Executive Summary");
            setIsGeneratorOpen(true);
          }}
          className="inline-flex items-center gap-2 rounded-xl bg-orange-500 px-4 py-2.5 font-mono text-xs font-bold tracking-wider text-black transition hover:bg-orange-400 active:scale-[0.98] shadow-lg shadow-orange-500/10"
        >
          <Download size={15} />
          GENERATE REPORT
        </button>
      </div>

      {/* =====================================================
          REPORT OVERVIEW CARDS
      ====================================================== */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Executive Reporting */}
        <div className="group relative overflow-hidden rounded-2xl border border-orange-500/20 bg-[#080807] p-6 transition-all duration-300 hover:border-orange-500/50 hover:shadow-[0_0_30px_rgba(249,115,22,0.08)]">
          <div className="pointer-events-none absolute right-0 top-0 h-16 w-16 border-r border-t border-orange-500/20" />

          <div className="flex items-start justify-between">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-orange-500/30 bg-orange-500/[0.08] text-orange-400 transition group-hover:bg-orange-500/15">
              <FileText size={21} strokeWidth={1.5} />
            </div>

            <span className="font-mono text-[8px] tracking-[0.2em] text-zinc-700">
              REPORT_01
            </span>
          </div>

          <h2 className="mt-6 text-lg font-semibold tracking-wide text-white">
            Executive reporting
          </h2>

          <p className="mt-2 text-sm leading-6 text-zinc-500">
            Board-ready summaries tailored for security leaders and compliance stakeholders.
          </p>

          <div className="mt-6 flex items-center justify-between border-t border-orange-500/10 pt-4">
            <span className="font-mono text-[9px] tracking-[0.18em] text-emerald-500">
              BOARD_READY
            </span>

            <button
              type="button"
              onClick={() => setIsExecutivePreviewOpen(true)}
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
              <BarChart3 size={21} strokeWidth={1.5} />
            </div>

            <span className="font-mono text-[8px] tracking-[0.2em] text-zinc-700">
              REPORT_02
            </span>
          </div>

          <h2 className="mt-6 text-lg font-semibold tracking-wide text-white">
            Analytics snapshots
          </h2>

          <p className="mt-2 text-sm leading-6 text-zinc-500">
            Track trend lines, control health, and remediation execution across teams.
          </p>

          <div className="mt-6 flex items-center justify-between border-t border-emerald-500/10 pt-4">
            <span className="font-mono text-[9px] tracking-[0.18em] text-emerald-500">
              LIVE_ANALYTICS
            </span>

            <button
              type="button"
              onClick={() => setIsAnalyticsPreviewOpen(true)}
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
                Create executive summaries, compliance reports, risk snapshots, and security
                analytics for your organization.
              </p>
            </div>

            <button
              type="button"
              onClick={() => {
                setSelectedReportType("Compliance Report");
                setIsGeneratorOpen(true);
              }}
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
            onClick={() => openGeneratorForType("Compliance Report")}
          />

          <ReportType
            title="Risk Report"
            description="Risk exposure, critical findings and remediation progress."
            color="green"
            onClick={() => openGeneratorForType("Risk Report")}
          />

          <ReportType
            title="Audit Report"
            description="Audit findings, observations, evidence and action items."
            color="orange"
            onClick={() => openGeneratorForType("Audit Report")}
          />
        </div>
      </div>

      {/* ========================================================
          MODAL: GENERATE REPORT
      ======================================================== */}
      <AnimatePresence>
        {isGeneratorOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsGeneratorOpen(false)}
              className="fixed inset-0 bg-black/70 backdrop-blur-sm"
            />

            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="relative w-full max-w-lg overflow-hidden rounded-2xl border border-orange-500/20 bg-[#0c0d12] p-6 text-white shadow-2xl"
            >
              <div className="flex items-center justify-between border-b border-orange-500/10 pb-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-orange-500/30 bg-orange-500/10 text-orange-400">
                    <Download size={20} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Generate Security Report</h3>
                    <p className="text-xs text-zinc-400">Configure parameters and export dataset</p>
                  </div>
                </div>
                <button
                  onClick={() => setIsGeneratorOpen(false)}
                  className="rounded-lg p-1.5 text-zinc-400 hover:bg-zinc-800 hover:text-white"
                >
                  <X size={18} />
                </button>
              </div>

              {generateSuccess ? (
                <div className="py-8 text-center">
                  <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400">
                    <CheckCircle2 size={32} />
                  </div>
                  <h4 className="mt-4 text-base font-semibold text-white">Report Successfully Generated!</h4>
                  <p className="mt-1 text-xs text-zinc-400">File download has started in your browser.</p>
                </div>
              ) : (
                <div className="mt-4 space-y-4">
                  <div>
                    <label className="text-xs font-semibold text-zinc-300">Report Type</label>
                    <div className="mt-2 grid grid-cols-2 gap-2">
                      {[
                        "Executive Summary",
                        "Compliance Report",
                        "Risk Report",
                        "Audit Report",
                      ].map((t) => (
                        <button
                          key={t}
                          type="button"
                          onClick={() => setSelectedReportType(t)}
                          className={`rounded-xl border p-2.5 text-left text-xs font-medium transition ${
                            selectedReportType === t
                              ? "border-orange-500 bg-orange-500/10 text-orange-400 font-semibold"
                              : "border-zinc-800 bg-[#050505] text-zinc-400 hover:border-zinc-700 hover:text-zinc-200"
                          }`}
                        >
                          {t}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="text-xs font-semibold text-zinc-300">Framework Scope</label>
                      <select
                        value={selectedFramework}
                        onChange={(e) => setSelectedFramework(e.target.value)}
                        className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                      >
                        <option value="ISO 27001">ISO 27001</option>
                        <option value="SOC 2 Type II">SOC 2 Type II</option>
                        <option value="GDPR">GDPR</option>
                        <option value="PCI DSS">PCI DSS</option>
                        <option value="All Frameworks">All Frameworks</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-xs font-semibold text-zinc-300">Reporting Period</label>
                      <select
                        value={selectedPeriod}
                        onChange={(e) => setSelectedPeriod(e.target.value)}
                        className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                      >
                        <option value="Last 30 Days">Last 30 Days</option>
                        <option value="Q2 2026">Q2 2026</option>
                        <option value="Year-to-Date">Year-to-Date</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-zinc-300">Export Format</label>
                    <div className="mt-2 flex gap-2">
                      {["CSV", "JSON", "PDF"].map((fmt) => (
                        <button
                          key={fmt}
                          type="button"
                          onClick={() => setSelectedFormat(fmt)}
                          className={`flex-1 rounded-xl py-2 text-xs font-semibold transition ${
                            selectedFormat === fmt
                              ? "bg-orange-500 text-black shadow-md shadow-orange-500/20"
                              : "border border-zinc-800 bg-[#050505] text-zinc-400 hover:border-zinc-700"
                          }`}
                        >
                          {fmt}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center justify-end gap-2 border-t border-zinc-800 pt-4">
                    <button
                      type="button"
                      onClick={() => setIsGeneratorOpen(false)}
                      className="rounded-xl border border-zinc-800 px-4 py-2 text-xs font-semibold text-zinc-400 hover:bg-zinc-800"
                    >
                      Cancel
                    </button>
                    <button
                      type="button"
                      onClick={handleDownloadReport}
                      className="flex items-center gap-1.5 rounded-xl bg-orange-500 px-4 py-2 text-xs font-semibold text-black transition hover:bg-orange-400 shadow-md shadow-orange-500/20"
                    >
                      <Download size={14} />
                      Generate & Download
                    </button>
                  </div>
                </div>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ========================================================
          MODAL: EXECUTIVE REPORT PREVIEW
      ======================================================== */}
      <AnimatePresence>
        {isExecutivePreviewOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsExecutivePreviewOpen(false)}
              className="fixed inset-0 bg-black/70 backdrop-blur-sm"
            />

            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="relative w-full max-w-xl overflow-hidden rounded-2xl border border-orange-500/20 bg-[#0c0d12] p-6 text-white shadow-2xl"
            >
              <div className="flex items-center justify-between border-b border-orange-500/10 pb-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-orange-500/30 bg-orange-500/10 text-orange-400">
                    <FileCheck size={20} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Executive Posture Deck</h3>
                    <p className="text-xs text-zinc-400">Board-ready compliance overview • Cycle Q2 2026</p>
                  </div>
                </div>
                <button
                  onClick={() => setIsExecutivePreviewOpen(false)}
                  className="rounded-lg p-1.5 text-zinc-400 hover:bg-zinc-800 hover:text-white"
                >
                  <X size={18} />
                </button>
              </div>

              <div className="mt-4 space-y-4">
                <div className="grid grid-cols-3 gap-3">
                  <div className="rounded-xl border border-zinc-800 bg-black/40 p-3 text-center">
                    <p className="text-[10px] text-zinc-500 uppercase font-semibold">Overall Readiness</p>
                    <p className="mt-1 text-2xl font-bold text-emerald-400">87%</p>
                    <p className="text-[10px] text-emerald-500/80">Audit Ready</p>
                  </div>
                  <div className="rounded-xl border border-zinc-800 bg-black/40 p-3 text-center">
                    <p className="text-[10px] text-zinc-500 uppercase font-semibold">Active Controls</p>
                    <p className="mt-1 text-2xl font-bold text-white">1,204</p>
                    <p className="text-[10px] text-zinc-400">+4% this quarter</p>
                  </div>
                  <div className="rounded-xl border border-zinc-800 bg-black/40 p-3 text-center">
                    <p className="text-[10px] text-zinc-500 uppercase font-semibold">Critical Risks</p>
                    <p className="mt-1 text-2xl font-bold text-orange-400">2</p>
                    <p className="text-[10px] text-orange-400/80">In Mitigation</p>
                  </div>
                </div>

                <div className="rounded-xl border border-zinc-800/80 bg-[#070707] p-4 text-xs leading-relaxed text-zinc-300">
                  <h4 className="font-semibold text-white mb-1.5">Executive Commentary</h4>
                  <p>
                    During the recent evaluation period, organizational cybersecurity posture met
                    all Tier-1 benchmarks for SOC 2 Type II and ISO 27001 readiness. Automated control
                    telemetry across cloud connectors confirms zero critical infrastructure misconfigurations.
                    The next internal ISMS assessment is scheduled within 3 days.
                  </p>
                </div>

                <div className="flex items-center justify-between border-t border-zinc-800 pt-4">
                  <button
                    type="button"
                    onClick={handleDownloadReport}
                    className="flex items-center gap-1.5 rounded-xl border border-orange-500/30 bg-orange-500/10 px-3.5 py-2 text-xs font-semibold text-orange-400 hover:bg-orange-500/20 transition"
                  >
                    <Download size={14} />
                    Download Snapshot Deck
                  </button>

                  <button
                    type="button"
                    onClick={() => setIsExecutivePreviewOpen(false)}
                    className="rounded-xl border border-zinc-800 px-4 py-2 text-xs font-semibold text-zinc-400 hover:bg-zinc-800"
                  >
                    Close
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ========================================================
          MODAL: VIEW ANALYTICS
      ======================================================== */}
      <AnimatePresence>
        {isAnalyticsPreviewOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsAnalyticsPreviewOpen(false)}
              className="fixed inset-0 bg-black/70 backdrop-blur-sm"
            />

            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="relative w-full max-w-xl overflow-hidden rounded-2xl border border-emerald-500/20 bg-[#0c0d12] p-6 text-white shadow-2xl"
            >
              <div className="flex items-center justify-between border-b border-emerald-500/10 pb-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-400">
                    <BarChart3 size={20} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Live Analytics Snapshot</h3>
                    <p className="text-xs text-zinc-400">Control coverage & remediation velocity metrics</p>
                  </div>
                </div>
                <button
                  onClick={() => setIsAnalyticsPreviewOpen(false)}
                  className="rounded-lg p-1.5 text-zinc-400 hover:bg-zinc-800 hover:text-white"
                >
                  <X size={18} />
                </button>
              </div>

              <div className="mt-4 space-y-4">
                {/* Framework bars */}
                <div className="space-y-3 rounded-xl border border-zinc-800 bg-black/40 p-4">
                  <h4 className="text-xs font-semibold text-zinc-300">Framework Coverage Distribution</h4>
                  {[
                    { name: "SOC 2 Type II", pct: 84, color: "#22c55e" },
                    { name: "ISO 27001:2022", pct: 81, color: "#f97316" },
                    { name: "GDPR Compliance", pct: 79, color: "#fb923c" },
                    { name: "PCI DSS v4.0", pct: 67, color: "#16a34a" },
                  ].map((fw) => (
                    <div key={fw.name} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-zinc-400">{fw.name}</span>
                        <span className="font-semibold text-white">{fw.pct}%</span>
                      </div>
                      <div className="h-2 w-full overflow-hidden rounded-full bg-zinc-800">
                        <div
                          className="h-full rounded-full transition-all duration-700"
                          style={{ width: `${fw.pct}%`, backgroundColor: fw.color }}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="rounded-xl border border-zinc-800 bg-[#070707] p-3">
                    <p className="text-zinc-500">Evidence Sync Velocity</p>
                    <p className="mt-1 text-lg font-bold text-white">4,521 items</p>
                    <p className="text-[11px] text-emerald-400 mt-0.5">+12% automated sync</p>
                  </div>
                  <div className="rounded-xl border border-zinc-800 bg-[#070707] p-3">
                    <p className="text-zinc-500">Incident MTTR (Mean Time to Resolve)</p>
                    <p className="mt-1 text-lg font-bold text-white">2.4 hours</p>
                    <p className="text-[11px] text-emerald-400 mt-0.5">-28% vs last month</p>
                  </div>
                </div>

                <div className="flex items-center justify-end border-t border-zinc-800 pt-4">
                  <button
                    type="button"
                    onClick={() => setIsAnalyticsPreviewOpen(false)}
                    className="rounded-xl border border-zinc-800 px-4 py-2 text-xs font-semibold text-zinc-400 hover:bg-zinc-800"
                  >
                    Close
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

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
    >
      <p className="font-mono text-[8px] tracking-[0.2em] text-zinc-600">
        {label}
      </p>

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
  onClick,
}: {
  title: string;
  description: string;
  color: "orange" | "green";
  onClick?: () => void;
}) {
  const isOrange = color === "orange";

  return (
    <div
      onClick={onClick}
      className={`group cursor-pointer rounded-2xl border bg-[#080807] p-5 transition-all duration-300 ${
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
