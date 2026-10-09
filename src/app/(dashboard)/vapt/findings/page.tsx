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
} from "lucide-react";

interface CVEFinding {
  cve_id: string;
  cvss_score: number;
  cvss_vector?: string;
  cisa_kev: boolean;
  summary?: string;
  remediation?: string;
  affected_product?: string;
  published_date: string;
}

export default function VAPTFindingsPage() {
  const [cves, setCves] = useState<CVEFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [kevOnly, setKevOnly] = useState(false);
  const [minCvss, setMinCvss] = useState<number>(0);
  const [searchQuery, setSearchQuery] = useState("");

  // Priority Calculator State
  const [calcCvss, setCalcCvss] = useState(8.5);
  const [calcKev, setCalcKev] = useState(true);
  const [calcCrit, setCalcCrit] = useState("HIGH");
  const [calcControl, setCalcControl] = useState(false);
  const [calcResult, setCalcResult] = useState<any>(null);

  const fetchCVEs = async () => {
    setLoading(true);
    try {
      let url = "/api/v1/vapt/cve";
      const params = new URLSearchParams();
      if (kevOnly) params.append("cisa_kev", "true");
      if (minCvss > 0) params.append("min_cvss", minCvss.toString());
      if (params.toString()) url += `?${params.toString()}`;

      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setCves(data);
      }
    } catch (err) {
      console.error("Failed to fetch CVE findings", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCVEs();
  }, [kevOnly, minCvss]);

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

  const filteredCVEs = cves.filter((c) => {
    if (!searchQuery) return true;
    return (
      c.cve_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.summary && c.summary.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (c.affected_product && c.affected_product.toLowerCase().includes(searchQuery.toLowerCase()))
    );
  });

  const totalCount = cves.length;
  const kevCount = cves.filter((c) => c.cisa_kev).length;
  const criticalCount = cves.filter((c) => c.cvss_score >= 9.0).length;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between rounded-2xl border border-slate-800 bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/40 p-6 shadow-xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-orange-500/10 text-orange-400 ring-1 ring-orange-500/20">
              <Flame className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">VAPT Prioritized Vulnerability Findings</h1>
              <p className="text-xs text-slate-400">
                Team B - NVD & CISA KEV CVE Ingestion Engine with Risk Prioritization Formula
              </p>
            </div>
          </div>
        </div>

        <button
          onClick={fetchCVEs}
          className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900/80 px-4 py-2.5 text-xs font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin text-indigo-400" : ""}`} />
          Refresh Feeds
        </button>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
          <span className="text-xs font-medium text-slate-400">Total Ingested CVEs</span>
          <p className="mt-3 text-3xl font-extrabold text-white">{totalCount}</p>
          <p className="mt-1 text-[11px] text-slate-500">NVD & vendor advisories</p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-rose-400">CISA KEV Active Exploits</span>
            <Flame className="h-4 w-4 text-rose-500" />
          </div>
          <p className="mt-3 text-3xl font-extrabold text-rose-400">{kevCount}</p>
          <p className="mt-1 text-[11px] text-rose-500/80 font-medium">Actively exploited in the wild</p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
          <span className="text-xs font-medium text-orange-400">Critical CVSS (9.0+)</span>
          <p className="mt-3 text-3xl font-extrabold text-orange-400">{criticalCount}</p>
          <p className="mt-1 text-[11px] text-slate-500">Highest severity rating</p>
        </div>
      </div>

      {/* Prioritization Formula Interactive Calculator */}
      <div className="rounded-2xl border border-indigo-900/50 bg-slate-900/80 p-5 shadow-xl">
        <div className="flex items-center gap-2 border-b border-slate-800 pb-3 mb-4">
          <Calculator className="h-5 w-5 text-indigo-400" />
          <h2 className="text-sm font-bold text-white">Vulnerability Prioritization Formula Simulator</h2>
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

      {/* Filters Bar */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between rounded-2xl border border-slate-800 bg-slate-900/40 p-4">
        <div className="flex flex-1 items-center gap-3">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search CVE ID, summary, or affected product..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-xl border border-slate-800 bg-slate-950 py-2.5 pl-10 pr-4 text-xs text-white placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
            />
          </div>

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
      </div>

      {/* CVE Table */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden shadow-xl">
        <table className="w-full text-left text-xs">
          <thead className="border-b border-slate-800 bg-slate-950/80 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            <tr>
              <th className="px-6 py-4">CVE ID</th>
              <th className="px-6 py-4">CVSS v3.1</th>
              <th className="px-6 py-4">CISA KEV</th>
              <th className="px-6 py-4">Affected Product</th>
              <th className="px-6 py-4">Summary</th>
              <th className="px-6 py-4">Remediation</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {loading ? (
              <tr>
                <td colSpan={6} className="py-12 text-center text-slate-500">
                  <RefreshCw className="mx-auto h-6 w-6 animate-spin text-indigo-500 mb-2" />
                  Loading daily CVE vulnerability feeds...
                </td>
              </tr>
            ) : filteredCVEs.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-12 text-center text-slate-500">
                  No CVE findings found.
                </td>
              </tr>
            ) : (
              filteredCVEs.map((cve) => (
                <tr key={cve.cve_id} className="hover:bg-slate-800/40 transition">
                  <td className="px-6 py-4 font-mono font-bold text-indigo-400">{cve.cve_id}</td>
                  <td className="px-6 py-4">
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
  );
}
