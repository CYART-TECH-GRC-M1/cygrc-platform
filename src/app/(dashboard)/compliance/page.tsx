"use client";

import React from "react";
import { Card, CardContent, CardHeader } from "@heroui/react";
import { motion } from "framer-motion";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
} from "recharts";

import {
  ClipboardCheck,
  ShieldCheck,
  FileCheck,
  AlertTriangle,
  TrendingUp,
  ArrowUpRight,
  CheckCircle2,
  Clock3,
  Sparkles,
  Activity,
} from "lucide-react";

/* =========================================================
   CYGRC COMPLIANCE DATA
========================================================= */

const complianceTrend = [
  { month: "Mar", score: 68 },
  { month: "Apr", score: 72 },
  { month: "May", score: 75 },
  { month: "Jun", score: 79 },
  { month: "Jul", score: 83 },
  { month: "Aug", score: 87 },
];

const frameworkData = [
  {
    name: "ISO 27001",
    score: 94,
    color: "#22c55e",
  },
  {
    name: "SOC 2",
    score: 89,
    color: "#4ade80",
  },
  {
    name: "NIST CSF",
    score: 82,
    color: "#f97316",
  },
  {
    name: "HIPAA",
    score: 76,
    color: "#fb923c",
  },
];

/* =========================================================
   KPI DATA
========================================================= */

const kpis = [
  {
    title: "Compliance Score",
    value: "87%",
    change: "+6.4%",
    description: "vs last month",
    icon: ShieldCheck,
    iconClass:
      "border-green-500/20 bg-green-500/10 text-green-400",
    valueClass: "text-green-400",
  },
  {
    title: "Active Controls",
    value: "124",
    change: "+12",
    description: "controls monitored",
    icon: ClipboardCheck,
    iconClass:
      "border-orange-500/20 bg-orange-500/10 text-orange-400",
    valueClass: "text-orange-400",
  },
  {
    title: "Requirements",
    value: "86",
    change: "+8%",
    description: "requirements tracked",
    icon: FileCheck,
    iconClass:
      "border-orange-500/20 bg-orange-500/10 text-orange-400",
    valueClass: "text-orange-400",
  },
  {
    title: "Open Issues",
    value: "7",
    change: "-18%",
    description: "requires attention",
    icon: AlertTriangle,
    iconClass:
      "border-red-500/20 bg-red-500/10 text-red-400",
    valueClass: "text-red-400",
  },
];

/* =========================================================
   CYGRC CARD STYLE
========================================================= */

const cardClass =
  "border border-[#1b2922] bg-[#0c110f] shadow-[0_10px_35px_rgba(0,0,0,0.25)]";

/* =========================================================
   PAGE
========================================================= */

export default function CompliancePage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[#050807] text-slate-100">
      {/* =====================================================
          BACKGROUND CYBER GLOW
      ===================================================== */}

      <div className="pointer-events-none absolute -right-32 top-20 h-96 w-96 rounded-full bg-orange-500/5 blur-3xl" />

      <div className="pointer-events-none absolute left-1/4 top-1/2 h-96 w-96 rounded-full bg-green-500/5 blur-3xl" />

      <div className="pointer-events-none absolute bottom-0 right-1/3 h-80 w-80 rounded-full bg-orange-500/5 blur-3xl" />

      <div className="relative space-y-7 p-6 lg:p-9">

        {/* =====================================================
            HEADER
        ===================================================== */}

        <motion.div
          initial={{ opacity: 0, y: -15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className={`${cardClass} relative overflow-hidden rounded-2xl p-6`}
        >
          {/* Top cyber line */}
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-orange-500/50 to-transparent" />

          <div className="absolute -right-20 -top-20 h-48 w-48 rounded-full bg-orange-500/10 blur-3xl" />

          <div className="absolute -bottom-20 left-1/3 h-48 w-48 rounded-full bg-green-500/10 blur-3xl" />

          <div className="relative flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">

            {/* TITLE */}

            <div>
              <div className="mb-3 flex items-center gap-3">

                <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-orange-500/20 bg-orange-500/10 text-orange-400 shadow-[0_0_20px_rgba(249,115,22,0.08)]">
                  <ShieldCheck size={22} />
                </div>

                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 animate-pulse rounded-full bg-green-400 shadow-[0_0_10px_rgba(34,197,94,0.8)]" />

                  <span className="text-xs font-semibold uppercase tracking-wider text-green-400">
                    Live Monitoring
                  </span>
                </div>
              </div>

              <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
                Compliance Overview
              </h1>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
                Monitor compliance posture, control effectiveness, and
                organizational readiness across frameworks.
              </p>
            </div>

            {/* STATUS */}

            <motion.div
              whileHover={{ y: -3 }}
              className="flex items-center gap-3 rounded-xl border border-green-500/20 bg-green-500/5 px-4 py-3"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-green-500/20 bg-green-500/10 text-green-400">
                <Activity size={19} />
              </div>

              <div>
                <p className="text-xs text-slate-500">
                  Overall Status
                </p>

                <p className="mt-1 text-sm font-bold text-green-400">
                  Healthy & Improving
                </p>
              </div>
            </motion.div>
          </div>
        </motion.div>

        {/* =====================================================
            KPI CARDS
        ===================================================== */}

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {kpis.map((item, index) => {
            const Icon = item.icon;

            return (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{
                  delay: index * 0.08,
                  duration: 0.45,
                }}
                whileHover={{
                  y: -4,
                  transition: { duration: 0.2 },
                }}
                className="group"
              >
                <Card
                  className={`${cardClass} relative overflow-hidden rounded-xl transition-all duration-300 hover:border-orange-500/20 hover:shadow-[0_10px_40px_rgba(249,115,22,0.08)]`}
                >
                  {/* Hover glow */}

                  <div className="pointer-events-none absolute -right-12 -top-12 h-28 w-28 rounded-full bg-orange-500/5 blur-2xl transition-all group-hover:bg-orange-500/10" />

                  <CardContent className="relative p-5">

                    <div className="flex items-start justify-between">

                      <div>
                        <p className="text-sm font-medium text-slate-400">
                          {item.title}
                        </p>

                        <motion.p
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{
                            delay: 0.2 + index * 0.08,
                          }}
                          className={`mt-3 text-3xl font-bold tracking-tight ${item.valueClass}`}
                        >
                          {item.value}
                        </motion.p>
                      </div>

                      <motion.div
                        whileHover={{
                          rotate: 8,
                          scale: 1.08,
                        }}
                        className={`flex h-11 w-11 items-center justify-center rounded-xl border ${item.iconClass}`}
                      >
                        <Icon size={21} />
                      </motion.div>
                    </div>

                    <div className="mt-5 flex items-center gap-2 text-xs">

                      <span className="inline-flex items-center gap-1 font-semibold text-green-400">
                        <ArrowUpRight size={13} />
                        {item.change}
                      </span>

                      <span className="text-slate-500">
                        {item.description}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>

        {/* =====================================================
            CHART + HEALTH
        ===================================================== */}

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">

          {/* ===================================================
              COMPLIANCE TREND
          =================================================== */}

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{
              delay: 0.3,
              duration: 0.5,
            }}
            className="xl:col-span-2"
          >
            <Card
              className={`${cardClass} h-full rounded-xl`}
            >
              <CardHeader className="flex items-start justify-between px-6 pt-6">

                <div>
                  <h2 className="text-lg font-semibold text-white">
                    Compliance Trend
                  </h2>

                  <p className="mt-1 text-sm text-slate-500">
                    Overall compliance score over the last six months
                  </p>
                </div>

                <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-orange-500/20 bg-orange-500/10 text-orange-400">
                  <TrendingUp size={19} />
                </div>
              </CardHeader>

              <CardContent className="px-4 pb-5 pt-2 sm:px-6">

                <div className="h-[300px]">

                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                  >
                    <AreaChart
                      data={complianceTrend}
                      margin={{
                        top: 15,
                        right: 10,
                        left: -15,
                        bottom: 5,
                      }}
                    >

                      <defs>
                        <linearGradient
                          id="cygrcComplianceGradient"
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="1"
                        >
                          <stop
                            offset="0%"
                            stopColor="#22c55e"
                            stopOpacity={0.35}
                          />

                          <stop
                            offset="50%"
                            stopColor="#f97316"
                            stopOpacity={0.15}
                          />

                          <stop
                            offset="100%"
                            stopColor="#050807"
                            stopOpacity={0}
                          />
                        </linearGradient>
                      </defs>

                      <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#1b2922"
                        vertical={false}
                      />

                      <XAxis
                        dataKey="month"
                        axisLine={false}
                        tickLine={false}
                        tick={{
                          fill: "#64748b",
                          fontSize: 12,
                        }}
                      />

                      <YAxis
                        domain={[50, 100]}
                        axisLine={false}
                        tickLine={false}
                        tick={{
                          fill: "#64748b",
                          fontSize: 12,
                        }}
                      />

                      <Tooltip
                        contentStyle={{
                          borderRadius: "10px",
                          border: "1px solid #1b2922",
                          backgroundColor: "#0c110f",
                          color: "#ffffff",
                          boxShadow:
                            "0 15px 40px rgba(0,0,0,0.35)",
                        }}
                        labelStyle={{
                          color: "#94a3b8",
                        }}
                        itemStyle={{
                          color: "#22c55e",
                        }}
                        formatter={(value) => [
                          `${value}%`,
                          "Compliance",
                        ]}
                      />

                      <Area
                        type="monotone"
                        dataKey="score"
                        stroke="#22c55e"
                        strokeWidth={3}
                        fill="url(#cygrcComplianceGradient)"
                        dot={{
                          r: 4,
                          fill: "#0c110f",
                          stroke: "#22c55e",
                          strokeWidth: 2,
                        }}
                        activeDot={{
                          r: 6,
                          fill: "#f97316",
                          stroke: "#ffffff",
                          strokeWidth: 2,
                        }}
                      />

                    </AreaChart>
                  </ResponsiveContainer>

                </div>

                {/* SCORE SUMMARY */}

                <div className="flex flex-col gap-4 rounded-xl border border-green-500/10 bg-green-500/5 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">

                  <div>
                    <p className="text-xs text-slate-500">
                      Current score
                    </p>

                    <p className="mt-1 text-xl font-bold text-green-400">
                      87%
                    </p>
                  </div>

                  <div className="sm:text-right">
                    <p className="text-xs text-slate-500">
                      Six-month improvement
                    </p>

                    <p className="mt-1 text-sm font-bold text-orange-400">
                      +19%
                    </p>
                  </div>

                </div>

              </CardContent>
            </Card>
          </motion.div>

          {/* ===================================================
              COMPLIANCE HEALTH
          =================================================== */}

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{
              delay: 0.4,
              duration: 0.5,
            }}
          >
            <Card
              className={`${cardClass} h-full rounded-xl`}
            >

              <CardHeader className="px-6 pt-6">

                <div>
                  <h2 className="text-lg font-semibold text-white">
                    Compliance Health
                  </h2>

                  <p className="mt-1 text-sm text-slate-500">
                    Overall organizational posture
                  </p>
                </div>

              </CardHeader>

              <CardContent className="flex flex-col items-center px-6 pb-6">

                <div className="relative mt-2 h-[220px] w-[220px]">

                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                  >
                    <RadialBarChart
                      cx="50%"
                      cy="50%"
                      innerRadius="72%"
                      outerRadius="100%"
                      barSize={18}
                      startAngle={90}
                      endAngle={-270}
                      data={[
                        {
                          name: "Compliance",
                          value: 87,
                          fill: "#22c55e",
                        },
                      ]}
                    >

                      <PolarAngleAxis
                        type="number"
                        domain={[0, 100]}
                        angleAxisId={0}
                        tick={false}
                      />

                      <RadialBar
                        background={{
                          fill: "#1b2922",
                        }}
                        dataKey="value"
                        cornerRadius={12}
                      />

                    </RadialBarChart>
                  </ResponsiveContainer>

                  <div className="absolute inset-0 flex flex-col items-center justify-center">

                    <span className="text-4xl font-bold text-white">
                      87%
                    </span>

                    <span className="mt-1 flex items-center gap-1 text-xs font-semibold text-green-400">
                      <span className="h-1.5 w-1.5 rounded-full bg-green-400" />
                      Healthy
                    </span>

                  </div>

                </div>

                <div className="grid w-full grid-cols-2 gap-3">

                  <div className="rounded-xl border border-green-500/10 bg-green-500/5 p-3">

                    <p className="text-xs text-slate-500">
                      Passing
                    </p>

                    <p className="mt-1 text-lg font-bold text-green-400">
                      108
                    </p>

                  </div>

                  <div className="rounded-xl border border-orange-500/10 bg-orange-500/5 p-3">

                    <p className="text-xs text-slate-500">
                      Attention
                    </p>

                    <p className="mt-1 text-lg font-bold text-orange-400">
                      16
                    </p>

                  </div>

                </div>

              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* =====================================================
            FRAMEWORK PERFORMANCE
        ===================================================== */}

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            delay: 0.5,
            duration: 0.5,
          }}
        >
          <Card
            className={`${cardClass} rounded-xl`}
          >

            <CardHeader className="flex items-center justify-between px-6 pt-6">

              <div>
                <h2 className="text-lg font-semibold text-white">
                  Framework Performance
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Compliance performance across active frameworks
                </p>
              </div>

              <div className="hidden h-10 w-10 items-center justify-center rounded-xl border border-orange-500/20 bg-orange-500/10 text-orange-400 sm:flex">
                <FileCheck size={19} />
              </div>

            </CardHeader>

            <CardContent className="grid grid-cols-1 gap-4 px-6 pb-6 md:grid-cols-2 xl:grid-cols-4">

              {frameworkData.map((framework, index) => (

                <motion.div
                  key={framework.name}
                  initial={{
                    opacity: 0,
                    scale: 0.95,
                  }}
                  animate={{
                    opacity: 1,
                    scale: 1,
                  }}
                  transition={{
                    delay: 0.55 + index * 0.08,
                  }}
                  whileHover={{
                    y: -3,
                  }}
                  className="rounded-xl border border-[#1b2922] bg-[#111714] p-4 transition-all hover:border-orange-500/20 hover:shadow-[0_8px_30px_rgba(249,115,22,0.06)]"
                >

                  <div className="flex items-center justify-between">

                    <div>
                      <p className="text-sm font-semibold text-slate-200">
                        {framework.name}
                      </p>

                      <p className="mt-1 text-xs text-slate-500">
                        Compliance score
                      </p>
                    </div>

                    <span
                      className="text-xl font-bold"
                      style={{
                        color: framework.color,
                      }}
                    >
                      {framework.score}%
                    </span>

                  </div>

                  {/* PROGRESS */}

                  <div className="mt-4 h-2 overflow-hidden rounded-full bg-[#1b2922]">

                    <motion.div
                      initial={{
                        width: 0,
                      }}
                      animate={{
                        width: `${framework.score}%`,
                      }}
                      transition={{
                        delay: 0.7 + index * 0.08,
                        duration: 0.8,
                      }}
                      className="h-full rounded-full"
                      style={{
                        backgroundColor: framework.color,
                      }}
                    />

                  </div>

                  {/* STATUS */}

                  <div className="mt-3 flex items-center justify-between">

                    <span className="text-xs text-slate-500">
                      Status
                    </span>

                    {framework.score >= 85 ? (
                      <span className="flex items-center gap-1 text-xs font-semibold text-green-400">
                        <CheckCircle2 size={13} />
                        Strong
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-xs font-semibold text-orange-400">
                        <Clock3 size={13} />
                        Improving
                      </span>
                    )}

                  </div>

                </motion.div>

              ))}

            </CardContent>
          </Card>
        </motion.div>

        {/* =====================================================
            BOTTOM STATUS
        ===================================================== */}

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
            delay: 0.7,
          }}
          className="flex flex-wrap items-center justify-center gap-2 rounded-xl border border-green-500/10 bg-green-500/5 py-3 text-xs text-slate-500"
        >

          <Sparkles
            size={14}
            className="text-orange-400"
          />

          <span>
            Compliance intelligence updated continuously
          </span>

          <span className="h-1.5 w-1.5 rounded-full bg-green-400 shadow-[0_0_8px_rgba(34,197,94,0.7)]" />

          <span className="font-semibold text-green-400">
            All systems operational
          </span>

        </motion.div>

      </div>
    </main>
  );
}