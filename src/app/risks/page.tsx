"use client";

import React from "react";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  ShieldAlert,
  Clock3,
  CheckCircle2,
  TrendingUp,
  Plus,
  Sparkles,
} from "lucide-react";

import PageShell from "../../components/ui/PageShell";
import RiskTable from "../../components/risks/RiskTable";
import RequirementList from "../../components/risks/RequirementList";

const riskStats = [
  {
    title: "Total Risks",
    value: "142",
    change: "+8%",
    description: "vs last month",
    icon: ShieldAlert,
    iconClass:
      "bg-orange-100 text-orange-600 dark:bg-orange-500/10 dark:text-orange-400",
    positive: false,
  },
  {
    title: "Critical Risks",
    value: "12",
    change: "-6%",
    description: "requires immediate action",
    icon: AlertTriangle,
    iconClass:
      "bg-red-100 text-red-600 dark:bg-red-500/10 dark:text-red-400",
    positive: true,
  },
  {
    title: "In Progress",
    value: "38",
    change: "+4%",
    description: "currently being treated",
    icon: Clock3,
    iconClass:
      "bg-amber-100 text-amber-600 dark:bg-amber-500/10 dark:text-amber-400",
    positive: false,
  },
  {
    title: "Resolved",
    value: "92",
    change: "+12%",
    description: "risks successfully closed",
    icon: CheckCircle2,
    iconClass:
      "bg-green-100 text-green-600 dark:bg-green-500/10 dark:text-green-400",
    positive: true,
  },
];

const riskTrend = [
  { month: "Mar", value: 72 },
  { month: "Apr", value: 64 },
  { month: "May", value: 58 },
  { month: "Jun", value: 52 },
  { month: "Jul", value: 46 },
  { month: "Aug", value: 39 },
];

export default function RisksPage() {
  return (
    <PageShell
      title="Risk Management"
      subtitle="Track, assess, and manage organizational risks with enterprise-grade oversight."
    >
      <div className="w-full space-y-7">

        {/* ================================================= */}
        {/* KPI CARDS */}
        {/* ================================================= */}

        <div className="grid w-full grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
          {riskStats.map((stat, index) => {
            const Icon = stat.icon;

            return (
              <motion.div
                key={stat.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{
                  delay: index * 0.08,
                  duration: 0.5,
                  ease: "easeOut",
                }}
                whileHover={{
                  y: -5,
                  transition: { duration: 0.2 },
                }}
                className="
                  group relative overflow-hidden
                  rounded-2xl
                  border border-slate-200
                  bg-white
                  p-6
                  shadow-sm
                  transition-all duration-300
                  hover:border-orange-200
                  hover:shadow-xl hover:shadow-orange-500/10
                  dark:border-slate-800
                  dark:bg-slate-900
                  dark:hover:border-orange-500/20
                "
              >
                {/* Decorative glow */}
                <div
                  className="
                    pointer-events-none absolute -right-10 -top-10
                    h-24 w-24 rounded-full
                    bg-orange-500/5 blur-2xl
                    transition-all duration-300
                    group-hover:bg-orange-500/10
                  "
                />

                <div className="relative flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
                      {stat.title}
                    </p>

                    <motion.h2
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{
                        delay: 0.2 + index * 0.08,
                      }}
                      className="
                        mt-2 text-3xl font-bold tracking-tight
                        text-slate-900 dark:text-white
                      "
                    >
                      {stat.value}
                    </motion.h2>
                  </div>

                  <motion.div
                    whileHover={{
                      rotate: 6,
                      scale: 1.05,
                    }}
                    className={`
                      flex h-11 w-11 items-center justify-center
                      rounded-xl
                      ${stat.iconClass}
                    `}
                  >
                    <Icon size={22} />
                  </motion.div>
                </div>

                <div className="relative mt-4 flex items-center gap-2 text-xs">
                  <span
                    className={
                      stat.positive
                        ? "font-semibold text-green-600 dark:text-green-400"
                        : "font-semibold text-orange-600 dark:text-orange-400"
                    }
                  >
                    {stat.change}
                  </span>

                  <span className="text-slate-400">
                    {stat.description}
                  </span>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* ================================================= */}
        {/* RISK OVERVIEW */}
        {/* ================================================= */}

        <div className="grid w-full grid-cols-1 gap-6 lg:grid-cols-3">

          {/* ================================================= */}
          {/* RISK TREND */}
          {/* ================================================= */}

          <motion.div
            initial={{ opacity: 0, y: 25 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              delay: 0.3,
              duration: 0.5,
            }}
            className="
              group relative overflow-hidden
              rounded-2xl
              border border-slate-200
              bg-white
              p-6
              shadow-sm
              transition-all duration-300
              hover:border-orange-200
              hover:shadow-xl hover:shadow-orange-500/5
              dark:border-slate-800
              dark:bg-slate-900
              dark:hover:border-orange-500/20
            "
          >
            <div
              className="
                pointer-events-none absolute
                -right-20 -top-20
                h-40 w-40 rounded-full
                bg-orange-500/5 blur-3xl
              "
            />

            <div className="relative flex items-start justify-between">
              <div>
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                  Risk Trend
                </h2>

                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  Open risk trend over the last six months
                </p>
              </div>

              <div
                className="
                  flex h-10 w-10 items-center justify-center
                  rounded-xl
                  bg-orange-100
                  text-orange-600
                  dark:bg-orange-500/10
                  dark:text-orange-400
                "
              >
                <TrendingUp size={19} />
              </div>
            </div>

            {/* Chart */}
            <div className="relative mt-7 h-56 w-full">

              {/* Grid */}
              <div className="absolute inset-0 flex flex-col justify-between">
                {[100, 75, 50, 25, 0].map((value) => (
                  <div
                    key={value}
                    className="flex items-center gap-3"
                  >
                    <span className="w-8 text-right text-[10px] text-slate-400">
                      {value}
                    </span>

                    <div className="h-px flex-1 bg-slate-100 dark:bg-slate-800" />
                  </div>
                ))}
              </div>

              {/* Bars */}
              <div
                className="
                  absolute bottom-0 left-12 right-0 top-0
                  flex items-end justify-between
                  gap-4 px-3
                "
              >
                {riskTrend.map((item, index) => {
                  const height = `${item.value * 1.65}px`;

                  return (
                    <div
                      key={item.month}
                      className="
                        flex h-full flex-1
                        flex-col items-center justify-end
                      "
                    >
                      <motion.div
                        initial={{
                          height: 0,
                          opacity: 0,
                        }}
                        animate={{
                          height,
                          opacity: 1,
                        }}
                        transition={{
                          delay: 0.45 + index * 0.08,
                          duration: 0.7,
                          ease: "easeOut",
                        }}
                        whileHover={{
                          scaleX: 1.08,
                          filter: "brightness(1.1)",
                        }}
                        className="
                          w-full max-w-[48px]
                          rounded-t-xl
                          bg-gradient-to-t
                          from-green-600
                          via-emerald-500
                          to-orange-400
                          shadow-lg
                          shadow-orange-500/10
                          transition-all
                        "
                      />

                      <span className="mt-3 text-xs font-medium text-slate-400">
                        {item.month}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Chart Summary */}
            <div
              className="
                mt-5 flex items-center justify-between
                rounded-xl
                border border-orange-100
                bg-orange-50
                px-4 py-3
                dark:border-orange-500/10
                dark:bg-orange-500/5
              "
            >
              <div>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Current open risks
                </p>

                <p className="mt-1 text-lg font-semibold text-slate-900 dark:text-white">
                  39
                </p>
              </div>

              <div className="text-right">
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Reduction
                </p>

                <p className="mt-1 text-sm font-semibold text-green-600 dark:text-green-400">
                  46% lower
                </p>
              </div>
            </div>
          </motion.div>

          {/* ================================================= */}
          {/* RISK DISTRIBUTION */}
          {/* ================================================= */}

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{
              delay: 0.4,
              duration: 0.5,
            }}
            className="
              relative overflow-hidden
              rounded-2xl
              border border-slate-200
              bg-white
              p-6
              shadow-sm
              transition-all duration-300
              hover:border-green-200
              hover:shadow-xl hover:shadow-green-500/5
              dark:border-slate-800
              dark:bg-slate-900
              dark:hover:border-green-500/20
            "
          >
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                  Risk Distribution
                </h2>

                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  Current risk severity
                </p>
              </div>

              <ShieldAlert
                size={20}
                className="text-orange-600 dark:text-orange-400"
              />
            </div>

            {/* Circular score */}
            <div className="mt-8 flex justify-center">
              <motion.div
                initial={{
                  rotate: -90,
                  scale: 0.8,
                  opacity: 0,
                }}
                animate={{
                  rotate: 0,
                  scale: 1,
                  opacity: 1,
                }}
                transition={{
                  delay: 0.5,
                  duration: 0.8,
                  ease: "easeOut",
                }}
                whileHover={{
                  scale: 1.04,
                }}
                className="
                  relative flex h-40 w-40
                  items-center justify-center
                  rounded-full
                  bg-[conic-gradient(#f97316_0deg,#fb923c_90deg,#22c55e_190deg,#16a34a_270deg,#e2e8f0_300deg)]
                  shadow-xl
                  shadow-orange-500/10
                "
              >
                <div
                  className="
                    flex h-32 w-32
                    flex-col items-center justify-center
                    rounded-full
                    bg-white
                    dark:bg-slate-900
                  "
                >
                  <span className="text-3xl font-bold text-slate-900 dark:text-white">
                    72%
                  </span>

                  <span className="mt-1 text-xs text-slate-500">
                    Risk Health
                  </span>
                </div>
              </motion.div>
            </div>

            {/* Legend */}
            <div className="mt-7 space-y-3">
              <RiskLegend
                label="Critical"
                value="12"
                className="bg-red-500"
              />

              <RiskLegend
                label="High"
                value="24"
                className="bg-orange-500"
              />

              <RiskLegend
                label="Medium"
                value="51"
                className="bg-amber-400"
              />

              <RiskLegend
                label="Low"
                value="55"
                className="bg-green-500"
              />
            </div>
          </motion.div>

          {/* ================================================= */}
          {/* RISK HEALTH CARD */}
          {/* ================================================= */}

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{
              delay: 0.5,
              duration: 0.5,
            }}
            whileHover={{
              y: -4,
            }}
            className="
              group relative overflow-hidden
              rounded-2xl
              border border-slate-200
              bg-gradient-to-br
              from-orange-50
              via-white
              to-green-50
              p-6
              shadow-sm
              transition-all duration-300
              hover:border-green-200
              hover:shadow-xl
              hover:shadow-green-500/10
              dark:border-slate-800
              dark:from-orange-500/10
              dark:via-slate-900
              dark:to-green-500/10
              dark:hover:border-green-500/20
            "
          >
            <div
              className="
                pointer-events-none absolute
                -right-16 -top-16
                h-36 w-36 rounded-full
                bg-green-500/10 blur-3xl
              "
            />

            <div className="relative">
              <div className="flex items-center gap-3">
                <div
                  className="
                    flex h-11 w-11
                    items-center justify-center
                    rounded-xl
                    bg-gradient-to-br
                    from-orange-500
                    to-green-600
                    text-white
                    shadow-lg
                    shadow-green-500/20
                  "
                >
                  <CheckCircle2 size={22} />
                </div>

                <div>
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                    Risk Health
                  </h2>

                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Overall organizational status
                  </p>
                </div>
              </div>

              <div className="mt-8">
                <div className="flex items-end justify-between">
                  <div>
                    <span className="text-5xl font-bold tracking-tight text-slate-900 dark:text-white">
                      72
                    </span>

                    <span className="ml-1 text-lg font-medium text-slate-400">
                      /100
                    </span>
                  </div>

                  <span
                    className="
                      rounded-full
                      bg-green-100
                      px-3 py-1
                      text-xs font-semibold
                      text-green-700
                      dark:bg-green-500/10
                      dark:text-green-400
                    "
                  >
                    Healthy
                  </span>
                </div>

                {/* Progress */}
                <div className="mt-5 h-2.5 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: "72%" }}
                    transition={{
                      delay: 0.7,
                      duration: 1,
                      ease: "easeOut",
                    }}
                    className="
                      h-full rounded-full
                      bg-gradient-to-r
                      from-orange-500
                      via-amber-500
                      to-green-500
                    "
                  />
                </div>

                <p className="mt-4 text-sm leading-6 text-slate-500 dark:text-slate-400">
                  Risk exposure is trending downward. Continue focusing on
                  critical and high-severity risks.
                </p>
              </div>

              <div
                className="
                  mt-6 flex items-center justify-between
                  border-t border-slate-200/80
                  pt-4
                  dark:border-slate-800
                "
              >
                <span className="text-xs text-slate-500 dark:text-slate-400">
                  Health score
                </span>

                <span className="text-sm font-semibold text-green-600 dark:text-green-400">
                  +8.4% this month
                </span>
              </div>
            </div>
          </motion.div>
        </div>

        {/* ================================================= */}
        {/* REQUIREMENTS */}
        {/* ================================================= */}

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            delay: 0.6,
            duration: 0.5,
          }}
          className="
            relative w-full overflow-hidden
            rounded-2xl
            border border-slate-200
            bg-white
            p-6
            shadow-sm
            transition-all duration-300
            hover:border-orange-200
            hover:shadow-xl hover:shadow-orange-500/5
            dark:border-slate-800
            dark:bg-slate-900
            dark:hover:border-orange-500/20
          "
        >
          <div
            className="
              pointer-events-none absolute
              -right-16 -top-16
              h-32 w-32 rounded-full
              bg-orange-500/5 blur-3xl
            "
          />

          <div className="relative mb-5 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                Visible Requirements
              </h2>

              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                Key compliance requirements related to risk management.
              </p>
            </div>

            <span
              className="
                rounded-full
                bg-orange-100
                px-3 py-1
                text-xs font-semibold
                text-orange-700
                dark:bg-orange-500/10
                dark:text-orange-300
              "
            >
              3 active items
            </span>
          </div>

          <div className="relative">
            <RequirementList />
          </div>
        </motion.div>

        {/* ================================================= */}
        {/* RISK REGISTER */}
        {/* ================================================= */}

        <motion.div
          initial={{
            opacity: 0,
            y: 25,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          transition={{
            delay: 0.7,
            duration: 0.55,
          }}
          className="w-full"
        >
          <div
            className="
              group relative w-full overflow-hidden
              rounded-2xl
              border border-slate-200
              bg-white
              shadow-sm
              transition-all duration-300
              hover:border-orange-200
              hover:shadow-xl
              hover:shadow-orange-500/5
              dark:border-slate-800
              dark:bg-slate-900
              dark:hover:border-orange-500/20
            "
          >
            {/* Decorative glow */}
            <div
              className="
                pointer-events-none absolute
                -right-24 -top-24
                h-48 w-48 rounded-full
                bg-orange-500/10 blur-3xl
              "
            />

            {/* Header */}
            <div
              className="
                relative flex flex-col gap-4
                border-b border-slate-200
                px-6 py-5
                sm:flex-row
                sm:items-center
                sm:justify-between
                dark:border-slate-800
              "
            >
              <div className="flex items-start gap-4">
                <div
                  className="
                    hidden h-11 w-11 shrink-0
                    items-center justify-center
                    rounded-xl
                    bg-gradient-to-br
                    from-orange-500
                    to-green-600
                    text-white
                    shadow-lg
                    shadow-green-500/20
                    sm:flex
                  "
                >
                  <ShieldAlert size={21} />
                </div>

                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                      Risk Register
                    </h2>

                    <span
                      className="
                        hidden items-center gap-1
                        rounded-full
                        bg-green-50
                        px-2 py-1
                        text-[10px]
                        font-semibold
                        text-green-600
                        sm:inline-flex
                        dark:bg-green-500/10
                        dark:text-green-400
                      "
                    >
                      <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                      Live
                    </span>
                  </div>

                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    Search, filter, and manage organizational risks.
                  </p>
                </div>
              </div>

              {/* Add Risk */}
              <motion.button
                type="button"
                whileHover={{
                  scale: 1.03,
                  boxShadow:
                    "0 12px 30px rgba(249,115,22,0.25)",
                }}
                whileTap={{
                  scale: 0.97,
                }}
                className="
                  inline-flex
                  items-center
                  justify-center
                  gap-2
                  rounded-xl
                  bg-gradient-to-r
                  from-orange-500
                  via-orange-600
                  to-green-600
                  px-4
                  py-2.5
                  text-sm
                  font-semibold
                  text-white
                  shadow-md
                  shadow-orange-500/20
                  transition-all
                  hover:from-orange-600
                  hover:to-green-700
                "
              >
                <Plus size={17} />
                Add Risk
              </motion.button>
            </div>

            {/* Table */}
            <div className="relative w-full overflow-x-auto p-4 sm:p-6">
              <RiskTable />
            </div>
          </div>
        </motion.div>

        {/* ================================================= */}
        {/* BOTTOM STATUS */}
        {/* ================================================= */}

        <motion.div
          initial={{
            opacity: 0,
            y: 10,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          transition={{
            delay: 0.85,
          }}
          className="
            flex items-center justify-center
            gap-2
            text-xs text-slate-400
          "
        >
          <Sparkles
            size={14}
            className="text-orange-500"
          />

          Risk intelligence updated continuously

          <span className="h-1 w-1 rounded-full bg-green-500" />

          <span className="text-green-500">
            System healthy
          </span>
        </motion.div>
      </div>
    </PageShell>
  );
}

/* ========================================================= */
/* RISK LEGEND */
/* ========================================================= */

type RiskLegendProps = {
  label: string;
  value: string;
  className: string;
};

function RiskLegend({
  label,
  value,
  className,
}: RiskLegendProps) {
  return (
    <motion.div
      whileHover={{
        x: 3,
      }}
      className="
        flex items-center justify-between
        rounded-lg
        px-2 py-1.5
        transition-colors
        hover:bg-orange-50
        dark:hover:bg-slate-800/50
      "
    >
      <div className="flex items-center gap-3">
        <span
          className={`
            h-2.5 w-2.5 rounded-full
            ${className}
          `}
        />

        <span className="text-sm text-slate-600 dark:text-slate-300">
          {label}
        </span>
      </div>

      <span className="text-sm font-semibold text-slate-900 dark:text-white">
        {value}
      </span>
    </motion.div>
  );
}