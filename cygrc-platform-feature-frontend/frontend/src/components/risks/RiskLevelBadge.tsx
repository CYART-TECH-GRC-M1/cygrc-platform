"use client";
import React from "react";

export default function RiskLevelBadge({ level }: { level: string }) {
  const base = "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium";
  switch (level) {
    case 'Low':
      return <span className={base + ' bg-emerald-800/10 text-emerald-300 border border-emerald-700'}>{level}</span>;
    case 'Medium':
      return <span className={base + ' bg-amber-800/10 text-amber-300 border border-amber-700'}>{level}</span>;
    case 'High':
      return <span className={base + ' bg-rose-700/10 text-rose-300 border border-rose-700'}>{level}</span>;
    default:
      return <span className={base + ' bg-rose-900/10 text-rose-300 border border-rose-700'}>{level}</span>;
  }
}
