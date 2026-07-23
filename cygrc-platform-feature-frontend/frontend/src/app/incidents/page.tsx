import Link from "next/link";

export default function IncidentsPage() {
  return (
    <main className="min-h-screen px-6 py-16 sm:px-10 lg:px-12">
      <div className="mx-auto max-w-6xl space-y-10">
        <div className="rounded-[1.75rem] border border-slate-800 bg-slate-950/95 p-10 shadow-[0_30px_60px_-30px_rgba(0,0,0,0.55)]">
          <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="uppercase tracking-[0.28em] text-xs font-semibold text-slate-400">Incident response</p>
              <h1 className="mt-3 text-4xl font-semibold tracking-tight text-white sm:text-5xl">Security incidents</h1>
              <p className="mt-4 max-w-2xl text-slate-300">
                Review active incidents, investigate alerts, and coordinate response actions with clarity.
              </p>
            </div>
            <Link
              href="/"
              className="inline-flex items-center justify-center rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm font-semibold text-slate-200 transition hover:border-slate-700 hover:bg-slate-800"
            >
              Back home
            </Link>
          </div>
        </div>

        <section className="rounded-[1.75rem] border border-slate-800 bg-slate-900 p-10">
          <div className="space-y-6">
            {[
              {
                status: "Active",
                title: "Unauthorized login detected",
                details: "Multiple failed sign-in attempts were blocked from an unknown IP address.",
                priority: "High",
              },
              {
                status: "Monitoring",
                title: "Potential data exfiltration",
                details: "Unusual outbound traffic patterns were flagged for review.",
                priority: "Medium",
              },
            ].map((incident, index) => (
              <article key={`${incident.title}-${index}`} className="rounded-3xl border border-slate-800 bg-slate-950 p-8">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <span className="rounded-full bg-slate-800 px-3 py-1 text-sm font-semibold text-slate-300">{incident.status}</span>
                  <span className="text-sm text-slate-400">Priority: {incident.priority}</span>
                </div>
                <h2 className="mt-4 text-2xl font-semibold text-white">{incident.title}</h2>
                <p className="mt-3 text-slate-300">{incident.details}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-3">
          {[
            { label: "Detection", value: "IDS & logs" },
            { label: "Response", value: "Actions assigned" },
            { label: "Records", value: "Compliance audit" },
          ].map((item) => (
            <div key={item.label} className="rounded-3xl border border-slate-800 bg-slate-900 p-6 text-slate-300">
              <p className="text-sm uppercase tracking-[0.24em] text-slate-400">{item.label}</p>
              <p className="mt-4 text-3xl font-semibold text-white">{item.value}</p>
            </div>
          ))}
        </section>
      </div>
    </main>
  );
}
