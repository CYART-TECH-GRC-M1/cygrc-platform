import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen px-6 py-16 sm:px-10 lg:px-12">
      <div className="mx-auto max-w-6xl space-y-10">
        <section className="overflow-hidden rounded-[2rem] border border-[var(--border)] bg-[var(--surface)] p-8 shadow-[0_20px_70px_rgba(15,23,42,0.08)] sm:p-10 lg:p-12 dark:shadow-[0_20px_70px_rgba(2,8,23,0.35)]">
          <div className="grid gap-10 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
            <div className="space-y-6">
              <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-slate-600 dark:border-slate-800 dark:bg-slate-900/70 dark:text-slate-300">
                Enterprise GRC platform
              </div>
              <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl dark:text-white">
                Govern risk, evidence, and compliance with clarity.
              </h1>
              <p className="max-w-2xl text-base leading-8 text-slate-600 dark:text-slate-300">
                A modern control center for audit readiness, policy alignment, and response planning — built for security leaders who need calm execution at scale.
              </p>
              <div className="flex flex-wrap gap-3">
                <Link href="/dashboard" className="inline-flex items-center justify-center rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-700 dark:bg-slate-100 dark:text-slate-950 dark:hover:bg-slate-200">
                  Open console
                </Link>
                <Link href="/signup" className="inline-flex items-center justify-center rounded-2xl border border-slate-300 bg-white px-6 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-400 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900/60 dark:text-slate-100 dark:hover:bg-slate-800">
                  Request access
                </Link>
              </div>
            </div>
            <div className="rounded-[1.5rem] border border-[var(--border)] bg-slate-950 p-6 text-white shadow-inner dark:border-slate-800">
              <div className="rounded-[1.25rem] border border-slate-800 bg-slate-900/80 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-400">Current posture</p>
                    <p className="mt-2 text-3xl font-semibold text-white">Stable</p>
                  </div>
                  <div className="rounded-full bg-emerald-500/15 px-3 py-1 text-sm text-emerald-300">94% healthy</div>
                </div>
                <div className="mt-6 grid gap-4 sm:grid-cols-2">
                  <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                    <p className="text-sm text-slate-400">Open issues</p>
                    <p className="mt-2 text-3xl font-semibold text-white">7</p>
                  </div>
                  <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                    <p className="text-sm text-slate-400">Evidence ready</p>
                    <p className="mt-2 text-3xl font-semibold text-white">28</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-3">
          {[
            {
              title: "Threat intelligence",
              description: "Understand active risks with clear alerts and prioritized indicators.",
              href: "/risks",
            },
            {
              title: "Incident response",
              description: "Coordinate actions, assign owners, and close issues faster.",
              href: "/incidents",
            },
            {
              title: "Security resources",
              description: "Document policies, playbooks, and guidance for frontline teams.",
              href: "/resources",
            },
          ].map((card) => (
            <Link key={card.title} href={card.href} className="rounded-[1.5rem] border border-[var(--border)] bg-[var(--surface)] p-8 shadow-[0_10px_35px_rgba(15,23,42,0.05)] transition hover:-translate-y-1 hover:shadow-[0_15px_45px_rgba(15,23,42,0.09)]">
              <h2 className="text-2xl font-semibold text-slate-900 dark:text-white">{card.title}</h2>
              <p className="mt-4 text-slate-600 dark:text-slate-300">{card.description}</p>
            </Link>
          ))}
        </section>

        <section className="rounded-[2rem] border border-[var(--border)] bg-[var(--surface)] p-8 shadow-[0_10px_35px_rgba(15,23,42,0.05)] sm:p-10">
          <div className="grid gap-6 lg:grid-cols-[1.1fr_0.45fr_0.45fr]">
            <div>
              <h2 className="text-3xl font-semibold text-slate-900 dark:text-white">Designed for leadership and operators</h2>
              <p className="mt-4 text-slate-600 dark:text-slate-300">
                The experience balances executive reporting with practical operational detail, giving teams a clearer path to decisions and follow-through.
              </p>
            </div>
            <Link href="/dashboard" className="rounded-[1.5rem] border border-[var(--border)] bg-slate-50 p-6 transition hover:bg-slate-100 dark:bg-slate-900/70 dark:hover:bg-slate-800">
              <p className="font-semibold text-slate-900 dark:text-white">Executive dashboard</p>
              <p className="mt-3 text-sm text-slate-600 dark:text-slate-400">Monitor metrics, controls, and risk posture from one view.</p>
            </Link>
            <Link href="/incidents" className="rounded-[1.5rem] border border-[var(--border)] bg-slate-50 p-6 transition hover:bg-slate-100 dark:bg-slate-900/70 dark:hover:bg-slate-800">
              <p className="font-semibold text-slate-900 dark:text-white">Incident response</p>
              <p className="mt-3 text-sm text-slate-600 dark:text-slate-400">Review active cases and coordinate response activities with clarity.</p>
            </Link>
          </div>
        </section>
      </div>
    </main>
  );
}
