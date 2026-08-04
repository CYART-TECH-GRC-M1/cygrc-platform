import Link from "next/link";

export default function VerifyPage() {
  return (
    <main className="min-h-screen px-6 py-16 sm:px-10 lg:px-12">
      <div className="mx-auto flex min-h-[calc(100vh-96px)] max-w-3xl flex-col justify-center">
        <div className="rounded-[1.75rem] border border-slate-800 bg-slate-950/95 p-10 shadow-[0_30px_60px_-30px_rgba(0,0,0,0.55)]">
          <div className="mb-10">
            <p className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-400">
              Verify your account
            </p>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
              Enter the OTP sent to your email.
            </h1>
            <p className="mt-4 max-w-2xl text-slate-300">
              For security, we require one-time verification before granting access to CYGRC.
            </p>
          </div>

          <form className="space-y-6">
            <label className="block">
              <span className="text-sm font-medium text-slate-300">One-time password</span>
              <input
                type="text"
                placeholder="Enter OTP"
                className="mt-3 w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-slate-100 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-600/50"
              />
            </label>
            <button
              type="submit"
              className="inline-flex w-full items-center justify-center rounded-2xl bg-slate-100 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200"
            >
              Verify OTP
            </button>
          </form>

          <div className="mt-8 flex flex-col gap-3 border-t border-slate-800 pt-6 text-sm text-slate-400 sm:flex-row sm:items-center sm:justify-between">
            <p>Didn&apos;t receive a code?</p>
            <button className="inline-flex items-center justify-center rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm font-semibold text-slate-200 transition hover:border-slate-700 hover:bg-slate-800">
              Resend code
            </button>
          </div>

          <div className="mt-8 text-sm text-slate-400">
            <p>
              This is a static verification page. Connect the OTP field to your backend or authentication service for real verification.
            </p>
            <p className="mt-3">
              Return to{' '}
              <Link href="/" className="font-semibold text-slate-100 underline decoration-slate-700 hover:text-white">
                home
              </Link>
              .
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
