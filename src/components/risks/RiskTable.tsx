"use client";
import React, { useEffect, useState } from "react";
import Link from "next/link";
import RiskLevelBadge from "./RiskLevelBadge";

type RiskItem = {
  id: string;
  title: string;
  level: string;
  owner?: string | null;
  status?: string;
  createdAt: string;
};

export default function RiskTable() {
  const [data, setData] = useState<RiskItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [q, setQ] = useState('');
  const [level, setLevel] = useState('');
  const [status, setStatus] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const [total, setTotal] = useState(0);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    setError(null);
    fetch(`/api/risks?q=${encodeURIComponent(q)}&level=${encodeURIComponent(level)}&status=${encodeURIComponent(status)}&page=${page}&pageSize=${pageSize}`)
      .then((r) => r.json())
      .then((json) => {
        if (!mounted) return;
        setData(json.data || []);
        setTotal(json.total || 0);
      })
      .catch((err) => setError(String(err)))
      .finally(() => mounted && setLoading(false));

    return () => { mounted = false; };
  }, [q, level, status, page]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2">
          <input placeholder="Search risks" value={q} onChange={(e)=>setQ(e.target.value)} className="rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-200" />
          <select value={level} onChange={(e)=>setLevel(e.target.value)} className="rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-200">
            <option value="">All levels</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
            <option value="Critical">Critical</option>
          </select>
          <select value={status} onChange={(e)=>setStatus(e.target.value)} className="rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-200">
            <option value="">All statuses</option>
            <option>Open</option>
            <option>In Progress</option>
            <option>Mitigated</option>
            <option>Accepted</option>
          </select>
        </div>

        <div>
          <Link href="/risks/new" className="rounded-2xl bg-slate-200 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-slate-300">Add Risk</Link>
        </div>
      </div>

      {loading ? (
        <div className="rounded-2xl bg-slate-900/50 p-6 text-center text-sm text-slate-300">Loading risks...</div>
      ) : error ? (
        <div className="rounded-2xl bg-rose-900/20 p-6 text-center text-sm text-rose-200">Error: {error}</div>
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/60">
          <table className="w-full table-auto">
            <thead className="bg-slate-950/30">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">Title</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">Level</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">Owner</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.map((r) => (
                <tr key={r.id} className="border-t border-slate-800">
                  <td className="px-4 py-3 text-sm text-slate-200">{r.title}</td>
                  <td className="px-4 py-3"><RiskLevelBadge level={r.level} /></td>
                  <td className="px-4 py-3 text-sm text-slate-300">{r.owner || '-'}</td>
                  <td className="px-4 py-3 text-sm text-slate-300">{r.status || '-'}</td>
                  <td className="px-4 py-3 text-sm text-slate-300"><Link href={`/risks/${r.id}`} className="text-sky-300 hover:underline">View</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="flex items-center justify-between">
        <div className="text-sm text-slate-400">Page {page} of {totalPages}</div>
        <div className="flex items-center gap-2">
          <button disabled={page<=1} onClick={()=>setPage(p=>Math.max(1,p-1))} className="rounded-md bg-slate-800 px-3 py-1 text-sm text-slate-200 disabled:opacity-40">Previous</button>
          <button disabled={page>=totalPages} onClick={()=>setPage(p=>Math.min(totalPages,p+1))} className="rounded-md bg-slate-800 px-3 py-1 text-sm text-slate-200 disabled:opacity-40">Next</button>
        </div>
      </div>
    </div>
  );
}
