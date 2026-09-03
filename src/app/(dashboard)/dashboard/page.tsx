
"use client";

import { Card, CardContent, CardHeader, Chip } from "@heroui/react";
import { motion } from "framer-motion";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
} from "recharts";
import {
  AlertTriangle,
  ShieldCheck,
  ClipboardCheck,
  Boxes,
  TrendingUp,
  TrendingDown,
  Activity,
  ArrowRight,
} from "lucide-react";

const riskTrendData = [
  { name: "Jan", risks: 42, controls: 85 },
  { name: "Feb", risks: 38, controls: 88 },
  { name: "Mar", risks: 45, controls: 86 },
  { name: "Apr", risks: 32, controls: 90 },
  { name: "May", risks: 28, controls: 93 },
  { name: "Jun", risks: 25, controls: 95 },
];

const complianceData = [
  {
    name: "Compliance",
    value: 87,
    fill: "#16A34A",
  },
];

const StatCard = ({
  icon: Icon,
  title,
  value,
  change,
  color,
}: any) => {
  const colorStyles: Record<string, string> = {
    orange:
      "bg-orange-50 text-orange-600 dark:bg-orange-950/30 dark:text-orange-400",
    green:
      "bg-green-50 text-green-600 dark:bg-green-950/30 dark:text-green-400",
    red:
      "bg-red-50 text-red-600 dark:bg-red-950/30 dark:text-red-400",
    emerald:
      "bg-emerald-50 text-emerald-600 dark:bg-emerald-950/30 dark:text-emerald-400",
  };

  return (
    <motion.div
      whileHover={{ y: -5, scale: 1.01 }}
      transition={{ type: "spring", stiffness: 300 }}
    >
      <Card className="group overflow-hidden border border-slate-200 bg-white shadow-soft transition-all duration-300 hover:border-orange-200 hover:shadow-lg dark:border-slate-800 dark:bg-slate-900 dark:hover:border-orange-900">
        <CardContent className="relative p-6">
          {/* Decorative gradient */}
          <div className="absolute -right-10 -top-10 h-24 w-24 rounded-full bg-orange-500/5 blur-2xl transition-all duration-300 group-hover:bg-orange-500/10" />

          <div className="relative flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
                {title}
              </p>

              <h3 className="mt-2 text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
                {value}
              </h3>
            </div>

            <div
              className={`rounded-xl p-3 shadow-sm ${colorStyles[color]}`}
            >
              <Icon size={24} strokeWidth={2} />
            </div>
          </div>

          <div className="mt-4 flex items-center gap-2 text-xs">
            {change > 0 ? (
              <span className="flex items-center gap-1 font-semibold text-green-600 dark:text-green-400">
                <TrendingUp size={14} />
                +{change}%
              </span>
            ) : (
              <span className="flex items-center gap-1 font-semibold text-red-500 dark:text-red-400">
                <TrendingDown size={14} />
                {change}%
              </span>
            )}

            <span className="text-slate-400">
              vs last month
            </span>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default function Dashboard() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            Executive Dashboard
          </h1>

          <p className="mt-1 text-slate-500 dark:text-slate-400">
            Real-time cybersecurity posture overview
          </p>
        </div>

        <motion.button
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          className="rounded-full bg-orange-500 px-5 py-2.5 text-sm font-semibold text-white shadow-md shadow-orange-500/20 transition-all hover:bg-orange-600 hover:shadow-lg hover:shadow-orange-500/30"
        >
          <span className="flex items-center gap-2">
            <Activity size={16} />
            Generate Report
          </span>
        </motion.button>
      </motion.div>

      {/* Statistics */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          icon={AlertTriangle}
          title="Total Risks"
          value="142"
          change={-8}
          color="red"
        />

        <StatCard
          icon={ShieldCheck}
          title="Active Controls"
          value="1,204"
          change={4}
          color="green"
        />

        <StatCard
          icon={ClipboardCheck}
          title="Compliance Score"
          value="87%"
          change={2}
          color="orange"
        />

        <StatCard
          icon={Boxes}
          title="Evidence Count"
          value="4,521"
          change={12}
          color="emerald"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Risk & Control Trends */}
        <Card className="overflow-hidden border border-slate-200 bg-white shadow-soft transition-all duration-300 hover:shadow-lg dark:border-slate-800 dark:bg-slate-900 lg:col-span-2">
          <CardHeader className="flex justify-between p-6 pb-0">
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                Risk & Control Trends
              </h3>

              <p className="text-sm text-slate-500 dark:text-slate-400">
                Last 6 months performance
              </p>
            </div>

            <div className="flex items-center gap-4 text-xs">
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-orange-500" />
                <span className="text-slate-500 dark:text-slate-400">
                  Risks
                </span>
              </div>

              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-green-500" />
                <span className="text-slate-500 dark:text-slate-400">
                  Controls
                </span>
              </div>
            </div>
          </CardHeader>

          <CardContent className="h-80 p-6 pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={riskTrendData}
                margin={{
                  top: 10,
                  right: 10,
                  left: -20,
                  bottom: 0,
                }}
              >
                <defs>
                  {/* Orange Risk Gradient */}
                  <linearGradient
                    id="orangeRisk"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop
                      offset="5%"
                      stopColor="#F97316"
                      stopOpacity={0.35}
                    />
                    <stop
                      offset="95%"
                      stopColor="#F97316"
                      stopOpacity={0}
                    />
                  </linearGradient>

                  {/* Green Control Gradient */}
                  <linearGradient
                    id="greenControl"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop
                      offset="5%"
                      stopColor="#16A34A"
                      stopOpacity={0.35}
                    />
                    <stop
                      offset="95%"
                      stopColor="#16A34A"
                      stopOpacity={0}
                    />
                  </linearGradient>
                </defs>

                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#e2e8f0"
                  className="dark:stroke-slate-700"
                  vertical={false}
                />

                <XAxis
                  dataKey="name"
                  stroke="#94a3b8"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />

                <YAxis
                  stroke="#94a3b8"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />

                <Tooltip
                  contentStyle={{
                    background: "rgba(15, 23, 42, 0.95)",
                    border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: "12px",
                    color: "#fff",
                    boxShadow: "0 10px 30px rgba(0,0,0,0.2)",
                  }}
                />

                {/* Green Controls */}
                <Area
                  type="monotone"
                  dataKey="controls"
                  stroke="#16A34A"
                  strokeWidth={3}
                  fillOpacity={1}
                  fill="url(#greenControl)"
                  animationDuration={1200}
                />

                {/* Orange Risks */}
                <Area
                  type="monotone"
                  dataKey="risks"
                  stroke="#F97316"
                  strokeWidth={3}
                  fillOpacity={1}
                  fill="url(#orangeRisk)"
                  animationDuration={1200}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Compliance */}
        <Card className="overflow-hidden border border-slate-200 bg-white shadow-soft transition-all duration-300 hover:shadow-lg dark:border-slate-800 dark:bg-slate-900">
          <CardHeader className="p-6 pb-0">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
              ISO 27001 Readiness
            </h3>

            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Current compliance posture
            </p>
          </CardHeader>

          <CardContent className="flex h-80 flex-col items-center justify-center p-6">
            <div className="relative h-52 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RadialBarChart
                  innerRadius="70%"
                  outerRadius="100%"
                  data={complianceData}
                  startAngle={90}
                  endAngle={-270}
                >
                  <PolarAngleAxis
                    type="number"
                    domain={[0, 100]}
                    angleAxisId={0}
                    tick={false}
                  />

                  <RadialBar
                    background={{
                      fill: "#e2e8f0",
                    }}
                    dataKey="value"
                    cornerRadius={20}
                    fill="#16A34A"
                  />
                </RadialBarChart>
              </ResponsiveContainer>

              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-5xl font-bold text-slate-900 dark:text-white">
                  87%
                </span>

                <p className="mt-1 text-sm font-medium text-green-600 dark:text-green-400">
                  Compliant
                </p>
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              className="mt-2 rounded-full border border-orange-200 bg-orange-50 px-4 py-2 text-sm font-semibold text-orange-600 transition-all hover:bg-orange-100 dark:border-orange-900 dark:bg-orange-950/30 dark:text-orange-400 dark:hover:bg-orange-950/50"
            >
              <span className="flex items-center gap-2">
                View Details
                <ArrowRight size={14} />
              </span>
            </motion.button>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Activity */}
        <Card className="border border-slate-200 bg-white shadow-soft transition-all duration-300 hover:shadow-lg dark:border-slate-800 dark:bg-slate-900">
          <CardHeader className="flex justify-between p-6 pb-0">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
              Recent Activity
            </h3>

            <button className="text-sm font-medium text-orange-500 transition-colors hover:text-orange-600">
              View All
            </button>
          </CardHeader>

          <CardContent className="space-y-5 p-6">
            {[
              {
                user: "Sarah Connor",
                action: "approved evidence for",
                target: "SOC2 Control A1.1",
                time: "2m ago",
                color: "green",
              },
              {
                user: "John Doe",
                action: "reported new risk in",
                target: "AWS Infrastructure",
                time: "1h ago",
                color: "red",
              },
              {
                user: "System",
                action: "auto-synced compliance data from",
                target: "Jira",
                time: "3h ago",
                color: "orange",
              },
            ].map((act, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className="flex items-start gap-3"
              >
                <div
                  className={`mt-2 h-2.5 w-2.5 shrink-0 rounded-full ${
                    act.color === "green"
                      ? "bg-green-500"
                      : act.color === "orange"
                      ? "bg-orange-500"
                      : "bg-red-500"
                  }`}
                />

                <div className="flex-1">
                  <p className="text-sm text-slate-700 dark:text-slate-300">
                    <span className="font-semibold text-slate-900 dark:text-white">
                      {act.user}
                    </span>{" "}
                    {act.action}{" "}
                    <span className="font-semibold text-orange-600 dark:text-orange-400">
                      {act.target}
                    </span>
                  </p>

                  <p className="mt-1 text-xs text-slate-400">
                    {act.time}
                  </p>
                </div>
              </motion.div>
            ))}
          </CardContent>
        </Card>

        {/* Upcoming Audits */}
        <Card className="border border-slate-200 bg-white shadow-soft transition-all duration-300 hover:shadow-lg dark:border-slate-800 dark:bg-slate-900">
          <CardHeader className="flex justify-between p-6 pb-0">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
              Upcoming Audits
            </h3>

            <button className="text-sm font-medium text-orange-500 transition-colors hover:text-orange-600">
              Schedule
            </button>
          </CardHeader>

          <CardContent className="p-6">
            <div className="space-y-3">
              {/* Audit 1 */}
              <motion.div
                whileHover={{ x: 3 }}
                className="flex items-center justify-between rounded-xl border border-orange-100 bg-orange-50/60 p-4 transition-all hover:border-orange-300 hover:shadow-sm dark:border-orange-900/40 dark:bg-orange-950/20 dark:hover:border-orange-800"
              >
                <div>
                  <h4 className="text-sm font-semibold text-slate-900 dark:text-white">
                    Internal ISMS Audit
                  </h4>

                  <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                    Auditor: Michael R.
                  </p>
                </div>

                <Chip
                  color="warning"
                  variant="soft"
                  size="sm"
                >
                  In 3 days
                </Chip>
              </motion.div>

              {/* Audit 2 */}
              <motion.div
                whileHover={{ x: 3 }}
                className="flex items-center justify-between rounded-xl border border-green-100 bg-green-50/60 p-4 transition-all hover:border-green-300 hover:shadow-sm dark:border-green-900/40 dark:bg-green-950/20 dark:hover:border-green-800"
              >
                <div>
                  <h4 className="text-sm font-semibold text-slate-900 dark:text-white">
                    SOC 2 Type II Review
                  </h4>

                  <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                    External: KPMG
                  </p>
                </div>

                <Chip
                  color="success"
                  variant="soft"
                  size="sm"
                >
                  Next week
                </Chip>
              </motion.div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

