"use client";

import React from "react";
import { motion } from "framer-motion";
import {
  ClipboardCheck,
  Clock3,
  CheckCircle2,
  AlertTriangle,
  Plus,
  ArrowUpRight,
  Search,
  Filter,
  CalendarDays,
  MoreHorizontal,
  FileText,
  ShieldCheck,
  Circle,
} from "lucide-react";

const auditStats = [
  {
    title: "Total Audits",
    value: "128",
    change: "+12%",
    description: "vs last month",
    icon: ClipboardCheck,
    color: "orange",
    positive: true,
  },
  {
    title: "In Progress",
    value: "24",
    change: "+4%",
    description: "vs last month",
    icon: Clock3,
    color: "orange",
    positive: true,
  },
  {
    title: "Completed",
    value: "91",
    change: "+18%",
    description: "vs last month",
    icon: CheckCircle2,
    color: "green",
    positive: true,
  },
  {
    title: "Overdue",
    value: "13",
    change: "-8%",
    description: "vs last month",
    icon: AlertTriangle,
    color: "red",
    positive: true,
  },
];

const audits = [
  {
    id: "AUD-2026-001",
    name: "ISO 27001 Internal Audit",
    framework: "ISO 27001",
    owner: "Security Team",
    dueDate: "Aug 12, 2026",
    progress: 82,
    status: "In Progress",
    priority: "High",
  },
  {
    id: "AUD-2026-002",
    name: "SOC 2 Type II Audit",
    framework: "SOC 2",
    owner: "Compliance Team",
    dueDate: "Aug 18, 2026",
    progress: 64,
    status: "In Progress",
    priority: "High",
  },
  {
    id: "AUD-2026-003",
    name: "GDPR Privacy Assessment",
    framework: "GDPR",
    owner: "Privacy Team",
    dueDate: "Aug 22, 2026",
    progress: 45,
    status: "In Progress",
    priority: "Medium",
  },
  {
    id: "AUD-2026-004",
    name: "PCI DSS Compliance Audit",
    framework: "PCI DSS",
    owner: "IT Security",
    dueDate: "Jul 30, 2026",
    progress: 100,
    status: "Completed",
    priority: "High",
  },
  {
    id: "AUD-2026-005",
    name: "Vendor Security Assessment",
    framework: "Third Party",
    owner: "Risk Team",
    dueDate: "Jul 28, 2026",
    progress: 100,
    status: "Completed",
    priority: "Medium",
  },
  {
    id: "AUD-2026-006",
    name: "Cloud Security Review",
    framework: "Cloud Security",
    owner: "Infrastructure",
    dueDate: "Aug 02, 2026",
    progress: 32,
    status: "Overdue",
    priority: "Critical",
  },
];

const frameworkData = [
  {
    name: "ISO 27001",
    audits: 42,
    completed: 34,
    percentage: 81,
    color: "#F97316",
  },
  {
    name: "SOC 2",
    audits: 31,
    completed: 26,
    percentage: 84,
    color: "#22C55E",
  },
  {
    name: "GDPR",
    audits: 24,
    completed: 19,
    percentage: 79,
    color: "#FB923C",
  },
  {
    name: "PCI DSS",
    audits: 18,
    completed: 12,
    percentage: 67,
    color: "#16A34A",
  },
];

function StatCard({
  title,
  value,
  change,
  description,
  icon: Icon,
  color,
  positive,
}: {
  title: string;
  value: string;
  change: string;
  description: string;
  icon: React.ElementType;
  color: string;
  positive: boolean;
}) {
  const iconColors: Record<string, string> = {
    orange:
      "bg-orange-500/10 text-orange-400 border-orange-500/20",
    green:
      "bg-green-500/10 text-green-400 border-green-500/20",
    red:
      "bg-red-500/10 text-red-400 border-red-500/20",
  };

  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ duration: 0.2 }}
      className="group relative overflow-hidden rounded-xl border border-white/[0.07] bg-[#090909] p-6 shadow-[0_8px_30px_rgba(0,0,0,0.18)] transition-all duration-300 hover:border-orange-500/20 hover:shadow-orange-950/10"
    >
      {/* Orange glow */}
      <div className="pointer-events-none absolute -right-10 -top-10 h-24 w-24 rounded-full bg-orange-500/5 blur-2xl transition-all duration-300 group-hover:bg-orange-500/10" />

      <div className="relative flex items-start justify-between">
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
          className={`flex h-12 w-12 items-center justify-center rounded-xl border ${
            iconColors[color]
          }`}
        >
          <Icon size={22} strokeWidth={2} />
        </div>
      </div>

      <div className="mt-5 flex items-center gap-2 text-xs">
        <span
          className={`font-semibold ${
            positive ? "text-green-400" : "text-red-400"
          }`}
        >
          {positive ? "↗" : "↘"} {change}
        </span>

        <span className="text-slate-500">
          {description}
        </span>
      </div>
    </motion.div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    "In Progress":
      "border-orange-500/20 bg-orange-500/10 text-orange-400",

    Completed:
      "border-green-500/20 bg-green-500/10 text-green-400",

    Overdue:
      "border-red-500/20 bg-red-500/10 text-red-400",
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium ${
        styles[status] ||
        "border-white/10 bg-white/5 text-slate-400"
      }`}
    >
      {status === "Completed" && (
        <CheckCircle2 size={13} />
      )}

      {status === "In Progress" && (
        <Clock3 size={13} />
      )}

      {status === "Overdue" && (
        <AlertTriangle size={13} />
      )}

      {status}
    </span>
  );
}

function PriorityBadge({
  priority,
}: {
  priority: string;
}) {
  const styles: Record<string, string> = {
    Critical: "text-red-400",
    High: "text-orange-400",
    Medium: "text-amber-400",
    Low: "text-green-400",
  };

  return (
    <span
      className={`text-xs font-semibold ${
        styles[priority] || "text-slate-400"
      }`}
    >
      {priority}
    </span>
  );
}

export default function AuditsPage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[#050505] text-white">
      {/* Background glows */}
      <div className="pointer-events-none absolute left-1/4 top-0 h-72 w-72 rounded-full bg-orange-500/[0.04] blur-[120px]" />

      <div className="pointer-events-none absolute right-0 top-1/3 h-80 w-80 rounded-full bg-green-500/[0.03] blur-[140px]" />

      <div className="relative space-y-7 p-6 lg:p-9">
        {/* PAGE HEADER */}
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col justify-between gap-5 xl:flex-row xl:items-center"
        >
          <div>
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-orange-500/20 bg-orange-500/10 text-orange-400">
                <ClipboardCheck size={22} />
              </div>

              <div>
                <h1 className="text-2xl font-bold tracking-tight text-white">
                  Audit Management
                </h1>

                <p className="mt-1 text-sm text-slate-400">
                  Plan, execute, and monitor organizational audits.
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button className="flex h-10 items-center gap-2 rounded-lg border border-white/10 bg-[#0a0a0a] px-4 text-sm font-medium text-slate-300 transition hover:border-orange-500/30 hover:bg-orange-500/5 hover:text-orange-400">
              <CalendarDays size={16} />
              Schedule
            </button>

            <button className="flex h-10 items-center gap-2 rounded-lg bg-orange-500 px-5 text-sm font-semibold text-white shadow-lg shadow-orange-900/20 transition hover:bg-orange-600">
              <Plus size={17} />
              Create Audit
            </button>
          </div>
        </motion.div>

        {/* STAT CARDS */}
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {auditStats.map((stat, index) => (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                delay: index * 0.08,
              }}
            >
              <StatCard {...stat} />
            </motion.div>
          ))}
        </div>

        {/* MAIN CONTENT GRID */}
        <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_350px]">
          {/* AUDITS TABLE */}
          <motion.section
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="overflow-hidden rounded-xl border border-white/[0.07] bg-[#090909] shadow-[0_8px_30px_rgba(0,0,0,0.15)]"
          >
            {/* TABLE HEADER */}
            <div className="flex flex-col gap-4 border-b border-white/[0.07] p-5 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <h2 className="text-lg font-semibold text-white">
                  Recent Audits
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Track audit activities and current status.
                </p>
              </div>

              <div className="flex gap-2">
                <div className="flex h-9 items-center gap-2 rounded-lg border border-white/10 bg-[#050505] px-3 transition focus-within:border-orange-500/30">
                  <Search
                    size={15}
                    className="text-slate-500"
                  />

                  <input
                    placeholder="Search audits..."
                    className="w-36 bg-transparent text-xs text-white outline-none placeholder:text-slate-600"
                  />
                </div>

                <button className="flex h-9 items-center gap-2 rounded-lg border border-white/10 bg-[#050505] px-3 text-xs text-slate-400 transition hover:border-orange-500/30 hover:text-orange-400">
                  <Filter size={14} />
                  Filter
                </button>
              </div>
            </div>

            {/* TABLE */}
            <div className="overflow-x-auto">
              <table className="w-full min-w-[900px]">
                <thead>
                  <tr className="border-b border-white/[0.06] text-left">
                    <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Audit
                    </th>

                    <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Framework
                    </th>

                    <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Owner
                    </th>

                    <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Due Date
                    </th>

                    <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Progress
                    </th>

                    <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Status
                    </th>

                    <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Priority
                    </th>

                    <th className="px-5 py-4" />
                  </tr>
                </thead>

                <tbody>
                  {audits.map((audit, index) => (
                    <motion.tr
                      key={audit.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{
                        delay: 0.3 + index * 0.05,
                      }}
                      className="group border-b border-white/[0.05] transition hover:bg-orange-500/[0.025]"
                    >
                      {/* Audit */}
                      <td className="px-5 py-4">
                        <div className="flex items-center gap-3">
                          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-orange-500/10 bg-orange-500/10 text-orange-400">
                            <FileText size={17} />
                          </div>

                          <div>
                            <p className="text-sm font-medium text-slate-200">
                              {audit.name}
                            </p>

                            <p className="mt-0.5 text-[11px] text-slate-600">
                              {audit.id}
                            </p>
                          </div>
                        </div>
                      </td>

                      {/* Framework */}
                      <td className="px-5 py-4">
                        <span className="rounded-md border border-white/[0.06] bg-white/[0.04] px-2.5 py-1 text-xs text-slate-400">
                          {audit.framework}
                        </span>
                      </td>

                      {/* Owner */}
                      <td className="px-5 py-4 text-sm text-slate-400">
                        {audit.owner}
                      </td>

                      {/* Due Date */}
                      <td className="px-5 py-4 text-sm text-slate-400">
                        {audit.dueDate}
                      </td>

                      {/* Progress */}
                      <td className="px-5 py-4">
                        <div className="w-24">
                          <div className="mb-1.5 flex items-center justify-between">
                            <span className="text-xs text-slate-400">
                              {audit.progress}%
                            </span>
                          </div>

                          <div className="h-1.5 overflow-hidden rounded-full bg-white/[0.06]">
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{
                                width: `${audit.progress}%`,
                              }}
                              transition={{
                                duration: 0.8,
                                delay:
                                  0.4 + index * 0.05,
                              }}
                              className={`h-full rounded-full ${
                                audit.status === "Overdue"
                                  ? "bg-red-500"
                                  : audit.status ===
                                    "Completed"
                                  ? "bg-green-500"
                                  : "bg-orange-500"
                              }`}
                            />
                          </div>
                        </div>
                      </td>

                      {/* Status */}
                      <td className="px-5 py-4">
                        <StatusBadge
                          status={audit.status}
                        />
                      </td>

                      {/* Priority */}
                      <td className="px-5 py-4">
                        <PriorityBadge
                          priority={audit.priority}
                        />
                      </td>

                      {/* More */}
                      <td className="px-5 py-4">
                        <button className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-500 transition hover:bg-orange-500/10 hover:text-orange-400">
                          <MoreHorizontal size={17} />
                        </button>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* TABLE FOOTER */}
            <div className="flex items-center justify-between border-t border-white/[0.06] px-5 py-4">
              <p className="text-xs text-slate-500">
                Showing{" "}
                <span className="text-slate-300">
                  6
                </span>{" "}
                of{" "}
                <span className="text-slate-300">
                  128
                </span>{" "}
                audits
              </p>

              <button className="flex items-center gap-1.5 text-xs font-medium text-orange-400 transition hover:text-orange-300">
                View all audits
                <ArrowUpRight size={14} />
              </button>
            </div>
          </motion.section>

          {/* RIGHT SIDEBAR */}
          <div className="space-y-6">
            {/* FRAMEWORK PERFORMANCE */}
            <motion.section
              initial={{ opacity: 0, x: 15 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.35 }}
              className="rounded-xl border border-white/[0.07] bg-[#090909] p-5 shadow-[0_8px_30px_rgba(0,0,0,0.15)]"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="font-semibold text-white">
                    Framework Coverage
                  </h2>

                  <p className="mt-1 text-xs text-slate-500">
                    Audit completion by framework
                  </p>
                </div>

                <ShieldCheck
                  size={20}
                  className="text-green-400"
                />
              </div>

              <div className="mt-6 space-y-5">
                {frameworkData.map((item) => (
                  <div key={item.name}>
                    <div className="mb-2 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span
                          className="h-2 w-2 rounded-full"
                          style={{
                            backgroundColor:
                              item.color,
                          }}
                        />

                        <span className="text-sm text-slate-300">
                          {item.name}
                        </span>
                      </div>

                      <span className="text-xs font-semibold text-slate-400">
                        {item.percentage}%
                      </span>
                    </div>

                    <div className="h-2 overflow-hidden rounded-full bg-white/[0.05]">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{
                          width: `${item.percentage}%`,
                        }}
                        transition={{
                          duration: 0.8,
                        }}
                        className="h-full rounded-full"
                        style={{
                          backgroundColor:
                            item.color,
                        }}
                      />
                    </div>

                    <p className="mt-1.5 text-[11px] text-slate-600">
                      {item.completed} of{" "}
                      {item.audits} audits completed
                    </p>
                  </div>
                ))}
              </div>
            </motion.section>

            {/* UPCOMING */}
            <motion.section
              initial={{ opacity: 0, x: 15 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.45 }}
              className="rounded-xl border border-white/[0.07] bg-[#090909] p-5 shadow-[0_8px_30px_rgba(0,0,0,0.15)]"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="font-semibold text-white">
                    Upcoming Deadlines
                  </h2>

                  <p className="mt-1 text-xs text-slate-500">
                    Next audit activities
                  </p>
                </div>

                <CalendarDays
                  size={19}
                  className="text-orange-400"
                />
              </div>

              <div className="mt-5 space-y-4">
                {[
                  {
                    title:
                      "ISO 27001 Internal Audit",
                    date: "Aug 12",
                    days: "5 days",
                    color: "orange",
                  },
                  {
                    title: "SOC 2 Type II Audit",
                    date: "Aug 18",
                    days: "11 days",
                    color: "green",
                  },
                  {
                    title:
                      "GDPR Privacy Assessment",
                    date: "Aug 22",
                    days: "15 days",
                    color: "orange",
                  },
                ].map((item) => (
                  <div
                    key={item.title}
                    className="flex items-center gap-3 rounded-lg border border-white/[0.05] bg-white/[0.02] p-3 transition hover:border-orange-500/20 hover:bg-orange-500/[0.02]"
                  >
                    <div
                      className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${
                        item.color === "green"
                          ? "bg-green-500/10"
                          : "bg-orange-500/10"
                      }`}
                    >
                      <CalendarDays
                        size={16}
                        className={
                          item.color === "green"
                            ? "text-green-400"
                            : "text-orange-400"
                        }
                      />
                    </div>

                    <div className="min-w-0 flex-1">
                      <p className="truncate text-xs font-medium text-slate-300">
                        {item.title}
                      </p>

                      <p className="mt-1 text-[11px] text-slate-600">
                        Due {item.date}
                      </p>
                    </div>

                    <span className="shrink-0 text-[10px] text-slate-500">
                      {item.days}
                    </span>
                  </div>
                ))}
              </div>
            </motion.section>
          </div>
        </div>
      </div>
    </main>
  );
}