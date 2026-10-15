
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, Chip } from "@heroui/react";
import { motion, AnimatePresence } from "framer-motion";
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
  X,
  Download,
  Calendar,
  CheckCircle2,
  Clock3,
  ExternalLink,
  Plus,
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
  const router = useRouter();

  // Report Modal State
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [reportScope, setReportScope] = useState("Executive Summary");
  const [reportFormat, setReportFormat] = useState("CSV");
  const [reportSuccess, setReportSuccess] = useState(false);

  // Activity Modal State
  const [isActivityModalOpen, setIsActivityModalOpen] = useState(false);
  const [activityFilter, setActivityFilter] = useState("all");

  // Schedule Modal State
  const [isScheduleModalOpen, setIsScheduleModalOpen] = useState(false);
  const [newAuditTitle, setNewAuditTitle] = useState("");
  const [newAuditAuditor, setNewAuditAuditor] = useState("");
  const [newAuditDueDate, setNewAuditDueDate] = useState("In 7 days");
  const [scheduleSuccess, setScheduleSuccess] = useState(false);

  // Upcoming Audits list state
  const [upcomingAudits, setUpcomingAudits] = useState([
    {
      id: "aud-1",
      title: "Internal ISMS Audit",
      auditor: "Michael R.",
      due: "In 3 days",
      badgeColor: "warning" as const,
      borderClass: "border-orange-100 dark:border-orange-900/40 bg-orange-50/60 dark:bg-orange-950/20 hover:border-orange-300 dark:hover:border-orange-800",
    },
    {
      id: "aud-2",
      title: "SOC 2 Type II Review",
      auditor: "External: KPMG",
      due: "Next week",
      badgeColor: "success" as const,
      borderClass: "border-green-100 dark:border-green-900/40 bg-green-50/60 dark:bg-green-950/20 hover:border-green-300 dark:hover:border-green-800",
    },
  ]);

  const allActivities = [
    {
      id: 1,
      type: "control",
      user: "Sarah Connor",
      action: "approved evidence for",
      target: "SOC2 Control A1.1",
      time: "2m ago",
      color: "green",
    },
    {
      id: 2,
      type: "risk",
      user: "John Doe",
      action: "reported new risk in",
      target: "AWS Infrastructure",
      time: "1h ago",
      color: "red",
    },
    {
      id: 3,
      type: "sync",
      user: "System",
      action: "auto-synced compliance data from",
      target: "Jira",
      time: "3h ago",
      color: "orange",
    },
    {
      id: 4,
      type: "control",
      user: "Alex Rivera",
      action: "re-evaluated control status for",
      target: "ISO 27001 Access Control A.9",
      time: "5h ago",
      color: "green",
    },
    {
      id: 5,
      type: "risk",
      user: "Michael R.",
      action: "mitigated vulnerability ticket in",
      target: "Production Kubernetes Cluster",
      time: "1d ago",
      color: "orange",
    },
    {
      id: 6,
      type: "sync",
      user: "System",
      action: "fetched telemetry data from",
      target: "AWS CloudTrail",
      time: "1d ago",
      color: "orange",
    },
  ];

  const handleDownloadReport = () => {
    const csvContent = [
      "CyGRC Executive Summary Report",
      `Generated At,${new Date().toISOString()}`,
      `Scope,${reportScope}`,
      `Format,${reportFormat}`,
      "----------------------------------------",
      "Metric,Value,Change",
      "Total Risks,142,-8%",
      "Active Controls,1204,+4%",
      "Compliance Score,87%,+2%",
      "Evidence Count,4521,+12%",
      "Framework,ISO 27001 Readiness (87% Compliant)",
      "Status,Audit Ready",
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `cygrc_${reportScope.toLowerCase().replace(/\s+/g, "_")}_report.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    setReportSuccess(true);
    setTimeout(() => {
      setReportSuccess(false);
      setIsReportModalOpen(false);
    }, 1500);
  };

  const handleScheduleAudit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAuditTitle.trim() || !newAuditAuditor.trim()) return;

    const newAudit = {
      id: `aud-${Date.now()}`,
      title: newAuditTitle.trim(),
      auditor: newAuditAuditor.trim(),
      due: newAuditDueDate.trim() || "In 7 days",
      badgeColor: "warning" as const,
      borderClass: "border-orange-100 dark:border-orange-900/40 bg-orange-50/60 dark:bg-orange-950/20 hover:border-orange-300 dark:hover:border-orange-800",
    };

    setUpcomingAudits((prev) => [newAudit, ...prev]);
    setScheduleSuccess(true);
    setTimeout(() => {
      setScheduleSuccess(false);
      setIsScheduleModalOpen(false);
      setNewAuditTitle("");
      setNewAuditAuditor("");
    }, 1200);
  };

  const filteredActivities = allActivities.filter((act) => {
    if (activityFilter === "all") return true;
    return act.type === activityFilter;
  });

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
          onClick={() => setIsReportModalOpen(true)}
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
              onClick={() => router.push("/compliance")}
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

            <button
              onClick={() => setIsActivityModalOpen(true)}
              className="text-sm font-medium text-orange-500 transition-colors hover:text-orange-600"
            >
              View All
            </button>
          </CardHeader>

          <CardContent className="space-y-5 p-6">
            {allActivities.slice(0, 3).map((act, i) => (
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

            <button
              onClick={() => setIsScheduleModalOpen(true)}
              className="text-sm font-medium text-orange-500 transition-colors hover:text-orange-600"
            >
              Schedule
            </button>
          </CardHeader>

          <CardContent className="p-6">
            <div className="space-y-3">
              {upcomingAudits.map((audit) => (
                <motion.div
                  key={audit.id}
                  whileHover={{ x: 3 }}
                  onClick={() => router.push("/audit")}
                  className={`flex cursor-pointer items-center justify-between rounded-xl border p-4 transition-all hover:shadow-sm ${audit.borderClass}`}
                >
                  <div>
                    <h4 className="text-sm font-semibold text-slate-900 dark:text-white">
                      {audit.title}
                    </h4>

                    <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                      Auditor: {audit.auditor}
                    </p>
                  </div>

                  <Chip
                    color={audit.badgeColor}
                    variant="soft"
                    size="sm"
                  >
                    {audit.due}
                  </Chip>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* ========================================================
          MODAL: GENERATE REPORT
      ======================================================== */}
      <AnimatePresence>
        {isReportModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsReportModalOpen(false)}
              className="fixed inset-0 bg-black/70 backdrop-blur-sm"
            />

            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="relative w-full max-w-lg overflow-hidden rounded-2xl border border-orange-500/20 bg-[#0b0c10] p-6 text-white shadow-2xl"
            >
              <div className="flex items-center justify-between border-b border-orange-500/10 pb-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-orange-500/30 bg-orange-500/10 text-orange-400">
                    <Activity size={20} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Generate Executive Report</h3>
                    <p className="text-xs text-zinc-400">Export cybersecurity posture snapshot</p>
                  </div>
                </div>
                <button
                  onClick={() => setIsReportModalOpen(false)}
                  className="rounded-lg p-1.5 text-zinc-400 hover:bg-zinc-800 hover:text-white"
                >
                  <X size={18} />
                </button>
              </div>

              {reportSuccess ? (
                <div className="py-8 text-center">
                  <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400">
                    <CheckCircle2 size={32} />
                  </div>
                  <h4 className="mt-4 text-base font-semibold text-white">Report Download Initiated!</h4>
                  <p className="mt-1 text-xs text-zinc-400">The snapshot file has been generated and saved.</p>
                </div>
              ) : (
                <div className="space-y-4 pt-5">
                  <div>
                    <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                      Report Scope
                    </label>
                    <div className="mt-2 grid grid-cols-2 gap-2">
                      {["Executive Summary", "Compliance Readiness", "Risk Posture", "Full Audit Pack"].map((scope) => (
                        <button
                          key={scope}
                          type="button"
                          onClick={() => setReportScope(scope)}
                          className={`rounded-xl border p-2.5 text-left text-xs font-medium transition ${
                            reportScope === scope
                              ? "border-orange-500 bg-orange-500/10 text-orange-400 font-semibold"
                              : "border-zinc-800 bg-[#070707] text-zinc-400 hover:border-zinc-700 hover:text-zinc-200"
                          }`}
                        >
                          {scope}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                      Export Format
                    </label>
                    <div className="mt-2 flex gap-3">
                      {["CSV", "JSON", "PDF"].map((fmt) => (
                        <button
                          key={fmt}
                          type="button"
                          onClick={() => setReportFormat(fmt)}
                          className={`flex-1 rounded-xl border py-2 text-xs font-semibold transition ${
                            reportFormat === fmt
                              ? "border-orange-500 bg-orange-500 text-black shadow-lg shadow-orange-500/20"
                              : "border-zinc-800 bg-[#070707] text-zinc-400 hover:border-zinc-700"
                          }`}
                        >
                          {fmt}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="rounded-xl border border-zinc-800 bg-black/40 p-3 text-xs text-zinc-400">
                    <p className="font-medium text-zinc-300">Live Snapshot Summary:</p>
                    <p className="mt-1">Includes 142 risks, 1,204 active controls, and 87% ISO 27001 readiness score.</p>
                  </div>

                  <div className="mt-6 flex items-center justify-between pt-2">
                    <button
                      type="button"
                      onClick={() => {
                        setIsReportModalOpen(false);
                        router.push("/reports");
                      }}
                      className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-orange-400 transition"
                    >
                      <span>Open Reports Hub</span>
                      <ExternalLink size={12} />
                    </button>

                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => setIsReportModalOpen(false)}
                        className="rounded-xl border border-zinc-800 px-4 py-2 text-xs font-semibold text-zinc-400 hover:bg-zinc-800"
                      >
                        Cancel
                      </button>
                      <button
                        type="button"
                        onClick={handleDownloadReport}
                        className="flex items-center gap-2 rounded-xl bg-orange-500 px-4 py-2 text-xs font-semibold text-black transition hover:bg-orange-400 shadow-md shadow-orange-500/20"
                      >
                        <Download size={14} />
                        Download Report
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ========================================================
          MODAL: ALL RECENT ACTIVITY
      ======================================================== */}
      <AnimatePresence>
        {isActivityModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsActivityModalOpen(false)}
              className="fixed inset-0 bg-black/70 backdrop-blur-sm"
            />

            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="relative w-full max-w-xl overflow-hidden rounded-2xl border border-orange-500/20 bg-[#0b0c10] p-6 text-white shadow-2xl"
            >
              <div className="flex items-center justify-between border-b border-orange-500/10 pb-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-orange-500/30 bg-orange-500/10 text-orange-400">
                    <Clock3 size={20} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Activity Audit Trail</h3>
                    <p className="text-xs text-zinc-400">Detailed event log of controls, risks & syncs</p>
                  </div>
                </div>
                <button
                  onClick={() => setIsActivityModalOpen(false)}
                  className="rounded-lg p-1.5 text-zinc-400 hover:bg-zinc-800 hover:text-white"
                >
                  <X size={18} />
                </button>
              </div>

              {/* Filters */}
              <div className="flex gap-2 pt-4">
                {[
                  { id: "all", label: "All Events" },
                  { id: "control", label: "Controls" },
                  { id: "risk", label: "Risks" },
                  { id: "sync", label: "Syncs" },
                ].map((f) => (
                  <button
                    key={f.id}
                    onClick={() => setActivityFilter(f.id)}
                    className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                      activityFilter === f.id
                        ? "bg-orange-500 text-black shadow-sm shadow-orange-500/20"
                        : "border border-zinc-800 bg-[#070707] text-zinc-400 hover:text-white"
                    }`}
                  >
                    {f.label}
                  </button>
                ))}
              </div>

              {/* Event list */}
              <div className="mt-4 max-h-80 space-y-3 overflow-y-auto pr-1">
                {filteredActivities.map((act) => (
                  <div
                    key={act.id}
                    className="flex items-start gap-3 rounded-xl border border-zinc-800/80 bg-[#070707] p-3 text-xs transition hover:border-orange-500/30"
                  >
                    <div
                      className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${
                        act.color === "green"
                          ? "bg-emerald-500"
                          : act.color === "orange"
                          ? "bg-orange-500"
                          : "bg-red-500"
                      }`}
                    />
                    <div className="flex-1">
                      <p className="text-zinc-300">
                        <span className="font-semibold text-white">{act.user}</span>{" "}
                        {act.action}{" "}
                        <span className="font-semibold text-orange-400">{act.target}</span>
                      </p>
                      <p className="mt-1 text-[11px] text-zinc-500">{act.time}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-5 flex items-center justify-between border-t border-orange-500/10 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setIsActivityModalOpen(false);
                    router.push("/incidents");
                  }}
                  className="text-xs text-orange-400 hover:underline"
                >
                  View Incident Management →
                </button>
                <button
                  type="button"
                  onClick={() => setIsActivityModalOpen(false)}
                  className="rounded-xl border border-zinc-800 px-4 py-2 text-xs font-semibold text-zinc-400 hover:bg-zinc-800"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ========================================================
          MODAL: SCHEDULE AUDIT
      ======================================================== */}
      <AnimatePresence>
        {isScheduleModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsScheduleModalOpen(false)}
              className="fixed inset-0 bg-black/70 backdrop-blur-sm"
            />

            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="relative w-full max-w-md overflow-hidden rounded-2xl border border-orange-500/20 bg-[#0b0c10] p-6 text-white shadow-2xl"
            >
              <div className="flex items-center justify-between border-b border-orange-500/10 pb-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-orange-500/30 bg-orange-500/10 text-orange-400">
                    <Calendar size={20} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Schedule Audit</h3>
                    <p className="text-xs text-zinc-400">Add an audit to the upcoming queue</p>
                  </div>
                </div>
                <button
                  onClick={() => setIsScheduleModalOpen(false)}
                  className="rounded-lg p-1.5 text-zinc-400 hover:bg-zinc-800 hover:text-white"
                >
                  <X size={18} />
                </button>
              </div>

              {scheduleSuccess ? (
                <div className="py-8 text-center">
                  <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400">
                    <CheckCircle2 size={32} />
                  </div>
                  <h4 className="mt-4 text-base font-semibold text-white">Audit Scheduled!</h4>
                  <p className="mt-1 text-xs text-zinc-400">Added to upcoming audits schedule list.</p>
                </div>
              ) : (
                <form onSubmit={handleScheduleAudit} className="mt-4 space-y-4">
                  <div>
                    <label className="text-xs font-semibold text-zinc-300">Audit Title *</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. NIST CSF 2.0 Review"
                      value={newAuditTitle}
                      onChange={(e) => setNewAuditTitle(e.target.value)}
                      className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#070707] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-zinc-300">Lead Auditor / Organization *</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Internal Team / PwC"
                      value={newAuditAuditor}
                      onChange={(e) => setNewAuditAuditor(e.target.value)}
                      className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#070707] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-zinc-300">Schedule / Due Time</label>
                    <input
                      type="text"
                      placeholder="e.g. In 2 weeks"
                      value={newAuditDueDate}
                      onChange={(e) => setNewAuditDueDate(e.target.value)}
                      className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#070707] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                    />
                  </div>

                  <div className="flex items-center justify-between pt-2">
                    <button
                      type="button"
                      onClick={() => {
                        setIsScheduleModalOpen(false);
                        router.push("/audit");
                      }}
                      className="text-xs text-orange-400 hover:underline"
                    >
                      Audit Hub →
                    </button>

                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => setIsScheduleModalOpen(false)}
                        className="rounded-xl border border-zinc-800 px-4 py-2 text-xs font-semibold text-zinc-400 hover:bg-zinc-800"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="flex items-center gap-1.5 rounded-xl bg-orange-500 px-4 py-2 text-xs font-semibold text-black transition hover:bg-orange-400 shadow-md shadow-orange-500/20"
                      >
                        <Plus size={14} />
                        Add Audit
                      </button>
                    </div>
                  </div>
                </form>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

