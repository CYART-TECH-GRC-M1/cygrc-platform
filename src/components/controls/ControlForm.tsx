"use client";
import React, { useState } from "react";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import { useRouter } from "next/navigation";

export default function ControlForm({ initial }: { initial?: any }) {
  const router = useRouter();
  const [title, setTitle] = useState(initial?.title || '');
  const [description, setDescription] = useState(initial?.description || '');
  const [framework, setFramework] = useState(initial?.framework || 'NIST');
  const [status, setStatus] = useState(initial?.status || 'Planned');
  const [owner, setOwner] = useState(initial?.owner || '');
  const [evidenceCount, setEvidenceCount] = useState(initial?.evidenceCount || 0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!title) return setError('Title required');
    setLoading(true); setError(null);
    try {
      const res = await fetch('/api/controls', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ title, description, framework, status, owner, evidenceCount }) });
      if (!res.ok) throw new Error('Create failed');
      const json = await res.json();
      router.push(`/controls/${json.data.id}`);
    } catch (err:any) { setError(err?.message || 'Unexpected error'); } finally { setLoading(false); }
  }

  async function onUpdate(e: React.FormEvent) {
    e.preventDefault();
    if (!initial?.id) return;
    setLoading(true); setError(null);
    try {
      const res = await fetch(`/api/controls/${initial.id}`, { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ title, description, framework, status, owner, evidenceCount }) });
      if (!res.ok) throw new Error('Update failed');
      router.refresh();
    } catch (err:any) { setError(err?.message || 'Unexpected error'); } finally { setLoading(false); }
  }

  return (
    <form onSubmit={initial?.id ? onUpdate : onCreate} className="space-y-4">
      <Input label="Title" value={title} onChange={(e)=>setTitle(e.target.value)} />
      <label className="block text-sm text-slate-300">Description</label>
      <textarea value={description} onChange={(e)=>setDescription(e.target.value)} className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-slate-100" />

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        <div>
          <label className="block text-sm text-slate-300">Framework</label>
          <select value={framework} onChange={(e)=>setFramework(e.target.value)} className="mt-2 w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-slate-100">
            <option>NIST</option>
            <option>ISO</option>
            <option>PCI</option>
          </select>
        </div>
        <div>
          <label className="block text-sm text-slate-300">Status</label>
          <select value={status} onChange={(e)=>setStatus(e.target.value)} className="mt-2 w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-slate-100">
            <option>Implemented</option>
            <option>Planned</option>
            <option>Not Implemented</option>
            <option>Deprecated</option>
          </select>
        </div>
      </div>

      <Input label="Owner (email)" value={owner} onChange={(e)=>setOwner(e.target.value)} />
      <Input label="Evidence count" type="number" value={String(evidenceCount)} onChange={(e)=>setEvidenceCount(Number(e.target.value))} />

      {error && <p className="text-sm text-rose-400">{error}</p>}
      <div>
        <Button type="submit" loading={loading}>{initial?.id ? 'Save control' : 'Add control'}</Button>
      </div>
    </form>
  );
}
