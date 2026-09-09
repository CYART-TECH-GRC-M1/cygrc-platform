"use client";

const bars = [
  { label: "ISO", value: 92 },
  { label: "SOC 2", value: 87 },
  { label: "PCI", value: 81 },
  { label: "HIPAA", value: 78 },
];

export default function ComplianceChart() {
  return (
    <div className="rounded-[1.5rem] border border-[var(--border)] bg-[var(--surface)] p-6 shadow-[0_10px_30px_rgba(15,23,42,0.05)]">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Control coverage</h3>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Coverage across key compliance frameworks</p>
        </div>
        <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-sm font-semibold text-emerald-600 dark:text-emerald-300">Healthy</span>
      </div>
      <div className="mt-6 flex items-end gap-4">
        {bars.map((bar) => (
          <div key={bar.label} className="flex flex-1 flex-col items-center gap-3">
            <div className="flex h-40 w-full items-end rounded-2xl bg-slate-100 p-2 dark:bg-slate-900">
              <div className="w-full rounded-xl bg-gradient-to-t from-sky-600 to-emerald-500" style={{ height: `${bar.value}%` }} />
            </div>
            <div className="text-center">
              <div className="text-sm font-medium text-slate-900 dark:text-white">{bar.label}</div>
              <div className="text-xs text-slate-500 dark:text-slate-400">{bar.value}%</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
