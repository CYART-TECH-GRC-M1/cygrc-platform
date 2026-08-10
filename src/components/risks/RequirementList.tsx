"use client";

import React from "react";
import { motion } from "framer-motion";
import {
  ShieldCheck,
  Clock3,
  CheckCircle2,
  AlertCircle,
  ArrowUpRight,
} from "lucide-react";

const requirements = [
  {
    title: "Multi-factor authentication for privileged accounts",
    category: "ACCESS CONTROL",
    owner: "Security Ops",
    due: "Due Jul 30",
    status: "In Progress",
    icon: ShieldCheck,
    statusClass:
      "bg-blue-50 text-blue-700 ring-1 ring-inset ring-blue-200 dark:bg-blue-500/10 dark:text-blue-400 dark:ring-blue-500/20",
  },
  {
    title: "Quarterly vulnerability review for internet-facing assets",
    category: "VULNERABILITY MANAGEMENT",
    owner: "IT Ops",
    due: "Due Aug 12",
    status: "Open",
    icon: AlertCircle,
    statusClass:
      "bg-amber-50 text-amber-700 ring-1 ring-inset ring-amber-200 dark:bg-amber-500/10 dark:text-amber-400 dark:ring-amber-500/20",
  },
  {
    title: "Retention and backup validation for audit evidence",
    category: "EVIDENCE HANDLING",
    owner: "Compliance",
    due: "Due Jul 20",
    status: "Completed",
    icon: CheckCircle2,
    statusClass:
      "bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-400 dark:ring-emerald-500/20",
  },
];

export default function RequirementList() {
  return (
    <section className="w-full rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900/70 sm:p-7">
      {/* Header */}
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-100 text-violet-600 dark:bg-violet-500/10 dark:text-violet-400">
              <ShieldCheck size={20} />
            </div>

            <div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                Visible Requirements
              </h2>

              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                Key compliance requirements and their current status.
              </p>
            </div>
          </div>
        </div>

        <div className="inline-flex w-fit items-center gap-2 rounded-full bg-violet-50 px-4 py-2 text-sm font-semibold text-violet-700 ring-1 ring-violet-200 dark:bg-violet-500/10 dark:text-violet-400 dark:ring-violet-500/20">
          <span className="h-2 w-2 rounded-full bg-violet-500" />
          {requirements.length} active items
        </div>
      </div>

      {/* Requirements */}
      <div className="grid gap-4 lg:grid-cols-2">
        {requirements.map((requirement, index) => {
          const Icon = requirement.icon;

          return (
            <motion.article
              key={requirement.title}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.08 }}
              whileHover={{ y: -3 }}
              className={`
                group relative overflow-hidden rounded-2xl
                border border-slate-200
                bg-slate-50/70
                p-5
                shadow-sm
                transition-all duration-300
                hover:border-violet-200
                hover:bg-white
                hover:shadow-lg
                dark:border-slate-800
                dark:bg-slate-950/40
                dark:hover:border-violet-500/30
                dark:hover:bg-slate-900
                ${index === 2 ? "lg:col-span-2" : ""}
              `}
            >
              {/* Accent */}
              <div className="absolute left-0 top-0 h-full w-1 bg-gradient-to-b from-violet-500 to-indigo-500 opacity-0 transition-opacity group-hover:opacity-100" />

              <div className="flex items-start justify-between gap-4">
                <div className="flex min-w-0 gap-4">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-white text-violet-600 shadow-sm ring-1 ring-slate-200 dark:bg-slate-900 dark:text-violet-400 dark:ring-slate-800">
                    <Icon size={20} />
                  </div>

                  <div className="min-w-0">
                    <h3 className="text-base font-semibold leading-6 text-slate-900 dark:text-white">
                      {requirement.title}
                    </h3>

                    <p className="mt-1 text-[11px] font-semibold tracking-[0.2em] text-slate-400">
                      {requirement.category}
                    </p>
                  </div>
                </div>

                <span
                  className={`shrink-0 rounded-full px-3 py-1.5 text-xs font-semibold ${requirement.statusClass}`}
                >
                  {requirement.status}
                </span>
              </div>

              <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 pt-4 dark:border-slate-800">
                <span className="text-sm font-medium text-slate-600 dark:text-slate-300">
                  {requirement.owner}
                </span>

                <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
                  <Clock3 size={15} />
                  {requirement.due}
                </div>
              </div>

              <button
                type="button"
                className="absolute bottom-4 right-4 opacity-0 transition-all group-hover:opacity-100"
                aria-label={`Open ${requirement.title}`}
              >
                <ArrowUpRight
                  size={18}
                  className="text-violet-600 dark:text-violet-400"
                />
              </button>
            </motion.article>
          );
        })}
      </div>
    </section>
  );
}