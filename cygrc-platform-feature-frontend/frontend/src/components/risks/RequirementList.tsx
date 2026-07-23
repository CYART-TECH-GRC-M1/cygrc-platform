type RequirementItem = {
  id: string;
  title: string;
  category: string;
  status: "Open" | "In Progress" | "Completed";
  owner: string;
  dueDate: string;
};

const requirements: RequirementItem[] = [
  {
    id: "req-1",
    title: "Multi-factor authentication for privileged accounts",
    category: "Access Control",
    status: "In Progress",
    owner: "Security Ops",
    dueDate: "Jul 30",
  },
  {
    id: "req-2",
    title: "Quarterly vulnerability review for internet-facing assets",
    category: "Vulnerability Management",
    status: "Open",
    owner: "IT Ops",
    dueDate: "Aug 12",
  },
  {
    id: "req-3",
    title: "Retention and backup validation for audit evidence",
    category: "Evidence Handling",
    status: "Completed",
    owner: "Compliance",
    dueDate: "Jul 20",
  },
];

function StatusBadge({ status }: { status: RequirementItem["status"] }) {
  const styles: Record<RequirementItem["status"], string> = {
    Open: "bg-amber-500/10 text-amber-300",
    "In Progress": "bg-sky-500/10 text-sky-300",
    Completed: "bg-emerald-500/10 text-emerald-300",
  };

  return <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${styles[status]}`}>{status}</span>;
}

export default function RequirementList() {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-white">Visible requirements</h2>
          <p className="mt-1 text-sm text-slate-400">Key compliance requirements and their current status.</p>
        </div>
        <span className="rounded-full bg-sky-500/10 px-3 py-1 text-sm text-sky-300">3 active items</span>
      </div>

      <div className="mt-4 grid gap-3 lg:grid-cols-2">
        {requirements.map((req) => (
          <div key={req.id} className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-sm font-medium text-white">{req.title}</p>
                <p className="mt-1 text-xs uppercase tracking-[0.24em] text-slate-500">{req.category}</p>
              </div>
              <StatusBadge status={req.status} />
            </div>
            <div className="mt-3 flex items-center justify-between text-sm text-slate-400">
              <span>{req.owner}</span>
              <span>Due {req.dueDate}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
