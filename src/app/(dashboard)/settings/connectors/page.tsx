"use client";

import React from "react";
import { motion } from "framer-motion";
import {
  Plug,
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ArrowUpRight,
  ShieldCheck,
  Database,
  Cloud,
  Server,
  KeyRound,
  RefreshCw,
  Settings2,
  Activity,
  Clock3,
  Code2,
  MessageSquare,
} from "lucide-react";

/* =========================================================
   CONNECTOR DATA
========================================================= */

const connectorStats = [
  {
    title: "Total Connectors",
    value: "24",
    change: "+3",
    description: "this month",
    icon: Plug,
    color: "orange",
  },
  {
    title: "Connected",
    value: "19",
    change: "+8%",
    description: "vs last month",
    icon: CheckCircle2,
    color: "green",
  },
  {
    title: "Needs Attention",
    value: "3",
    change: "2 new",
    description: "require action",
    icon: AlertTriangle,
    color: "orange",
  },
  {
    title: "Data Sync",
    value: "98.7%",
    change: "+2.4%",
    description: "successful syncs",
    icon: RefreshCw,
    color: "green",
  },
];

const connectors = [
  {
    name: "Microsoft Azure",
    description: "Cloud infrastructure and identity",
    category: "Cloud",
    icon: Cloud,
    iconColor: "text-orange-400",
    iconBg: "bg-orange-500/10",
    status: "Connected",
    lastSync: "2 minutes ago",
    records: "12,482",
    health: 99,
  },
  {
    name: "GitHub",
    description: "Repositories and security findings",
    category: "Development",
    icon: Code2,
    iconColor: "text-green-400",
    iconBg: "bg-green-500/10",
    status: "Connected",
    lastSync: "5 minutes ago",
    records: "8,921",
    health: 98,
  },
  {
    name: "Slack",
    description: "Security notifications and alerts",
    category: "Communication",
    icon: MessageSquare,
    iconColor: "text-green-400",
    iconBg: "bg-green-500/10",
    status: "Connected",
    lastSync: "8 minutes ago",
    records: "3,284",
    health: 97,
  },
  {
    name: "AWS",
    description: "Cloud resources and configuration",
    category: "Cloud",
    icon: Cloud,
    iconColor: "text-orange-400",
    iconBg: "bg-orange-500/10",
    status: "Needs Attention",
    lastSync: "42 minutes ago",
    records: "16,204",
    health: 74,
  },
  {
    name: "Jira",
    description: "Tickets and remediation workflows",
    category: "Project Management",
    icon: Database,
    iconColor: "text-green-400",
    iconBg: "bg-green-500/10",
    status: "Connected",
    lastSync: "12 minutes ago",
    records: "6,721",
    health: 96,
  },
  {
    name: "Microsoft Entra ID",
    description: "Identity and access management",
    category: "Identity",
    icon: KeyRound,
    iconColor: "text-orange-400",
    iconBg: "bg-orange-500/10",
    status: "Connected",
    lastSync: "3 minutes ago",
    records: "4,831",
    health: 100,
  },
  {
    name: "ServiceNow",
    description: "Incident and change management",
    category: "ITSM",
    icon: Server,
    iconColor: "text-green-400",
    iconBg: "bg-green-500/10",
    status: "Disconnected",
    lastSync: "Yesterday",
    records: "2,194",
    health: 0,
  },
  {
    name: "Okta",
    description: "Workforce identity platform",
    category: "Identity",
    icon: ShieldCheck,
    iconColor: "text-orange-400",
    iconBg: "bg-orange-500/10",
    status: "Connected",
    lastSync: "7 minutes ago",
    records: "7,412",
    health: 99,
  },
];

const categories = [
  { name: "All Connectors", count: 24 },
  { name: "Cloud", count: 6 },
  { name: "Identity", count: 5 },
  { name: "Development", count: 4 },
  { name: "ITSM", count: 3 },
  { name: "Communication", count: 3 },
];

/* =========================================================
   STAT CARD
========================================================= */

function StatCard({
  title,
  value,
  change,
  description,
  icon: Icon,
  color,
}: {
  title: string;
  value: string;
  change: string;
  description: string;
  icon: React.ElementType;
  color: string;
}) {
  const colors: Record<string, string> = {
    orange:
      "bg-orange-500/10 text-orange-400 border-orange-500/20",
    green:
      "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  };

  return (
    <motion.div
      whileHover={{ y: -3 }}
      transition={{ duration: 0.2 }}
      className="relative overflow-hidden rounded-xl border border-white/[0.08] bg-[#0b0d0c] p-6 shadow-[0_8px_30px_rgba(0,0,0,0.25)]"
    >
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-orange-500/30 to-transparent" />

      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-400">
            {title}
          </p>

          <motion.p
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-3 text-3xl font-bold tracking-tight text-white"
          >
            {value}
          </motion.p>
        </div>

        <div
          className={`flex h-12 w-12 items-center justify-center rounded-xl border ${colors[color]}`}
        >
          <Icon size={22} strokeWidth={2} />
        </div>
      </div>

      <div className="mt-5 flex items-center gap-2 text-xs">
        <span
          className={
            color === "orange"
              ? "font-semibold text-orange-400"
              : "font-semibold text-emerald-400"
          }
        >
          ↗ {change}
        </span>

        <span className="text-slate-500">
          {description}
        </span>
      </div>
    </motion.div>
  );
}

/* =========================================================
   STATUS BADGE
========================================================= */

function StatusBadge({ status }: { status: string }) {
  if (status === "Connected") {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400">
        <CheckCircle2 size={13} />
        Connected
      </span>
    );
  }

  if (status === "Needs Attention") {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full border border-orange-500/20 bg-orange-500/10 px-3 py-1 text-xs font-medium text-orange-400">
        <AlertTriangle size={13} />
        Needs Attention
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-red-500/20 bg-red-500/10 px-3 py-1 text-xs font-medium text-red-400">
      <XCircle size={13} />
      Disconnected
    </span>
  );
}

/* =========================================================
   MAIN PAGE
========================================================= */

export default function ConnectorsPage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[#050606] text-white">

      {/* =====================================================
          BACKGROUND GLOW
      ===================================================== */}

      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -right-40 top-20 h-96 w-96 rounded-full bg-orange-500/[0.04] blur-3xl" />

        <div className="absolute bottom-0 left-1/3 h-96 w-96 rounded-full bg-emerald-500/[0.035] blur-3xl" />

        <div className="absolute left-0 top-1/2 h-80 w-80 rounded-full bg-orange-500/[0.025] blur-3xl" />
      </div>

      {/* =====================================================
          PAGE CONTENT
      ===================================================== */}

      <div className="relative space-y-7 p-6 lg:p-9">

        {/* ===================================================
            HEADER
        =================================================== */}

        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col justify-between gap-5 xl:flex-row xl:items-center"
        >
          <div>
            <div className="flex items-center gap-3">

              {/* ICON */}

              <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-orange-500/20 bg-orange-500/10 text-orange-400">
                <Plug size={22} />
              </div>

              {/* TITLE */}

              <div>
                <h1 className="text-2xl font-bold tracking-tight text-white">
                  Connectors
                </h1>

                <p className="mt-1 text-sm text-slate-400">
                  Connect CYGRC with your security and business ecosystem.
                </p>
              </div>

            </div>
          </div>

          {/* ADD CONNECTOR */}

          <button className="flex h-10 items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-orange-500 to-orange-600 px-5 text-sm font-semibold text-black shadow-lg shadow-orange-900/20 transition hover:from-orange-400 hover:to-orange-500">
            <Plus size={17} />
            Add Connector
          </button>
        </motion.div>

        {/* ===================================================
            STATISTICS
        =================================================== */}

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {connectorStats.map((stat, index) => (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.08 }}
            >
              <StatCard {...stat} />
            </motion.div>
          ))}
        </div>

        {/* ===================================================
            MAIN GRID
        =================================================== */}

        <div className="grid gap-6 xl:grid-cols-[230px_minmax(0,1fr)]">

          {/* =================================================
              CATEGORIES
          ================================================= */}

          <motion.aside
            initial={{ opacity: 0, x: -15 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.25 }}
            className="h-fit rounded-xl border border-white/[0.08] bg-[#0b0d0c] p-4"
          >

            <div className="mb-4 px-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Categories
              </p>
            </div>

            <div className="space-y-1">

              {categories.map((category, index) => (
                <button
                  key={category.name}
                  className={`flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-left text-sm transition ${
                    index === 0
                      ? "bg-orange-500/10 text-orange-400"
                      : "text-slate-400 hover:bg-white/[0.04] hover:text-white"
                  }`}
                >
                  <span>{category.name}</span>

                  <span
                    className={`rounded-md px-2 py-0.5 text-[10px] ${
                      index === 0
                        ? "bg-orange-500/10 text-orange-400"
                        : "bg-white/[0.04] text-slate-600"
                    }`}
                  >
                    {category.count}
                  </span>
                </button>
              ))}

            </div>

            <div className="my-5 h-px bg-white/[0.06]" />

            {/* HEALTH */}

            <div className="rounded-lg border border-orange-500/10 bg-orange-500/[0.04] p-3">

              <div className="flex items-center gap-2">

                <Activity
                  size={15}
                  className="text-orange-400"
                />

                <span className="text-xs font-semibold text-slate-300">
                  Connector Health
                </span>

              </div>

              <div className="mt-3 flex items-end justify-between">

                <span className="text-2xl font-bold text-white">
                  96.4%
                </span>

                <span className="text-[10px] font-medium text-emerald-400">
                  Healthy
                </span>

              </div>

              <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/[0.06]">
                <div className="h-full w-[96%] rounded-full bg-gradient-to-r from-orange-500 to-emerald-500" />
              </div>

            </div>
          </motion.aside>

          {/* =================================================
              CONNECTOR SECTION
          ================================================= */}

          <motion.section
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="overflow-hidden rounded-xl border border-white/[0.08] bg-[#0b0d0c]"
          >

            {/* TOOLBAR */}

            <div className="flex flex-col gap-4 border-b border-white/[0.07] p-5 lg:flex-row lg:items-center lg:justify-between">

              <div>
                <h2 className="text-lg font-semibold text-white">
                  Connected Services
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Manage integrations and synchronization settings.
                </p>
              </div>

              <div className="flex gap-2">

                {/* SEARCH */}

                <div className="flex h-9 items-center gap-2 rounded-lg border border-white/10 bg-[#050606] px-3">

                  <Search
                    size={15}
                    className="text-slate-500"
                  />

                  <input
                    placeholder="Search connectors..."
                    className="w-40 bg-transparent text-xs text-white outline-none placeholder:text-slate-600"
                  />

                </div>

                {/* FILTER */}

                <button className="flex h-9 items-center gap-2 rounded-lg border border-white/10 bg-[#050606] px-3 text-xs text-slate-400 transition hover:border-orange-500/20 hover:text-orange-400">
                  <Filter size={14} />
                  Filter
                </button>

              </div>
            </div>

            {/* =================================================
                CONNECTOR CARDS
            ================================================= */}

            <div className="grid gap-4 p-5 md:grid-cols-2">

              {connectors.map((connector, index) => {
                const Icon = connector.icon;

                return (
                  <motion.div
                    key={connector.name}
                    initial={{
                      opacity: 0,
                      y: 12,
                    }}
                    animate={{
                      opacity: 1,
                      y: 0,
                    }}
                    transition={{
                      delay: 0.35 + index * 0.05,
                    }}
                    whileHover={{
                      y: -2,
                    }}
                    className="group relative overflow-hidden rounded-xl border border-white/[0.07] bg-[#080a09] p-5 transition hover:border-orange-500/20 hover:shadow-[0_8px_30px_rgba(249,115,22,0.06)]"
                  >

                    {/* TOP LINE */}

                    <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-orange-500/50 to-transparent opacity-0 transition group-hover:opacity-100" />

                    {/* CARD HEADER */}

                    <div className="flex items-start justify-between">

                      <div className="flex items-center gap-3">

                        <div
                          className={`flex h-11 w-11 items-center justify-center rounded-xl ${connector.iconBg} ${connector.iconColor}`}
                        >
                          <Icon size={22} />
                        </div>

                        <div>
                          <h3 className="text-sm font-semibold text-white">
                            {connector.name}
                          </h3>

                          <p className="mt-1 text-[11px] text-slate-600">
                            {connector.category}
                          </p>
                        </div>

                      </div>

                      <button className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-600 transition hover:bg-white/[0.05] hover:text-orange-400">
                        <MoreHorizontal size={17} />
                      </button>

                    </div>

                    {/* DESCRIPTION */}

                    <p className="mt-4 text-xs leading-5 text-slate-500">
                      {connector.description}
                    </p>

                    {/* STATUS */}

                    <div className="mt-4">
                      <StatusBadge status={connector.status} />
                    </div>

                    {/* HEALTH */}

                    <div className="mt-5">

                      <div className="mb-2 flex items-center justify-between">

                        <span className="text-[11px] text-slate-600">
                          Connection health
                        </span>

                        <span
                          className={`text-[11px] font-semibold ${
                            connector.health >= 90
                              ? "text-emerald-400"
                              : connector.health > 0
                              ? "text-orange-400"
                              : "text-red-400"
                          }`}
                        >
                          {connector.health}%
                        </span>

                      </div>

                      <div className="h-1.5 overflow-hidden rounded-full bg-white/[0.05]">

                        <motion.div
                          initial={{ width: 0 }}
                          animate={{
                            width: `${connector.health}%`,
                          }}
                          transition={{
                            duration: 0.8,
                          }}
                          className={`h-full rounded-full ${
                            connector.health >= 90
                              ? "bg-emerald-500"
                              : connector.health > 0
                              ? "bg-orange-500"
                              : "bg-red-500"
                          }`}
                        />

                      </div>

                    </div>

                    {/* FOOTER */}

                    <div className="mt-5 flex items-center justify-between border-t border-white/[0.05] pt-4">

                      <div>

                        <p className="text-[10px] uppercase tracking-wider text-slate-600">
                          Last sync
                        </p>

                        <div className="mt-1 flex items-center gap-1.5">

                          <Clock3
                            size={12}
                            className="text-slate-600"
                          />

                          <span className="text-[11px] text-slate-400">
                            {connector.lastSync}
                          </span>

                        </div>

                      </div>

                      <div className="text-right">

                        <p className="text-[10px] uppercase tracking-wider text-slate-600">
                          Records
                        </p>

                        <p className="mt-1 text-xs font-semibold text-slate-300">
                          {connector.records}
                        </p>

                      </div>

                    </div>

                    {/* ACTIONS */}

                    <div className="mt-4 flex gap-2">

                      <button className="flex h-8 flex-1 items-center justify-center gap-1.5 rounded-lg border border-white/[0.07] bg-white/[0.02] text-[11px] font-medium text-slate-400 transition hover:border-orange-500/20 hover:bg-orange-500/[0.04] hover:text-orange-400">
                        <Settings2 size={13} />
                        Configure
                      </button>

                      <button className="flex h-8 w-9 items-center justify-center rounded-lg border border-white/[0.07] bg-white/[0.02] text-slate-500 transition hover:border-orange-500/20 hover:bg-orange-500/[0.04] hover:text-orange-400">
                        <ArrowUpRight size={14} />
                      </button>

                    </div>

                  </motion.div>
                );
              })}

            </div>

            {/* =================================================
                FOOTER
            ================================================= */}

            <div className="flex items-center justify-between border-t border-white/[0.06] px-5 py-4">

              <p className="text-xs text-slate-500">
                Showing{" "}
                <span className="text-slate-300">
                  8
                </span>{" "}
                of{" "}
                <span className="text-slate-300">
                  24
                </span>{" "}
                connectors
              </p>

              <button className="flex items-center gap-1.5 text-xs font-medium text-orange-400 transition hover:text-orange-300">
                View all connectors
                <ArrowUpRight size={14} />
              </button>

            </div>

          </motion.section>
        </div>
      </div>
    </main>
  );
}