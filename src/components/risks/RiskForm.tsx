"use client";
import React, { useState } from "react";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import { useRouter } from "next/navigation";

export default function RiskForm({ initial }: { initial?: any }) {
  const router = useRouter();
  const [title, setTitle] = useState(initial?.title || '');
  const [description, setDescription] = useState(initial?.description || '');
  const [level, setLevel] = useState(initial?.level || 'Low');
  const [owner, setOwner] = useState(initial?.owner || '');
  const [status, setStatus] = useState(initial?.status || 'Open');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!title) return setError('Title is required');
    setLoading(true);
    try {
      const res = await fetch('/api/risks', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title, description, level, owner, status }) });
      if (!res.ok) throw new Error('Create failed');
      const json = await res.json();
      router.push(`/risks/${json.data.id}`);
    } catch (err:any) {
      setError(err?.message || 'Unexpected error');
    } finally { setLoading(false); }
  }

  async function onUpdate(e: React.FormEvent) {
    e.preventDefault();
    if (!initial?.id) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/risks/${initial.id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title, description, level, owner, status }) });
      if (!res.ok) throw new Error('Update failed');
      const json = await res.json();
      router.refresh();
    } catch (err:any) {
      setError(err?.message || 'Unexpected error');
    } finally { setLoading(false); }
  }

  return (
    <form onSubmit={initial?.id ? onUpdate : onCreate} className="space-y-4">
      <Input label="Title" value={title} onChange={(e)=>setTitle(e.target.value)} />
      <label className="block text-sm text-slate-300">Description</label>
      <textarea value={description} onChange={(e)=>setDescription(e.target.value)} className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-slate-100" />

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        <div>
          <label className="block text-sm text-slate-300">Risk Level</label>
          <select value={level} onChange={(e)=>setLevel(e.target.value)} className="mt-2 w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-slate-100">
            <option>Low</option>
            <option>Medium</option>
            <option>High</option>
            <option>Critical</option>
          </select>
        </div>

        <div>
          <Input label="Risk Owner (email)" value={owner} onChange={(e)=>setOwner(e.target.value)} />
        </div>
      </div>

      <div>
        <label className="block text-sm text-slate-300">Status</label>
        <select value={status} onChange={(e)=>setStatus(e.target.value)} className="mt-2 w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-slate-100">
          <option>Open</option>
          <option>In Progress</option>
          <option>Mitigated</option>
          <option>Accepted</option>
        </select>
      </div>

      {error && <p className="text-sm text-rose-400">{error}</p>}
      <div>
        <Button type="submit" loading={loading}>{initial?.id ? 'Save changes' : 'Create risk'}</Button>
      </div>
    </form>
  );
}
