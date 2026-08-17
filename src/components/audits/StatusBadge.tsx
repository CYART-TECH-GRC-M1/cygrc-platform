"use client";
import React from "react";

export default function StatusBadge({ status }: { status: string }) {
  const base = "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium";
  if (status === 'Open') return <span className={base + ' bg-rose-600/10 text-rose-300 border border-rose-700'}>{status}</span>;
  if (status === 'In Progress') return <span className={base + ' bg-amber-600/10 text-amber-300 border border-amber-700'}>{status}</span>;
  return <span className={base + ' bg-emerald-600/10 text-emerald-300 border border-emerald-700'}>{status}</span>;
}
