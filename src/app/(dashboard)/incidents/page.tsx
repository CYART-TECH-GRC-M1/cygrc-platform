"use client";

import React from "react";
import { motion } from "framer-motion";
import {
AlertTriangle,
ShieldAlert,
Activity,
Clock3,
CheckCircle2,
ArrowUpRight,
Search,
Filter,
Server,
UserRound,
Network,
} from "lucide-react";

const incidentStats = [
{
title: "TOTAL INCIDENTS",
value: "128",
change: "+8%",
description: "vs last month",
icon: ShieldAlert,
color: "orange",
},
{
title: "ACTIVE INCIDENTS",
value: "12",
change: "-14%",
description: "currently investigating",
icon: AlertTriangle,
color: "orange",
},
{
title: "UNDER MONITORING",
value: "27",
change: "+5%",
description: "being monitored",
icon: Activity,
color: "green",
},
{
title: "RESOLVED",
value: "89",
change: "+12%",
description: "successfully resolved",
icon: CheckCircle2,
color: "green",
},
];

const incidents = [
{
id: "INC-1024",
title: "Unauthorized login detected",
description:
"Multiple failed sign-in attempts were detected from an unknown IP address.",
status: "Active",
priority: "High",
source: "Authentication",
time: "12 min ago",
icon: UserRound,
},
{
id: "INC-1023",
title: "Potential data exfiltration",
description:
"Unusual outbound network traffic was detected and requires investigation.",
status: "Monitoring",
priority: "Medium",
source: "Network",
time: "1 hour ago",
icon: Network,
},
{
id: "INC-1022",
title: "Suspicious endpoint activity",
description:
"An endpoint generated abnormal process activity during scheduled monitoring.",
status: "Active",
priority: "High",
source: "Endpoint",
time: "3 hours ago",
icon: Server,
},
{
id: "INC-1021",
title: "Failed security policy update",
description:
"A security policy update failed to synchronize with one managed system.",
status: "Resolved",
priority: "Low",
source: "Policy",
time: "Yesterday",
icon: ShieldAlert,
},
];

export default function IncidentsPage() {
return ( <div className="w-full space-y-7">
{/* =====================================================
PAGE HEADER
====================================================== */}

  <div className="flex w-full flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
    {/* LEFT SIDE */}

    <div>
      <div className="mb-2 flex items-center gap-2">
        <div className="h-1 w-8 rounded-full bg-orange-500" />

        <span className="font-mono text-[9px] font-semibold tracking-[0.2em] text-orange-400">
          INCIDENT_MANAGEMENT
        </span>
      </div>

      <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
        Incident Management
      </h1>

      <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-500">
        Monitor security incidents, investigate threats, and coordinate
        response actions.
      </p>
    </div>

    {/* RIGHT SIDE ACTIONS */}

    <div className="flex w-full shrink-0 items-center gap-3 lg:w-auto lg:pt-1">
      <motion.button
        whileHover={{ y: -2 }}
        whileTap={{ scale: 0.98 }}
        type="button"
        className="flex h-11 items-center justify-center gap-2 rounded-xl border border-zinc-800 bg-[#080807] px-4 text-sm font-semibold text-zinc-400 transition-all hover:border-emerald-500/30 hover:bg-emerald-500/[0.04] hover:text-emerald-400"
      >
        <Filter size={16} />
        Filter
      </motion.button>

      <motion.button
        whileHover={{ y: -2 }}
        whileTap={{ scale: 0.98 }}
        type="button"
        className="flex h-11 items-center justify-center gap-2 rounded-xl bg-orange-500 px-5 text-sm font-semibold text-black shadow-lg shadow-orange-500/10 transition-all hover:bg-orange-400 hover:shadow-orange-500/20"
      >
        <AlertTriangle size={17} />
        Report Incident
      </motion.button>
    </div>
  </div>

  {/* =====================================================
      STATISTICS
  ====================================================== */}

  <div className="grid w-full grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
    {incidentStats.map((stat, index) => {
      const Icon = stat.icon;
      const isOrange = stat.color === "orange";

      return (
        <motion.div
          key={stat.title}
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.08 }}
          whileHover={{ y: -4 }}
          className={`relative overflow-hidden rounded-2xl border bg-[#080807] p-6 transition-all duration-300 ${
            isOrange
              ? "border-orange-500/15 hover:border-orange-500/40 hover:shadow-[0_10px_35px_rgba(249,115,22,0.06)]"
              : "border-emerald-500/15 hover:border-emerald-500/40 hover:shadow-[0_10px_35px_rgba(16,185,129,0.06)]"
          }`}
        >
          <div
            className={`absolute right-0 top-0 h-16 w-16 border-r border-t ${
              isOrange
                ? "border-orange-500/15"
                : "border-emerald-500/15"
            }`}
          />

          <div className="relative flex items-start justify-between">
            <div>
              <p className="font-mono text-[9px] font-semibold tracking-[0.18em] text-zinc-600">
                {stat.title}
              </p>

              <h3 className="mt-3 text-3xl font-semibold tracking-tight text-white">
                {stat.value}
              </h3>
            </div>

            <div
              className={`flex h-11 w-11 items-center justify-center rounded-xl border ${
                isOrange
                  ? "border-orange-500/20 bg-orange-500/10 text-orange-400"
                  : "border-emerald-500/20 bg-emerald-500/10 text-emerald-400"
              }`}
            >
              <Icon size={21} strokeWidth={1.8} />
            </div>
          </div>

          <div className="relative mt-4 flex items-center gap-2 text-xs">
            <span
              className={
                stat.change.startsWith("-")
                  ? "font-semibold text-orange-400"
                  : "font-semibold text-emerald-400"
              }
            >
              {stat.change}
            </span>

            <span className="text-zinc-600">{stat.description}</span>
          </div>
        </motion.div>
      );
    })}
  </div>

  {/* =====================================================
      SEARCH + FILTER STATUS
  ====================================================== */}

  <motion.div
    initial={{ opacity: 0, y: 18 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.3 }}
    className="w-full rounded-2xl border border-orange-500/15 bg-[#080807] p-5"
  >
    <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      {/* SEARCH */}

      <div className="w-full lg:max-w-md">
        <div className="flex h-11 items-center gap-2 rounded-xl border border-zinc-800 bg-[#050505] px-3 transition focus-within:border-orange-500/40">
          <Search size={17} className="shrink-0 text-zinc-600" />

          <input
            type="text"
            placeholder="Search incidents..."
            className="w-full bg-transparent text-sm text-zinc-200 outline-none placeholder:text-zinc-600"
          />
        </div>
      </div>

      {/* STATUS BUTTONS */}

      <div className="flex flex-wrap gap-2">
        <StatusBadge label="All" active />
        <StatusBadge label="Active" />
        <StatusBadge label="Monitoring" />
        <StatusBadge label="Resolved" />
      </div>
    </div>
  </motion.div>

  {/* =====================================================
      INCIDENT LIST
  ====================================================== */}

  <motion.div
    initial={{ opacity: 0, y: 18 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.4 }}
    className="w-full"
  >
    <div className="w-full overflow-hidden rounded-2xl border border-orange-500/15 bg-[#080807]">
      {/* HEADER */}

      <div className="flex flex-col gap-3 border-b border-orange-500/10 px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <div className="h-1 w-6 rounded-full bg-emerald-500" />

            <span className="font-mono text-[8px] tracking-[0.2em] text-emerald-500">
              INCIDENT_REPOSITORY
            </span>
          </div>

          <h2 className="mt-2 text-lg font-semibold text-white">
            Security Incidents
          </h2>

          <p className="mt-1 text-sm text-zinc-600">
            Review and investigate reported security incidents.
          </p>
        </div>

        <button
          type="button"
          className="flex items-center gap-2 text-xs font-semibold tracking-wider text-orange-400 transition hover:text-orange-300"
        >
          VIEW ALL
          <ArrowUpRight size={15} />
        </button>
      </div>

      {/* INCIDENTS */}

      <div className="w-full divide-y divide-orange-500/10">
        {incidents.map((incident, index) => {
          const Icon = incident.icon;

          return (
            <motion.article
              key={incident.id}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.45 + index * 0.08 }}
              className="group p-6 transition hover:bg-orange-500/[0.02]"
            >
              <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
                {/* LEFT */}

                <div className="flex min-w-0 gap-4">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-orange-500/15 bg-orange-500/10 text-orange-400">
                    <Icon size={20} />
                  </div>

                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-[10px] font-semibold text-orange-400">
                        {incident.id}
                      </span>

                      <IncidentStatus status={incident.status} />

                      <PriorityBadge priority={incident.priority} />
                    </div>

                    <h3 className="mt-2 text-base font-semibold text-zinc-200">
                      {incident.title}
                    </h3>

                    <p className="mt-1 max-w-3xl text-sm leading-6 text-zinc-600">
                      {incident.description}
                    </p>
                  </div>
                </div>

                {/* RIGHT */}

                <div className="flex shrink-0 items-center justify-between gap-6 lg:justify-end">
                  <div className="text-right">
                    <p className="font-mono text-[8px] tracking-[0.15em] text-zinc-700">
                      SOURCE
                    </p>

                    <p className="mt-1 text-sm font-medium text-zinc-400">
                      {incident.source}
                    </p>
                  </div>

                  <div className="text-right">
                    <p className="font-mono text-[8px] tracking-[0.15em] text-zinc-700">
                      UPDATED
                    </p>

                    <p className="mt-1 flex items-center gap-1 text-sm font-medium text-zinc-400">
                      <Clock3 size={13} />
                      {incident.time}
                    </p>
                  </div>

                  <button
                    type="button"
                    aria-label={`Open ${incident.title}`}
                    className="flex h-9 w-9 items-center justify-center rounded-lg border border-zinc-800 bg-[#050505] text-zinc-600 opacity-0 transition group-hover:opacity-100 hover:border-orange-500/30 hover:text-orange-400"
                  >
                    <ArrowUpRight size={15} />
                  </button>
                </div>
              </div>
            </motion.article>
          );
        })}
      </div>
    </div>
  </motion.div>

  {/* =====================================================
      RESPONSE OVERVIEW
  ====================================================== */}

  <div className="grid w-full grid-cols-1 gap-5 lg:grid-cols-3">
    <ResponseCard
      icon={AlertTriangle}
      title="Detection"
      value="IDS & Logs"
      description="Threats are detected through security monitoring sources."
      color="orange"
    />

    <ResponseCard
      icon={Activity}
      title="Response"
      value="Actions Assigned"
      description="Response actions are assigned to responsible teams."
      color="green"
    />

    <ResponseCard
      icon={CheckCircle2}
      title="Compliance"
      value="Audit Records"
      description="Incident records are maintained for compliance reviews."
      color="green"
    />
  </div>
</div>


);
}

/* =========================================================
STATUS FILTER
========================================================= */

function StatusBadge({
label,
active = false,
}: {
label: string;
active?: boolean;
}) {
return (
<button
type="button"
className={
active
? "rounded-lg bg-orange-500 px-3 py-2 text-xs font-semibold text-black shadow-sm shadow-orange-500/10"
: "rounded-lg border border-zinc-800 bg-[#050505] px-3 py-2 text-xs font-medium text-zinc-500 transition hover:border-emerald-500/30 hover:text-emerald-400"
}
>
{label} </button>
);
}

/* =========================================================
INCIDENT STATUS
========================================================= */

function IncidentStatus({ status }: { status: string }) {
const styles =
status === "Active"
? "border-red-500/20 bg-red-500/10 text-red-400"
: status === "Monitoring"
? "border-orange-500/20 bg-orange-500/10 text-orange-400"
: "border-emerald-500/20 bg-emerald-500/10 text-emerald-400";

return (
<span
className={`rounded-full border px-2.5 py-1 text-[10px] font-semibold ${styles}`}
>
{status} </span>
);
}

/* =========================================================
PRIORITY
========================================================= */

function PriorityBadge({ priority }: { priority: string }) {
const styles =
priority === "High"
? "text-red-400"
: priority === "Medium"
? "text-orange-400"
: "text-emerald-400";

return (
<span className={`text-[10px] font-semibold ${styles}`}>
{priority} Priority </span>
);
}

/* =========================================================
RESPONSE CARD
========================================================= */

type ResponseCardProps = {
icon: React.ElementType;
title: string;
value: string;
description: string;
color: "orange" | "green";
};

function ResponseCard({
icon: Icon,
title,
value,
description,
color,
}: ResponseCardProps) {
const isOrange = color === "orange";

return (
<motion.div
whileHover={{ y: -4 }}
className={`rounded-2xl border bg-[#080807] p-6 transition-all duration-300 ${
        isOrange
          ? "border-orange-500/15 hover:border-orange-500/40"
          : "border-emerald-500/15 hover:border-emerald-500/40"
      }`}
> <div className="flex items-start gap-4">
<div
className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border ${
            isOrange
              ? "border-orange-500/20 bg-orange-500/10 text-orange-400"
              : "border-emerald-500/20 bg-emerald-500/10 text-emerald-400"
          }`}
> <Icon size={20} /> </div>

    <div>
      <p className="font-mono text-[8px] tracking-[0.2em] text-zinc-600">
        {title.toUpperCase()}
      </p>

      <h3 className="mt-2 text-xl font-semibold text-white">{value}</h3>

      <p className="mt-2 text-xs leading-5 text-zinc-600">
        {description}
      </p>
    </div>
  </div>
</motion.div>


);
}
