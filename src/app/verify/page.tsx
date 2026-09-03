"use client";

import Link from "next/link";
import { LogoFull } from "@/components/Logo";
import { ArrowLeft, MailCheck, RotateCcw } from "lucide-react";
import { motion } from "framer-motion";

export default function VerifyPage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-gradient-to-br from-violet-50 via-white to-indigo-50 px-4 py-10 sm:px-6 dark:from-slate-950 dark:via-slate-950 dark:to-indigo-950">

      {/* Background effects */}
      <div className="pointer-events-none absolute -left-32 -top-32 h-80 w-80 rounded-full bg-violet-400/20 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-32 -right-32 h-80 w-80 rounded-full bg-indigo-400/20 blur-3xl" />

      <div className="relative flex min-h-screen items-center justify-center">

        <motion.div
          initial={{ opacity: 0, y: 30, scale: 0.97 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-2xl"
        >
          <div className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white/95 p-6 shadow-[0_30px_80px_rgba(15,23,42,0.12)] backdrop-blur-xl sm:p-10 dark:border-slate-800 dark:bg-slate-950/95">

            {/* Header */}
            <div className="mb-10 flex items-center justify-between">
              <LogoFull />

              <Link
                href="/"
                className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-900"
              >
                <ArrowLeft size={16} />
                Home
              </Link>
            </div>

            {/* Icon */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{
                delay: 0.2,
                type: "spring",
                stiffness: 180,
              }}
              className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-500 via-purple-600 to-indigo-700 shadow-lg shadow-violet-500/25"
            >
              <MailCheck
                size={32}
                strokeWidth={2}
                className="text-white"
              />
            </motion.div>

            {/* Heading */}
            <div className="mb-8">
              <p className="text-sm font-semibold uppercase tracking-[0.25em] text-violet-600 dark:text-violet-400">
                Verify your account
              </p>

              <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl dark:text-white">
                Enter your verification code
              </h1>

              <p className="mt-3 max-w-xl leading-7 text-slate-500 dark:text-slate-400">
                We sent a one-time password to your email address.
                Enter the code below to securely verify your CyGRC account.
              </p>
            </div>

            {/* OTP Form */}
            <form className="space-y-5">

              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">
                  One-time password
                </label>

                <input
                  type="text"
                  inputMode="numeric"
                  maxLength={6}
                  placeholder="Enter 6-digit OTP"
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-4 text-center text-lg font-semibold tracking-[0.4em] text-slate-900 outline-none transition placeholder:tracking-normal placeholder:text-slate-400 focus:border-violet-500 focus:ring-4 focus:ring-violet-500/10 dark:border-slate-700 dark:bg-slate-900 dark:text-white dark:placeholder:text-slate-500"
                />
              </div>

              <button
                type="submit"
                className="w-full rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-6 py-4 text-sm font-bold text-white shadow-lg shadow-violet-500/20 transition hover:-translate-y-0.5 hover:from-violet-700 hover:to-indigo-700"
              >
                Verify account
              </button>
            </form>

            {/* Resend */}
            <div className="mt-6 flex flex-col items-center justify-between gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 sm:flex-row dark:border-slate-800 dark:bg-slate-900/60">
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Didn't receive the code?
              </p>

              <button
                type="button"
                className="inline-flex items-center gap-2 rounded-xl border border-violet-200 bg-white px-4 py-2 text-sm font-semibold text-violet-600 transition hover:bg-violet-50 dark:border-violet-900/50 dark:bg-slate-950 dark:text-violet-400 dark:hover:bg-violet-950/30"
              >
                <RotateCcw size={15} />
                Resend code
              </button>
            </div>

            {/* Footer */}
            <div className="mt-8 border-t border-slate-200 pt-6 text-center dark:border-slate-800">
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Your verification helps keep your CyGRC account secure.
              </p>

              <Link
                href="/login"
                className="mt-3 inline-block text-sm font-semibold text-violet-600 hover:text-violet-700 dark:text-violet-400"
              >
                Back to Sign in
              </Link>
            </div>

          </div>
        </motion.div>
      </div>
    </main>
  );
}