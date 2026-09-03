"use client";
import React, { useEffect, useState } from "react";
import Link from "next/link";
import ControlStatusBadge from "./ControlStatusBadge";

type ControlItem = { id: string; title: string; framework: string; status: string; owner?: string | null; evidenceCount?: number };

export default function ControlTable() {
  const [items, setItems] = useState<ControlItem[]>([]);
  const [q, setQ] = useState('');
  const [framework, setFramework] = useState('');
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(()=>{
    setLoading(true); setError(null);
    fetch(`/api/controls?q=${encodeURIComponent(q)}&framework=${encodeURIComponent(framework)}&status=${encodeURIComponent(status)}`)
      .then(r=>r.json()).then(json=>setItems(json.data || [])).catch(e=>setError(String(e))).finally(()=>setLoading(false));
  }, [q, framework, status]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <input placeholder="Search controls" value={q} onChange={(e)=>setQ(e.target.value)} className="rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-200" />
          <select value={framework} onChange={(e)=>setFramework(e.target.value)} className="rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-200">
            <option value="">All frameworks</option>
            <option value="NIST">NIST</option>
            <option value="ISO">ISO</option>
            <option value="PCI">PCI</option>
          </select>
          <select value={status} onChange={(e)=>setStatus(e.target.value)} className="rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-200">
            <option value="">All statuses</option>
            <option>Implemented</option>
            <option>Planned</option>
            <option>Not Implemented</option>
            <option>Deprecated</option>
          </select>
        </div>

        <div>
          <Link href="/controls/new" className="rounded-2xl bg-slate-200 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-slate-300">Add Control</Link>
        </div>
      </div>

      {loading ? (
        <div className="rounded-2xl bg-slate-900/50 p-6 text-center text-sm text-slate-300">Loading controls...</div>
      ) : error ? (
        <div className="rounded-2xl bg-rose-900/20 p-6 text-center text-sm text-rose-200">Error: {error}</div>
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/60">
          <table className="w-full table-auto">
            <thead className="bg-slate-950/30">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">Control</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">Framework</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">Owner</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">Evidence</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map(i=> (
                <tr key={i.id} className="border-t border-slate-800">
                  <td className="px-4 py-3 text-sm text-slate-200">{i.title}</td>
                  <td className="px-4 py-3 text-sm text-slate-300">{i.framework}</td>
                  <td className="px-4 py-3"><ControlStatusBadge status={i.status} /></td>
                  <td className="px-4 py-3 text-sm text-slate-300">{i.owner || '-'}</td>
                  <td className="px-4 py-3 text-sm text-slate-300">{i.evidenceCount || 0}</td>
                  <td className="px-4 py-3 text-sm text-slate-300"><Link href={`/controls/${i.id}`} className="text-sky-300 hover:underline">View</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
