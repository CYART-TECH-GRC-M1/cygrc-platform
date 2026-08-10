import Link from "next/link";

const roles = [
  {
    title: "Security Analyst",
    description: "Monitor threats, investigate alerts, and maintain incident response readiness.",
  },
  {
    title: "IT Administrator",
    description: "Manage access, configure systems, and enforce security policy across the environment.",
  },
  {
    title: "Executive",
    description: "Review security posture, approve response plans, and track program metrics.",
  },
];

export default function RolesPage() {
  return (
    <main className="min-h-screen px-6 py-16 sm:px-10 lg:px-12">
      <div className="mx-auto max-w-5xl space-y-10">
        <section className="rounded-[1.75rem] border border-slate-800 bg-slate-950/95 p-10 shadow-[0_30px_60px_-30px_rgba(0,0,0,0.55)]">
          <div className="space-y-4">
            <p className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-400">Sign up as</p>
            <h1 className="text-4xl font-semibold tracking-tight text-white">Choose the role that fits your team.</h1>
            <p className="max-w-2xl text-slate-300">
              Select a role to tailor CYGRC for your security or IT responsibilities.
            </p>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-3">
          {roles.map((role) => (
            <article key={role.title} className="rounded-3xl border border-slate-800 bg-slate-900 p-8 transition hover:border-slate-700 hover:bg-slate-950">
              <h2 className="text-2xl font-semibold text-white">{role.title}</h2>
              <p className="mt-4 text-slate-300">{role.description}</p>
              <div className="mt-6">
                <Link
                  href={`/signup?role=${encodeURIComponent(role.title)}`}
                  className="inline-flex rounded-2xl bg-slate-100 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200"
                >
                  Sign up as {role.title.split(" ")[0]}
                </Link>
              </div>
            </article>
          ))}
        </section>

        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 text-sm text-slate-400">
          <p>
            This page lets users choose a role before signup. You can use the selected role to customize onboarding or permissions.
          </p>
          <p className="mt-3">
            Return to{' '}
            <Link href="/signup" className="font-semibold text-slate-100 underline decoration-slate-700 hover:text-white">
              signup
            </Link>
            .
          </p>
        </div>
      </div>
    </main>
  );
}
