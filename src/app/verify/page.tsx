"use client";

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { LogoFull } from "@/components/Logo";
import { ArrowLeft, MailCheck, RotateCcw, CheckCircle2, AlertCircle } from "lucide-react";
import { motion } from "framer-motion";

function VerifyContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const emailParam = searchParams?.get("email") || "operator@enterprise.cygrc.com";

  const [otp, setOtp] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [resendCooldown, setResendCooldown] = useState(0);
  const [resendNotice, setResendNotice] = useState(false);

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (resendCooldown > 0) {
      timer = setTimeout(() => setResendCooldown((prev) => prev - 1), 1000);
    }
    return () => clearTimeout(timer);
  }, [resendCooldown]);

  const handleVerify = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const cleanOtp = otp.trim().replace(/\s+/g, "");
    if (!cleanOtp) {
      setError("Please enter the 6-digit verification code.");
      return;
    }

    if (cleanOtp.length < 6) {
      setError("Verification code must be exactly 6 digits.");
      return;
    }

    setLoading(true);

    setTimeout(() => {
      // Mock successful verification & store demo session
      if (typeof window !== "undefined") {
        localStorage.setItem(
          "cygrc_user",
          JSON.stringify({
            email: emailParam,
            role: "Security Administrator",
            verified: true,
          })
        );
        localStorage.setItem("cygrc_token", "demo-token-verified-access");
      }
      setLoading(false);
      router.push("/dashboard");
    }, 700);
  };

  const handleResend = () => {
    if (resendCooldown > 0) return;
    setResendNotice(true);
    setResendCooldown(30);
    setTimeout(() => setResendNotice(false), 5000);
  };

  return (
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
          We sent a one-time password to{" "}
          <span className="font-semibold text-slate-700 dark:text-slate-200">
            {emailParam}
          </span>
          . Enter the 6-digit code below to securely verify your CyGRC account.
        </p>
      </div>

      {/* Error / Resend Alerts */}
      {error && (
        <div className="mb-5 flex items-center gap-2.5 rounded-xl border border-rose-500/30 bg-rose-500/10 p-3.5 text-xs text-rose-500 dark:text-rose-400">
          <AlertCircle size={16} className="shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {resendNotice && (
        <div className="mb-5 flex items-center gap-2.5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3.5 text-xs text-emerald-600 dark:text-emerald-400">
          <CheckCircle2 size={16} className="shrink-0" />
          <span>A fresh 6-digit verification code has been dispatched to {emailParam}.</span>
        </div>
      )}

      {/* OTP Form */}
      <form onSubmit={handleVerify} className="space-y-5">
        <div>
          <label className="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">
            One-time password
          </label>

          <input
            type="text"
            inputMode="numeric"
            maxLength={6}
            value={otp}
            onChange={(e) => {
              const val = e.target.value.replace(/\D/g, "");
              setOtp(val);
              if (error) setError("");
            }}
            placeholder="000000"
            className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-4 text-center text-2xl font-bold tracking-[0.5em] text-slate-900 outline-none transition placeholder:tracking-normal placeholder:text-slate-400 focus:border-violet-500 focus:ring-4 focus:ring-violet-500/10 dark:border-slate-700 dark:bg-slate-900 dark:text-white dark:placeholder:text-slate-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-6 py-4 text-sm font-bold text-white shadow-lg shadow-violet-500/20 transition hover:-translate-y-0.5 hover:from-violet-700 hover:to-indigo-700 disabled:opacity-50"
        >
          {loading ? "Verifying Credentials..." : "Verify Account"}
        </button>
      </form>

      {/* Resend */}
      <div className="mt-6 flex flex-col items-center justify-between gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 sm:flex-row dark:border-slate-800 dark:bg-slate-900/60">
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Didn't receive the code?
        </p>

        <button
          type="button"
          onClick={handleResend}
          disabled={resendCooldown > 0}
          className="inline-flex items-center gap-2 rounded-xl border border-violet-200 bg-white px-4 py-2 text-sm font-semibold text-violet-600 transition hover:bg-violet-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-violet-900/50 dark:bg-slate-950 dark:text-violet-400 dark:hover:bg-violet-950/30"
        >
          <RotateCcw size={15} />
          {resendCooldown > 0 ? `Resend code (${resendCooldown}s)` : "Resend code"}
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
  );
}

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
          <Suspense
            fallback={
              <div className="rounded-[2rem] border border-slate-800 bg-slate-950 p-10 text-center text-slate-400">
                Loading verification portal...
              </div>
            }
          >
            <VerifyContent />
          </Suspense>
        </motion.div>
      </div>
    </main>
  );
}