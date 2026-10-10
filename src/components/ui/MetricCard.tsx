"use client";
import React from "react";

type Props = {
  title: string;
  value: string | number;
  delta?: string;
  children?: React.ReactNode;
};

export default function MetricCard({ title, value, delta, children }: Props) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase text-slate-400">{title}</p>
          <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
        </div>
        {delta && <div className="rounded-md bg-slate-800/40 px-2 py-1 text-sm text-slate-200">{delta}</div>}
      </div>
      {children}
    </div>
  );
}
