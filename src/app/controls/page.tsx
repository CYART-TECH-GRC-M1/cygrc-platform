"use client";

import React from "react";
import { motion } from "framer-motion";
import PageShell from "../../components/ui/PageShell";
import ControlTable from "../../components/controls/ControlTable";

import {
  BarChart3,
  ShieldCheck,
  Clock3,
  AlertTriangle,
  CheckCircle2,
  Sparkles,
  Layers3,
} from "lucide-react";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

const chartData = [
  { name: "ISO", controls: 42 },
  { name: "SOC2", controls: 36 },
  { name: "NIST", controls: 28 },
  { name: "HIPAA", controls: 18 },
];

const controlStats = [
  {
    title: "Total Controls",
    value: "124",
    description: "across all frameworks",
    icon: Layers3,
    iconBg:
      "bg-orange-100 text-orange-600 dark:bg-orange-500/10 dark:text-orange-400",
    valueColor: "text-slate-900 dark:text-white",
  },
  {
    title: "Implemented",
    value: "98",
    description: "controls operational",
    icon: CheckCircle2,
    iconBg:
      "bg-green-100 text-green-600 dark:bg-green-500/10 dark:text-green-400",
    valueColor: "text-green-600 dark:text-green-400",
  },
  {
    title: "Pending",
    value: "19",
    description: "awaiting implementation",
    icon: Clock3,
    iconBg:
      "bg-amber-100 text-amber-600 dark:bg-amber-500/10 dark:text-amber-400",
    valueColor: "text-amber-600 dark:text-amber-400",
  },
  {
    title: "Critical",
    value: "7",
    description: "requires attention",
    icon: AlertTriangle,
    iconBg:
      "bg-red-100 text-red-600 dark:bg-red-500/10 dark:text-red-400",
    valueColor: "text-red-600 dark:text-red-400",
  },
];

export default function ControlsPage() {
  return (
    <PageShell
      title="Compliance Controls"
      subtitle="Manage controls across frameworks, track implementation, and assign responsible owners."
    >
      <div className="w-full space-y-7">

        {/* ================================================= */}
        {/* KPI CARDS */}
        {/* ================================================= */}

        <div className="grid w-full grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
          {controlStats.map((stat, index) => {
            const Icon = stat.icon;

            return (
              <motion.div
                key={stat.title}
                initial={{
                  opacity: 0,
                  y: 20,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                transition={{
                  delay: index * 0.08,
                  duration: 0.5,
                  ease: "easeOut",
                }}
                whileHover={{
                  y: -5,
                  transition: {
                    duration: 0.2,
                  },
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
                  hover:shadow-xl
                  hover:shadow-orange-500/10
                  dark:border-slate-800
                  dark:bg-slate-900
                  dark:hover:border-orange-500/20
                "
              >
                {/* Decorative Glow */}
                <div
                  className="
                    pointer-events-none
                    absolute -right-10 -top-10
                    h-24 w-24
                    rounded-full
                    bg-orange-500/5
                    blur-2xl
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
                      initial={{
                        opacity: 0,
                        scale: 0.9,
                      }}
                      animate={{
                        opacity: 1,
                        scale: 1,
                      }}
                      transition={{
                        delay: 0.2 + index * 0.08,
                        duration: 0.4,
                      }}
                      className={`mt-2 text-3xl font-bold tracking-tight ${stat.valueColor}`}
                    >
                      {stat.value}
                    </motion.h2>
                  </div>

                  <motion.div
                    whileHover={{
                      scale: 1.08,
                      rotate: 5,
                    }}
                    className={`
                      flex h-11 w-11
                      items-center justify-center
                      rounded-xl
                      ${stat.iconBg}
                    `}
                  >
                    <Icon size={22} />
                  </motion.div>
                </div>

                <p className="relative mt-4 text-xs text-slate-400">
                  {stat.description}
                </p>
              </motion.div>
            );
          })}
        </div>

        {/* ================================================= */}
        {/* OVERVIEW ROW */}
        {/* ================================================= */}

        <div className="grid w-full grid-cols-1 gap-6 lg:grid-cols-3">

          {/* ================================================= */}
          {/* CONTROL COVERAGE */}
          {/* ================================================= */}

          <motion.div
            initial={{
              opacity: 0,
              y: 20,
            }}
            animate={{
              opacity: 1,
              y: 0,
            }}
            transition={{
              delay: 0.35,
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
              hover:shadow-xl
              hover:shadow-green-500/5
              dark:border-slate-800
              dark:bg-slate-900
              dark:hover:border-green-500/20
            "
          >
            <div
              className="
                pointer-events-none
                absolute -right-16 -top-16
                h-36 w-36
                rounded-full
                bg-green-500/5
                blur-3xl
              "
            />

            <div className="relative flex items-start justify-between">
              <div>
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                  Control Coverage
                </h2>

                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  Overall implementation progress
                </p>
              </div>

              <div
                className="
                  flex h-10 w-10
                  items-center justify-center
                  rounded-xl
                  bg-green-100
                  text-green-600
                  dark:bg-green-500/10
                  dark:text-green-400
                "
              >
                <ShieldCheck size={20} />
              </div>
            </div>

            {/* Percentage */}
            <div className="mt-8 flex items-end justify-between">
              <div>
                <span className="text-5xl font-bold tracking-tight text-slate-900 dark:text-white">
                  79%
                </span>

                <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                  Controls implemented
                </p>
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
            <div className="mt-6 h-2.5 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
              <motion.div
                initial={{
                  width: 0,
                }}
                animate={{
                  width: "79%",
                }}
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

            <div className="mt-5 flex items-center justify-between">
              <span className="text-xs text-slate-500 dark:text-slate-400">
                98 implemented
              </span>

              <span className="text-xs font-semibold text-orange-600 dark:text-orange-400">
                26 remaining
              </span>
            </div>
          </motion.div>

          {/* ================================================= */}
          {/* FRAMEWORK SUMMARY */}
          {/* ================================================= */}

          <motion.div
            initial={{
              opacity: 0,
              y: 20,
            }}
            animate={{
              opacity: 1,
              y: 0,
            }}
            transition={{
              delay: 0.42,
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
              hover:border-orange-200
              hover:shadow-xl
              hover:shadow-orange-500/5
              dark:border-slate-800
              dark:bg-slate-900
              dark:hover:border-orange-500/20
            "
          >
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                  Framework Coverage
                </h2>

                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  Active compliance frameworks
                </p>
              </div>

              <BarChart3
                size={20}
                className="text-orange-500"
              />
            </div>

            <div className="mt-7 space-y-5">
              {chartData.map((item, index) => {
                const percentage = Math.round(
                  (item.controls / 42) * 100
                );

                return (
                  <div key={item.name}>
                    <div className="mb-2 flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                        {item.name}
                      </span>

                      <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
                        {item.controls}
                      </span>
                    </div>

                    <div className="h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                      <motion.div
                        initial={{
                          width: 0,
                        }}
                        animate={{
                          width: `${percentage}%`,
                        }}
                        transition={{
                          delay: 0.65 + index * 0.1,
                          duration: 0.7,
                          ease: "easeOut",
                        }}
                        className={`
                          h-full rounded-full
                          ${
                            index === 0
                              ? "bg-orange-500"
                              : index === 1
                              ? "bg-green-500"
                              : index === 2
                              ? "bg-emerald-500"
                              : "bg-amber-500"
                          }
                        `}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>

          {/* ================================================= */}
          {/* CONTROL STATUS */}
          {/* ================================================= */}

          <motion.div
            initial={{
              opacity: 0,
              y: 20,
            }}
            animate={{
              opacity: 1,
              y: 0,
            }}
            transition={{
              delay: 0.49,
              duration: 0.5,
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
                pointer-events-none
                absolute -right-16 -top-16
                h-36 w-36
                rounded-full
                bg-green-500/10
                blur-3xl
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
                  <ShieldCheck size={22} />
                </div>

                <div>
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                    Control Health
                  </h2>

                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Current compliance posture
                  </p>
                </div>
              </div>

              <div className="mt-8">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-4xl font-bold text-slate-900 dark:text-white">
                      84%
                    </span>

                    <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                      Overall health
                    </p>
                  </div>

                  <div
                    className="
                      flex h-14 w-14
                      items-center justify-center
                      rounded-full
                      bg-green-100
                      dark:bg-green-500/10
                    "
                  >
                    <CheckCircle2
                      size={28}
                      className="text-green-600 dark:text-green-400"
                    />
                  </div>
                </div>

                <div className="mt-6 space-y-3">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-500 dark:text-slate-400">
                      Implemented
                    </span>

                    <span className="font-semibold text-green-600 dark:text-green-400">
                      98
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-500 dark:text-slate-400">
                      Pending
                    </span>

                    <span className="font-semibold text-amber-600 dark:text-amber-400">
                      19
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-500 dark:text-slate-400">
                      Critical
                    </span>

                    <span className="font-semibold text-red-600 dark:text-red-400">
                      7
                    </span>
                  </div>
                </div>
              </div>

              <div
                className="
                  mt-6
                  border-t
                  border-slate-200/80
                  pt-4
                  dark:border-slate-800
                "
              >
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-green-500" />

                  <span className="text-xs font-medium text-green-600 dark:text-green-400">
                    Compliance posture is healthy
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* ================================================= */}
        {/* BAR CHART */}
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
            delay: 0.55,
            duration: 0.55,
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
            hover:shadow-xl
            hover:shadow-orange-500/5
            dark:border-slate-800
            dark:bg-slate-900
            dark:hover:border-orange-500/20
          "
        >
          {/* Glow */}
          <div
            className="
              pointer-events-none
              absolute -right-20 -top-20
              h-40 w-40
              rounded-full
              bg-orange-500/5
              blur-3xl
            "
          />

          <div className="relative mb-6 flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3">
                <div
                  className="
                    flex h-10 w-10
                    items-center justify-center
                    rounded-xl
                    bg-orange-100
                    text-orange-600
                    dark:bg-orange-500/10
                    dark:text-orange-400
                  "
                >
                  <BarChart3 size={19} />
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                    Controls by Framework
                  </h3>

                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    Distribution of controls across compliance frameworks.
                  </p>
                </div>
              </div>
            </div>

            <span
              className="
                hidden rounded-full
                bg-green-100
                px-3 py-1
                text-xs font-semibold
                text-green-700
                sm:block
                dark:bg-green-500/10
                dark:text-green-400
              "
            >
              4 Frameworks
            </span>
          </div>

          <div className="relative h-80">
            <ResponsiveContainer
              width="100%"
              height="100%"
            >
              <BarChart
                data={chartData}
                margin={{
                  top: 10,
                  right: 10,
                  left: -10,
                  bottom: 0,
                }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#e2e8f0"
                  vertical={false}
                />

                <XAxis
                  dataKey="name"
                  stroke="#94a3b8"
                  tickLine={false}
                  axisLine={false}
                />

                <YAxis
                  stroke="#94a3b8"
                  tickLine={false}
                  axisLine={false}
                />

                <Tooltip
                  cursor={{
                    fill: "rgba(249,115,22,0.06)",
                  }}
                  contentStyle={{
                    backgroundColor: "#ffffff",
                    border: "1px solid #e2e8f0",
                    borderRadius: "12px",
                    boxShadow:
                      "0 10px 30px rgba(15,23,42,0.10)",
                  }}
                  labelStyle={{
                    color: "#0f172a",
                    fontWeight: 600,
                  }}
                />

                <Bar
                  dataKey="controls"
                  fill="#f97316"
                  radius={[8, 8, 0, 0]}
                  animationDuration={1200}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* ================================================= */}
        {/* CONTROL INVENTORY */}
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
            delay: 0.65,
            duration: 0.55,
          }}
          className="
            group relative overflow-hidden
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
          {/* Decorative Glow */}
          <div
            className="
              pointer-events-none
              absolute -right-24 -top-24
              h-48 w-48
              rounded-full
              bg-green-500/10
              blur-3xl
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
                <Layers3 size={21} />
              </div>

              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                    Control Inventory
                  </h3>

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
                  View, search, filter, and manage compliance controls.
                </p>
              </div>
            </div>

            {/* Status */}
            <div
              className="
                flex items-center gap-2
                rounded-xl
                border border-green-100
                bg-green-50
                px-3 py-2
                dark:border-green-500/10
                dark:bg-green-500/5
              "
            >
              <CheckCircle2
                size={16}
                className="text-green-600 dark:text-green-400"
              />

              <span className="text-xs font-semibold text-green-700 dark:text-green-400">
                98 Implemented
              </span>
            </div>
          </div>

          {/* Table */}
          <div className="relative w-full overflow-x-auto p-4 sm:p-6">
            <ControlTable />
          </div>
        </motion.div>

        {/* ================================================= */}
        {/* FOOTER STATUS */}
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
            delay: 0.8,
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

          Compliance controls monitored continuously

          <span className="h-1 w-1 rounded-full bg-green-500" />

          <span className="text-green-500">
            System healthy
          </span>
        </motion.div>
      </div>
    </PageShell>
  );
}