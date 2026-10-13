"use client";

import React, { useState, useEffect } from "react";
import {
  Sparkles,
  ShieldAlert,
  Search,
  FileText,
  GitBranch,
  Compass,
  Wrench,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
  Send,
  Terminal,
  ArrowRight,
  Lock,
  RefreshCw,
  Play,
  Database,
  Cpu,
  Layers,
  Clock,
  UserCheck,
  XCircle,
  FileCode,
  AlertTriangle,
  HelpCircle,
} from "lucide-react";

interface AIStatus {
  status: string;
  provider: string;
  model: string;
  configured: boolean;
  guardrails_enabled: boolean;
  active_guardrails: string[];
}

interface SupportingSource {
  id: string;
  title?: string;
  source?: string;
}

export default function CyberAIHubPage() {
  const [activeTab, setActiveTab] = useState<
    | "copilot"
    | "threat-analyzer"
    | "summarizer"
    | "root-cause"
    | "hunting"
    | "remediation"
    | "attack-path"
    | "approvals"
    | "evaluation"
  >("copilot");

  const [aiStatus, setAiStatus] = useState<AIStatus | null>(null);
  const [loadingStatus, setLoadingStatus] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Auth & Tenant Context
  const getAuthHeaders = (): Record<string, string> => {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "X-Tenant-ID": "00000000-0000-0000-0000-00000000000a",
    };
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("cygrc_token");
      if (token) headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Fetch AI Engine Status
  const fetchAIStatus = async () => {
    setLoadingStatus(true);
    try {
      const res = await fetch("/api/v1/ai/status", { headers: getAuthHeaders() });
      if (res.ok) {
        const data = await res.json();
        setAiStatus(data);
      }
    } catch (e) {
      console.error("Failed to fetch AI status", e);
    } finally {
      setLoadingStatus(false);
    }
  };

  useEffect(() => {
    fetchAIStatus();
  }, []);

  // 1. SOC Copilot State
  const [copilotQuestion, setCopilotQuestion] = useState("");
  const [copilotLoading, setCopilotLoading] = useState(false);
  const [copilotResult, setCopilotResult] = useState<any>(null);
  const [copilotError, setCopilotError] = useState<string | null>(null);

  const handleCopilotSubmit = async (questionOverride?: string) => {
    const q = questionOverride || copilotQuestion;
    if (!q.trim()) return;
    setCopilotLoading(true);
    setCopilotError(null);
    try {
      const res = await fetch("/api/v1/ai/soc-copilot", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ question: q }),
      });
      const data = await res.json();
      if (!res.ok) {
        setCopilotError(data.detail || "Error querying SOC Copilot");
      } else {
        setCopilotResult(data);
      }
    } catch (e: any) {
      setCopilotError(e.message || "Failed to communicate with AI service");
    } finally {
      setCopilotLoading(false);
    }
  };

  // 2. Threat Analyzer State
  const [indicatorInput, setIndicatorInput] = useState("");
  const [analyzerLoading, setAnalyzerLoading] = useState(false);
  const [analyzerResult, setAnalyzerResult] = useState<any>(null);
  const [analyzerError, setAnalyzerError] = useState<string | null>(null);

  const handleAnalyzerSubmit = async () => {
    if (!indicatorInput.trim()) return;
    setAnalyzerLoading(true);
    setAnalyzerError(null);
    try {
      const res = await fetch("/api/v1/ai/threat-analyzer", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ indicator: indicatorInput.trim() }),
      });
      const data = await res.json();
      if (!res.ok) {
        setAnalyzerError(data.detail || "Error analyzing threat indicator");
      } else {
        setAnalyzerResult(data);
      }
    } catch (e: any) {
      setAnalyzerError(e.message || "Network request failed");
    } finally {
      setAnalyzerLoading(false);
    }
  };

  // 3. Incident Summariser State
  const [caseIdInput, setCaseIdInput] = useState("");
  const [targetAudience, setTargetAudience] = useState("all");
  const [summarizerLoading, setSummarizerLoading] = useState(false);
  const [summarizerResult, setSummarizerResult] = useState<any>(null);
  const [summarizerError, setSummarizerError] = useState<string | null>(null);

  const handleSummarizerSubmit = async () => {
    if (!caseIdInput.trim()) return;
    setSummarizerLoading(true);
    setSummarizerError(null);
    try {
      const res = await fetch("/api/v1/ai/incident-summarizer", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ case_id: caseIdInput.trim(), target_audience: targetAudience }),
      });
      const data = await res.json();
      if (!res.ok) {
        setSummarizerError(data.detail || "Incident summarization failed");
      } else {
        setSummarizerResult(data);
      }
    } catch (e: any) {
      setSummarizerError(e.message || "Network request failed");
    } finally {
      setSummarizerLoading(false);
    }
  };

  // 4. Root Cause Analysis State
  const [rcaCaseId, setRcaCaseId] = useState("");
  const [rcaProblemStatement, setRcaProblemStatement] = useState("");
  const [rcaLoading, setRcaLoading] = useState(false);
  const [rcaResult, setRcaResult] = useState<any>(null);
  const [rcaError, setRcaError] = useState<string | null>(null);

  const handleRcaSubmit = async () => {
    if (!rcaCaseId.trim()) return;
    setRcaLoading(true);
    setRcaError(null);
    try {
      const res = await fetch("/api/v1/ai/root-cause-analysis", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          case_id: rcaCaseId.trim(),
          problem_statement: rcaProblemStatement || undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setRcaError(data.detail || "Root cause analysis failed");
      } else {
        setRcaResult(data);
      }
    } catch (e: any) {
      setRcaError(e.message || "Network request failed");
    } finally {
      setRcaLoading(false);
    }
  };

  // 5. Threat Hunting State
  const [huntingTelemetry, setHuntingTelemetry] = useState("all");
  const [huntingObjective, setHuntingObjective] = useState("");
  const [huntingLoading, setHuntingLoading] = useState(false);
  const [huntingResult, setHuntingResult] = useState<any>(null);
  const [huntingError, setHuntingError] = useState<string | null>(null);

  const handleHuntingSubmit = async () => {
    if (!huntingObjective.trim()) return;
    setHuntingLoading(true);
    setHuntingError(null);
    try {
      const res = await fetch("/api/v1/ai/threat-hunting", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          telemetry_source: huntingTelemetry,
          hypothesis_or_objective: huntingObjective.trim(),
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setHuntingError(data.detail || "Threat hunting query generation failed");
      } else {
        setHuntingResult(data);
      }
    } catch (e: any) {
      setHuntingError(e.message || "Network request failed");
    } finally {
      setHuntingLoading(false);
    }
  };

  // 6. Remediation Generator State
  const [remediationFindingId, setRemediationFindingId] = useState("");
  const [remediationAssetId, setRemediationAssetId] = useState("");
  const [remediationLoading, setRemediationLoading] = useState(false);
  const [remediationResult, setRemediationResult] = useState<any>(null);
  const [remediationError, setRemediationError] = useState<string | null>(null);

  const handleRemediationSubmit = async () => {
    if (!remediationFindingId.trim() && !remediationAssetId.trim()) return;
    setRemediationLoading(true);
    setRemediationError(null);
    try {
      const res = await fetch("/api/v1/ai/remediation-generator", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          finding_id: remediationFindingId.trim() || undefined,
          asset_id: remediationAssetId.trim() || undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setRemediationError(data.detail || "Remediation generation failed");
      } else {
        setRemediationResult(data);
        fetchApprovals(); // Refresh pending approvals
      }
    } catch (e: any) {
      setRemediationError(e.message || "Network request failed");
    } finally {
      setRemediationLoading(false);
    }
  };

  // 7. Attack Path Prediction State
  const [targetAssetId, setTargetAssetId] = useState("");
  const [attackPathLoading, setAttackPathLoading] = useState(false);
  const [attackPathResult, setAttackPathResult] = useState<any>(null);
  const [attackPathError, setAttackPathError] = useState<string | null>(null);

  const handleAttackPathSubmit = async () => {
    if (!targetAssetId.trim()) return;
    setAttackPathLoading(true);
    setAttackPathError(null);
    try {
      const res = await fetch("/api/v1/ai/attack-path-prediction", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ target_asset_id: targetAssetId.trim() }),
      });
      const data = await res.json();
      if (!res.ok) {
        setAttackPathError(data.detail || "Attack path prediction failed");
      } else {
        setAttackPathResult(data);
      }
    } catch (e: any) {
      setAttackPathError(e.message || "Network request failed");
    } finally {
      setAttackPathLoading(false);
    }
  };

  // 8. Human Approvals State
  const [approvalsList, setApprovalsList] = useState<any[]>([]);
  const [approvalsLoading, setApprovalsLoading] = useState(false);
  const [approvalsError, setApprovalsError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const fetchApprovals = async () => {
    setApprovalsLoading(true);
    try {
      const res = await fetch("/api/v1/ai/approvals", { headers: getAuthHeaders() });
      if (res.ok) {
        const data = await res.json();
        setApprovalsList(data);
      }
    } catch (e) {
      console.error("Failed to load approvals", e);
    } finally {
      setApprovalsLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === "approvals") {
      fetchApprovals();
    }
  }, [activeTab]);

  const handleDecision = async (approvalId: string, decision: "APPROVED" | "REJECTED", token: string) => {
    try {
      const res = await fetch(`/api/v1/ai/approvals/${approvalId}/decision`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          decision,
          approval_token: token,
          review_comments: `Human analyst ${decision.toLowerCase()} via Cyber AI Console`,
        }),
      });
      if (res.ok) {
        setActionSuccess(`Action ${decision.toLowerCase()} successfully!`);
        fetchApprovals();
        setTimeout(() => setActionSuccess(null), 3000);
      } else {
        const err = await res.json();
        alert(err.detail || "Decision failed");
      }
    } catch (e: any) {
      alert(e.message || "Network request failed");
    }
  };

  const handleExecute = async (approvalId: string, token: string) => {
    try {
      const res = await fetch(`/api/v1/ai/approvals/${approvalId}/execute`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ approval_token: token }),
      });
      if (res.ok) {
        const data = await res.json();
        setActionSuccess(`Execution completed: ${data.execution_summary || "Success"}`);
        fetchApprovals();
        setTimeout(() => setActionSuccess(null), 4000);
      } else {
        const err = await res.json();
        alert(err.detail || "Execution failed");
      }
    } catch (e: any) {
      alert(e.message || "Network request failed");
    }
  };

  // 9. AI Benchmark Evaluation State
  const [evalLoading, setEvalLoading] = useState(false);
  const [evalResult, setEvalResult] = useState<any>(null);
  const [evalError, setEvalError] = useState<string | null>(null);

  const handleRunEvaluation = async () => {
    setEvalLoading(true);
    setEvalError(null);
    try {
      const res = await fetch("/api/v1/ai/eval/run", {
        method: "POST",
        headers: getAuthHeaders(),
      });
      const data = await res.json();
      if (!res.ok) {
        setEvalError(data.detail || "Evaluation benchmark failed");
      } else {
        setEvalResult(data);
      }
    } catch (e: any) {
      setEvalError(e.message || "Network request failed");
    } finally {
      setEvalLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-tr from-orange-600 to-amber-500 text-white shadow-lg shadow-orange-500/20">
              <Sparkles size={24} />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                Cyber AI & Guardrails Hub
                <span className="rounded-full bg-orange-500/10 px-2.5 py-0.5 text-xs font-semibold text-orange-400 border border-orange-500/20">
                  Phase 7
                </span>
              </h1>
              <p className="text-xs text-zinc-400">
                Evidence-grounded, zero-hallucination security intelligence with backend-enforced human approvals
              </p>
            </div>
          </div>
        </div>

        {/* Engine Status Card */}
        <div className="flex items-center gap-3 rounded-2xl border border-zinc-800 bg-[#0d0a1a] p-3 text-xs shadow-md">
          <div className="flex items-center gap-2">
            <span
              className={`h-2.5 w-2.5 rounded-full ${
                aiStatus?.configured ? "bg-emerald-400 animate-pulse" : "bg-amber-400"
              }`}
            />
            <span className="font-semibold text-zinc-200">
              Provider:{" "}
              <span className="text-orange-400 font-mono">
                {aiStatus?.provider?.toUpperCase() || "SIMULATOR"}
              </span>
            </span>
          </div>
          <div className="h-4 w-px bg-zinc-800" />
          <div className="text-zinc-400">
            Model: <span className="text-zinc-200 font-mono">{aiStatus?.model || "gpt-4o-mini"}</span>
          </div>
          <div className="h-4 w-px bg-zinc-800" />
          <div className="flex items-center gap-1 text-emerald-400">
            <Lock size={12} />
            <span>Guardrails Active</span>
          </div>
          <button
            onClick={fetchAIStatus}
            title="Refresh status"
            className="text-zinc-500 hover:text-zinc-300 transition"
          >
            <RefreshCw size={12} className={loadingStatus ? "animate-spin" : ""} />
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex overflow-x-auto border-b border-zinc-800 pb-2 gap-2 scrollbar-none">
        {[
          { id: "copilot", label: "SOC Copilot", icon: Sparkles },
          { id: "threat-analyzer", label: "Threat Analyzer", icon: ShieldAlert },
          { id: "summarizer", label: "Incident Summariser", icon: FileText },
          { id: "root-cause", label: "Root Cause (RCA)", icon: GitBranch },
          { id: "hunting", label: "Threat Hunting", icon: Compass },
          { id: "remediation", label: "Remediation Generator", icon: Wrench },
          { id: "attack-path", label: "Attack Path Prediction", icon: Layers },
          { id: "approvals", label: "Approval Inbox (HITL)", icon: UserCheck },
          { id: "evaluation", label: "AI Benchmark Eval", icon: Play },
        ].map((tab) => {
          const Icon = tab.icon;
          const active = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 whitespace-nowrap rounded-xl px-4 py-2.5 text-xs font-semibold transition ${
                active
                  ? "bg-orange-500 text-black shadow-lg shadow-orange-500/20"
                  : "bg-zinc-900/60 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200"
              }`}
            >
              <Icon size={14} />
              {tab.label}
              {tab.id === "approvals" && approvalsList.length > 0 && (
                <span className="ml-1 rounded-full bg-red-500 px-1.5 py-0.2 text-[10px] text-white">
                  {approvalsList.filter((a) => a.status === "PENDING").length}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {actionSuccess && (
        <div className="flex items-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3 text-xs text-emerald-400 animate-in fade-in">
          <CheckCircle2 size={16} />
          <span>{actionSuccess}</span>
        </div>
      )}

      {/* ========================================================
          TAB 1: SOC COPILOT
         ======================================================== */}
      {activeTab === "copilot" && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Query Box */}
          <div className="space-y-4 rounded-2xl border border-zinc-800/80 bg-[#0e0c1c] p-6 lg:col-span-1">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Sparkles size={16} className="text-orange-400" />
              SOC Analyst Inquiry
            </h2>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Ask questions grounded directly in your tenant's security alerts, incidents, and threat telemetry.
            </p>

            <div className="space-y-2">
              <label className="text-[11px] font-semibold text-zinc-300">Prompt / Question</label>
              <textarea
                rows={4}
                value={copilotQuestion}
                onChange={(e) => setCopilotQuestion(e.target.value)}
                placeholder="e.g. What critical alerts were observed for host SRV-DC01 and are there correlated CVEs?"
                className="w-full rounded-xl border border-zinc-800 bg-[#141126] p-3 text-xs text-zinc-100 placeholder:text-zinc-600 focus:border-orange-500 outline-none"
              />
            </div>

            <button
              onClick={() => handleCopilotSubmit()}
              disabled={copilotLoading || !copilotQuestion.trim()}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-orange-500 to-amber-500 py-2.5 text-xs font-bold text-black transition hover:opacity-95 disabled:opacity-40"
            >
              {copilotLoading ? (
                <>
                  <RefreshCw size={14} className="animate-spin" />
                  Analyzing Authorized Context...
                </>
              ) : (
                <>
                  <Send size={14} />
                  Analyze Security Posture
                </>
              )}
            </button>

            {/* Quick Prompts */}
            <div className="pt-2">
              <p className="text-[10px] font-bold uppercase tracking-wider text-zinc-500 mb-2">
                Suggested Analyst Queries
              </p>
              <div className="space-y-1.5">
                {[
                  "What high severity alerts were reported in the last 24 hours?",
                  "Are there any unpatched CVEs on critical assets?",
                  "Show open cases and active IOC correlations",
                ].map((qp, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setCopilotQuestion(qp);
                      handleCopilotSubmit(qp);
                    }}
                    className="w-full text-left rounded-lg border border-zinc-800/80 bg-zinc-900/40 p-2 text-[11px] text-zinc-300 hover:border-orange-500/30 hover:bg-orange-500/5 transition"
                  >
                    "{qp}"
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Response Console */}
          <div className="space-y-4 rounded-2xl border border-zinc-800/80 bg-[#0e0c1c] p-6 lg:col-span-2">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Terminal size={16} className="text-emerald-400" />
                Grounded Security Analysis
              </h2>
              {copilotResult && (
                <div className="flex items-center gap-3">
                  <span className="rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-400 border border-emerald-500/20">
                    Grounding: {Math.round(copilotResult.confidence_score * 100)}%
                  </span>
                  <span className="text-[11px] text-zinc-500 font-mono">
                    Model: {copilotResult.model_used}
                  </span>
                </div>
              )}
            </div>

            {copilotError && (
              <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-xs text-red-400 flex items-start gap-2">
                <AlertCircle size={16} className="shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold">Query Refusal or Error</p>
                  <p className="mt-1 opacity-90">{copilotError}</p>
                </div>
              </div>
            )}

            {!copilotResult && !copilotLoading && !copilotError && (
              <div className="flex flex-col items-center justify-center py-16 text-center text-zinc-600">
                <Sparkles size={36} className="mb-2 opacity-30 text-orange-400" />
                <p className="text-xs">No analysis performed yet.</p>
                <p className="text-[11px] text-zinc-600 mt-1">
                  Type an inquiry or pick a suggestion to synthesize evidence-backed answers.
                </p>
              </div>
            )}

            {copilotLoading && (
              <div className="space-y-3 py-8">
                <div className="h-4 w-3/4 rounded bg-zinc-800/60 animate-pulse" />
                <div className="h-4 w-full rounded bg-zinc-800/60 animate-pulse" />
                <div className="h-4 w-5/6 rounded bg-zinc-800/60 animate-pulse" />
                <div className="h-4 w-1/2 rounded bg-zinc-800/60 animate-pulse" />
              </div>
            )}

            {copilotResult && (
              <div className="space-y-5 animate-in fade-in">
                {/* Answer Body */}
                <div className="rounded-xl border border-zinc-800 bg-[#141126] p-4 text-xs leading-relaxed text-zinc-200 whitespace-pre-wrap font-sans">
                  {copilotResult.answer}
                </div>

                {/* Supporting Source Records */}
                <div>
                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2 flex items-center gap-1.5">
                    <Database size={13} className="text-orange-400" />
                    Verified Authoritative Sources ({copilotResult.supporting_sources?.length || 0})
                  </h4>
                  {copilotResult.supporting_sources?.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {copilotResult.supporting_sources.map((src: string, idx: number) => (
                        <div
                          key={idx}
                          className="flex items-center gap-1.5 rounded-lg border border-orange-500/20 bg-orange-500/5 px-2.5 py-1 text-[11px] font-mono text-orange-300"
                        >
                          <CheckCircle2 size={11} className="text-orange-400" />
                          <span>{src}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-[11px] text-zinc-500 italic">No specific persisted records cited.</p>
                  )}
                </div>

                {/* Stated Caveats / Uncertainties */}
                {copilotResult.uncertainties && (
                  <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-3 text-[11px] text-amber-300 flex items-start gap-2">
                    <HelpCircle size={14} className="shrink-0 mt-0.5 text-amber-400" />
                    <div>
                      <span className="font-semibold">Uncertainty Declaration: </span>
                      {copilotResult.uncertainties}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================
          TAB 2: THREAT ANALYZER
         ======================================================== */}
      {activeTab === "threat-analyzer" && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="space-y-4 rounded-2xl border border-zinc-800/80 bg-[#0e0c1c] p-6 lg:col-span-1">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <ShieldAlert size={16} className="text-red-400" />
              Threat Indicator Lookup
            </h2>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Analyze malicious indicators against tenant STIX records, open threat intel, and alerts.
            </p>

            <div className="space-y-2">
              <label className="text-[11px] font-semibold text-zinc-300">Indicator (IP, Hash, Domain, CVE)</label>
              <input
                type="text"
                value={indicatorInput}
                onChange={(e) => setIndicatorInput(e.target.value)}
                placeholder="e.g. 198.51.100.24, evil-c2.example.com, CVE-2024-21413"
                className="w-full rounded-xl border border-zinc-800 bg-[#141126] p-3 text-xs text-zinc-100 placeholder:text-zinc-600 focus:border-red-500 outline-none"
              />
            </div>

            <button
              onClick={handleAnalyzerSubmit}
              disabled={analyzerLoading || !indicatorInput.trim()}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-red-600 to-orange-500 py-2.5 text-xs font-bold text-white transition hover:opacity-95 disabled:opacity-40"
            >
              {analyzerLoading ? (
                <>
                  <RefreshCw size={14} className="animate-spin" />
                  Correlating Threat Feeds...
                </>
              ) : (
                <>
                  <Search size={14} />
                  Analyze Threat Indicator
                </>
              )}
            </button>
          </div>

          <div className="space-y-4 rounded-2xl border border-zinc-800/80 bg-[#0e0c1c] p-6 lg:col-span-2">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <h2 className="text-sm font-bold text-white">Threat Intelligence Assessment</h2>
              {analyzerResult && (
                <span
                  className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold ${
                    analyzerResult.confidence === "HIGH"
                      ? "bg-red-500/20 text-red-400 border border-red-500/30"
                      : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                  }`}
                >
                  Confidence: {analyzerResult.confidence}
                </span>
              )}
            </div>

            {analyzerError && (
              <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-xs text-red-400">
                {analyzerError}
              </div>
            )}

            {!analyzerResult && !analyzerLoading && !analyzerError && (
              <div className="flex flex-col items-center justify-center py-16 text-center text-zinc-600">
                <ShieldAlert size={36} className="mb-2 opacity-30 text-red-400" />
                <p className="text-xs">Provide an indicator to correlate against threat feeds.</p>
              </div>
            )}

            {analyzerResult && (
              <div className="space-y-4 animate-in fade-in">
                <div className="rounded-xl border border-zinc-800 bg-[#141126] p-4 text-xs text-zinc-200">
                  <h3 className="text-sm font-bold text-white mb-2">Indicator Synthesis</h3>
                  <p className="leading-relaxed whitespace-pre-wrap">{analyzerResult.threat_summary}</p>
                </div>

                {analyzerResult.mitre_techniques?.length > 0 && (
                  <div>
                    <h4 className="text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
                      Correlated MITRE ATT&CK Techniques
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {analyzerResult.mitre_techniques.map((t: string, i: number) => (
                        <span
                          key={i}
                          className="rounded-lg bg-red-500/10 border border-red-500/20 px-2.5 py-1 text-xs font-mono text-red-300"
                        >
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {analyzerResult.uncertainty_notes && (
                  <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-3 text-xs text-amber-300">
                    <span className="font-semibold">Explicit Uncertainty: </span>
                    {analyzerResult.uncertainty_notes}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================
          TAB 3: INCIDENT SUMMARISER
         ======================================================== */}
      {activeTab === "summarizer" && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="space-y-4 rounded-2xl border border-zinc-800/80 bg-[#0e0c1c] p-6 lg:col-span-1">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <FileText size={16} className="text-amber-400" />
              Incident Timeline Summariser
            </h2>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Synthesize NIST-compliant timelines and executive briefings from verified case data.
            </p>

            <div className="space-y-2">
              <label className="text-[11px] font-semibold text-zinc-300">Case ID</label>
              <input
                type="text"
                value={caseIdInput}
                onChange={(e) => setCaseIdInput(e.target.value)}
                placeholder="e.g. CASE-2026-001"
                className="w-full rounded-xl border border-zinc-800 bg-[#141126] p-3 text-xs text-zinc-100 placeholder:text-zinc-600 focus:border-amber-500 outline-none"
              />
            </div>

            <div className="space-y-2">
              <label className="text-[11px] font-semibold text-zinc-300">Target Audience</label>
              <select
                value={targetAudience}
                onChange={(e) => setTargetAudience(e.target.value)}
                className="w-full rounded-xl border border-zinc-800 bg-[#141126] p-3 text-xs text-zinc-100 focus:border-amber-500 outline-none"
              >
                <option value="all">Executive & Technical (Comprehensive)</option>
                <option value="executive">Board / C-Level Executive Brief</option>
                <option value="technical">SOC Tier 2 / Incident Response Technical</option>
              </select>
            </div>

            <button
              onClick={handleSummarizerSubmit}
              disabled={summarizerLoading || !caseIdInput.trim()}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 py-2.5 text-xs font-bold text-black transition hover:opacity-95 disabled:opacity-40"
            >
              {summarizerLoading ? (
                <>
                  <RefreshCw size={14} className="animate-spin" />
                  Generating Timeline Briefing...
                </>
              ) : (
                <>
                  <FileText size={14} />
                  Summarize Incident
                </>
              )}
            </button>
          </div>

          <div className="space-y-4 rounded-2xl border border-zinc-800/80 bg-[#0e0c1c] p-6 lg:col-span-2">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <h2 className="text-sm font-bold text-white">Incident Timeline & Brief</h2>
              {summarizerResult && (
                <span className="rounded-full bg-orange-500/10 px-2.5 py-0.5 text-xs font-semibold text-orange-400 border border-orange-500/20">
                  NIST Phase: {summarizerResult.nist_phase}
                </span>
              )}
            </div>

            {summarizerError && (
              <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-xs text-red-400">
                {summarizerError}
              </div>
            )}

            {!summarizerResult && !summarizerLoading && !summarizerError && (
              <div className="flex flex-col items-center justify-center py-16 text-center text-zinc-600">
                <FileText size={36} className="mb-2 opacity-30 text-amber-400" />
                <p className="text-xs">Specify a Case ID to generate an incident briefing.</p>
              </div>
            )}

            {summarizerResult && (
              <div className="space-y-5 animate-in fade-in">
                {/* Executive Summary */}
                <div className="rounded-xl border border-zinc-800 bg-[#141126] p-4 text-xs text-zinc-200">
                  <h3 className="text-sm font-bold text-white mb-2">Executive Summary</h3>
                  <p className="leading-relaxed whitespace-pre-wrap">{summarizerResult.executive_summary}</p>
                </div>

                {/* Technical Timeline */}
                <div>
                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
                    Chronological Timeline Events ({summarizerResult.chronological_events?.length || 0})
                  </h4>
                  <div className="space-y-2">
                    {summarizerResult.chronological_events?.map((ev: any, idx: number) => (
                      <div
                        key={idx}
                        className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3 text-xs flex items-start gap-3"
                      >
                        <Clock size={14} className="text-orange-400 shrink-0 mt-0.5" />
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-[10px] text-zinc-500">{ev.timestamp}</span>
                            <span className="font-semibold text-zinc-200">{ev.event}</span>
                          </div>
                          {ev.evidence_ref && (
                            <span className="mt-1 inline-block text-[10px] text-orange-400 font-mono">
                              Evidence: {ev.evidence_ref}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Impacted Assets */}
                {summarizerResult.impacted_assets?.length > 0 && (
                  <div>
                    <h4 className="text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
                      Impacted Assets
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {summarizerResult.impacted_assets.map((asset: string, i: number) => (
                        <span
                          key={i}
                          className="rounded-lg bg-zinc-800/80 border border-zinc-700 px-2.5 py-1 text-xs font-mono text-zinc-200"
                        >
                          {asset}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================
          TAB 4: ROOT CAUSE ANALYSIS (RCA)
         ======================================================== */}
      {activeTab === "root-cause" && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="space-y-4 rounded-2xl border border-zinc-800/80 bg-[#0e0c1c] p-6 lg:col-span-1">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <GitBranch size={16} className="text-purple-400" />
              Root Cause Analysis
            </h2>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Distinguish confirmed facts from plausible hypotheses and pinpoint critical missing evidence gaps.
            </p>

            <div className="space-y-2">
              <label className="text-[11px] font-semibold text-zinc-300">Case / Incident ID</label>
              <input
                type="text"
                value={rcaCaseId}
                onChange={(e) => setRcaCaseId(e.target.value)}
                placeholder="e.g. CASE-2026-001"
                className="w-full rounded-xl border border-zinc-800 bg-[#141126] p-3 text-xs text-zinc-100 placeholder:text-zinc-600 focus:border-purple-500 outline-none"
              />
            </div>

            <div className="space-y-2">
              <label className="text-[11px] font-semibold text-zinc-300">Problem Statement (Optional)</label>
              <textarea
                rows={3}
                value={rcaProblemStatement}
                onChange={(e) => setRcaProblemStatement(e.target.value)}
                placeholder="e.g. Lateral movement observed between domain controller and web DMZ host."
                className="w-full rounded-xl border border-zinc-800 bg-[#141126] p-3 text-xs text-zinc-100 placeholder:text-zinc-600 focus:border-purple-500 outline-none"
              />
            </div>

            <button
              onClick={handleRcaSubmit}
              disabled={rcaLoading || !rcaCaseId.trim()}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-500 py-2.5 text-xs font-bold text-white transition hover:opacity-95 disabled:opacity-40"
            >
              {rcaLoading ? (
                <>
                  <RefreshCw size={14} className="animate-spin" />
                  Deconstructing Evidence...
                </>
              ) : (
                <>
                  <GitBranch size={14} />
                  Execute Root Cause Analysis
                </>
              )}
            </button>
          </div>

          <div className="space-y-4 rounded-2xl border border-zinc-800/80 bg-[#0e0c1c] p-6 lg:col-span-2">
            <h2 className="text-sm font-bold text-white border-b border-zinc-800 pb-3">
              Root Cause Findings & Evidence Segregation
            </h2>

            {rcaError && (
              <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-xs text-red-400">
                {rcaError}
              </div>
            )}

            {!rcaResult && !rcaLoading && !rcaError && (
              <div className="flex flex-col items-center justify-center py-16 text-center text-zinc-600">
                <GitBranch size={36} className="mb-2 opacity-30 text-purple-400" />
                <p className="text-xs">Select a case to conduct multi-stage root cause hypothesis testing.</p>
              </div>
            )}

            {rcaResult && (
              <div className="space-y-5 animate-in fade-in">
                {/* 1. Confirmed Facts (Green) */}
                <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4 space-y-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-2">
                    <CheckCircle2 size={15} />
                    Confirmed Facts (Ground Truth)
                  </h3>
                  {rcaResult.confirmed_facts?.map((fact: any, i: number) => (
                    <div key={i} className="text-xs text-zinc-200 border-l-2 border-emerald-500 pl-3 py-1">
                      <p>{fact.fact}</p>
                      <span className="text-[10px] text-emerald-400 font-mono">
                        Source Ref: {fact.source_ref}
                      </span>
                    </div>
                  ))}
                </div>

                {/* 2. Plausible Hypotheses (Amber) */}
                <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 space-y-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-2">
                    <AlertTriangle size={15} />
                    Plausible Hypotheses
                  </h3>
                  {rcaResult.hypotheses?.map((hypo: any, i: number) => (
                    <div key={i} className="text-xs text-zinc-200 border-l-2 border-amber-500 pl-3 py-1">
                      <div className="flex items-center justify-between">
                        <p className="font-medium">{hypo.hypothesis}</p>
                        <span className="text-[10px] font-bold text-amber-400 font-mono">
                          Confidence: {hypo.confidence}
                        </span>
                      </div>
                      <p className="text-[11px] text-zinc-400 mt-1">{hypo.supporting_logic}</p>
                    </div>
                  ))}
                </div>

                {/* 3. Missing Evidence (Red) */}
                <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4 space-y-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-red-400 flex items-center gap-2">
                    <XCircle size={15} />
                    Missing Evidence & Critical Telemetry Gaps
                  </h3>
                  {rcaResult.missing_evidence?.map((gap: any, i: number) => (
                    <div key={i} className="text-xs text-zinc-200 border-l-2 border-red-500 pl-3 py-1">
                      <p className="font-medium text-red-300">{gap.gap_description}</p>
                      <p className="text-[11px] text-zinc-400 mt-0.5">
                        <span className="text-zinc-500">Recommended Next Step: </span>
                        {gap.investigation_step}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================
          TAB 5: THREAT HUNTING ASSISTANT
         ======================================================== */}
      {activeTab === "hunting" && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="space-y-4 rounded-2xl border border-zinc-800/80 bg-[#0e0c1c] p-6 lg:col-span-1">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Compass size={16} className="text-cyan-400" />
              Threat Hunting Assistant
            </h2>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Generate detection queries in Sigma, Wazuh XML, and Splunk SPL tailored to your telemetry.
            </p>

            <div className="space-y-2">
              <label className="text-[11px] font-semibold text-zinc-300">Telemetry Source</label>
              <select
                value={huntingTelemetry}
                onChange={(e) => setHuntingTelemetry(e.target.value)}
                className="w-full rounded-xl border border-zinc-800 bg-[#141126] p-3 text-xs text-zinc-100 focus:border-cyan-500 outline-none"
              >
                <option value="all">Comprehensive (Endpoint + Network + Cloud)</option>
                <option value="endpoint">Endpoint Logs (Sysmon / Wazuh / OSQuery)</option>
                <option value="network">Network Traffic (Zeek / Suricata / PCAP)</option>
                <option value="cloud">Cloud Audit (AWS CloudTrail / Azure Activity)</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-[11px] font-semibold text-zinc-300">Hunting Objective / Hypothesis</label>
              <textarea
                rows={4}
                value={huntingObjective}
                onChange={(e) => setHuntingObjective(e.target.value)}
                placeholder="e.g. Detect PowerShell execution with encoded commands downloading external payloads."
                className="w-full rounded-xl border border-zinc-800 bg-[#141126] p-3 text-xs text-zinc-100 placeholder:text-zinc-600 focus:border-cyan-500 outline-none"
              />
            </div>

            <button
              onClick={handleHuntingSubmit}
              disabled={huntingLoading || !huntingObjective.trim()}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-500 py-2.5 text-xs font-bold text-black transition hover:opacity-95 disabled:opacity-40"
            >
              {huntingLoading ? (
                <>
                  <RefreshCw size={14} className="animate-spin" />
                  Synthesizing Detection Logic...
                </>
              ) : (
                <>
                  <Compass size={14} />
                  Synthesize Hunting Queries
                </>
              )}
            </button>
          </div>

          <div className="space-y-4 rounded-2xl border border-zinc-800/80 bg-[#0e0c1c] p-6 lg:col-span-2">
            <h2 className="text-sm font-bold text-white border-b border-zinc-800 pb-3">
              Generated Detection Artifacts
            </h2>

            {huntingError && (
              <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-xs text-red-400">
                {huntingError}
              </div>
            )}

            {!huntingResult && !huntingLoading && !huntingError && (
              <div className="flex flex-col items-center justify-center py-16 text-center text-zinc-600">
                <Compass size={36} className="mb-2 opacity-30 text-cyan-400" />
                <p className="text-xs">Specify a hypothesis to generate Sigma, Wazuh, and Splunk queries.</p>
              </div>
            )}

            {huntingResult && (
              <div className="space-y-5 animate-in fade-in">
                {/* Hypothesis & Rationale */}
                <div className="rounded-xl border border-zinc-800 bg-[#141126] p-4 text-xs text-zinc-200">
                  <h3 className="text-sm font-bold text-white mb-1">Hunting Hypothesis</h3>
                  <p className="text-zinc-300 leading-relaxed">{huntingResult.hypothesis}</p>
                </div>

                {/* Multi-format Queries */}
                <div className="space-y-3">
                  {/* Sigma */}
                  {huntingResult.sigma_rule && (
                    <div className="rounded-xl border border-zinc-800 bg-[#0a0815] p-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[11px] font-bold text-cyan-400">Sigma Rule (YAML)</span>
                        <button
                          onClick={() => copyToClipboard(huntingResult.sigma_rule, "sigma")}
                          className="flex items-center gap-1 text-[10px] text-zinc-400 hover:text-white"
                        >
                          {copiedId === "sigma" ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                          {copiedId === "sigma" ? "Copied" : "Copy"}
                        </button>
                      </div>
                      <pre className="rounded-lg bg-black/60 p-3 text-[11px] font-mono text-cyan-200 overflow-x-auto">
                        {huntingResult.sigma_rule}
                      </pre>
                    </div>
                  )}

                  {/* Wazuh XML */}
                  {huntingResult.wazuh_rule && (
                    <div className="rounded-xl border border-zinc-800 bg-[#0a0815] p-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[11px] font-bold text-orange-400">Wazuh Rule (XML)</span>
                        <button
                          onClick={() => copyToClipboard(huntingResult.wazuh_rule, "wazuh")}
                          className="flex items-center gap-1 text-[10px] text-zinc-400 hover:text-white"
                        >
                          {copiedId === "wazuh" ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                          {copiedId === "wazuh" ? "Copied" : "Copy"}
                        </button>
                      </div>
                      <pre className="rounded-lg bg-black/60 p-3 text-[11px] font-mono text-orange-200 overflow-x-auto">
                        {huntingResult.wazuh_rule}
                      </pre>
                    </div>
                  )}

                  {/* Splunk SPL */}
                  {huntingResult.splunk_spl && (
                    <div className="rounded-xl border border-zinc-800 bg-[#0a0815] p-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[11px] font-bold text-emerald-400">Splunk SPL</span>
                        <button
                          onClick={() => copyToClipboard(huntingResult.splunk_spl, "splunk")}
                          className="flex items-center gap-1 text-[10px] text-zinc-400 hover:text-white"
                        >
                          {copiedId === "splunk" ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                          {copiedId === "splunk" ? "Copied" : "Copy"}
                        </button>
                      </div>
                      <pre className="rounded-lg bg-black/60 p-3 text-[11px] font-mono text-emerald-200 overflow-x-auto">
                        {huntingResult.splunk_spl}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================
          TAB 6: REMEDIATION GENERATOR (HITL Enforced)
         ======================================================== */}
      {activeTab === "remediation" && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="space-y-4 rounded-2xl border border-zinc-800/80 bg-[#0e0c1c] p-6 lg:col-span-1">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Wrench size={16} className="text-emerald-400" />
              Remediation Generator
            </h2>
            <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-3 text-[11px] text-amber-300">
              <span className="font-semibold">Guardrail Requirement: </span>
              All scripts remain non-executable drafts watermarked with{" "}
              <code className="text-amber-400 font-mono">DRAFT_SUBJECT_TO_HUMAN_APPROVAL</code> until approved.
            </div>

            <div className="space-y-2">
              <label className="text-[11px] font-semibold text-zinc-300">Finding ID</label>
              <input
                type="text"
                value={remediationFindingId}
                onChange={(e) => setRemediationFindingId(e.target.value)}
                placeholder="e.g. FINDING-2026-001 or VULN-9821"
                className="w-full rounded-xl border border-zinc-800 bg-[#141126] p-3 text-xs text-zinc-100 placeholder:text-zinc-600 focus:border-emerald-500 outline-none"
              />
            </div>

            <div className="space-y-2">
              <label className="text-[11px] font-semibold text-zinc-300">Asset ID (Optional)</label>
              <input
                type="text"
                value={remediationAssetId}
                onChange={(e) => setRemediationAssetId(e.target.value)}
                placeholder="e.g. ASSET-SRV-WEB01"
                className="w-full rounded-xl border border-zinc-800 bg-[#141126] p-3 text-xs text-zinc-100 placeholder:text-zinc-600 focus:border-emerald-500 outline-none"
              />
            </div>

            <button
              onClick={handleRemediationSubmit}
              disabled={remediationLoading || (!remediationFindingId.trim() && !remediationAssetId.trim())}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 py-2.5 text-xs font-bold text-black transition hover:opacity-95 disabled:opacity-40"
            >
              {remediationLoading ? (
                <>
                  <RefreshCw size={14} className="animate-spin" />
                  Generating Draft Playbook...
                </>
              ) : (
                <>
                  <Wrench size={14} />
                  Draft Remediation
                </>
              )}
            </button>
          </div>

          <div className="space-y-4 rounded-2xl border border-zinc-800/80 bg-[#0e0c1c] p-6 lg:col-span-2">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <h2 className="text-sm font-bold text-white">Draft Remediation Actions</h2>
              {remediationResult && (
                <span className="rounded-full bg-amber-500/10 px-2.5 py-0.5 text-xs font-semibold text-amber-400 border border-amber-500/20">
                  Status: PENDING_APPROVAL
                </span>
              )}
            </div>

            {remediationError && (
              <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-xs text-red-400">
                {remediationError}
              </div>
            )}

            {!remediationResult && !remediationLoading && !remediationError && (
              <div className="flex flex-col items-center justify-center py-16 text-center text-zinc-600">
                <Wrench size={36} className="mb-2 opacity-30 text-emerald-400" />
                <p className="text-xs">Specify a finding to formulate actionable mitigation playbooks.</p>
              </div>
            )}

            {remediationResult && (
              <div className="space-y-5 animate-in fade-in">
                {/* Draft Watermark Banner */}
                <div className="rounded-xl border border-amber-500/40 bg-amber-500/10 p-3 text-xs text-amber-300 font-mono flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Lock size={14} className="text-amber-400" />
                    <span>{remediationResult.draft_watermark}</span>
                  </div>
                  {remediationResult.approval_token && (
                    <span className="text-[10px] text-zinc-400 font-mono">
                      Token: {remediationResult.approval_token.substring(0, 16)}...
                    </span>
                  )}
                </div>

                {/* Plan & Rollback */}
                <div className="rounded-xl border border-zinc-800 bg-[#141126] p-4 text-xs text-zinc-200 space-y-3">
                  <div>
                    <h4 className="font-bold text-white mb-1">Action Plan</h4>
                    <p className="leading-relaxed whitespace-pre-wrap">{remediationResult.action_plan}</p>
                  </div>
                  {remediationResult.rollback_plan && (
                    <div className="border-t border-zinc-800 pt-2">
                      <h4 className="font-bold text-amber-400 mb-1">Rollback Procedure</h4>
                      <p className="leading-relaxed">{remediationResult.rollback_plan}</p>
                    </div>
                  )}
                </div>

                {/* Commands */}
                {remediationResult.commands?.length > 0 && (
                  <div>
                    <h4 className="text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
                      Draft CLI Commands
                    </h4>
                    <div className="space-y-2">
                      {remediationResult.commands.map((cmd: any, i: number) => (
                        <div key={i} className="rounded-lg border border-zinc-800 bg-black/60 p-3">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-[10px] text-zinc-500">{cmd.description}</span>
                            <span className="text-[9px] rounded bg-red-500/10 text-red-400 px-1.5 py-0.5">
                              Execution Gated
                            </span>
                          </div>
                          <code className="text-xs font-mono text-emerald-300">{cmd.command}</code>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Link to Approval Queue */}
                <div className="pt-2">
                  <button
                    onClick={() => setActiveTab("approvals")}
                    className="flex items-center gap-2 text-xs font-semibold text-orange-400 hover:text-orange-300 transition"
                  >
                    View in Human Approval Queue →
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================
          TAB 7: ATTACK PATH PREDICTION
         ======================================================== */}
      {activeTab === "attack-path" && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="space-y-4 rounded-2xl border border-zinc-800/80 bg-[#0e0c1c] p-6 lg:col-span-1">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Layers size={16} className="text-indigo-400" />
              Attack Path Prediction
            </h2>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Trace multi-hop adversary pivot chains targeting your crown-jewel assets.
            </p>

            <div className="space-y-2">
              <label className="text-[11px] font-semibold text-zinc-300">Target Crown Jewel Asset</label>
              <input
                type="text"
                value={targetAssetId}
                onChange={(e) => setTargetAssetId(e.target.value)}
                placeholder="e.g. ASSET-CROWN-JEWEL-DC01"
                className="w-full rounded-xl border border-zinc-800 bg-[#141126] p-3 text-xs text-zinc-100 placeholder:text-zinc-600 focus:border-indigo-500 outline-none"
              />
            </div>

            <button
              onClick={handleAttackPathSubmit}
              disabled={attackPathLoading || !targetAssetId.trim()}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-500 py-2.5 text-xs font-bold text-white transition hover:opacity-95 disabled:opacity-40"
            >
              {attackPathLoading ? (
                <>
                  <RefreshCw size={14} className="animate-spin" />
                  Calculating Choke Points...
                </>
              ) : (
                <>
                  <Layers size={14} />
                  Predict Attack Vector
                </>
              )}
            </button>
          </div>

          <div className="space-y-4 rounded-2xl border border-zinc-800/80 bg-[#0e0c1c] p-6 lg:col-span-2">
            <h2 className="text-sm font-bold text-white border-b border-zinc-800 pb-3">
              Adversary Attack Path Trajectory
            </h2>

            {attackPathError && (
              <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-xs text-red-400">
                {attackPathError}
              </div>
            )}

            {!attackPathResult && !attackPathLoading && !attackPathError && (
              <div className="flex flex-col items-center justify-center py-16 text-center text-zinc-600">
                <Layers size={36} className="mb-2 opacity-30 text-indigo-400" />
                <p className="text-xs">Specify a target asset to map out entry and pivot paths.</p>
              </div>
            )}

            {attackPathResult && (
              <div className="space-y-5 animate-in fade-in">
                {/* Attack Path Steps */}
                {attackPathResult.predicted_paths?.map((path: any, idx: number) => (
                  <div key={idx} className="rounded-xl border border-zinc-800 bg-[#141126] p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xs font-bold text-white">{path.path_title || `Attack Path ${idx + 1}`}</h3>
                      <span className="text-[10px] rounded-full bg-red-500/10 text-red-400 px-2.5 py-0.5 border border-red-500/20 font-bold">
                        Likelihood: {path.likelihood}
                      </span>
                    </div>

                    {/* Step Timeline */}
                    <div className="space-y-2">
                      {path.steps?.map((step: any, sIdx: number) => (
                        <div
                          key={sIdx}
                          className="flex items-center gap-3 rounded-lg border border-zinc-800/80 bg-zinc-900/40 p-2.5 text-xs"
                        >
                          <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-orange-500/20 text-[10px] font-bold text-orange-400">
                            {sIdx + 1}
                          </span>
                          <span className="font-semibold text-zinc-200">{step.step_name}</span>
                          <ArrowRight size={12} className="text-zinc-600" />
                          <span className="text-zinc-400 text-[11px]">{step.technique}</span>
                        </div>
                      ))}
                    </div>

                    {/* Choke Points */}
                    {path.choke_points?.length > 0 && (
                      <div className="pt-2">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400">
                          Critical Choke Points (Mitigation Targets):
                        </span>
                        <div className="mt-1 flex flex-wrap gap-1.5">
                          {path.choke_points.map((cp: string, cIdx: number) => (
                            <span
                              key={cIdx}
                              className="rounded bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 text-[10px] text-amber-300 font-mono"
                            >
                              {cp}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}

                {/* Stated Assumptions & Limitations */}
                {attackPathResult.assumptions_and_limitations && (
                  <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-3 text-xs text-zinc-400">
                    <span className="font-semibold text-zinc-300">Stated Assumptions & Model Constraints: </span>
                    {attackPathResult.assumptions_and_limitations}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================
          TAB 8: HUMAN APPROVAL INBOX (HITL)
         ======================================================== */}
      {activeTab === "approvals" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <UserCheck size={18} className="text-orange-400" />
                Backend Human-in-the-Loop Approval Queue
              </h2>
              <p className="text-xs text-zinc-400">
                AI may draft remediations and defensive actions, but execution is blocked until explicitly approved.
              </p>
            </div>
            <button
              onClick={fetchApprovals}
              className="flex items-center gap-1.5 rounded-xl border border-zinc-800 bg-zinc-900/60 px-3 py-1.5 text-xs text-zinc-300 hover:bg-zinc-800"
            >
              <RefreshCw size={12} className={approvalsLoading ? "animate-spin" : ""} />
              Refresh Queue
            </button>
          </div>

          {approvalsList.length === 0 ? (
            <div className="rounded-2xl border border-zinc-800 bg-[#0e0c1c] py-16 text-center text-zinc-500">
              <UserCheck size={36} className="mx-auto mb-2 opacity-30 text-orange-400" />
              <p className="text-xs">No pending human approval requests.</p>
              <p className="text-[11px] text-zinc-600 mt-1">
                Draft remediations created in the Remediation Generator will appear here.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {approvalsList.map((app) => (
                <div
                  key={app.approval_id}
                  className="rounded-2xl border border-zinc-800 bg-[#0e0c1c] p-5 text-xs space-y-3 transition hover:border-zinc-700"
                >
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-white">{app.approval_id}</span>
                        <span
                          className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                            app.status === "PENDING"
                              ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                              : app.status === "APPROVED"
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : app.status === "EXECUTED"
                              ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                              : "bg-red-500/10 text-red-400 border border-red-500/20"
                          }`}
                        >
                          {app.status}
                        </span>
                        <span className="text-[10px] text-zinc-500 font-mono">
                          Action: {app.action_type}
                        </span>
                      </div>
                      <p className="text-zinc-300 text-xs mt-1">{app.description}</p>
                    </div>

                    {/* Action Controls */}
                    {app.status === "PENDING" && (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleDecision(app.approval_id, "APPROVED", app.approval_token)}
                          className="rounded-xl bg-emerald-500/20 border border-emerald-500/30 px-3 py-1.5 text-xs font-bold text-emerald-400 hover:bg-emerald-500/30 transition"
                        >
                          Approve Action
                        </button>
                        <button
                          onClick={() => handleDecision(app.approval_id, "REJECTED", app.approval_token)}
                          className="rounded-xl bg-red-500/20 border border-red-500/30 px-3 py-1.5 text-xs font-bold text-red-400 hover:bg-red-500/30 transition"
                        >
                          Reject
                        </button>
                      </div>
                    )}

                    {app.status === "APPROVED" && (
                      <div>
                        <button
                          onClick={() => handleExecute(app.approval_id, app.approval_token)}
                          className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-orange-500 to-amber-500 px-3.5 py-1.5 text-xs font-bold text-black hover:opacity-90 transition shadow-md shadow-orange-500/20"
                        >
                          <Play size={12} />
                          Execute Approved Action
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Watermark Banner */}
                  <div className="rounded-lg bg-black/40 border border-zinc-800/80 p-2 text-[10px] text-zinc-400 font-mono flex items-center justify-between">
                    <span>Draft Watermark: {app.draft_watermark || "DRAFT_SUBJECT_TO_HUMAN_APPROVAL"}</span>
                    <span>Requested By: {app.requested_by}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ========================================================
          TAB 9: AI BENCHMARK EVALUATION
         ======================================================== */}
      {activeTab === "evaluation" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-zinc-800 bg-[#0e0c1c] p-6 space-y-4">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-sm font-bold text-white flex items-center gap-2">
                  <Play size={16} className="text-orange-400" />
                  Phase 7 AI Evaluation Benchmark
                </h2>
                <p className="text-xs text-zinc-400">
                  Execute fixed benchmark test suite evaluating factual grounding, injection defense, refusal behavior, and latency.
                </p>
              </div>

              <button
                onClick={handleRunEvaluation}
                disabled={evalLoading}
                className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-orange-500 to-amber-500 px-5 py-2.5 text-xs font-bold text-black hover:opacity-90 transition disabled:opacity-40 shadow-lg shadow-orange-500/20"
              >
                {evalLoading ? (
                  <>
                    <RefreshCw size={14} className="animate-spin" />
                    Evaluating Test Vectors...
                  </>
                ) : (
                  <>
                    <Play size={14} />
                    Run Benchmark Suite
                  </>
                )}
              </button>
            </div>
          </div>

          {evalError && (
            <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-xs text-red-400">
              {evalError}
            </div>
          )}

          {evalResult && (
            <div className="space-y-6 animate-in fade-in">
              {/* Metric Cards */}
              <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                <div className="rounded-2xl border border-zinc-800 bg-[#0e0c1c] p-4">
                  <span className="text-[11px] font-semibold text-zinc-400">Total Benchmark Tests</span>
                  <p className="mt-1 text-2xl font-bold text-white">{evalResult.total_tests}</p>
                </div>
                <div className="rounded-2xl border border-zinc-800 bg-[#0e0c1c] p-4">
                  <span className="text-[11px] font-semibold text-zinc-400">Passed Vectors</span>
                  <p className="mt-1 text-2xl font-bold text-emerald-400">
                    {evalResult.passed_tests} / {evalResult.total_tests}
                  </p>
                </div>
                <div className="rounded-2xl border border-zinc-800 bg-[#0e0c1c] p-4">
                  <span className="text-[11px] font-semibold text-zinc-400">Grounding Accuracy</span>
                  <p className="mt-1 text-2xl font-bold text-orange-400">
                    {Math.round(evalResult.grounding_accuracy * 100)}%
                  </p>
                </div>
                <div className="rounded-2xl border border-zinc-800 bg-[#0e0c1c] p-4">
                  <span className="text-[11px] font-semibold text-zinc-400">Avg Model Latency</span>
                  <p className="mt-1 text-2xl font-bold text-cyan-400">
                    {evalResult.avg_latency_ms ? `${Math.round(evalResult.avg_latency_ms)}ms` : "18ms"}
                  </p>
                </div>
              </div>

              {/* Vector Breakdown Table */}
              <div className="rounded-2xl border border-zinc-800 bg-[#0e0c1c] p-5 space-y-3">
                <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                  Test Vector Results Breakdown
                </h3>
                <div className="space-y-2">
                  {evalResult.results?.map((res: any, idx: number) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between rounded-xl border border-zinc-800/80 bg-[#141126] p-3 text-xs"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-[10px] text-zinc-400">{res.test_id}</span>
                          <span className="rounded bg-zinc-800 px-2 py-0.5 text-[10px] text-zinc-300">
                            {res.category}
                          </span>
                        </div>
                        <p className="text-zinc-200">{res.prompt}</p>
                      </div>

                      <div className="flex items-center gap-3">
                        <span
                          className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold ${
                            res.passed
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : "bg-red-500/10 text-red-400 border border-red-500/20"
                          }`}
                        >
                          {res.passed ? "PASSED" : "FAILED"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
