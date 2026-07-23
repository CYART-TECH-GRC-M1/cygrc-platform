"use client";
import React, { useEffect, useState } from "react";
import FileIcon from "./FileIcon";

type Item = { id: string; name: string; type: string; size: number; createdAt: string };

export default function EvidenceTable() {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [q, setQ] = useState('');

  async function load() {
    setLoading(true); setError(null);
    try {
      const res = await fetch(`/api/evidence?q=${encodeURIComponent(q)}`);
      const json = await res.json();
      setItems(json.data || []);
    } catch (err:any) { setError(String(err)); }
    setLoading(false);
  }

  useEffect(()=>{ load(); }, [q]);

  async function preview(id: string) {
    const res = await fetch(`/api/evidence/${id}`);
    const json = await res.json();
    const dataUrl = json.data?.dataUrl;
    if (dataUrl) {
      const w = window.open();
      if (w) w.document.write(`<iframe src="${dataUrl}" style="width:100%;height:100%;border:0"></iframe>`);
    }
  }

  async function download(item: Item) {
    const res = await fetch(`/api/evidence/${item.id}`);
    const json = await res.json();
    const dataUrl = json.data?.dataUrl;
    if (!dataUrl) return;
    const a = document.createElement('a');
    a.href = dataUrl;
    a.download = item.name;
    document.body.appendChild(a);
    a.click();
    a.remove();
  }

  async function remove(id: string) {
    if (!confirm('Delete evidence?')) return;
    try {
      const res = await fetch(`/api/evidence/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Delete failed');
      setItems((s)=>s.filter(i=>i.id!==id));
    } catch (err:any) { alert(String(err)); }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <input placeholder="Search evidence" value={q} onChange={(e)=>setQ(e.target.value)} className="rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-200" />
      </div>

      {loading ? <div className="rounded-2xl bg-slate-900/50 p-6 text-sm text-slate-300">Loading...</div> : error ? <div className="rounded-2xl bg-rose-900/20 p-6 text-sm text-rose-200">{error}</div> : (
        <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/60">
          <table className="w-full table-auto">
            <thead className="bg-slate-950/30">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">File</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">Size</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">Uploaded</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map(i => (
                <tr key={i.id} className="border-t border-slate-800">
                  <td className="px-4 py-3 text-sm text-slate-200 flex items-center gap-3"><FileIcon name={i.name} />{i.name}</td>
                  <td className="px-4 py-3 text-sm text-slate-300">{(i.size/1024).toFixed(1)} KB</td>
                  <td className="px-4 py-3 text-sm text-slate-300">{new Date(i.createdAt).toLocaleString()}</td>
                  <td className="px-4 py-3 text-sm text-slate-300 flex gap-2">
                    <button onClick={()=>preview(i.id)} className="rounded px-3 py-1 text-sm bg-slate-800 text-slate-200">Preview</button>
                    <button onClick={()=>download(i)} className="rounded px-3 py-1 text-sm bg-slate-800 text-slate-200">Download</button>
                    <button onClick={()=>remove(i.id)} className="rounded px-3 py-1 text-sm bg-rose-700 text-white">Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
