"use client";

import React from "react";
import {
  Building2,
  ShieldCheck,
  ChevronRight,
  Fingerprint,
  LockKeyhole,
  Bell,
  KeyRound,
} from "lucide-react";

export default function SettingsPage() {
  return (
    <main className="min-h-screen w-full bg-[#050504] px-4 py-6 text-white sm:px-6 lg:px-8">
      <div className="mx-auto w-full max-w-[1600px]">
        {/* PAGE HEADER */}
        <div className="mb-7">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 animate-pulse rounded-full bg-orange-500 shadow-[0_0_10px_#f97316]" />

            <span className="text-[10px] font-medium tracking-[0.22em] text-orange-500">
              SYSTEM_CONFIGURATION
            </span>
          </div>

          <h1 className="mt-2 text-2xl font-semibold tracking-tight text-white sm:text-3xl">
            Settings
          </h1>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-500">
            Administrators can manage organization preferences, identities,
            and integrations.
          </p>
        </div>

        <div className="w-full space-y-6">
          {/* SETTINGS OVERVIEW */}
          <div className="grid w-full gap-4 md:grid-cols-2">
            {/* ORGANIZATION PROFILE */}
            <section className="group relative w-full overflow-hidden rounded-2xl border border-orange-500/15 bg-[#080807] p-5 transition-all duration-300 hover:border-orange-500/40 hover:shadow-[0_0_30px_rgba(249,115,22,0.08)]">
              <div className="pointer-events-none absolute -right-16 -top-16 h-32 w-32 rounded-full bg-orange-500/10 blur-3xl transition-all duration-500 group-hover:bg-orange-500/20" />

              <div className="relative flex items-start justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-orange-500/20 bg-orange-500/10 text-orange-400">
                    <Building2 size={20} strokeWidth={1.6} />
                  </div>

                  <div>
                    <h2 className="text-lg font-semibold text-white">
                      Organization profile
                    </h2>

                    <p className="mt-1 text-sm text-zinc-500">
                      Organization and operational information
                    </p>
                  </div>
                </div>

                <ChevronRight
                  size={18}
                  className="shrink-0 text-zinc-700 transition-all duration-300 group-hover:translate-x-1 group-hover:text-orange-400"
                />
              </div>

              <div className="relative mt-5 border-t border-orange-500/10 pt-4">
                <p className="text-sm leading-6 text-zinc-500">
                  Define the operational context for policy ownership,
                  regional oversight, and audit scope.
                </p>

                <div className="mt-4 flex items-center gap-2 text-[10px] tracking-[0.15em] text-orange-500">
                  <span className="h-1.5 w-1.5 rounded-full bg-orange-500 shadow-[0_0_8px_#f97316]" />
                  ORGANIZATION_CONFIG
                </div>
              </div>
            </section>

            {/* SECURITY CONTROLS */}
            <section className="group relative w-full overflow-hidden rounded-2xl border border-emerald-500/15 bg-[#080807] p-5 transition-all duration-300 hover:border-emerald-500/40 hover:shadow-[0_0_30px_rgba(16,185,129,0.08)]">
              <div className="pointer-events-none absolute -right-16 -top-16 h-32 w-32 rounded-full bg-emerald-500/10 blur-3xl transition-all duration-500 group-hover:bg-emerald-500/20" />

              <div className="relative flex items-start justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-emerald-500/20 bg-emerald-500/10 text-emerald-400">
                    <ShieldCheck size={20} strokeWidth={1.6} />
                  </div>

                  <div>
                    <h2 className="text-lg font-semibold text-white">
                      Security controls
                    </h2>

                    <p className="mt-1 text-sm text-zinc-500">
                      Authentication and security preferences
                    </p>
                  </div>
                </div>

                <ChevronRight
                  size={18}
                  className="shrink-0 text-zinc-700 transition-all duration-300 group-hover:translate-x-1 group-hover:text-emerald-400"
                />
              </div>

              <div className="relative mt-5 border-t border-emerald-500/10 pt-4">
                <p className="text-sm leading-6 text-zinc-500">
                  Configure SSO, session policies, MFA, notification routing,
                  and API retention.
                </p>

                <div className="mt-4 flex items-center gap-2 text-[10px] tracking-[0.15em] text-emerald-500">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981]" />
                  SECURITY_CONFIG
                </div>
              </div>
            </section>
          </div>

          {/* SECURITY CONFIGURATION */}
          <section className="relative w-full overflow-hidden rounded-2xl border border-orange-500/10 bg-[#080807]">
            <div
              className="pointer-events-none absolute inset-0 opacity-30"
              style={{
                backgroundImage: `
                  linear-gradient(
                    rgba(249, 115, 22, 0.035) 1px,
                    transparent 1px
                  ),
                  linear-gradient(
                    90deg,
                    rgba(249, 115, 22, 0.035) 1px,
                    transparent 1px
                  )
                `,
                backgroundSize: "40px 40px",
              }}
            />

            <div className="relative border-b border-orange-500/10 px-5 py-5">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-orange-500/20 bg-orange-500/10 text-orange-400">
                  <Fingerprint size={19} strokeWidth={1.5} />
                </div>

                <div>
                  <h2 className="text-lg font-semibold text-white">
                    Security configuration
                  </h2>

                  <p className="mt-1 text-sm text-zinc-600">
                    Manage authentication and access protection.
                  </p>
                </div>
              </div>
            </div>

            <div className="relative divide-y divide-orange-500/10">
              <SettingRow
                icon={<Fingerprint size={18} />}
                title="Multi-factor authentication"
                description="Require additional verification for administrator accounts."
                status="ENABLED"
                color="green"
              />

              <SettingRow
                icon={<LockKeyhole size={18} />}
                title="Session security"
                description="Configure session duration and automatic timeout policies."
                status="SECURE"
                color="orange"
              />

              <SettingRow
                icon={<Bell size={18} />}
                title="Security notifications"
                description="Receive alerts for important security and compliance events."
                status="ACTIVE"
                color="green"
              />

              <SettingRow
                icon={<KeyRound size={18} />}
                title="API access"
                description="Manage API keys and integration authentication policies."
                status="PROTECTED"
                color="orange"
              />
            </div>
          </section>

          {/* SYSTEM STATUS */}
          <section className="relative w-full overflow-hidden rounded-2xl border border-orange-500/10 bg-[#080807] p-5">
            <div className="pointer-events-none absolute -right-20 -top-20 h-40 w-40 rounded-full bg-emerald-500/5 blur-3xl" />

            <div className="relative flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400 shadow-[0_0_12px_#10b981]" />

                  <span className="text-[10px] tracking-[0.2em] text-emerald-500">
                    SYSTEM_STATUS
                  </span>
                </div>

                <h2 className="mt-2 text-lg font-semibold text-white">
                  CYGRC security environment
                </h2>

                <p className="mt-1 text-sm text-zinc-600">
                  All core security services are operating normally.
                </p>
              </div>

              <div className="flex shrink-0 items-center gap-3 rounded-xl border border-emerald-500/15 bg-emerald-500/5 px-4 py-3">
                <ShieldCheck
                  size={18}
                  className="text-emerald-400"
                  strokeWidth={1.6}
                />

                <div>
                  <p className="text-[10px] tracking-widest text-zinc-600">
                    SECURITY STATUS
                  </p>

                  <p className="text-sm font-semibold text-emerald-400">
                    OPERATIONAL
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* FOOTER STATUS */}
          <div className="flex flex-wrap items-center justify-center gap-x-8 gap-y-3 py-2 text-[9px] tracking-[0.15em] text-zinc-700">
            <span className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              IDENTITY_PROTECTED
            </span>

            <span className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-orange-500" />
              ACCESS_CONTROL
            </span>

            <span className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              SECURITY_ACTIVE
            </span>
          </div>
        </div>
      </div>
    </main>
  );
}

/* =========================================
   SETTING ROW
========================================= */

function SettingRow({
  icon,
  title,
  description,
  status,
  color,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  status: string;
  color: "orange" | "green";
}) {
  const isGreen = color === "green";

  return (
    <div className="group flex w-full flex-col gap-4 px-5 py-5 transition-all duration-300 hover:bg-white/[0.015] sm:flex-row sm:items-center sm:justify-between">
      <div className="flex min-w-0 items-center gap-4">
        <div
          className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border ${
            isGreen
              ? "border-emerald-500/20 bg-emerald-500/10 text-emerald-400"
              : "border-orange-500/20 bg-orange-500/10 text-orange-400"
          }`}
        >
          {icon}
        </div>

        <div className="min-w-0">
          <h3 className="text-sm font-semibold text-zinc-200">
            {title}
          </h3>

          <p className="mt-1 text-xs leading-5 text-zinc-600">
            {description}
          </p>
        </div>
      </div>

      <div
        className={`flex shrink-0 items-center gap-2 text-[9px] tracking-[0.15em] ${
          isGreen ? "text-emerald-400" : "text-orange-400"
        }`}
      >
        <span
          className={`h-1.5 w-1.5 rounded-full ${
            isGreen
              ? "bg-emerald-400 shadow-[0_0_8px_#10b981]"
              : "bg-orange-400 shadow-[0_0_8px_#f97316]"
          }`}
        />

        {status}
      </div>
    </div>
  );
}