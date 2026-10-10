"use client";

import React from "react";
import {
Users,
ShieldCheck,
UserRound,
Building2,
ChevronRight,
Fingerprint,
} from "lucide-react";

const users = [
{
name: "Alex Morgan",
role: "Admin",
department: "Security",
},
{
name: "Mina Patel",
role: "Auditor",
department: "Internal Audit",
},
{
name: "Noah Kim",
role: "Analyst",
department: "Risk Operations",
},
];

export default function UsersPage() {
return ( <div className="w-full space-y-6">
{/* =====================================================
PAGE HEADER
====================================================== */}

  <div className="flex flex-col gap-3">
    <div className="flex items-center gap-2">
      <div className="h-1 w-8 rounded-full bg-orange-500" />

      <span className="font-mono text-[9px] font-semibold tracking-[0.2em] text-orange-400">
        USER_MANAGEMENT
      </span>
    </div>

    <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
      Users
    </h1>

    <p className="max-w-2xl text-sm leading-6 text-zinc-500">
      Manage access, role assignments, and collaboration across the
      organization.
    </p>
  </div>

  {/* =====================================================
      USER OVERVIEW
  ====================================================== */}

  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
    <UserStat
      icon={<Users size={20} />}
      label="TOTAL USERS"
      value="3"
      color="orange"
    />

    <UserStat
      icon={<ShieldCheck size={20} />}
      label="ADMINS"
      value="1"
      color="green"
    />

    <UserStat
      icon={<UserRound size={20} />}
      label="AUDITORS"
      value="1"
      color="orange"
    />

    <UserStat
      icon={<Fingerprint size={20} />}
      label="ACTIVE ACCESS"
      value="100%"
      color="green"
    />
  </div>

  {/* =====================================================
      USERS SECTION
  ====================================================== */}

  <section className="relative overflow-hidden rounded-2xl border border-orange-500/10 bg-[#080807]">
    <div className="cyber-users-grid pointer-events-none absolute inset-0 opacity-30" />

    {/* Header */}

    <div className="relative flex flex-col gap-4 border-b border-orange-500/10 px-5 py-5 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-orange-500/20 bg-orange-500/10 text-orange-400">
          <Users size={20} strokeWidth={1.5} />
        </div>

        <div>
          <h2 className="text-lg font-semibold text-white">
            Organization users
          </h2>

          <p className="mt-1 text-sm text-zinc-600">
            Manage access, roles, and organizational responsibilities.
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 font-mono text-[9px] tracking-[0.18em] text-emerald-500">
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400 shadow-[0_0_10px_#10b981]" />
        ACCESS_SYSTEM_ACTIVE
      </div>
    </div>

    {/* User Cards */}

    <div className="relative grid gap-4 p-5 md:grid-cols-3">
      {users.map((entry, index) => (
        <UserCard
          key={entry.name}
          user={entry}
          index={index}
        />
      ))}
    </div>
  </section>

  {/* =====================================================
      ACCESS CONTROL
  ====================================================== */}

  <section className="relative overflow-hidden rounded-2xl border border-emerald-500/10 bg-[#080807]">
    <div className="cyber-users-grid pointer-events-none absolute inset-0 opacity-20" />

    <div className="relative border-b border-emerald-500/10 px-5 py-5">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-emerald-500/20 bg-emerald-500/10 text-emerald-400">
          <ShieldCheck size={19} strokeWidth={1.5} />
        </div>

        <div>
          <h2 className="text-lg font-semibold text-white">
            Access control
          </h2>

          <p className="mt-1 text-sm text-zinc-600">
            Review user roles and access permissions.
          </p>
        </div>
      </div>
    </div>

    <div className="relative divide-y divide-emerald-500/10">
      <AccessRow
        title="Administrator access"
        description="Full platform administration and security configuration."
        status="PROTECTED"
        color="orange"
      />

      <AccessRow
        title="Audit access"
        description="Access to audits, evidence, controls, and compliance records."
        status="ACTIVE"
        color="green"
      />

      <AccessRow
        title="Risk operations"
        description="Manage risks, assessments, mitigation plans, and monitoring."
        status="ACTIVE"
        color="green"
      />
    </div>
  </section>

  {/* =====================================================
      USER SECURITY STATUS
  ====================================================== */}

  <section className="rounded-2xl border border-orange-500/10 bg-[#080807] p-5">
    <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400 shadow-[0_0_12px_#10b981]" />

          <span className="font-mono text-[9px] tracking-[0.2em] text-emerald-500">
            IDENTITY_STATUS
          </span>
        </div>

        <h2 className="mt-2 text-lg font-semibold text-white">
          User access environment
        </h2>

        <p className="mt-1 text-sm text-zinc-600">
          Identity and access controls are operating normally.
        </p>
      </div>

      <div className="flex items-center gap-3 rounded-xl border border-emerald-500/15 bg-emerald-500/5 px-4 py-3">
        <Fingerprint
          size={20}
          className="text-emerald-400"
          strokeWidth={1.5}
        />

        <div>
          <p className="font-mono text-[9px] tracking-widest text-zinc-600">
            ACCESS STATUS
          </p>

          <p className="text-sm font-semibold text-emerald-400">
            SECURE
          </p>
        </div>
      </div>
    </div>
  </section>

  {/* =====================================================
      FOOTER STATUS
  ====================================================== */}

  <div className="flex flex-wrap items-center justify-center gap-x-8 gap-y-3 py-2 font-mono text-[9px] tracking-[0.15em] text-zinc-700">
    <span className="flex items-center gap-2">
      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
      IDENTITY_PROTECTED
    </span>

    <span className="flex items-center gap-2">
      <span className="h-1.5 w-1.5 rounded-full bg-orange-500" />
      ROLE_MANAGEMENT
    </span>

    <span className="flex items-center gap-2">
      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
      ACCESS_MONITORED
    </span>
  </div>

  {/* =====================================================
      LOCAL PAGE CSS
  ====================================================== */}

  <style jsx>{`
    .cyber-users-grid {
      background-image:
        linear-gradient(
          rgba(249, 115, 22, 0.035) 1px,
          transparent 1px
        ),
        linear-gradient(
          90deg,
          rgba(249, 115, 22, 0.035) 1px,
          transparent 1px
        );
      background-size: 40px 40px;
    }
  `}</style>
</div>


);
}

/* =========================================================
USER STAT
========================================================= */

function UserStat({
icon,
label,
value,
color,
}: {
icon: React.ReactNode;
label: string;
value: string;
color: "orange" | "green";
}) {
const isGreen = color === "green";

return (
<div
className={`group relative overflow-hidden rounded-2xl border bg-[#080807] p-5 transition-all duration-300 ${
        isGreen
          ? "border-emerald-500/15 hover:border-emerald-500/40 hover:shadow-[0_0_30px_rgba(16,185,129,0.06)]"
          : "border-orange-500/15 hover:border-orange-500/40 hover:shadow-[0_0_30px_rgba(249,115,22,0.06)]"
      }`}
>
<div
className={`pointer-events-none absolute -right-12 -top-12 h-28 w-28 rounded-full blur-3xl ${
          isGreen ? "bg-emerald-500/10" : "bg-orange-500/10"
        }`}
/>


  <div className="relative flex items-center justify-between">
    <div
      className={`flex h-10 w-10 items-center justify-center rounded-xl border ${
        isGreen
          ? "border-emerald-500/20 bg-emerald-500/10 text-emerald-400"
          : "border-orange-500/20 bg-orange-500/10 text-orange-400"
      }`}
    >
      {icon}
    </div>

    <span className="font-mono text-[8px] tracking-[0.18em] text-zinc-700">
      DATA_STREAM
    </span>
  </div>

  <p className="relative mt-5 font-mono text-[9px] tracking-[0.18em] text-zinc-600">
    {label}
  </p>

  <p className="relative mt-1 text-3xl font-bold tracking-tight text-white">
    {value}
  </p>

  <div className="relative mt-4 h-px w-full bg-zinc-900">
    <div
      className={`h-px w-3/4 transition-all duration-700 group-hover:w-full ${
        isGreen ? "bg-emerald-500" : "bg-orange-500"
      }`}
    />
  </div>
</div>


);
}

/* =========================================================
USER CARD
========================================================= */

function UserCard({
user,
index,
}: {
user: {
name: string;
role: string;
department: string;
};
index: number;
}) {
const isGreen = user.role === "Auditor";

return (
<div
className={`group relative overflow-hidden rounded-2xl border bg-[#070706] p-5 transition-all duration-300 ${
        isGreen
          ? "border-emerald-500/15 hover:border-emerald-500/40 hover:shadow-[0_0_25px_rgba(16,185,129,0.05)]"
          : "border-orange-500/15 hover:border-orange-500/40 hover:shadow-[0_0_25px_rgba(249,115,22,0.05)]"
      }`}
>
<div
className={`absolute right-0 top-0 h-14 w-14 border-r border-t transition ${
          isGreen
            ? "border-emerald-500/0 group-hover:border-emerald-500/30"
            : "border-orange-500/0 group-hover:border-orange-500/30"
        }`}
/>


  <div className="flex items-start justify-between">
    <div className="flex items-center gap-3">
      <div
        className={`flex h-12 w-12 items-center justify-center rounded-full border text-sm font-bold ${
          isGreen
            ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
            : "border-orange-500/30 bg-orange-500/10 text-orange-400"
        }`}
      >
        {getInitials(user.name)}
      </div>

      <div>
        <p className="font-semibold text-white">{user.name}</p>

        <p className="mt-1 font-mono text-[9px] text-zinc-600">
          USER_0{index + 1}
        </p>
      </div>
    </div>

    <div
      className={`h-2 w-2 rounded-full ${
        isGreen
          ? "bg-emerald-400 shadow-[0_0_10px_#10b981]"
          : "bg-orange-400 shadow-[0_0_10px_#f97316]"
      }`}
    />
  </div>

  <div className="mt-6">
    <p className="font-mono text-[9px] tracking-[0.2em] text-zinc-700">
      ROLE
    </p>

    <p
      className={`mt-1 text-sm font-medium ${
        isGreen ? "text-emerald-400" : "text-orange-400"
      }`}
    >
      {user.role}
    </p>
  </div>

  <div className="mt-4">
    <div className="flex items-center gap-2">
      <Building2 size={13} className="text-zinc-700" />

      <p className="text-xs text-zinc-500">{user.department}</p>
    </div>
  </div>

  <div className="mt-5 flex items-center justify-between border-t border-zinc-900 pt-4">
    <span className="flex items-center gap-2 font-mono text-[9px] tracking-[0.15em] text-emerald-500">
      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 shadow-[0_0_7px_#10b981]" />
      ACTIVE
    </span>

    <ChevronRight
      size={15}
      className={`text-zinc-700 transition-all group-hover:translate-x-1 ${
        isGreen
          ? "group-hover:text-emerald-400"
          : "group-hover:text-orange-400"
      }`}
    />
  </div>
</div>

);
}

/* =========================================================
ACCESS ROW
========================================================= */

function AccessRow({
title,
description,
status,
color,
}: {
title: string;
description: string;
status: string;
color: "orange" | "green";
}) {
const isGreen = color === "green";

return ( <div className="group flex flex-col gap-4 px-5 py-5 transition hover:bg-white/[0.015] sm:flex-row sm:items-center sm:justify-between"> <div> <h3 className="text-sm font-semibold text-zinc-200">{title}</h3>


    <p className="mt-1 text-xs leading-5 text-zinc-600">
      {description}
    </p>
  </div>

  <div
    className={`flex shrink-0 items-center gap-2 font-mono text-[9px] tracking-[0.15em] ${
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

/* =========================================================
INITIALS
========================================================= */

function getInitials(name: string) {
return name
.split(" ")
.map((part) => part[0])
.join("")
.slice(0, 2)
.toUpperCase();
}
