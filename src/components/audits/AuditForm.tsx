"use client";
import React, { useState } from "react";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import { useRouter } from "next/navigation";

export default function AuditForm({ initial }: { initial?: any }) {
  const router = useRouter();
  const [title, setTitle] = useState(initial?.title || '');
  const [description, setDescription] = useState(initial?.description || '');
  const [auditor, setAuditor] = useState(initial?.auditor || '');
  const [dueDate, setDueDate] = useState(initial?.dueDate || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!title) return setError('Title is required');
    setLoading(true);
    try {
      const res = await fetch('/api/audits', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title, description, auditor, dueDate }) });
      if (!res.ok) throw new Error('Failed to create');
      const json = await res.json();
      router.push(`/audits/${json.data.id}`);
    } catch (err: any) {
      setError(err?.message || 'Unexpected error');
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <Input label="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
      <label className="block text-sm text-slate-300">Description</label>
      <textarea value={description} onChange={(e) => setDescription(e.target.value)} className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-slate-100" />

      <Input label="Assign auditor (email)" value={auditor} onChange={(e) => setAuditor(e.target.value)} />
      <label className="block text-sm text-slate-300">Due date</label>
      <input type="date" value={dueDate} onChange={(e)=>setDueDate(e.target.value)} className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-slate-100" />

      {error && <p className="text-sm text-rose-400">{error}</p>}
      <div>
        <Button type="submit" loading={loading}>Create Audit</Button>
      </div>
    </form>
  );
}
