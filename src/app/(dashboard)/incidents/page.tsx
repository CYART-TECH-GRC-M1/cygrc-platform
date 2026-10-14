"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
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
X,
Plus,
Check,
Trash2,
ChevronDown,
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

interface IncidentItem {
  id: string;
  title: string;
  description: string;
  status: "Active" | "Monitoring" | "Resolved";
  priority: "High" | "Medium" | "Low";
  source: string;
  time: string;
  icon?: any;
}

const initialIncidents: IncidentItem[] = [
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
  const [incidentsList, setIncidentsList] = useState<IncidentItem[]>(initialIncidents);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [priorityFilter, setPriorityFilter] = useState("All");
  const [isFilterOpen, setIsFilterOpen] = useState(false);

  // Modal: Report Incident
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [newPriority, setNewPriority] = useState<IncidentItem["priority"]>("High");
  const [newSource, setNewSource] = useState("Authentication");
  const [newStatus, setNewStatus] = useState<IncidentItem["status"]>("Active");
  const [reportSuccess, setReportSuccess] = useState(false);

  // Modal: Incident Investigation / Detail
  const [selectedIncident, setSelectedIncident] = useState<IncidentItem | null>(null);
  const [investigationNote, setInvestigationNote] = useState("");
  const [updateSuccess, setUpdateSuccess] = useState(false);

  const activeFiltersCount =
    (statusFilter !== "All" ? 1 : 0) + (priorityFilter !== "All" ? 1 : 0);

  const filteredIncidents = incidentsList.filter((incident) => {
    const matchesSearch = `${incident.id} ${incident.title} ${incident.description} ${incident.source}`
      .toLowerCase()
      .includes(searchQuery.toLowerCase());

    const matchesStatus =
      statusFilter === "All" || incident.status === statusFilter;

    const matchesPriority =
      priorityFilter === "All" || incident.priority === priorityFilter;

    return matchesSearch && matchesStatus && matchesPriority;
  });

  const handleReportIncident = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newDescription.trim()) return;

    const nextId = `INC-${1020 + incidentsList.length + 1}`;
    let icon = ShieldAlert;
    if (newSource === "Authentication") icon = UserRound;
    else if (newSource === "Network") icon = Network;
    else if (newSource === "Endpoint") icon = Server;

    const newIncident: IncidentItem = {
      id: nextId,
      title: newTitle.trim(),
      description: newDescription.trim(),
      status: newStatus,
      priority: newPriority,
      source: newSource,
      time: "Just now",
      icon,
    };

    setIncidentsList((prev) => [newIncident, ...prev]);
    setReportSuccess(true);
    setTimeout(() => {
      setReportSuccess(false);
      setIsReportModalOpen(false);
      setNewTitle("");
      setNewDescription("");
    }, 1200);
  };

  const handleUpdateStatus = (newStatusVal: IncidentItem["status"]) => {
    if (!selectedIncident) return;
    const updated = { ...selectedIncident, status: newStatusVal, time: "Updated just now" };
    setIncidentsList((prev) =>
      prev.map((inc) => (inc.id === selectedIncident.id ? updated : inc))
    );
    setSelectedIncident(updated);
    setUpdateSuccess(true);
    setTimeout(() => setUpdateSuccess(false), 1500);
  };

  const handleDeleteIncident = (id: string) => {
    setIncidentsList((prev) => prev.filter((inc) => inc.id !== id));
    setSelectedIncident(null);
  };

  const handleResetFilters = () => {
    setSearchQuery("");
    setStatusFilter("All");
    setPriorityFilter("All");
  };

  return (
    <div className="w-full space-y-7">
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
            onClick={() => setIsFilterOpen(!isFilterOpen)}
            className={`flex h-11 items-center justify-center gap-2 rounded-xl border px-4 text-sm font-semibold transition-all ${
              activeFiltersCount > 0
                ? "border-orange-500 bg-orange-500/10 text-orange-400"
                : "border-zinc-800 bg-[#080807] text-zinc-400 hover:border-emerald-500/30 hover:bg-emerald-500/[0.04] hover:text-emerald-400"
            }`}
          >
            <Filter size={16} />
            Filter
            {activeFiltersCount > 0 && (
              <span className="flex h-4 w-4 items-center justify-center rounded-full bg-orange-500 text-[10px] font-bold text-black">
                {activeFiltersCount}
              </span>
            )}
          </motion.button>

          <motion.button
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.98 }}
            type="button"
            onClick={() => setIsReportModalOpen(true)}
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
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search incidents by title, ID, source..."
                className="w-full bg-transparent text-sm text-zinc-200 outline-none placeholder:text-zinc-600"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className="text-xs text-zinc-500 hover:text-white"
                >
                  <X size={14} />
                </button>
              )}
            </div>
          </div>

          {/* STATUS BUTTONS */}
          <div className="flex flex-wrap gap-2">
            {["All", "Active", "Monitoring", "Resolved"].map((label) => (
              <StatusBadge
                key={label}
                label={label}
                active={statusFilter === label}
                onClick={() => setStatusFilter(label)}
              />
            ))}
          </div>
        </div>

        {/* PRIORITY FILTER DROPDOWN */}
        <AnimatePresence>
          {isFilterOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-4 border-t border-zinc-800 pt-4"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <span className="text-xs font-semibold text-zinc-400">Filter by Priority:</span>
                  <div className="flex gap-2">
                    {["All", "High", "Medium", "Low"].map((p) => (
                      <button
                        key={p}
                        onClick={() => setPriorityFilter(p)}
                        className={`rounded-lg px-2.5 py-1 text-xs font-medium transition ${
                          priorityFilter === p
                            ? "bg-orange-500 text-black font-semibold"
                            : "border border-zinc-800 bg-black/40 text-zinc-400 hover:text-white"
                        }`}
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                </div>

                {activeFiltersCount > 0 && (
                  <button
                    onClick={handleResetFilters}
                    className="text-xs text-orange-400 hover:underline"
                  >
                    Reset all filters
                  </button>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* ACTIVE FILTERS PILL */}
      {(searchQuery || statusFilter !== "All" || priorityFilter !== "All") && (
        <div className="flex flex-wrap items-center gap-2 rounded-xl border border-orange-500/10 bg-orange-500/[0.02] px-4 py-2.5 text-xs">
          <span className="text-zinc-500">Active filters:</span>
          {searchQuery && (
            <span className="flex items-center gap-1 rounded-md bg-zinc-800 px-2 py-0.5 text-zinc-300">
              Query: &quot;{searchQuery}&quot;
              <button onClick={() => setSearchQuery("")} className="hover:text-white">
                <X size={11} />
              </button>
            </span>
          )}
          {statusFilter !== "All" && (
            <span className="flex items-center gap-1 rounded-md bg-zinc-800 px-2 py-0.5 text-orange-400">
              Status: {statusFilter}
              <button onClick={() => setStatusFilter("All")} className="hover:text-white">
                <X size={11} />
              </button>
            </span>
          )}
          {priorityFilter !== "All" && (
            <span className="flex items-center gap-1 rounded-md bg-zinc-800 px-2 py-0.5 text-emerald-400">
              Priority: {priorityFilter}
              <button onClick={() => setPriorityFilter("All")} className="hover:text-white">
                <X size={11} />
              </button>
            </span>
          )}
          <button
            onClick={handleResetFilters}
            className="text-zinc-500 hover:text-orange-400 ml-auto"
          >
            Clear all
          </button>
        </div>
      )}

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
                Review and investigate reported security incidents ({filteredIncidents.length} shown).
              </p>
            </div>

            <button
              type="button"
              onClick={handleResetFilters}
              className="flex items-center gap-2 text-xs font-semibold tracking-wider text-orange-400 transition hover:text-orange-300"
            >
              VIEW ALL
              <ArrowUpRight size={15} />
            </button>
          </div>

          {/* INCIDENTS */}
          <div className="w-full divide-y divide-orange-500/10">
            {filteredIncidents.length === 0 ? (
              <div className="p-12 text-center">
                <ShieldAlert size={32} className="mx-auto mb-2 text-zinc-700" />
                <p className="text-sm text-zinc-500">No incidents match your current criteria</p>
                <button
                  onClick={handleResetFilters}
                  className="mt-3 text-xs text-orange-400 hover:underline"
                >
                  Reset all filters
                </button>
              </div>
            ) : (
              filteredIncidents.map((incident, index) => {
                const Icon = incident.icon || ShieldAlert;

                return (
                  <motion.article
                    key={incident.id}
                    initial={{ opacity: 0, x: -12 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 + index * 0.05 }}
                    onClick={() => setSelectedIncident(incident)}
                    className="group cursor-pointer p-6 transition hover:bg-orange-500/[0.02]"
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

                          <h3 className="mt-2 text-base font-semibold text-zinc-200 group-hover:text-white transition">
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
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedIncident(incident);
                          }}
                          className="flex h-9 w-9 items-center justify-center rounded-lg border border-zinc-800 bg-[#050505] text-zinc-600 opacity-70 group-hover:opacity-100 transition hover:border-orange-500/30 hover:text-orange-400"
                        >
                          <ArrowUpRight size={15} />
                        </button>
                      </div>
                    </div>
                  </motion.article>
                );
              })
            )}
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

      {/* ========================================================
          MODAL: REPORT INCIDENT
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
              className="relative w-full max-w-lg overflow-hidden rounded-2xl border border-orange-500/20 bg-[#0c0d12] p-6 text-white shadow-2xl"
            >
              <div className="flex items-center justify-between border-b border-orange-500/10 pb-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-orange-500/30 bg-orange-500/10 text-orange-400">
                    <AlertTriangle size={20} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Report Security Incident</h3>
                    <p className="text-xs text-zinc-400">Submit a new incident for triage and remediation</p>
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
                  <h4 className="mt-4 text-base font-semibold text-white">Incident Reported!</h4>
                  <p className="mt-1 text-xs text-zinc-400">Added to Incident Repository and flagged for investigation.</p>
                </div>
              ) : (
                <form onSubmit={handleReportIncident} className="mt-4 space-y-4">
                  <div>
                    <label className="text-xs font-semibold text-zinc-300">Incident Title *</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Unusual outbound traffic spike from database cluster"
                      value={newTitle}
                      onChange={(e) => setNewTitle(e.target.value)}
                      className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-zinc-300">Description *</label>
                    <textarea
                      required
                      rows={3}
                      placeholder="Describe symptoms, indicators of compromise, and affected systems..."
                      value={newDescription}
                      onChange={(e) => setNewDescription(e.target.value)}
                      className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                    />
                  </div>

                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <label className="text-xs font-semibold text-zinc-300">Priority</label>
                      <select
                        value={newPriority}
                        onChange={(e) => setNewPriority(e.target.value as IncidentItem["priority"])}
                        className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3 py-2 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                      >
                        <option value="High">High</option>
                        <option value="Medium">Medium</option>
                        <option value="Low">Low</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-xs font-semibold text-zinc-300">Source</label>
                      <select
                        value={newSource}
                        onChange={(e) => setNewSource(e.target.value)}
                        className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3 py-2 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                      >
                        <option value="Authentication">Authentication</option>
                        <option value="Network">Network</option>
                        <option value="Endpoint">Endpoint</option>
                        <option value="Policy">Policy</option>
                        <option value="Cloud">Cloud</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-xs font-semibold text-zinc-300">Initial Status</label>
                      <select
                        value={newStatus}
                        onChange={(e) => setNewStatus(e.target.value as IncidentItem["status"])}
                        className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3 py-2 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                      >
                        <option value="Active">Active</option>
                        <option value="Monitoring">Monitoring</option>
                        <option value="Resolved">Resolved</option>
                      </select>
                    </div>
                  </div>

                  <div className="flex items-center justify-end gap-2 pt-3">
                    <button
                      type="button"
                      onClick={() => setIsReportModalOpen(false)}
                      className="rounded-xl border border-zinc-800 px-4 py-2 text-xs font-semibold text-zinc-400 hover:bg-zinc-800"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="flex items-center gap-1.5 rounded-xl bg-orange-500 px-4 py-2 text-xs font-semibold text-black transition hover:bg-orange-400 shadow-md shadow-orange-500/20"
                    >
                      <Plus size={14} />
                      Submit Incident
                    </button>
                  </div>
                </form>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ========================================================
          MODAL: INCIDENT INVESTIGATION & ACTIONS
      ======================================================== */}
      <AnimatePresence>
        {selectedIncident && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedIncident(null)}
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
                    <ShieldAlert size={20} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">{selectedIncident.id}</h3>
                    <p className="text-xs text-zinc-400">{selectedIncident.source} • {selectedIncident.time}</p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedIncident(null)}
                  className="rounded-lg p-1.5 text-zinc-400 hover:bg-zinc-800 hover:text-white"
                >
                  <X size={18} />
                </button>
              </div>

              {updateSuccess && (
                <div className="mt-3 flex items-center gap-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 p-2.5 text-xs text-emerald-400">
                  <CheckCircle2 size={16} />
                  <span>Incident status updated successfully!</span>
                </div>
              )}

              <div className="mt-4 space-y-4">
                <div>
                  <h4 className="text-sm font-semibold text-white">{selectedIncident.title}</h4>
                  <p className="mt-1 text-xs text-zinc-400 leading-relaxed">{selectedIncident.description}</p>
                </div>

                <div className="grid grid-cols-2 gap-3 rounded-xl border border-zinc-800 bg-black/40 p-3.5 text-xs">
                  <div>
                    <span className="text-zinc-500">Current Status:</span>
                    <div className="mt-1">
                      <IncidentStatus status={selectedIncident.status} />
                    </div>
                  </div>
                  <div>
                    <span className="text-zinc-500">Severity:</span>
                    <div className="mt-1">
                      <PriorityBadge priority={selectedIncident.priority} />
                    </div>
                  </div>
                </div>

                <div>
                  <label className="text-xs font-semibold text-zinc-300">Update Incident Status</label>
                  <div className="mt-2 flex gap-2">
                    {(["Active", "Monitoring", "Resolved"] as IncidentItem["status"][]).map((st) => (
                      <button
                        key={st}
                        type="button"
                        onClick={() => handleUpdateStatus(st)}
                        className={`flex-1 rounded-xl py-2 text-xs font-semibold transition ${
                          selectedIncident.status === st
                            ? "bg-orange-500 text-black shadow-md shadow-orange-500/20"
                            : "border border-zinc-800 bg-[#050505] text-zinc-400 hover:border-zinc-700"
                        }`}
                      >
                        {st}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-between border-t border-zinc-800 pt-4">
                  <button
                    type="button"
                    onClick={() => handleDeleteIncident(selectedIncident.id)}
                    className="flex items-center gap-1.5 text-xs text-red-400 hover:text-red-300 transition"
                  >
                    <Trash2 size={14} />
                    Delete Incident
                  </button>

                  <button
                    type="button"
                    onClick={() => setSelectedIncident(null)}
                    className="rounded-xl border border-zinc-800 px-4 py-2 text-xs font-semibold text-zinc-400 hover:bg-zinc-800"
                  >
                    Close
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

/* =========================================================
STATUS FILTER
========================================================= */

function StatusBadge({
  label,
  active = false,
  onClick,
}: {
  label: string;
  active?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={
        active
          ? "rounded-lg bg-orange-500 px-3 py-2 text-xs font-semibold text-black shadow-sm shadow-orange-500/10"
          : "rounded-lg border border-zinc-800 bg-[#050505] px-3 py-2 text-xs font-medium text-zinc-500 transition hover:border-emerald-500/30 hover:text-emerald-400"
      }
    >
      {label}
    </button>
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
