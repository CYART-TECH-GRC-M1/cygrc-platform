"use client";
import React, { useEffect, useState } from "react";
import Sidebar from "../../../components/ui/Sidebar";
import TopNav from "../../../components/ui/TopNav";
import RiskForm from "../../../components/risks/RiskForm";
import { useParams, useRouter } from "next/navigation";

export default function RiskDetailsPage() {
  const params = useParams();
  const id = params?.id;
  const router = useRouter();
  const [initial, setInitial] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    fetch(`/api/risks/${id}`).then(r=>r.json()).then(json=>setInitial(json.data)).catch(e=>setError(String(e))).finally(()=>setLoading(false));
  }, [id]);

  async function onDelete() {
    if (!id) return;
    if (!confirm('Delete this risk?')) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/risks/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Delete failed');
      router.push('/risks');
    } catch (err:any) { setError(err?.message || 'Unexpected error'); } finally { setLoading(false); }
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
                <div className="rounded-2xl bg-slate-900/50 p-6 text-sm text-slate-300">Loading risk...</div>
              ) : error ? (
                <div className="rounded-2xl bg-rose-900/20 p-6 text-sm text-rose-200">{error}</div>
              ) : initial ? (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h1 className="text-2xl font-semibold text-white">{initial.title}</h1>
                    <div className="flex gap-2">
                      <button onClick={onDelete} className="rounded-2xl bg-rose-600 px-3 py-2 text-sm font-semibold text-white">Delete</button>
                    </div>
                  </div>

                  <div className="max-w-2xl">
                    <RiskForm initial={initial} />
                  </div>
                </div>
              ) : (
                <div className="text-sm text-slate-300">Risk not found</div>
              )}
            </main>
          </div>
        </div>
      </div>
    </div>
  );
}
