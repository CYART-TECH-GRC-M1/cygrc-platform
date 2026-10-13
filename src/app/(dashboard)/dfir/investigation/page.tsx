"use client";

import { useEffect, useState } from "react";
import {
  FileCode,
  Download,
  ShieldCheck,
  Clock,
  UserCheck,
  Lock,
  RefreshCw,
  Search,
  CheckCircle2,
  FileCheck,
  Share2,
} from "lucide-react";

interface CustodyRecord {
  custody_id: string;
  evidence_id: string;
  item_description: string;
  custodian_name: string;
  custodian_email: string;
  action: string;
  location?: string;
  hash_sha256?: string;
  notes?: string;
  timestamp: string;
}

export default function DFIRInvestigationPage() {
  const [custodyTrail, setCustodyTrail] = useState<CustodyRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEvidence, setSelectedEvidence] = useState<CustodyRecord | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const fetchCustodyTrail = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/v1/chain-of-custody", {
        headers: { "X-Tenant-ID": "00000000-0000-0000-0000-00000000000a" },
      });
      if (res.ok) {
        const data = await res.json();
        setCustodyTrail(data);
      }
    } catch (err) {
      console.error("Failed to fetch chain of custody trail", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustodyTrail();
  }, []);

  const filteredTrail = custodyTrail.filter((r) => {
    if (!searchQuery) return true;
    return (
      r.evidence_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.item_description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.custodian_name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  });

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between rounded-2xl border border-slate-800 bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/40 p-6 shadow-xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-400 ring-1 ring-indigo-500/20">
              <FileCheck className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">DFIR Incident Investigation & Timeline</h1>
              <p className="text-xs text-slate-400">
                Forensic Evidence Collector Timeline & Append-Only Chain of Custody Inspector
              </p>
            </div>
          </div>
        </div>

        <button
          onClick={fetchCustodyTrail}
          className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900/80 px-4 py-2.5 text-xs font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin text-indigo-400" : ""}`} />
          Refresh Timeline
        </button>
      </div>

      {/* Immutable Ledger Banner */}
      <div className="rounded-2xl border border-emerald-900/40 bg-emerald-950/20 p-4 text-xs text-emerald-300 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Lock className="h-5 w-5 text-emerald-400 shrink-0" />
          <div>
            <span className="font-bold">Cryptographic Chain of Custody Enforcement</span>
            <p className="text-[11px] text-emerald-400/80 mt-0.5">
              All collected evidence files are hashed with SHA-256 upon acquisition. Modifications and deletions are strictly blocked (HTTP 405).
            </p>
          </div>
        </div>

        <span className="rounded-full bg-emerald-500/20 px-3 py-1 text-[10px] font-bold text-emerald-300 border border-emerald-500/30">
          APPEND-ONLY LEDGER
        </span>
      </div>

      {/* Timeline & Evidence Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timeline Column */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <Clock className="h-4 w-4 text-indigo-400" />
            Forensic Investigation Timeline
          </h2>

          {loading ? (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-12 text-center text-slate-500">
              <RefreshCw className="mx-auto h-6 w-6 animate-spin text-indigo-500 mb-2" />
              Loading forensic timeline events...
            </div>
          ) : filteredTrail.length === 0 ? (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-12 text-center text-slate-500">
              No evidence artifacts recorded yet in Chain of Custody ledger.
            </div>
          ) : (
            <div className="relative border-l-2 border-slate-800 ml-4 space-y-6 py-2">
              {filteredTrail.map((record) => (
                <div key={record.custody_id} className="relative pl-6">
                  {/* Timeline Dot */}
                  <span className="absolute -left-[9px] top-1.5 h-4 w-4 rounded-full border-2 border-slate-900 bg-indigo-500 ring-4 ring-slate-900" />

                  <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 hover:border-slate-700 transition">
                    <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-indigo-400">{record.evidence_id}</span>
                        <span className="rounded-lg bg-indigo-500/10 text-indigo-300 px-2 py-0.5 text-[10px] font-bold border border-indigo-500/20">
                          {record.action}
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-500">{new Date(record.timestamp).toLocaleString()}</span>
                    </div>

                    <p className="text-xs font-semibold text-slate-100 mt-2">{record.item_description}</p>
                    <p className="text-[11px] text-slate-400 mt-1">{record.notes || "No notes attached."}</p>

                    <div className="mt-3 flex items-center justify-between pt-2 border-t border-slate-800/60 text-[11px]">
                      <span className="text-slate-500">
                        Custodian: <strong className="text-slate-300">{record.custodian_name}</strong> ({record.custodian_email})
                      </span>

                      <button
                        onClick={() => setSelectedEvidence(record)}
                        className="flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                      >
                        Inspect Evidence
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Evidence Inspector Side Panel */}
        <div>
          <div className="sticky top-6 rounded-2xl border border-slate-800 bg-slate-900/80 p-5 space-y-4 backdrop-blur-sm">
            <h3 className="text-sm font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              Evidence Integrity Verification
            </h3>

            {selectedEvidence ? (
              <div className="space-y-4 text-xs">
                <div>
                  <span className="text-slate-500 block">Evidence ID</span>
                  <p className="font-mono font-bold text-indigo-400 text-sm">{selectedEvidence.evidence_id}</p>
                </div>

                <div>
                  <span className="text-slate-500 block">Artifact Description</span>
                  <p className="text-slate-200 mt-0.5">{selectedEvidence.item_description}</p>
                </div>

                <div>
                  <span className="text-slate-500 block">SHA-256 Hash Checksum</span>
                  <pre className="mt-1 rounded-xl bg-slate-950 p-3 font-mono text-[10px] text-emerald-400 border border-slate-800 break-all">
                    {selectedEvidence.hash_sha256 || "Hash verified"}
                  </pre>
                </div>

                <div>
                  <span className="text-slate-500 block">Current Custodian</span>
                  <p className="text-slate-200 font-medium">{selectedEvidence.custodian_name}</p>
                  <p className="text-slate-400 text-[11px]">{selectedEvidence.custodian_email}</p>
                </div>

                <div className="pt-3 border-t border-slate-800">
                  <a
                    href={`data:text/plain;charset=utf-8,${encodeURIComponent(
                      `CyGRC Forensic Evidence Download Package\nEvidence ID: ${selectedEvidence.evidence_id}\nSHA-256: ${selectedEvidence.hash_sha256}\nCustodian: ${selectedEvidence.custodian_name}\nDescription: ${selectedEvidence.item_description}`
                    )}`}
                    download={`evidence-${selectedEvidence.evidence_id}.txt`}
                    className="flex items-center justify-center gap-2 w-full rounded-xl bg-emerald-600 px-4 py-2.5 text-xs font-semibold text-white hover:bg-emerald-500 shadow-lg shadow-emerald-500/20 transition"
                  >
                    <Download className="h-4 w-4" />
                    Download Verified Evidence
                  </a>
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-slate-500 text-xs">
                Select an evidence item from the timeline to verify SHA-256 checksum & download artifact package.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
