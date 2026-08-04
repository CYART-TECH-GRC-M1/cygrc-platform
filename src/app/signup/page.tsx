import Link from "next/link";

export default function SignUpPage() {
  return (
    <main className="min-h-screen px-6 py-16 sm:px-10 lg:px-12">
      <div className="mx-auto flex min-h-[calc(100vh-96px)] max-w-3xl flex-col justify-center">
        <div className="rounded-[1.75rem] border border-slate-800 bg-slate-950/95 p-10 shadow-[0_30px_60px_-30px_rgba(0,0,0,0.55)]">
          <div className="mb-10 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-400">
                Create account
              </p>
              <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                Join CYGRC for secure operations.
              </h1>
            </div>
            <div className="flex flex-col gap-3 sm:items-end">
              <Link
                href="/"
                className="inline-flex items-center justify-center rounded-2xl border border-slate-800 bg-slate-900 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:border-slate-700 hover:bg-slate-800"
              >
                Back home
              </Link>
              <Link
                href="/roles"
                className="inline-flex items-center justify-center rounded-2xl border border-slate-800 bg-slate-900 px-4 py-2 text-sm font-semibold text-slate-100 transition hover:border-slate-700 hover:bg-slate-800"
              >
                Choose your role
              </Link>
            </div>
          </div>

          <form className="space-y-6">
            <label className="block">
              <span className="text-sm font-medium text-slate-300">Full name</span>
              <input
                type="text"
                placeholder="Your name"
                className="mt-3 w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-slate-100 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-600/50"
              />
            </label>
            <label className="block">
              <span className="text-sm font-medium text-slate-300">Email address</span>
              <input
                type="email"
                placeholder="you@example.com"
                className="mt-3 w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-slate-100 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-600/50"
              />
            </label>
            <label className="block">
              <span className="text-sm font-medium text-slate-300">Password</span>
              <input
                type="password"
                placeholder="Choose a password"
                className="mt-3 w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-slate-100 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-600/50"
              />
            </label>
            <label className="block">
              <span className="text-sm font-medium text-slate-300">Re-enter password</span>
              <input
                type="password"
                placeholder="Confirm your password"
                className="mt-3 w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-slate-100 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-600/50"
              />
            </label>
            <button
              type="submit"
              className="inline-flex w-full items-center justify-center rounded-2xl bg-slate-100 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200"
            >
              Sign up
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-slate-300">
            <p>
              After signing up, enter the OTP sent to your email on the verification page.
            </p>
            <p className="mt-2">
              <Link href="/verify" className="font-semibold text-slate-100 underline decoration-slate-700 hover:text-white">
                Enter OTP
              </Link>
            </p>
          </div>

          <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6 text-sm text-slate-400">
            <p>
              This is a static sign-up page for the CYGRC portal. Replace the form handler with your signup or authentication integration.
            </p>
            <p className="mt-3">
              Already have an account?{' '}
              <Link href="/login" className="font-semibold text-slate-100 underline decoration-slate-700 hover:text-white">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
