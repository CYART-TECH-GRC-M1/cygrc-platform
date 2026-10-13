"use client";

import { useEffect, useState } from "react";
import {
  Briefcase,
  ShieldCheck,
  AlertOctagon,
  Clock,
  Plus,
  RefreshCw,
  Search,
  User,
  ChevronRight,
  ArrowRight,
  CheckCircle2,
  SlidersHorizontal,
} from "lucide-react";

interface IncidentCase {
  case_id: string;
  case_number: string;
  title: string;
  nist_phase: "PREPARATION" | "DETECTION_ANALYSIS" | "CONTAINMENT_ERADICATION_RECOVERY" | "POST_INCIDENT_ACTIVITY";
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  status: "OPEN" | "IN_PROGRESS" | "RESOLVED" | "CLOSED";
  summary?: string;
  assigned_analyst?: string;
  alerts_linked?: string[];
  created_at: string;
  updated_at: string;
}

export default function SOCCasesPage() {
  const [cases, setCases] = useState<IncidentCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [phaseFilter, setPhaseFilter] = useState<string>("ALL");
  const [severityFilter, setSeverityFilter] = useState<string>("ALL");
  const [selectedCase, setSelectedCase] = useState<IncidentCase | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  // Form State
  const [newTitle, setNewTitle] = useState("");
  const [newPhase, setNewPhase] = useState("DETECTION_ANALYSIS");
  const [newSeverity, setNewSeverity] = useState("HIGH");
  const [newAnalyst, setNewAnalyst] = useState("SOC Lead Analyst");
  const [newSummary, setNewSummary] = useState("");

  const fetchCases = async () => {
    setLoading(true);
    try {
      let url = "/api/v1/cases";
      const params = new URLSearchParams();
      if (phaseFilter !== "ALL") params.append("nist_phase", phaseFilter);
      if (severityFilter !== "ALL") params.append("severity", severityFilter);
      if (params.toString()) url += `?${params.toString()}`;

      const res = await fetch(url, {
        headers: { "X-Tenant-ID": "00000000-0000-0000-0000-00000000000a" },
      });
      if (res.ok) {
        const data = await res.json();
        setCases(data);
      }
    } catch (err) {
      console.error("Failed to fetch incident cases", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, [phaseFilter, severityFilter]);

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch("/api/v1/cases", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Tenant-ID": "00000000-0000-0000-0000-00000000000a",
        },
        body: JSON.stringify({
          title: newTitle || "Investigating Potential Ransomware Activity",
          nist_phase: newPhase,
          severity: newSeverity,
          assigned_analyst: newAnalyst,
          summary: newSummary || "Active investigation triggered by high-severity SOC alert stream.",
        }),
      });

      if (res.ok) {
        setIsCreateOpen(false);
        setNewTitle("");
        setNewSummary("");
        fetchCases();
      }
    } catch (err) {
      console.error("Error creating incident case", err);
    }
  };

  const handleAdvancePhase = async (case_id: string, currentPhase: string) => {
    const nextPhaseMap: Record<string, string> = {
      PREPARATION: "DETECTION_ANALYSIS",
      DETECTION_ANALYSIS: "CONTAINMENT_ERADICATION_RECOVERY",
      CONTAINMENT_ERADICATION_RECOVERY: "POST_INCIDENT_ACTIVITY",
      POST_INCIDENT_ACTIVITY: "POST_INCIDENT_ACTIVITY",
    };
    const nextPhase = nextPhaseMap[currentPhase] || "CONTAINMENT_ERADICATION_RECOVERY";

    try {
      const res = await fetch(`/api/v1/cases/${case_id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Tenant-ID": "00000000-0000-0000-0000-00000000000a",
        },
        body: JSON.stringify({ nist_phase: nextPhase, status: "IN_PROGRESS" }),
      });
      if (res.ok) {
        fetchCases();
        if (selectedCase && selectedCase.case_id === case_id) {
          setSelectedCase((prev) => (prev ? { ...prev, nist_phase: nextPhase as any } : null));
        }
      }
    } catch (err) {
      console.error("Failed to advance NIST phase", err);
    }
  };

  // Metrics
  const totalCases = cases.length;
  const analysisCount = cases.filter((c) => c.nist_phase === "DETECTION_ANALYSIS").length;
  const containmentCount = cases.filter((c) => c.nist_phase === "CONTAINMENT_ERADICATION_RECOVERY").length;
  const postIncidentCount = cases.filter((c) => c.nist_phase === "POST_INCIDENT_ACTIVITY").length;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between rounded-2xl border border-slate-800 bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/40 p-6 shadow-xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-400 ring-1 ring-indigo-500/20">
              <Briefcase className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">NIST SP 800-61 Incident Case Management</h1>
              <p className="text-xs text-slate-400">
                Incident Response Workflow Engine & NIST SP 800-61 Lifecycle Tracking
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchCases}
            className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900/80 px-4 py-2.5 text-xs font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin text-indigo-400" : ""}`} />
            Refresh
          </button>

          <button
            onClick={() => setIsCreateOpen(true)}
            className="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white shadow-lg shadow-indigo-500/20 hover:bg-indigo-500 transition"
          >
            <Plus className="h-4 w-4" />
            Create Incident Case
          </button>
        </div>
      </div>

      {/* NIST SP 800-61 Lifecycle Metrics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
          <span className="text-xs font-medium text-slate-400">Total Active Cases</span>
          <p className="mt-3 text-3xl font-extrabold text-white">{totalCases}</p>
          <p className="mt-1 text-[11px] text-slate-500">Tracked under NIST IR framework</p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
          <span className="text-xs font-medium text-amber-400">1. Detection & Analysis</span>
          <p className="mt-3 text-3xl font-extrabold text-amber-400">{analysisCount}</p>
          <p className="mt-1 text-[11px] text-slate-500">Initial scope & vector triage</p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
          <span className="text-xs font-medium text-rose-400">2. Containment & Eradication</span>
          <p className="mt-3 text-3xl font-extrabold text-rose-400">{containmentCount}</p>
          <p className="mt-1 text-[11px] text-slate-500">Active containment & threat removal</p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
          <span className="text-xs font-medium text-emerald-400">3. Post-Incident Activity</span>
          <p className="mt-3 text-3xl font-extrabold text-emerald-400">{postIncidentCount}</p>
          <p className="mt-1 text-[11px] text-slate-500">Lessons learned & evidence archiving</p>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between rounded-2xl border border-slate-800 bg-slate-900/40 p-4">
        <div className="flex items-center gap-3">
          <select
            value={phaseFilter}
            onChange={(e) => setPhaseFilter(e.target.value)}
            className="rounded-xl border border-slate-800 bg-slate-950 py-2.5 px-3 text-xs text-slate-300 focus:border-indigo-500 focus:outline-none"
          >
            <option value="ALL">All NIST Phases</option>
            <option value="PREPARATION">Preparation</option>
            <option value="DETECTION_ANALYSIS">Detection & Analysis</option>
            <option value="CONTAINMENT_ERADICATION_RECOVERY">Containment & Eradication</option>
            <option value="POST_INCIDENT_ACTIVITY">Post-Incident Activity</option>
          </select>

          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="rounded-xl border border-slate-800 bg-slate-950 py-2.5 px-3 text-xs text-slate-300 focus:border-indigo-500 focus:outline-none"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>
      </div>

      {/* Cases List */}
      <div className="grid grid-cols-1 gap-4">
        {loading ? (
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 py-12 text-center text-slate-500">
            <RefreshCw className="mx-auto h-6 w-6 animate-spin text-indigo-500 mb-2" />
            Loading NIST incident response cases...
          </div>
        ) : cases.length === 0 ? (
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 py-12 text-center text-slate-500">
            No incident cases found matching criteria. Click "Create Incident Case" to register a case.
          </div>
        ) : (
          cases.map((c) => (
            <div
              key={c.case_id}
              className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 hover:border-slate-700 transition"
            >
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs font-bold text-indigo-400">{c.case_number}</span>
                    <span
                      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[10px] font-bold ${
                        c.severity === "CRITICAL"
                          ? "bg-rose-500/15 text-rose-400"
                          : c.severity === "HIGH"
                          ? "bg-orange-500/15 text-orange-400"
                          : "bg-amber-500/15 text-amber-400"
                      }`}
                    >
                      {c.severity}
                    </span>
                    <span className="rounded-lg bg-slate-800 px-2 py-0.5 text-[10px] text-slate-300">
                      NIST: {c.nist_phase.replace(/_/g, " ")}
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-white mt-1">{c.title}</h3>
                  <p className="text-xs text-slate-400 max-w-3xl">{c.summary || "No summary recorded."}</p>
                </div>

                <div className="flex items-center gap-3">
                  <div className="text-right text-xs mr-4 hidden sm:block">
                    <span className="text-slate-500 block text-[10px]">Assigned Analyst</span>
                    <span className="font-medium text-slate-200">{c.assigned_analyst || "Unassigned"}</span>
                  </div>

                  <button
                    onClick={() => handleAdvancePhase(c.case_id, c.nist_phase)}
                    className="flex items-center gap-2 rounded-xl bg-indigo-600/80 px-3.5 py-2 text-xs font-semibold text-white hover:bg-indigo-600 transition"
                  >
                    Advance Phase
                    <ArrowRight className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create Case Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <form onSubmit={handleCreateCase} className="w-full max-w-lg rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white">Create NIST SP 800-61 Incident Case</h3>

            <div>
              <label className="text-xs font-medium text-slate-400">Incident Title</label>
              <input
                type="text"
                required
                placeholder="e.g., Critical Database Exfiltration & Malware Outbreak"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                className="mt-1 w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white focus:border-indigo-500 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-medium text-slate-400">NIST Phase</label>
                <select
                  value={newPhase}
                  onChange={(e) => setNewPhase(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white focus:border-indigo-500 focus:outline-none"
                >
                  <option value="PREPARATION">Preparation</option>
                  <option value="DETECTION_ANALYSIS">Detection & Analysis</option>
                  <option value="CONTAINMENT_ERADICATION_RECOVERY">Containment & Eradication</option>
                  <option value="POST_INCIDENT_ACTIVITY">Post-Incident Activity</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-medium text-slate-400">Severity</label>
                <select
                  value={newSeverity}
                  onChange={(e) => setNewSeverity(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white focus:border-indigo-500 focus:outline-none"
                >
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                  <option value="CRITICAL">Critical</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-xs font-medium text-slate-400">Assigned Analyst</label>
              <input
                type="text"
                value={newAnalyst}
                onChange={(e) => setNewAnalyst(e.target.value)}
                className="mt-1 w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white focus:border-indigo-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-slate-400">Executive Summary</label>
              <textarea
                rows={3}
                placeholder="Describe scope, affected assets, and initial containment actions..."
                value={newSummary}
                onChange={(e) => setNewSummary(e.target.value)}
                className="mt-1 w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white focus:border-indigo-500 focus:outline-none"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setIsCreateOpen(false)}
                className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-2 text-xs text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500"
              >
                Register Incident Case
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
