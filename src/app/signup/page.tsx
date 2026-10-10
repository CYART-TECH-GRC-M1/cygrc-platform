"use client";

import Link from "next/link";
import { useState } from "react";
import {
  ArrowRight,
  CheckCircle2,
  Eye,
  EyeOff,
  Fingerprint,
  LockKeyhole,
  Mail,
  ShieldCheck,
  User,
  Zap,
} from "lucide-react";

export default function SignUpPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false);

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#050302] text-white">
      {/* =========================================================
          CYBER BACKGROUND
      ========================================================== */}

      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        {/* Main orange glow */}
        <div className="absolute left-1/2 top-[25%] h-[500px] w-[800px] -translate-x-1/2 rounded-full bg-orange-600/10 blur-[150px]" />

        {/* Green glow */}
        <div className="absolute right-[-180px] top-[35%] h-[500px] w-[500px] rounded-full bg-emerald-500/10 blur-[130px]" />

        {/* Orange glow left */}
        <div className="absolute bottom-[-200px] left-[-150px] h-[500px] w-[500px] rounded-full bg-orange-500/10 blur-[140px]" />

        {/* Grid */}
        <div
          className="absolute inset-0 opacity-[0.12]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,120,0,0.25) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,120,0,0.25) 1px, transparent 1px)
            `,
            backgroundSize: "55px 55px",
          }}
        />

        {/* Scan line */}
        <div className="cyber-scan absolute left-0 top-0 h-px w-full bg-gradient-to-r from-transparent via-orange-500/70 to-transparent" />

        {/* Moving horizontal lines */}
        <div className="absolute left-0 top-[35%] h-px w-full bg-gradient-to-r from-transparent via-orange-500/20 to-transparent" />

        <div className="absolute left-0 top-[70%] h-px w-full bg-gradient-to-r from-transparent via-emerald-500/10 to-transparent" />

        {/* Particles */}
        <div className="cyber-particle absolute left-[12%] top-[22%] h-1 w-1 rounded-full bg-orange-400 shadow-[0_0_12px_#ff7800]" />

        <div className="cyber-particle-delay absolute left-[20%] top-[65%] h-1 w-1 rounded-full bg-emerald-400 shadow-[0_0_12px_#00ff88]" />

        <div className="cyber-particle absolute right-[18%] top-[20%] h-1 w-1 rounded-full bg-orange-400 shadow-[0_0_12px_#ff7800]" />

        <div className="cyber-particle-delay absolute right-[12%] top-[72%] h-1 w-1 rounded-full bg-green-400 shadow-[0_0_12px_#00ff88]" />

        <div className="cyber-particle absolute left-[7%] top-[48%] h-1.5 w-1.5 rounded-full bg-orange-500 shadow-[0_0_16px_#ff7800]" />

        <div className="cyber-particle-delay absolute right-[7%] top-[45%] h-1.5 w-1.5 rounded-full bg-emerald-400 shadow-[0_0_16px_#00ff88]" />

        {/* Radar rings */}
        <div className="absolute left-[8%] top-[35%] h-32 w-32 rounded-full border border-orange-500/10" />

        <div className="absolute left-[8%] top-[35%] h-20 w-20 translate-x-6 translate-y-6 rounded-full border border-orange-500/10" />

        <div className="absolute right-[5%] bottom-[15%] h-40 w-40 rounded-full border border-emerald-500/10" />

        <div className="absolute right-[5%] bottom-[15%] h-24 w-24 translate-x-8 translate-y-8 rounded-full border border-emerald-500/10" />
      </div>

      {/* =========================================================
          TOP SYSTEM BAR
      ========================================================== */}

      <header className="relative z-20 border-b border-orange-500/10 bg-black/40 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5 sm:px-8">
          {/* Logo */}
          <Link
            href="/"
            className="group flex items-center gap-3"
          >
            <div className="relative flex h-9 w-9 items-center justify-center rounded-full border border-orange-500/50 bg-orange-500/5">
              <ShieldCheck
                size={18}
                className="text-orange-400 transition group-hover:text-emerald-400"
              />

              <span className="absolute inset-0 rounded-full border border-orange-500/20 animate-ping" />
            </div>

            <div>
              <div className="font-mono text-sm font-medium tracking-[0.35em] text-white">
                CYGRC
              </div>

              <div className="font-mono text-[8px] tracking-[0.25em] text-orange-500/70">
                SECURITY ECOSYSTEM
              </div>
            </div>
          </Link>

          {/* System status */}
          <div className="hidden items-center gap-6 font-mono text-[9px] uppercase tracking-[0.25em] text-slate-500 sm:flex">
            <span>
              SYSTEM_STATUS:
              <span className="ml-2 text-emerald-400">
                ONLINE
              </span>
            </span>

            <span>
              ENCRYPTION:
              <span className="ml-2 text-orange-400">
                ACTIVE
              </span>
            </span>
          </div>

          {/* Existing user */}
          <Link
            href="/login"
            className="group flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.2em] text-slate-400 transition hover:text-orange-400"
          >
            Existing user

            <ArrowRight
              size={13}
              className="transition group-hover:translate-x-1"
            />
          </Link>
        </div>
      </header>

      {/* =========================================================
          MAIN
      ========================================================== */}

      <section className="relative z-10 flex min-h-[calc(100vh-64px)] items-center justify-center px-5 py-12 sm:px-8">
        <div className="grid w-full max-w-6xl items-center gap-16 lg:grid-cols-[0.9fr_1fr]">
          {/* =====================================================
              LEFT CONTENT
          ====================================================== */}

          <div className="hidden lg:block">
            <div className="mb-6 flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.3em] text-orange-500">
              <span className="h-2 w-2 animate-pulse rounded-full bg-orange-500 shadow-[0_0_12px_#ff7800]" />

              SYSTEM_PROTOCOL_HARDENED
            </div>

            <h1 className="max-w-xl text-6xl font-extralight leading-[1.05] tracking-[-0.04em] text-white xl:text-7xl">
              BUILD YOUR

              <span className="block bg-gradient-to-r from-orange-400 via-yellow-300 to-emerald-400 bg-clip-text text-transparent">
                SECURITY
              </span>

              <span className="block">
                COMMAND CENTER.
              </span>
            </h1>

            <p className="mt-7 max-w-lg font-mono text-sm leading-7 text-slate-500">
              Establish your secure enterprise identity and
              gain access to governance, risk, compliance,
              audit and security operations.
            </p>

            {/* System information */}
            <div className="mt-10 space-y-4">
              <SystemLine
                number="01"
                title="IDENTITY"
                text="Secure enterprise authentication"
              />

              <SystemLine
                number="02"
                title="GOVERNANCE"
                text="Centralized GRC operations"
              />

              <SystemLine
                number="03"
                title="PROTECTION"
                text="Continuous security monitoring"
              />
            </div>

            <div className="mt-10 flex items-center gap-3 font-mono text-[9px] uppercase tracking-[0.25em] text-slate-600">
              <span className="text-emerald-400">
                ●
              </span>

              NETWORK_SECURE

              <span className="mx-2 text-slate-800">
                /
              </span>

              TLS_1.3

              <span className="mx-2 text-slate-800">
                /
              </span>

              ZERO_TRUST
            </div>
          </div>

          {/* =====================================================
              SIGNUP PANEL
          ====================================================== */}

          <div className="relative mx-auto w-full max-w-xl">
            {/* Outer glow */}
            <div className="absolute -inset-5 rounded-[2rem] bg-gradient-to-r from-orange-500/10 via-yellow-500/5 to-emerald-500/10 blur-2xl" />

            {/* Panel */}
            <div className="relative overflow-hidden rounded-[1.5rem] border border-orange-500/20 bg-[#090604]/90 shadow-[0_30px_100px_rgba(0,0,0,0.65)] backdrop-blur-2xl">
              {/* Top accent */}
              <div className="h-px w-full bg-gradient-to-r from-transparent via-orange-500 to-transparent" />

              {/* Corner decorations */}
              <div className="absolute left-0 top-0 h-8 w-8 border-l border-t border-orange-500/50" />

              <div className="absolute right-0 top-0 h-8 w-8 border-r border-t border-orange-500/50" />

              <div className="absolute bottom-0 left-0 h-8 w-8 border-b border-l border-emerald-500/30" />

              <div className="absolute bottom-0 right-0 h-8 w-8 border-b border-r border-emerald-500/30" />

              <div className="p-7 sm:p-10">
                {/* =================================================
                    PANEL HEADER
                ================================================== */}

                <div className="mb-8">
                  <div className="mb-4 flex items-center justify-between">
                    <div className="flex items-center gap-3 font-mono text-[9px] uppercase tracking-[0.25em] text-orange-500">
                      <Zap size={13} />

                      INITIALIZE_IDENTITY
                    </div>

                    <span className="font-mono text-[8px] tracking-[0.2em] text-slate-600">
                      001 / 003
                    </span>
                  </div>

                  <h2 className="text-3xl font-extralight tracking-tight text-white sm:text-4xl">
                    Create your{" "}
                    <span className="bg-gradient-to-r from-orange-400 to-emerald-400 bg-clip-text text-transparent">
                      account.
                    </span>
                  </h2>

                  <p className="mt-3 font-mono text-xs leading-6 text-slate-500">
                    REGISTER A SECURE ENTERPRISE IDENTITY TO
                    ACCESS THE CYGRC SECURITY ECOSYSTEM.
                  </p>
                </div>

                {/* =================================================
                    FORM
                ================================================== */}

                <form className="space-y-5">
                  {/* Full name */}
                  <CyberInput
                    label="FULL_NAME"
                    placeholder="Enter your full name"
                    icon={<User size={16} />}
                    type="text"
                  />

                  {/* Email */}
                  <CyberInput
                    label="EMAIL_ADDRESS"
                    placeholder="operator@company.com"
                    icon={<Mail size={16} />}
                    type="email"
                  />

                  {/* =================================================
                      PASSWORD
                  ================================================== */}

                  <div>
                    <label className="mb-2 flex items-center justify-between font-mono text-[9px] uppercase tracking-[0.2em] text-slate-500">
                      <span>PASSWORD</span>

                      <span className="text-orange-500/60">
                        REQUIRED
                      </span>
                    </label>

                    <div className="relative">
                      <LockKeyhole
                        size={16}
                        className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-600"
                      />

                      <input
                        type={
                          showPassword
                            ? "text"
                            : "password"
                        }
                        placeholder="Create secure password"
                        className="h-13 w-full rounded-xl border border-slate-800 bg-black/40 pl-11 pr-12 font-mono text-sm text-white outline-none transition placeholder:text-slate-700 focus:border-orange-500/60 focus:bg-orange-500/[0.03] focus:ring-1 focus:ring-orange-500/20"
                      />

                      <button
                        type="button"
                        onClick={() =>
                          setShowPassword(
                            !showPassword
                          )
                        }
                        aria-label={
                          showPassword
                            ? "Hide password"
                            : "Show password"
                        }
                        className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg p-2 text-slate-600 transition hover:bg-white/5 hover:text-orange-400"
                      >
                        {showPassword ? (
                          <EyeOff size={16} />
                        ) : (
                          <Eye size={16} />
                        )}
                      </button>
                    </div>

                    {/* Strength */}
                    <div className="mt-2 flex gap-1">
                      <span className="h-1 flex-1 rounded-full bg-orange-500" />

                      <span className="h-1 flex-1 rounded-full bg-orange-500/60" />

                      <span className="h-1 flex-1 rounded-full bg-slate-800" />

                      <span className="h-1 flex-1 rounded-full bg-slate-800" />
                    </div>

                    <p className="mt-2 font-mono text-[8px] uppercase tracking-[0.15em] text-slate-600">
                      PASSWORD_SECURITY_LEVEL: MEDIUM
                    </p>
                  </div>

                  {/* =================================================
                      CONFIRM PASSWORD
                  ================================================== */}

                  <div>
                    <label className="mb-2 block font-mono text-[9px] uppercase tracking-[0.2em] text-slate-500">
                      CONFIRM_PASSWORD
                    </label>

                    <div className="relative">
                      <LockKeyhole
                        size={16}
                        className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-600"
                      />

                      <input
                        type={
                          showConfirmPassword
                            ? "text"
                            : "password"
                        }
                        placeholder="Repeat secure password"
                        className="h-13 w-full rounded-xl border border-slate-800 bg-black/40 pl-11 pr-12 font-mono text-sm text-white outline-none transition placeholder:text-slate-700 focus:border-emerald-500/60 focus:bg-emerald-500/[0.03] focus:ring-1 focus:ring-emerald-500/20"
                      />

                      <button
                        type="button"
                        onClick={() =>
                          setShowConfirmPassword(
                            !showConfirmPassword
                          )
                        }
                        aria-label={
                          showConfirmPassword
                            ? "Hide confirm password"
                            : "Show confirm password"
                        }
                        className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg p-2 text-slate-600 transition hover:bg-white/5 hover:text-emerald-400"
                      >
                        {showConfirmPassword ? (
                          <EyeOff size={16} />
                        ) : (
                          <Eye size={16} />
                        )}
                      </button>
                    </div>
                  </div>

                  {/* =================================================
                      AGREEMENT
                  ================================================== */}

                  <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-slate-800/70 bg-white/[0.015] p-4 transition hover:border-orange-500/20">
                    <input
                      type="checkbox"
                      className="mt-0.5 h-4 w-4 accent-orange-500"
                    />

                    <span className="font-mono text-[9px] leading-5 tracking-[0.08em] text-slate-600">
                      I AGREE TO THE CYGRC SECURITY POLICY
                      AND ENTERPRISE TERMS OF SERVICE.
                    </span>
                  </label>

                  {/* =================================================
                      SUBMIT
                  ================================================== */}

                  <button
                    type="submit"
                    className="group relative flex h-14 w-full items-center justify-center gap-3 overflow-hidden rounded-xl bg-gradient-to-r from-orange-500 via-orange-400 to-emerald-500 font-mono text-xs font-bold uppercase tracking-[0.2em] text-black shadow-[0_0_35px_rgba(255,120,0,0.18)] transition duration-300 hover:shadow-[0_0_45px_rgba(255,120,0,0.32)]"
                  >
                    <span className="absolute inset-0 -translate-x-full bg-white/20 transition duration-700 group-hover:translate-x-full" />

                    <span className="relative">
                      Initialize Account
                    </span>

                    <ArrowRight
                      size={17}
                      className="relative transition-transform group-hover:translate-x-1"
                    />
                  </button>
                </form>

                {/* =================================================
                    BIOMETRIC / FINGERPRINT AUTHENTICATION
                ================================================== */}

                <div className="my-7 flex items-center gap-4">
                  <div className="h-px flex-1 bg-slate-800" />

                  <span className="font-mono text-[8px] uppercase tracking-[0.2em] text-slate-700">
                    OR SECURE BIOMETRICS
                  </span>

                  <div className="h-px flex-1 bg-slate-800" />
                </div>

                <button
                  type="button"
                  className="group relative flex w-full items-center justify-center gap-3 overflow-hidden rounded-xl border border-slate-800 bg-black/30 px-5 py-3.5 font-mono text-[9px] uppercase tracking-[0.18em] text-slate-500 transition duration-300 hover:border-orange-500/50 hover:bg-orange-500/[0.04] hover:text-orange-400"
                >
                  {/* Hover glow */}
                  <span className="pointer-events-none absolute inset-0 bg-gradient-to-r from-orange-500/0 via-orange-500/[0.06] to-emerald-500/0 opacity-0 transition duration-300 group-hover:opacity-100" />

                  {/* Fingerprint icon */}
                  <span className="relative flex h-9 w-9 items-center justify-center rounded-lg border border-orange-500/20 bg-orange-500/[0.04] transition duration-300 group-hover:border-orange-500/50 group-hover:bg-orange-500/10">
                    <Fingerprint
                      size={21}
                      strokeWidth={1.8}
                      className="text-orange-500 transition duration-300 group-hover:scale-110 group-hover:text-emerald-400"
                    />

                    {/* Fingerprint pulse */}
                    <span className="absolute inset-0 rounded-lg border border-orange-500/0 transition duration-300 group-hover:border-orange-500/30" />
                  </span>

                  <span className="relative">
                    Continue with SSO / Biometrics
                  </span>

                  <ArrowRight
                    size={14}
                    className="relative text-slate-700 transition duration-300 group-hover:translate-x-1 group-hover:text-emerald-400"
                  />
                </button>

                {/* =================================================
                    SECURITY PROTOCOL
                ================================================== */}

                <div className="my-7 flex items-center gap-4">
                  <div className="h-px flex-1 bg-slate-800" />

                  <span className="font-mono text-[8px] uppercase tracking-[0.2em] text-slate-700">
                    SECURE PROTOCOL
                  </span>

                  <div className="h-px flex-1 bg-slate-800" />
                </div>

                {/* Security info */}
                <div className="grid grid-cols-2 gap-3">
                  <SecurityBadge
                    icon={<ShieldCheck size={15} />}
                    text="ZERO TRUST"
                  />

                  <SecurityBadge
                    icon={<CheckCircle2 size={15} />}
                    text="TLS 1.3"
                  />
                </div>

                {/* =================================================
                    LOGIN
                ================================================== */}

                <div className="mt-7 text-center">
                  <span className="font-mono text-[10px] uppercase tracking-[0.12em] text-slate-600">
                    ALREADY REGISTERED?
                  </span>

                  <Link
                    href="/login"
                    className="ml-2 font-mono text-[10px] uppercase tracking-[0.15em] text-orange-400 transition hover:text-emerald-400"
                  >
                    ACCESS SYSTEM →
                  </Link>
                </div>

                {/* =================================================
                    OTP
                ================================================== */}

                <div className="mt-5 border-t border-slate-800/70 pt-5 text-center">
                  <p className="font-mono text-[9px] uppercase tracking-[0.12em] text-slate-600">
                    EMAIL VERIFICATION REQUIRED AFTER
                    REGISTRATION
                  </p>

                  <Link
                    href="/verify"
                    className="mt-2 inline-block font-mono text-[9px] uppercase tracking-[0.15em] text-emerald-500 transition hover:text-emerald-400"
                  >
                    ENTER OTP →
                  </Link>
                </div>
              </div>
            </div>

            {/* Bottom system status */}
            <div className="mt-4 flex items-center justify-between px-2 font-mono text-[8px] uppercase tracking-[0.2em] text-slate-700">
              <span>
                AUTH_MODULE: ACTIVE
              </span>

              <span>
                STATUS:
                <span className="ml-1 text-emerald-500">
                  READY
                </span>
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================
          STYLES
      ========================================================== */}

      <style jsx global>{`
        @keyframes cyberScan {
          0% {
            transform: translateY(-100vh);
            opacity: 0;
          }

          10% {
            opacity: 1;
          }

          90% {
            opacity: 1;
          }

          100% {
            transform: translateY(100vh);
            opacity: 0;
          }
        }

        @keyframes cyberParticle {
          0%,
          100% {
            transform: translateY(0) scale(1);
            opacity: 0.4;
          }

          50% {
            transform: translateY(-25px) scale(1.8);
            opacity: 1;
          }
        }

        .cyber-scan {
          animation: cyberScan 7s linear infinite;
        }

        .cyber-particle {
          animation: cyberParticle 4s ease-in-out infinite;
        }

        .cyber-particle-delay {
          animation: cyberParticle 5s ease-in-out infinite;
          animation-delay: 1.5s;
        }
      `}</style>
    </main>
  );
}

/* ===============================================================
   SYSTEM LINE
================================================================ */

function SystemLine({
  number,
  title,
  text,
}: {
  number: string;
  title: string;
  text: string;
}) {
  return (
    <div className="group flex items-center gap-4 border-l border-orange-500/20 pl-4 transition hover:border-orange-500/70">
      <span className="font-mono text-[9px] text-orange-500/60">
        {number}
      </span>

      <div>
        <p className="font-mono text-[10px] tracking-[0.2em] text-slate-300">
          {title}
        </p>

        <p className="mt-1 font-mono text-[9px] text-slate-600">
          {text}
        </p>
      </div>
    </div>
  );
}

/* ===============================================================
   CYBER INPUT
================================================================ */

function CyberInput({
  label,
  placeholder,
  icon,
  type,
}: {
  label: string;
  placeholder: string;
  icon: React.ReactNode;
  type: string;
}) {
  return (
    <div>
      <label className="mb-2 block font-mono text-[9px] uppercase tracking-[0.2em] text-slate-500">
        {label}
      </label>

      <div className="relative">
        <div className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-600">
          {icon}
        </div>

        <input
          type={type}
          placeholder={placeholder}
          className="h-13 w-full rounded-xl border border-slate-800 bg-black/40 pl-11 pr-4 font-mono text-sm text-white outline-none transition placeholder:text-slate-700 focus:border-orange-500/60 focus:bg-orange-500/[0.03] focus:ring-1 focus:ring-orange-500/20"
        />

        <div className="pointer-events-none absolute right-4 top-1/2 h-1.5 w-1.5 -translate-y-1/2 rounded-full bg-orange-500/40" />
      </div>
    </div>
  );
}

/* ===============================================================
   SECURITY BADGE
================================================================ */

function SecurityBadge({
  icon,
  text,
}: {
  icon: React.ReactNode;
  text: string;
}) {
  return (
    <div className="flex items-center justify-center gap-2 rounded-lg border border-slate-800 bg-black/30 py-3 font-mono text-[8px] tracking-[0.18em] text-slate-600">
      <span className="text-emerald-500">
        {icon}
      </span>

      {text}
    </div>
  );
}