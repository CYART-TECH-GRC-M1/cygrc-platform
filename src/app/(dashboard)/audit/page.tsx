"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
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
  X,
  Trash2,
  Check,
  Calendar,
  Sliders,
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

interface AuditItem {
  id: string;
  name: string;
  framework: string;
  owner: string;
  dueDate: string;
  progress: number;
  status: "In Progress" | "Completed" | "Overdue";
  priority: "Critical" | "High" | "Medium" | "Low";
}

const initialAudits: AuditItem[] = [
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

export default function AuditsPage() {
  const [auditsList, setAuditsList] = useState<AuditItem[]>(initialAudits);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [frameworkFilter, setFrameworkFilter] = useState("All");
  const [isFilterOpen, setIsFilterOpen] = useState(false);

  // Modal: Create Audit
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [createName, setCreateName] = useState("");
  const [createFramework, setCreateFramework] = useState("ISO 27001");
  const [createOwner, setCreateOwner] = useState("");
  const [createDueDate, setCreateDueDate] = useState("Sep 15, 2026");
  const [createPriority, setCreatePriority] = useState<AuditItem["priority"]>("High");
  const [createSuccess, setCreateSuccess] = useState(false);

  // Modal: Schedule Audit Activity
  const [isScheduleModalOpen, setIsScheduleModalOpen] = useState(false);
  const [scheduleTitle, setScheduleTitle] = useState("");
  const [scheduleDate, setScheduleDate] = useState("");
  const [scheduleDays, setScheduleDays] = useState("7 days");
  const [scheduleSuccess, setScheduleSuccess] = useState(false);

  // Modal: Manage/Edit Audit
  const [selectedAudit, setSelectedAudit] = useState<AuditItem | null>(null);
  const [manageSuccess, setManageSuccess] = useState(false);

  // Upcoming deadlines state
  const [upcomingDeadlines, setUpcomingDeadlines] = useState([
    {
      title: "ISO 27001 Internal Audit",
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
      title: "GDPR Privacy Assessment",
      date: "Aug 22",
      days: "15 days",
      color: "orange",
    },
  ]);

  const activeFiltersCount =
    (statusFilter !== "All" ? 1 : 0) + (frameworkFilter !== "All" ? 1 : 0);

  const filteredAudits = auditsList.filter((audit) => {
    const matchesSearch = `${audit.id} ${audit.name} ${audit.framework} ${audit.owner}`
      .toLowerCase()
      .includes(searchQuery.toLowerCase());

    const matchesStatus =
      statusFilter === "All" || audit.status === statusFilter;

    const matchesFramework =
      frameworkFilter === "All" || audit.framework === frameworkFilter;

    return matchesSearch && matchesStatus && matchesFramework;
  });

  const handleCreateAudit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!createName.trim() || !createOwner.trim()) return;

    const nextId = `AUD-2026-${String(auditsList.length + 1).padStart(3, "0")}`;
    const newAudit: AuditItem = {
      id: nextId,
      name: createName.trim(),
      framework: createFramework,
      owner: createOwner.trim(),
      dueDate: createDueDate,
      progress: 0,
      status: "In Progress",
      priority: createPriority,
    };

    setAuditsList((prev) => [newAudit, ...prev]);
    setCreateSuccess(true);
    setTimeout(() => {
      setCreateSuccess(false);
      setIsCreateModalOpen(false);
      setCreateName("");
      setCreateOwner("");
    }, 1200);
  };

  const handleScheduleActivity = (e: React.FormEvent) => {
    e.preventDefault();
    if (!scheduleTitle.trim()) return;

    const newDeadline = {
      title: scheduleTitle.trim(),
      date: scheduleDate.trim() || "Sep 01",
      days: scheduleDays.trim() || "10 days",
      color: "orange",
    };

    setUpcomingDeadlines((prev) => [newDeadline, ...prev]);
    setScheduleSuccess(true);
    setTimeout(() => {
      setScheduleSuccess(false);
      setIsScheduleModalOpen(false);
      setScheduleTitle("");
      setScheduleDate("");
    }, 1200);
  };

  const handleUpdateAudit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAudit) return;

    setAuditsList((prev) =>
      prev.map((a) => (a.id === selectedAudit.id ? selectedAudit : a))
    );
    setManageSuccess(true);
    setTimeout(() => {
      setManageSuccess(false);
      setSelectedAudit(null);
    }, 1000);
  };

  const handleDeleteAudit = (id: string) => {
    setAuditsList((prev) => prev.filter((a) => a.id !== id));
    setSelectedAudit(null);
  };

  const handleResetFilters = () => {
    setSearchQuery("");
    setStatusFilter("All");
    setFrameworkFilter("All");
  };

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
            <button
              onClick={() => setIsScheduleModalOpen(true)}
              className="flex h-10 items-center gap-2 rounded-lg border border-white/10 bg-[#0a0a0a] px-4 text-sm font-medium text-slate-300 transition hover:border-orange-500/30 hover:bg-orange-500/5 hover:text-orange-400"
            >
              <CalendarDays size={16} />
              Schedule
            </button>

            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="flex h-10 items-center gap-2 rounded-lg bg-orange-500 px-5 text-sm font-semibold text-white shadow-lg shadow-orange-900/20 transition hover:bg-orange-600"
            >
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

              <div className="relative flex items-center gap-2">
                <div className="flex h-9 items-center gap-2 rounded-lg border border-white/10 bg-[#050505] px-3 transition focus-within:border-orange-500/30">
                  <Search
                    size={15}
                    className="text-slate-500"
                  />

                  <input
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search audits..."
                    className="w-36 bg-transparent text-xs text-white outline-none placeholder:text-slate-600"
                  />
                  {searchQuery && (
                    <button
                      onClick={() => setSearchQuery("")}
                      className="text-xs text-slate-500 hover:text-white"
                    >
                      <X size={12} />
                    </button>
                  )}
                </div>

                <button
                  onClick={() => setIsFilterOpen(!isFilterOpen)}
                  className={`flex h-9 items-center gap-2 rounded-lg border px-3 text-xs font-semibold transition ${
                    activeFiltersCount > 0
                      ? "border-orange-500 bg-orange-500/10 text-orange-400"
                      : "border-white/10 bg-[#050505] text-slate-400 hover:border-orange-500/30 hover:text-orange-400"
                  }`}
                >
                  <Filter size={14} />
                  Filter
                  {activeFiltersCount > 0 && (
                    <span className="flex h-4 w-4 items-center justify-center rounded-full bg-orange-500 text-[10px] font-bold text-black">
                      {activeFiltersCount}
                    </span>
                  )}
                </button>

                {/* FILTER DROPDOWN */}
                <AnimatePresence>
                  {isFilterOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: 8, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 8, scale: 0.95 }}
                      className="absolute right-0 top-11 z-30 w-72 rounded-xl border border-orange-500/20 bg-[#0c0d12] p-4 shadow-2xl"
                    >
                      <div className="flex items-center justify-between border-b border-zinc-800 pb-2.5">
                        <span className="text-xs font-semibold text-zinc-200">
                          Filter Audits
                        </span>
                        {activeFiltersCount > 0 && (
                          <button
                            onClick={() => {
                              setStatusFilter("All");
                              setFrameworkFilter("All");
                            }}
                            className="text-[11px] text-orange-400 hover:underline"
                          >
                            Reset
                          </button>
                        )}
                      </div>

                      <div className="mt-3 space-y-3">
                        <div>
                          <label className="text-[11px] font-medium text-zinc-400">
                            Status
                          </label>
                          <div className="mt-1 flex flex-wrap gap-1.5">
                            {["All", "In Progress", "Completed", "Overdue"].map((st) => (
                              <button
                                key={st}
                                onClick={() => setStatusFilter(st)}
                                className={`rounded-lg px-2.5 py-1 text-[11px] font-semibold transition ${
                                  statusFilter === st
                                    ? "bg-orange-500 text-black font-bold"
                                    : "border border-zinc-800 bg-black/40 text-zinc-400 hover:text-zinc-200"
                                }`}
                              >
                                {st}
                              </button>
                            ))}
                          </div>
                        </div>

                        <div>
                          <label className="text-[11px] font-medium text-zinc-400">
                            Framework
                          </label>
                          <div className="mt-1 flex flex-wrap gap-1.5">
                            {["All", "ISO 27001", "SOC 2", "GDPR", "PCI DSS", "Third Party", "Cloud Security"].map((fw) => (
                              <button
                                key={fw}
                                onClick={() => setFrameworkFilter(fw)}
                                className={`rounded-lg px-2.5 py-1 text-[11px] font-semibold transition ${
                                  frameworkFilter === fw
                                    ? "bg-orange-500 text-black font-bold"
                                    : "border border-zinc-800 bg-black/40 text-zinc-400 hover:text-zinc-200"
                                }`}
                              >
                                {fw}
                              </button>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div className="mt-4 border-t border-zinc-800 pt-2.5 text-right">
                        <button
                          onClick={() => setIsFilterOpen(false)}
                          className="rounded-lg bg-zinc-800 px-3 py-1 text-xs font-medium text-zinc-200 hover:bg-zinc-700"
                        >
                          Done
                        </button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>

            {/* ACTIVE FILTERS PILLS */}
            {(activeFiltersCount > 0 || searchQuery) && (
              <div className="flex flex-wrap items-center gap-2 border-b border-white/[0.06] bg-orange-500/[0.02] px-5 py-2.5 text-xs">
                <span className="text-[11px] text-zinc-500">Active filters:</span>
                {searchQuery && (
                  <span className="flex items-center gap-1 rounded-md bg-zinc-800 px-2 py-0.5 text-zinc-300 text-[11px]">
                    Search: &quot;{searchQuery}&quot;
                    <button onClick={() => setSearchQuery("")} className="hover:text-white">
                      <X size={11} />
                    </button>
                  </span>
                )}
                {statusFilter !== "All" && (
                  <span className="flex items-center gap-1 rounded-md bg-zinc-800 px-2 py-0.5 text-orange-400 text-[11px]">
                    Status: {statusFilter}
                    <button onClick={() => setStatusFilter("All")} className="hover:text-white">
                      <X size={11} />
                    </button>
                  </span>
                )}
                {frameworkFilter !== "All" && (
                  <span className="flex items-center gap-1 rounded-md bg-zinc-800 px-2 py-0.5 text-emerald-400 text-[11px]">
                    Framework: {frameworkFilter}
                    <button onClick={() => setFrameworkFilter("All")} className="hover:text-white">
                      <X size={11} />
                    </button>
                  </span>
                )}
                <button
                  onClick={handleResetFilters}
                  className="text-[11px] text-zinc-500 hover:text-orange-400 ml-auto"
                >
                  Clear all
                </button>
              </div>
            )}

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
                  {filteredAudits.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="py-12 text-center">
                        <AlertTriangle size={28} className="mx-auto mb-2 text-slate-600" />
                        <p className="text-sm text-slate-400">No audits found</p>
                        <p className="mt-1 text-xs text-slate-600">Try adjusting your search or filters.</p>
                      </td>
                    </tr>
                  ) : (
                    filteredAudits.map((audit, index) => (
                      <motion.tr
                        key={audit.id}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{
                          delay: 0.1 + index * 0.04,
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
                              <div
                                className={`h-full rounded-full transition-all duration-500 ${
                                  audit.status === "Overdue"
                                    ? "bg-red-500"
                                    : audit.status === "Completed"
                                    ? "bg-green-500"
                                    : "bg-orange-500"
                                }`}
                                style={{ width: `${audit.progress}%` }}
                              />
                            </div>
                          </div>
                        </td>

                        {/* Status */}
                        <td className="px-5 py-4">
                          <StatusBadge status={audit.status} />
                        </td>

                        {/* Priority */}
                        <td className="px-5 py-4">
                          <PriorityBadge priority={audit.priority} />
                        </td>

                        {/* More Actions */}
                        <td className="px-5 py-4">
                          <button
                            onClick={() => setSelectedAudit({ ...audit })}
                            aria-label={`Manage audit ${audit.name}`}
                            className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-500 transition hover:bg-orange-500/10 hover:text-orange-400"
                          >
                            <MoreHorizontal size={17} />
                          </button>
                        </td>
                      </motion.tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* TABLE FOOTER */}
            <div className="flex items-center justify-between border-t border-white/[0.06] px-5 py-4">
              <p className="text-xs text-slate-500">
                Showing{" "}
                <span className="text-slate-300">
                  {filteredAudits.length}
                </span>{" "}
                of{" "}
                <span className="text-slate-300">
                  {auditsList.length}
                </span>{" "}
                audits
              </p>

              <button
                onClick={handleResetFilters}
                className="flex items-center gap-1.5 text-xs font-medium text-orange-400 transition hover:text-orange-300"
              >
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
                      <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{
                          backgroundColor: item.color,
                          width: `${item.percentage}%`,
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

            {/* UPCOMING DEADLINES */}
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

                <button
                  onClick={() => setIsScheduleModalOpen(true)}
                  className="text-slate-400 hover:text-orange-400 transition"
                  title="Schedule New Activity"
                >
                  <CalendarDays size={19} />
                </button>
              </div>

              <div className="mt-5 space-y-4">
                {upcomingDeadlines.map((item) => (
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

      {/* ========================================================
          MODAL: CREATE AUDIT
      ======================================================== */}
      <AnimatePresence>
        {isCreateModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsCreateModalOpen(false)}
              className="fixed inset-0 bg-black/70 backdrop-blur-sm"
            />

            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="relative w-full max-w-lg overflow-hidden rounded-2xl border border-orange-500/20 bg-[#0c0d12] p-6 text-white shadow-2xl"
            >
              <div className="flex items-center justify-between border-b border-orange-500/10 pb-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-orange-500/30 bg-orange-500/10 text-orange-400">
                    <Plus size={20} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Create New Audit</h3>
                    <p className="text-xs text-zinc-400">Plan and initiate a compliance assessment</p>
                  </div>
                </div>
                <button
                  onClick={() => setIsCreateModalOpen(false)}
                  className="rounded-lg p-1.5 text-zinc-400 hover:bg-zinc-800 hover:text-white"
                >
                  <X size={18} />
                </button>
              </div>

              {createSuccess ? (
                <div className="py-8 text-center">
                  <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400">
                    <CheckCircle2 size={32} />
                  </div>
                  <h4 className="mt-4 text-base font-semibold text-white">Audit Created!</h4>
                  <p className="mt-1 text-xs text-zinc-400">The audit has been added to your management register.</p>
                </div>
              ) : (
                <form onSubmit={handleCreateAudit} className="mt-4 space-y-4">
                  <div>
                    <label className="text-xs font-semibold text-zinc-300">Audit Name *</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. NIST SP 800-53 Baseline Audit"
                      value={createName}
                      onChange={(e) => setCreateName(e.target.value)}
                      className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="text-xs font-semibold text-zinc-300">Framework</label>
                      <select
                        value={createFramework}
                        onChange={(e) => setCreateFramework(e.target.value)}
                        className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                      >
                        <option value="ISO 27001">ISO 27001</option>
                        <option value="SOC 2">SOC 2</option>
                        <option value="GDPR">GDPR</option>
                        <option value="PCI DSS">PCI DSS</option>
                        <option value="Third Party">Third Party</option>
                        <option value="Cloud Security">Cloud Security</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-xs font-semibold text-zinc-300">Priority</label>
                      <select
                        value={createPriority}
                        onChange={(e) => setCreatePriority(e.target.value as AuditItem["priority"])}
                        className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                      >
                        <option value="Critical">Critical</option>
                        <option value="High">High</option>
                        <option value="Medium">Medium</option>
                        <option value="Low">Low</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-zinc-300">Audit Owner / Team *</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Internal Audit / SecOps"
                      value={createOwner}
                      onChange={(e) => setCreateOwner(e.target.value)}
                      className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-zinc-300">Target Due Date</label>
                    <input
                      type="text"
                      placeholder="e.g. Sep 30, 2026"
                      value={createDueDate}
                      onChange={(e) => setCreateDueDate(e.target.value)}
                      className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                    />
                  </div>

                  <div className="flex items-center justify-end gap-2 pt-3">
                    <button
                      type="button"
                      onClick={() => setIsCreateModalOpen(false)}
                      className="rounded-xl border border-zinc-800 px-4 py-2 text-xs font-semibold text-zinc-400 hover:bg-zinc-800"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="flex items-center gap-1.5 rounded-xl bg-orange-500 px-4 py-2 text-xs font-semibold text-black transition hover:bg-orange-400 shadow-md shadow-orange-500/20"
                    >
                      <Plus size={14} />
                      Create Audit
                    </button>
                  </div>
                </form>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ========================================================
          MODAL: SCHEDULE AUDIT ACTIVITY
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
              className="relative w-full max-w-md overflow-hidden rounded-2xl border border-orange-500/20 bg-[#0c0d12] p-6 text-white shadow-2xl"
            >
              <div className="flex items-center justify-between border-b border-orange-500/10 pb-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-orange-500/30 bg-orange-500/10 text-orange-400">
                    <CalendarDays size={20} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Schedule Audit Deadline</h3>
                    <p className="text-xs text-zinc-400">Add an audit review milestone</p>
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
                  <h4 className="mt-4 text-base font-semibold text-white">Activity Scheduled!</h4>
                  <p className="mt-1 text-xs text-zinc-400">Added to upcoming deadlines calendar.</p>
                </div>
              ) : (
                <form onSubmit={handleScheduleActivity} className="mt-4 space-y-4">
                  <div>
                    <label className="text-xs font-semibold text-zinc-300">Activity Title *</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. FedRAMP Quarterly Attestation"
                      value={scheduleTitle}
                      onChange={(e) => setScheduleTitle(e.target.value)}
                      className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="text-xs font-semibold text-zinc-300">Due Month / Date</label>
                      <input
                        type="text"
                        placeholder="e.g. Sep 18"
                        value={scheduleDate}
                        onChange={(e) => setScheduleDate(e.target.value)}
                        className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                      />
                    </div>

                    <div>
                      <label className="text-xs font-semibold text-zinc-300">Days Remaining</label>
                      <input
                        type="text"
                        placeholder="e.g. 14 days"
                        value={scheduleDays}
                        onChange={(e) => setScheduleDays(e.target.value)}
                        className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-end gap-2 pt-3">
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
                      <CalendarDays size={14} />
                      Schedule
                    </button>
                  </div>
                </form>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ========================================================
          MODAL: MANAGE AUDIT DETAILS & STATUS
      ======================================================== */}
      <AnimatePresence>
        {selectedAudit && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedAudit(null)}
              className="fixed inset-0 bg-black/70 backdrop-blur-sm"
            />

            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="relative w-full max-w-lg overflow-hidden rounded-2xl border border-orange-500/20 bg-[#0c0d12] p-6 text-white shadow-2xl"
            >
              <div className="flex items-center justify-between border-b border-orange-500/10 pb-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-orange-500/30 bg-orange-500/10 text-orange-400">
                    <FileText size={18} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">{selectedAudit.name}</h3>
                    <p className="text-xs text-zinc-400">{selectedAudit.id} • {selectedAudit.framework}</p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedAudit(null)}
                  className="rounded-lg p-1.5 text-zinc-400 hover:bg-zinc-800 hover:text-white"
                >
                  <X size={18} />
                </button>
              </div>

              {manageSuccess ? (
                <div className="py-8 text-center">
                  <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400">
                    <CheckCircle2 size={32} />
                  </div>
                  <h4 className="mt-4 text-base font-semibold text-white">Audit Updated!</h4>
                  <p className="mt-1 text-xs text-zinc-400">Progress and status saved successfully.</p>
                </div>
              ) : (
                <form onSubmit={handleUpdateAudit} className="mt-4 space-y-4">
                  <div className="rounded-xl border border-zinc-800 bg-black/40 p-3.5 space-y-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-zinc-500">Owner:</span>
                      <span className="text-zinc-200 font-medium">{selectedAudit.owner}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-zinc-500">Target Due Date:</span>
                      <span className="text-zinc-200 font-medium">{selectedAudit.dueDate}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-zinc-500">Priority:</span>
                      <span className="text-orange-400 font-semibold">{selectedAudit.priority}</span>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-semibold text-zinc-300">
                        Audit Progress ({selectedAudit.progress}%)
                      </label>
                    </div>
                    <input
                      type="range"
                      min={0}
                      max={100}
                      value={selectedAudit.progress}
                      onChange={(e) =>
                        setSelectedAudit({
                          ...selectedAudit,
                          progress: Number(e.target.value),
                          status:
                            Number(e.target.value) === 100
                              ? "Completed"
                              : selectedAudit.status === "Completed"
                              ? "In Progress"
                              : selectedAudit.status,
                        })
                      }
                      className="mt-2 w-full accent-orange-500"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="text-xs font-semibold text-zinc-300">Status</label>
                      <select
                        value={selectedAudit.status}
                        onChange={(e) =>
                          setSelectedAudit({
                            ...selectedAudit,
                            status: e.target.value as AuditItem["status"],
                            progress:
                              e.target.value === "Completed" ? 100 : selectedAudit.progress,
                          })
                        }
                        className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                      >
                        <option value="In Progress">In Progress</option>
                        <option value="Completed">Completed</option>
                        <option value="Overdue">Overdue</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-xs font-semibold text-zinc-300">Priority</label>
                      <select
                        value={selectedAudit.priority}
                        onChange={(e) =>
                          setSelectedAudit({
                            ...selectedAudit,
                            priority: e.target.value as AuditItem["priority"],
                          })
                        }
                        className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                      >
                        <option value="Critical">Critical</option>
                        <option value="High">High</option>
                        <option value="Medium">Medium</option>
                        <option value="Low">Low</option>
                      </select>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-4">
                    <button
                      type="button"
                      onClick={() => handleDeleteAudit(selectedAudit.id)}
                      className="flex items-center gap-1.5 text-xs text-red-400 hover:text-red-300 transition"
                    >
                      <Trash2 size={14} />
                      Remove Audit
                    </button>

                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => setSelectedAudit(null)}
                        className="rounded-xl border border-zinc-800 px-4 py-2 text-xs font-semibold text-zinc-400 hover:bg-zinc-800"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="flex items-center gap-1.5 rounded-xl bg-orange-500 px-4 py-2 text-xs font-semibold text-black transition hover:bg-orange-400 shadow-md shadow-orange-500/20"
                      >
                        <Check size={14} />
                        Save Changes
                      </button>
                    </div>
                  </div>
                </form>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </main>
  );
}