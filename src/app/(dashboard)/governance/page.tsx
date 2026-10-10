"use client";

import { motion } from "framer-motion";
import {
  Landmark,
  ShieldCheck,
  Users,
  ClipboardList,
  CheckCircle2,
  AlertTriangle,
  CalendarDays,
  FileCheck2,
  ArrowUpRight,
} from "lucide-react";
import PageShell from "@/components/ui/PageShell";

const stats = [
  {
    title: "Governance Score",
    value: "94%",
    icon: ShieldCheck,
    color: "emerald",
    change: "+4%",
  },
  {
    title: "Policies",
    value: "128",
    icon: ClipboardList,
    color: "orange",
    change: "+8",
  },
  {
    title: "Board Members",
    value: "14",
    icon: Users,
    color: "emerald",
    change: "+1",
  },
  {
    title: "Open Reviews",
    value: "9",
    icon: Landmark,
    color: "orange",
    change: "-2",
  },
];

const policies = [
  {
    name: "Information Security Policy",
    owner: "CISO",
    status: "Approved",
  },
  {
    name: "Risk Management Policy",
    owner: "Risk Office",
    status: "Under Review",
  },
  {
    name: "Data Privacy Policy",
    owner: "Compliance",
    status: "Approved",
  },
  {
    name: "Vendor Security Policy",
    owner: "Procurement",
    status: "Draft",
  },
];

const activities = [
  "Board meeting completed",
  "Quarterly policy review finished",
  "Risk committee meeting scheduled",
  "Internal audit approved",
];

export default function GovernancePage() {
  return (
    <PageShell
      title="Governance"
      subtitle="Manage organizational governance, board oversight, policies, and strategic controls."
    >
      <div className="space-y-6">

        {/* KPI Cards */}
        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
          {stats.map((item, index) => {
            const Icon = item.icon;
            const orange = item.color === "orange";

            return (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.08 }}
                className={`rounded-2xl border bg-[#080807] p-6 ${
                  orange
                    ? "border-orange-500/20"
                    : "border-emerald-500/20"
                }`}
              >
                <div className="flex items-start justify-between">

                  <div>
                    <p className="text-xs tracking-widest text-zinc-500 uppercase">
                      {item.title}
                    </p>

                    <h2 className="mt-3 text-3xl font-bold text-white">
                      {item.value}
                    </h2>

                    <p className="mt-2 text-sm text-emerald-400">
                      {item.change}
                    </p>
                  </div>

                  <div
                    className={`flex h-12 w-12 items-center justify-center rounded-xl ${
                      orange
                        ? "bg-orange-500/10 text-orange-400"
                        : "bg-emerald-500/10 text-emerald-400"
                    }`}
                  >
                    <Icon size={24} />
                  </div>

                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Governance Domains */}
        <div className="grid gap-6 lg:grid-cols-2">

          <div className="rounded-2xl border border-orange-500/15 bg-[#080807] p-6">

            <p className="text-xs tracking-widest text-orange-400 uppercase">
              Governance Domains
            </p>

            <h2 className="mt-2 text-xl font-semibold text-white">
              Core Governance Areas
            </h2>

            <div className="mt-6 space-y-4">

              <Domain title="Corporate Governance" />

              <Domain title="Risk Oversight" />

              <Domain title="Cyber Security Governance" />

              <Domain title="Compliance Governance" />

              <Domain title="Business Continuity" />

            </div>

          </div>

          <div className="rounded-2xl border border-emerald-500/15 bg-[#080807] p-6">

            <p className="text-xs tracking-widest text-emerald-400 uppercase">
              Board Overview
            </p>

            <h2 className="mt-2 text-xl font-semibold text-white">
              Governance Committee
            </h2>

            <div className="mt-6 space-y-4">

              <BoardMember
                name="Chief Executive Officer"
                role="Chairperson"
              />

              <BoardMember
                name="Chief Information Security Officer"
                role="Security Lead"
              />

              <BoardMember
                name="Chief Risk Officer"
                role="Risk Oversight"
              />

              <BoardMember
                name="Compliance Manager"
                role="Compliance Lead"
              />

            </div>

          </div>

        </div>

        {/* Policies */}
        <div className="rounded-2xl border border-orange-500/15 bg-[#080807]">

          <div className="border-b border-orange-500/10 p-6">

            <h2 className="text-xl font-semibold text-white">
              Policy Repository
            </h2>

          </div>

          <div className="divide-y divide-orange-500/10">

            {policies.map((policy) => (

              <div
                key={policy.name}
                className="flex flex-col gap-4 p-5 md:flex-row md:items-center md:justify-between"
              >

                <div>

                  <h3 className="font-semibold text-white">
                    {policy.name}
                  </h3>

                  <p className="text-sm text-zinc-500">
                    Owner: {policy.owner}
                  </p>

                </div>

                <div className="flex items-center gap-2">

                  <CheckCircle2
                    size={18}
                    className="text-emerald-400"
                  />

                  <span className="text-sm text-zinc-300">
                    {policy.status}
                  </span>

                </div>

              </div>

            ))}

          </div>

        </div>

        {/* Bottom Section */}
        <div className="grid gap-6 lg:grid-cols-2">

          <div className="rounded-2xl border border-orange-500/15 bg-[#080807] p-6">

            <h2 className="mb-5 text-lg font-semibold text-white">
              Compliance Status
            </h2>

            <Status
              icon={<CheckCircle2 className="text-emerald-400" />}
              title="Policies Approved"
              value="92%"
            />

            <Status
              icon={<AlertTriangle className="text-orange-400" />}
              title="Pending Reviews"
              value="8%"
            />

            <Status
              icon={<FileCheck2 className="text-emerald-400" />}
              title="Audit Ready"
              value="Yes"
            />

          </div>

          <div className="rounded-2xl border border-emerald-500/15 bg-[#080807] p-6">

            <h2 className="mb-5 text-lg font-semibold text-white">
              Recent Activities
            </h2>

            {activities.map((activity) => (

              <div
                key={activity}
                className="mb-4 flex items-center justify-between rounded-xl border border-orange-500/10 p-4"
              >

                <div className="flex items-center gap-3">

                  <CalendarDays
                    size={18}
                    className="text-orange-400"
                  />

                  <span className="text-sm text-zinc-300">
                    {activity}
                  </span>

                </div>

                <ArrowUpRight
                  size={16}
                  className="text-zinc-500"
                />

              </div>

            ))}

          </div>

        </div>

      </div>
    </PageShell>
  );
}

function Domain({ title }: { title: string }) {
  return (
    <div className="rounded-xl border border-orange-500/10 bg-[#111] p-4 text-white">
      {title}
    </div>
  );
}

function BoardMember({
  name,
  role,
}: {
  name: string;
  role: string;
}) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-emerald-500/10 bg-[#111] p-4">
      <div>
        <h3 className="font-semibold text-white">{name}</h3>
        <p className="text-sm text-zinc-500">{role}</p>
      </div>
      <Users className="text-emerald-400" size={20} />
    </div>
  );
}

function Status({
  icon,
  title,
  value,
}: {
  icon: React.ReactNode;
  title: string;
  value: string;
}) {
  return (
    <div className="mb-4 flex items-center justify-between rounded-xl border border-orange-500/10 bg-[#111] p-4">
      <div className="flex items-center gap-3">
        {icon}
        <span className="text-zinc-300">{title}</span>
      </div>
      <span className="font-semibold text-white">{value}</span>
    </div>
  );
}