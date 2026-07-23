"use client";
import React, { useEffect, useState } from "react";
import Sidebar from "../../../components/ui/Sidebar";
import TopNav from "../../../components/ui/TopNav";
import StatusBadge from "../../../components/audits/StatusBadge";
import { useParams } from "next/navigation";

export default function AuditDetailsPage() {
  const params = useParams();
  const id = params?.id;
  const [audit, setAudit] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [auditor, setAuditor] = useState('');
  const [status, setStatus] = useState('');

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    fetch(`/api/audits/${id}`).then(r=>r.json()).then(json=>{ setAudit(json.data); setAuditor(json.data?.auditor||''); setStatus(json.data?.status||''); }).catch(e=>setError(String(e))).finally(()=>setLoading(false));
  }, [id]);

  async function save() {
    if (!id) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/audits/${id}`, { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ auditor, status }) });
      if (!res.ok) throw new Error('Save failed');
      const json = await res.json();
      setAudit(json.data);
    } catch (err:any) {
      setError(err?.message || 'Unexpected error');
    } finally { setLoading(false); }
  }

  return (
    <div className="min-h-screen bg-[var(--background)]">
      <div className="mx-auto max-w-7xl">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-[260px_1fr]">
          <Sidebar />
          <div className="flex flex-col gap-6">
            <TopNav />
            <main className="px-4 py-6">
              {loading ? (
                <div className="rounded-2xl bg-slate-900/50 p-6 text-sm text-slate-300">Loading...</div>
              ) : error ? (
                <div className="rounded-2xl bg-rose-900/20 p-6 text-sm text-rose-200">{error}</div>
              ) : audit ? (
                <div className="space-y-6">
                  <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-6">
                    <div className="flex items-start justify-between">
                      <div>
                        <h1 className="text-2xl font-semibold text-white">{audit.title}</h1>
                        <p className="mt-2 text-sm text-slate-300">{audit.description}</p>
                      </div>
                      <div className="space-y-2 text-right">
                        <StatusBadge status={audit.status} />
                        <div className="text-sm text-slate-400">Due: {audit.dueDate || '-'}</div>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 max-w-xl">
                    <h3 className="text-sm font-semibold text-white">Assignment</h3>
                    <label className="block text-sm text-slate-300 mt-3">Auditor (email)</label>
                    <input value={auditor} onChange={(e)=>setAuditor(e.target.value)} className="mt-2 w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-slate-100" />

                    <label className="block text-sm text-slate-300 mt-3">Status</label>
                    <select value={status} onChange={(e)=>setStatus(e.target.value)} className="mt-2 w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-slate-100">
                      <option>Open</option>
                      <option>In Progress</option>
                      <option>Completed</option>
                    </select>

                    <div className="mt-4 flex gap-2">
                      <button onClick={save} className="rounded-2xl bg-slate-200 px-4 py-2 text-sm font-semibold text-slate-950">Save</button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-sm text-slate-300">Audit not found</div>
              )}
            </main>
          </div>
        </div>
      </div>
    </div>
  );
}
