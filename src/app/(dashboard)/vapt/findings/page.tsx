"use client";

import { useEffect, useState } from "react";
import {
  ShieldAlert,
  AlertTriangle,
  Flame,
  CheckCircle2,
  RefreshCw,
  Search,
  Calculator,
  ExternalLink,
  ChevronRight,
  Filter,
  Server,
  Activity,
  Layers,
  Send,
  Check,
  XCircle,
  Clock,
  Radio,
  FileText,
} from "lucide-react";

interface VulnerabilityFinding {
  finding_id: string;
  tenant_id: string;
  asset_id: string;
  scan_job_id?: string;
  cve_id?: string;
  title: string;
  severity: string;
  cvss_score?: number;
  cisa_kev: boolean;
  priority_score: number;
  priority_level: string;
  scanner_source: string;
  evidence?: string;
  remediation?: string;
  status: string;
  remediation_notes?: string;
  jira_ticket_key?: string;
  jira_ticket_url?: string;
  first_observed_at: string;
  last_observed_at: string;
  created_at: string;
}

interface CVEFeedItem {
  cve_id: string;
  cvss_score?: number;
  cvss_vector?: string;
  cisa_kev: boolean;
  summary?: string;
  remediation?: string;
  affected_product?: string;
  published_date: string;
}

interface ScannerHealth {
  nmap: { tool: string; is_installed: boolean; status: string; path?: string };
  owasp_zap: { tool: string; connected: boolean; status: string; endpoint?: string };
  openvas: { tool: string; connected: boolean; status: string; host?: string };
}

export default function VAPTFindingsPage() {
  const [activeTab, setActiveTab] = useState<"findings" | "feeds">("findings");

  // Findings state
  const [findings, setFindings] = useState<VulnerabilityFinding[]>([]);
  const [loadingFindings, setLoadingFindings] = useState(true);
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [pushingJira, setPushingJira] = useState<string | null>(null);

  // Feeds state
  const [cves, setCves] = useState<CVEFeedItem[]>([]);
  const [loadingFeeds, setLoadingFeeds] = useState(false);
  const [kevOnly, setKevOnly] = useState(false);
  const [feedStatus, setFeedStatus] = useState<any>(null);

  // Scanner health state
  const [scannerHealth, setScannerHealth] = useState<ScannerHealth | null>(null);

  // Priority Calculator state
  const [calcCvss, setCalcCvss] = useState(8.5);
  const [calcKev, setCalcKev] = useState(true);
  const [calcCrit, setCalcCrit] = useState("HIGH");
  const [calcControl, setCalcControl] = useState(false);
  const [calcResult, setCalcResult] = useState<any>(null);

  const fetchFindings = async () => {
    setLoadingFindings(true);
    try {
      const res = await fetch("/api/v1/vapt/findings");
      if (res.ok) {
        const data = await res.json();
        setFindings(data);
      }
    } catch (err) {
      console.error("Failed to load vulnerability findings", err);
    } finally {
      setLoadingFindings(false);
    }
  };

  const fetchScannerHealth = async () => {
    try {
      const res = await fetch("/api/v1/vapt/findings/scanners/health");
      if (res.ok) {
        const data = await res.json();
        setScannerHealth(data.scanners);
      }
    } catch (err) {
      console.error("Failed to load scanner health", err);
    }
  };

  const fetchCVEs = async () => {
    setLoadingFeeds(true);
    try {
      let url = "/api/v1/vapt/cve";
      if (kevOnly) url += "?cisa_kev=true";
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setCves(data);
      }

      const statusRes = await fetch("/api/v1/vapt/cve/feed-status");
      if (statusRes.ok) {
        const sData = await statusRes.json();
        setFeedStatus(sData);
      }
    } catch (err) {
      console.error("Failed to fetch CVE feeds", err);
    } finally {
      setLoadingFeeds(false);
    }
  };

  useEffect(() => {
    fetchFindings();
    fetchScannerHealth();
    fetchCVEs();
  }, [kevOnly]);

  const handlePushJira = async (findingId: string) => {
    setPushingJira(findingId);
    try {
      const res = await fetch(`/api/v1/vapt/findings/${findingId}/push-jira`, {
        method: "POST",
      });
      if (res.ok) {
        const data = await res.json();
        setFindings((prev) =>
          prev.map((f) =>
            f.finding_id === findingId
              ? {
                  ...f,
                  jira_ticket_key: data.jira_ticket?.ticket_key,
                  jira_ticket_url: data.jira_ticket?.self_url,
                  status: f.status === "OPEN" ? "REMEDIATING" : f.status,
                }
              : f
          )
        );
      }
    } catch (err) {
      console.error("Failed to push Jira ticket", err);
    } finally {
      setPushingJira(null);
    }
  };

  const [feedingGRC, setFeedingGRC] = useState<string | null>(null);
  const [grcSuccessMsg, setGrcSuccessMsg] = useState<string | null>(null);

  const handleFeedToGRC = async (finding: VulnerabilityFinding) => {
    setFeedingGRC(finding.finding_id);
    try {
      const res = await fetch("/api/v1/vapt/cve/evidence/feed-to-grc", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Tenant-ID": "00000000-0000-0000-0000-00000000000a",
        },
        body: JSON.stringify({
          cve_id: finding.cve_id || finding.finding_id,
          cvss_score: finding.cvss_score || 7.5,
          affected_product: finding.asset_id,
          control_code: "A.12.6.1",
        }),
      });
      if (res.ok) {
        setGrcSuccessMsg(`Finding ${finding.finding_id} converted to Control A.12.6.1 evidence & synced to Risk Register!`);
        setTimeout(() => setGrcSuccessMsg(null), 4000);
      }
    } catch (err) {
      console.error("Failed to feed to GRC", err);
    } finally {
      setFeedingGRC(null);
    }
  };

  const handleCalculatePriority = async () => {
    try {
      const res = await fetch("/api/v1/vapt/cve/prioritize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cvss_score: calcCvss,
          is_cisa_kev: calcKev,
          asset_criticality: calcCrit,
          has_mitigating_control: calcControl,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setCalcResult(data);
      }
    } catch (err) {
      console.error("Error calculating priority", err);
    }
  };

  const filteredFindings = findings.filter((f) => {
    if (severityFilter !== "ALL" && f.severity !== severityFilter) return false;
    if (statusFilter !== "ALL" && f.status !== statusFilter) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        f.title.toLowerCase().includes(q) ||
        f.finding_id.toLowerCase().includes(q) ||
        (f.cve_id && f.cve_id.toLowerCase().includes(q)) ||
        f.asset_id.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const urgentCount = findings.filter((f) => f.priority_level === "P1_URGENT").length;
  const highCount = findings.filter((f) => f.priority_level === "P2_HIGH").length;
  const remediatingCount = findings.filter((f) => f.status === "REMEDIATING" || f.jira_ticket_key).length;

  return (
    <div className="space-y-6 pb-12">
      {/* Header Banner */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between rounded-2xl border border-slate-800 bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/40 p-6 shadow-xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-orange-500/10 text-orange-400 ring-1 ring-orange-500/20">
              <ShieldAlert className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">VAPT Vulnerability Management</h1>
              <p className="text-xs text-slate-400">
                Asset Findings Lifecycle, Scanner Adapters, NVD/KEV Feeds & Risk Prioritization Engine
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              fetchFindings();
              fetchScannerHealth();
              fetchCVEs();
            }}
            className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900/80 px-4 py-2.5 text-xs font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition"
          >
            <RefreshCw className={`h-4 w-4 ${loadingFindings ? "animate-spin text-indigo-400" : ""}`} />
            Sync & Refresh
          </button>
        </div>
      </div>

      {/* Scanner Connectivity Status Bar */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 backdrop-blur-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-400">
            <Radio className="h-4 w-4 text-emerald-400 animate-pulse" />
            Scanner Engine Connectivity
          </div>
          <div className="flex flex-wrap items-center gap-3 text-xs">
            {/* Nmap */}
            <div className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-950 px-3 py-1.5">
              <span className="font-mono font-semibold text-slate-300">Nmap:</span>
              <span
                className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold ${
                  scannerHealth?.nmap.status === "READY"
                    ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                    : "bg-amber-500/15 text-amber-300 border border-amber-500/30"
                }`}
              >
                {scannerHealth?.nmap.status === "READY" ? "READY (Binary)" : "FIXTURE MODE"}
              </span>
            </div>

            {/* OWASP ZAP */}
            <div className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-950 px-3 py-1.5">
              <span className="font-mono font-semibold text-slate-300">OWASP ZAP:</span>
              <span
                className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold ${
                  scannerHealth?.owasp_zap.connected
                    ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                    : "bg-indigo-500/15 text-indigo-300 border border-indigo-500/30"
                }`}
              >
                {scannerHealth?.owasp_zap.connected ? "ONLINE" : "FIXTURE READY"}
              </span>
            </div>

            {/* OpenVAS */}
            <div className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-950 px-3 py-1.5">
              <span className="font-mono font-semibold text-slate-300">OpenVAS:</span>
              <span
                className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold ${
                  scannerHealth?.openvas.connected
                    ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                    : "bg-indigo-500/15 text-indigo-300 border border-indigo-500/30"
                }`}
              >
                {scannerHealth?.openvas.connected ? "ONLINE" : "FIXTURE READY"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* KPI Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
          <span className="text-xs font-medium text-slate-400">Total Asset Findings</span>
          <p className="mt-3 text-3xl font-extrabold text-white">{findings.length}</p>
          <p className="mt-1 text-[11px] text-slate-500">Persisted tenant vulnerabilities</p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-rose-400">P1 Urgent Risk (Score ≥14)</span>
            <Flame className="h-4 w-4 text-rose-500" />
          </div>
          <p className="mt-3 text-3xl font-extrabold text-rose-400">{urgentCount}</p>
          <p className="mt-1 text-[11px] text-rose-500/80 font-medium">Requires immediate escalation</p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
          <span className="text-xs font-medium text-orange-400">P2 High Priority (10 - 13.9)</span>
          <p className="mt-3 text-3xl font-extrabold text-orange-400">{highCount}</p>
          <p className="mt-1 text-[11px] text-slate-500">7-day remediation SLA</p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-indigo-400">Jira Ticket Synced</span>
            <Send className="h-4 w-4 text-indigo-400" />
          </div>
          <p className="mt-3 text-3xl font-extrabold text-indigo-400">{remediatingCount}</p>
          <p className="mt-1 text-[11px] text-indigo-300/80 font-medium">Active remediation track</p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800">
        <button
          onClick={() => setActiveTab("findings")}
          className={`flex items-center gap-2 px-5 py-3 text-xs font-bold transition border-b-2 ${
            activeTab === "findings"
              ? "border-indigo-500 text-white bg-indigo-500/10"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Layers className="h-4 w-4" />
          Asset Findings ({findings.length})
        </button>
        <button
          onClick={() => setActiveTab("feeds")}
          className={`flex items-center gap-2 px-5 py-3 text-xs font-bold transition border-b-2 ${
            activeTab === "feeds"
              ? "border-indigo-500 text-white bg-indigo-500/10"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Flame className="h-4 w-4" />
          NVD & CISA KEV Threat Feeds ({cves.length})
        </button>
      </div>

      {activeTab === "findings" ? (
        <div className="space-y-4">
          {/* Findings Filter Bar */}
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between rounded-2xl border border-slate-800 bg-slate-900/40 p-4">
            <div className="flex flex-1 items-center gap-3">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                <input
                  type="text"
                  placeholder="Search finding ID, title, CVE, or affected asset..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 py-2.5 pl-10 pr-4 text-xs text-white placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-300 focus:outline-none"
              >
                <option value="ALL">All Severities</option>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>

              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-300 focus:outline-none"
              >
                <option value="ALL">All Statuses</option>
                <option value="OPEN">Open</option>
                <option value="REMEDIATING">Remediating</option>
                <option value="REMEDIATED">Remediated</option>
              </select>
            </div>
          </div>

          {/* Findings Table */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden shadow-xl">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-800 bg-slate-950/80 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                <tr>
                  <th className="px-6 py-4">Finding ID / Asset</th>
                  <th className="px-6 py-4">Vulnerability Title</th>
                  <th className="px-6 py-4">Priority Score</th>
                  <th className="px-6 py-4">Severity</th>
                  <th className="px-6 py-4">Scanner Source</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Jira Ticket</th>
                  <th className="px-6 py-4">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {loadingFindings ? (
                  <tr>
                    <td colSpan={8} className="py-12 text-center text-slate-500">
                      <RefreshCw className="mx-auto h-6 w-6 animate-spin text-indigo-500 mb-2" />
                      Loading vulnerability findings...
                    </td>
                  </tr>
                ) : filteredFindings.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-12 text-center text-slate-500">
                      <CheckCircle2 className="mx-auto h-8 w-8 text-emerald-500 mb-2" />
                      No active vulnerability findings found for this filter criteria.
                    </td>
                  </tr>
                ) : (
                  filteredFindings.map((finding) => (
                    <tr key={finding.finding_id} className="hover:bg-slate-800/40 transition">
                      <td className="px-6 py-4">
                        <div className="font-mono font-bold text-indigo-400">{finding.finding_id}</div>
                        <div className="flex items-center gap-1 text-[10px] text-slate-500 mt-0.5">
                          <Server className="h-3 w-3" />
                          {finding.asset_id}
                        </div>
                      </td>

                      <td className="px-6 py-4">
                        <div className="font-medium text-slate-200">{finding.title}</div>
                        {finding.cve_id && (
                          <div className="flex items-center gap-2 mt-1">
                            <span className="font-mono text-[10px] text-indigo-300 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                              {finding.cve_id}
                            </span>
                            {finding.cisa_kev && (
                              <span className="inline-flex items-center gap-1 rounded bg-rose-500/20 text-rose-300 px-1.5 py-0.5 text-[9px] font-bold border border-rose-500/30">
                                <Flame className="h-2.5 w-2.5" />
                                KEV ACTIVE
                              </span>
                            )}
                          </div>
                        )}
                      </td>

                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <span
                            className={`inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-bold ${
                              finding.priority_level === "P1_URGENT"
                                ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                                : finding.priority_level === "P2_HIGH"
                                ? "bg-orange-500/20 text-orange-300 border border-orange-500/30"
                                : finding.priority_level === "P3_MEDIUM"
                                ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                                : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                            }`}
                          >
                            {finding.priority_score} ({finding.priority_level})
                          </span>
                        </div>
                      </td>

                      <td className="px-6 py-4">
                        <span
                          className={`font-semibold text-[11px] ${
                            finding.severity === "CRITICAL"
                              ? "text-rose-400"
                              : finding.severity === "HIGH"
                              ? "text-orange-400"
                              : "text-amber-400"
                          }`}
                        >
                          {finding.severity}
                        </span>
                      </td>

                      <td className="px-6 py-4">
                        <span className="font-mono text-[11px] text-slate-400">{finding.scanner_source}</span>
                      </td>

                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold ${
                            finding.status === "REMEDIATED"
                              ? "bg-emerald-500/20 text-emerald-300"
                              : finding.status === "REMEDIATING"
                              ? "bg-indigo-500/20 text-indigo-300"
                              : "bg-slate-800 text-slate-300"
                          }`}
                        >
                          {finding.status}
                        </span>
                      </td>

                      <td className="px-6 py-4">
                        {finding.jira_ticket_key ? (
                          <a
                            href={finding.jira_ticket_url || "#"}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 font-mono text-[11px] text-indigo-400 hover:text-indigo-300 underline"
                          >
                            {finding.jira_ticket_key}
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        ) : (
                          <span className="text-[11px] text-slate-500">Not Synced</span>
                        )}
                      </td>

                      <td className="px-6 py-4">
                        {!finding.jira_ticket_key ? (
                          <button
                            onClick={() => handlePushJira(finding.finding_id)}
                            disabled={pushingJira === finding.finding_id}
                            className="inline-flex items-center gap-1 rounded-lg border border-indigo-500/40 bg-indigo-500/10 px-2.5 py-1 text-[11px] font-semibold text-indigo-300 hover:bg-indigo-500/20 transition disabled:opacity-50"
                          >
                            {pushingJira === finding.finding_id ? (
                              <RefreshCw className="h-3 w-3 animate-spin" />
                            ) : (
                              <Send className="h-3 w-3" />
                            )}
                            Push Jira
                          </button>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-[10px] text-emerald-400 font-medium">
                            <Check className="h-3 w-3" />
                            Ticket Active
                          </span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Prioritization Formula Interactive Simulator */}
          <div className="rounded-2xl border border-indigo-900/50 bg-slate-900/80 p-5 shadow-xl">
            <div className="flex items-center gap-2 border-b border-slate-800 pb-3 mb-4">
              <Calculator className="h-5 w-5 text-indigo-400" />
              <h2 className="text-sm font-bold text-white">Vulnerability Prioritization Formula Simulator (v1.2)</h2>
              <span className="ml-auto font-mono text-[10px] text-indigo-300 bg-indigo-500/10 px-2.5 py-1 rounded-full border border-indigo-500/20">
                Priority = CVSS + KEV (+3.0) + Crit (+1.0 to +4.0) - Control (-2.0)
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="text-xs text-slate-400 block mb-1">CVSS Base Score ({calcCvss})</label>
                <input
                  type="range"
                  min="0"
                  max="10"
                  step="0.1"
                  value={calcCvss}
                  onChange={(e) => setCalcCvss(parseFloat(e.target.value))}
                  className="w-full accent-indigo-500"
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 block mb-1">CISA KEV Active Exploit?</label>
                <label className="flex items-center gap-2 text-xs text-slate-200 mt-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={calcKev}
                    onChange={(e) => setCalcKev(e.target.checked)}
                    className="rounded accent-indigo-500"
                  />
                  Yes (+3.0 KEV Bonus)
                </label>
              </div>

              <div>
                <label className="text-xs text-slate-400 block mb-1">Target Asset Criticality</label>
                <select
                  value={calcCrit}
                  onChange={(e) => setCalcCrit(e.target.value)}
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs text-white focus:outline-none"
                >
                  <option value="CRITICAL">Critical (+4.0)</option>
                  <option value="HIGH">High (+3.0)</option>
                  <option value="MEDIUM">Medium (+2.0)</option>
                  <option value="LOW">Low (+1.0)</option>
                </select>
              </div>

              <div>
                <label className="text-xs text-slate-400 block mb-1">Mitigating Control Active?</label>
                <label className="flex items-center gap-2 text-xs text-slate-200 mt-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={calcControl}
                    onChange={(e) => setCalcControl(e.target.checked)}
                    className="rounded accent-indigo-500"
                  />
                  Yes (-2.0 Credit)
                </label>
              </div>
            </div>

            <div className="mt-4 flex items-center justify-between border-t border-slate-800 pt-3">
              <button
                onClick={handleCalculatePriority}
                className="rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500 transition"
              >
                Calculate Risk Priority
              </button>

              {calcResult && (
                <div className="flex items-center gap-3 font-mono text-xs">
                  <span className="text-slate-400">{calcResult.formula_string}</span>
                  <span className="rounded-lg bg-rose-500/20 text-rose-300 px-3 py-1 font-bold border border-rose-500/30">
                    {calcResult.priority_level} ({calcResult.priority_score})
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Threat Feeds Table */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-800 p-4 bg-slate-950/80">
              <div className="flex items-center gap-3">
                <span className="text-xs font-bold text-white uppercase tracking-wider">
                  NVD & CISA KEV Intelligence Feeds
                </span>
                <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={kevOnly}
                    onChange={(e) => setKevOnly(e.target.checked)}
                    className="rounded accent-indigo-500"
                  />
                  CISA KEV Only
                </label>
              </div>

              {feedStatus && (
                <span className="text-[11px] text-slate-400">
                  Last Sync: {feedStatus.last_sync_timestamp ? new Date(feedStatus.last_sync_timestamp).toLocaleTimeString() : "Ready"}
                </span>
              )}
            </div>

            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-800 bg-slate-950 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                <tr>
                  <th className="px-6 py-4">CVE ID</th>
                  <th className="px-6 py-4">CVSS Score</th>
                  <th className="px-6 py-4">CISA KEV</th>
                  <th className="px-6 py-4">Affected Product</th>
                  <th className="px-6 py-4">Summary</th>
                  <th className="px-6 py-4">Remediation Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {loadingFeeds ? (
                  <tr>
                    <td colSpan={6} className="py-12 text-center text-slate-500">
                      <RefreshCw className="mx-auto h-6 w-6 animate-spin text-indigo-500 mb-2" />
                      Loading live CVE vulnerability feeds...
                    </td>
                  </tr>
                ) : cves.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-12 text-center text-slate-500">
                      No CVE records found.
                    </td>
                  </tr>
                ) : (
                  cves.map((cve) => (
                    <tr key={cve.cve_id} className="hover:bg-slate-800/40 transition">
                      <td className="px-6 py-4 font-mono font-bold text-indigo-400">{cve.cve_id}</td>
                      <td className="px-6 py-4">
                        {cve.cvss_score !== null && cve.cvss_score !== undefined ? (
                          <span
                            className={`inline-flex items-center rounded-full px-2.5 py-1 text-[11px] font-bold ${
                              cve.cvss_score >= 9.0
                                ? "bg-rose-500/15 text-rose-400"
                                : cve.cvss_score >= 7.0
                                ? "bg-orange-500/15 text-orange-400"
                                : "bg-amber-500/15 text-amber-400"
                            }`}
                          >
                            {cve.cvss_score}
                          </span>
                        ) : (
                          <span className="text-[10px] text-slate-500 italic">Pending Scoring</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {cve.cisa_kev ? (
                          <span className="inline-flex items-center gap-1 rounded-full bg-rose-500/20 text-rose-400 px-2.5 py-0.5 text-[10px] font-bold border border-rose-500/30">
                            <Flame className="h-3 w-3" />
                            ACTIVE EXPLOIT
                          </span>
                        ) : (
                          <span className="text-[10px] text-slate-500">Standard</span>
                        )}
                      </td>
                      <td className="px-6 py-4 font-medium text-slate-200">{cve.affected_product || "N/A"}</td>
                      <td className="px-6 py-4 text-[11px] text-slate-400 max-w-xs truncate">{cve.summary}</td>
                      <td className="px-6 py-4 text-[11px] text-emerald-400">{cve.remediation}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
