import Link from "next/link";

export default function ResourcesPage() {
  return (
    <main className="min-h-screen px-6 py-16 sm:px-10 lg:px-12">
      <div className="mx-auto max-w-6xl space-y-10">
        <div className="rounded-[1.75rem] border border-slate-800 bg-slate-950/95 p-10 shadow-[0_30px_60px_-30px_rgba(0,0,0,0.55)]">
          <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="uppercase tracking-[0.28em] text-xs font-semibold text-slate-400">Security resources</p>
              <h1 className="mt-3 text-4xl font-semibold tracking-tight text-white sm:text-5xl">Learn and respond smarter.</h1>
              <p className="mt-4 max-w-2xl text-slate-300">
                Explore guides, policies, and tools to improve your cybersecurity program.
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

        <section className="grid gap-6 lg:grid-cols-3">
          {[
            {
              title: "Incident playbook",
              description: "A structured process for triage, containment, and remediation.",
            },
            {
              title: "Threat modeling",
              description: "Understand your attack surface and prioritize protections.",
            },
            {
              title: "Security checklist",
              description: "Best practices for hardening systems and protecting critical data.",
            },
          ].map((resource) => (
            <article key={resource.title} className="rounded-3xl border border-slate-800 bg-slate-900 p-8">
              <h2 className="text-2xl font-semibold text-white">{resource.title}</h2>
              <p className="mt-4 text-slate-300">{resource.description}</p>
            </article>
          ))}
        </section>

        <section className="rounded-[1.75rem] border border-slate-800 bg-slate-950/95 p-10">
          <div className="space-y-6">
            <h2 className="text-3xl font-semibold text-white">Cybersecurity essentials</h2>
            <ul className="space-y-4 text-slate-300">
              <li className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                <p className="font-semibold text-white">Multi-factor authentication</p>
                <p className="mt-2 text-sm text-slate-400">Enable MFA everywhere to reduce account takeover risk.</p>
              </li>
              <li className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                <p className="font-semibold text-white">Security awareness</p>
                <p className="mt-2 text-sm text-slate-400">Train teams on phishing, social engineering, and secure habits.</p>
              </li>
              <li className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                <p className="font-semibold text-white">Update policies</p>
                <p className="mt-2 text-sm text-slate-400">Keep incident response and access policies current for rapid action.</p>
              </li>
            </ul>
          </div>
        </section>
      </div>
    </main>
  );
}
