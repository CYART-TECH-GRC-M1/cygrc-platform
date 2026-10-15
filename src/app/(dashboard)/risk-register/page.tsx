"use client";

import { useState } from "react";
import { Chip } from "@heroui/react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  ChevronDown,
  Download,
  Plus,
  Pencil,
  ShieldAlert,
  X,
  CheckCircle2,
  Trash2,
  Filter,
  Check,
} from "lucide-react";

interface RiskItem {
  id: string;
  name: string;
  owner: string;
  severity: "Critical" | "High" | "Medium" | "Low";
  status: "Open" | "Mitigating" | "Resolved" | "Accepted";
}

const initialRisks: RiskItem[] = [
  {
    id: "RSK-001",
    name: "Data Breach via Phishing",
    owner: "John Doe",
    severity: "Critical",
    status: "Mitigating",
  },
  {
    id: "RSK-002",
    name: "Unpatched Server Vulnerabilities",
    owner: "Sarah Connor",
    severity: "High",
    status: "Open",
  },
  {
    id: "RSK-003",
    name: "Lack of MFA on Admin Panel",
    owner: "IT Security",
    severity: "Medium",
    status: "Resolved",
  },
  {
    id: "RSK-004",
    name: "Third-party Vendor Compliance",
    owner: "Procurement",
    severity: "Low",
    status: "Accepted",
  },
];

const columns = [
  "ID",
  "RISK NAME",
  "OWNER",
  "SEVERITY",
  "STATUS",
  "ACTIONS",
];

export default function RiskRegister() {
  const [risksList, setRisksList] = useState<RiskItem[]>(initialRisks);
  const [filterValue, setFilterValue] = useState("");
  const [severityFilter, setSeverityFilter] = useState<string>("All");
  const [statusFilter, setStatusFilter] = useState<string>("All");
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [exportNotice, setExportNotice] = useState(false);

  // Modal: Register New Risk
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [newOwner, setNewOwner] = useState("");
  const [newSeverity, setNewSeverity] = useState<RiskItem["severity"]>("High");
  const [newStatus, setNewStatus] = useState<RiskItem["status"]>("Open");
  const [addSuccess, setAddSuccess] = useState(false);

  // Modal: Edit Risk
  const [editingRisk, setEditingRisk] = useState<RiskItem | null>(null);
  const [editSuccess, setEditSuccess] = useState(false);

  const activeFiltersCount =
    (severityFilter !== "All" ? 1 : 0) + (statusFilter !== "All" ? 1 : 0);

  const filteredRisks = risksList.filter((risk) => {
    const matchesSearch = `${risk.id} ${risk.name} ${risk.owner} ${risk.severity} ${risk.status}`
      .toLowerCase()
      .includes(filterValue.toLowerCase());

    const matchesSeverity =
      severityFilter === "All" || risk.severity === severityFilter;

    const matchesStatus =
      statusFilter === "All" || risk.status === statusFilter;

    return matchesSearch && matchesSeverity && matchesStatus;
  });

  const handleExportCSV = () => {
    const headers = ["ID", "Risk Name", "Owner", "Severity", "Status"];
    const rows = filteredRisks.map((r) => [
      `"${r.id}"`,
      `"${r.name.replace(/"/g, '""')}"`,
      `"${r.owner.replace(/"/g, '""')}"`,
      `"${r.severity}"`,
      `"${r.status}"`,
    ]);
    const csvContent = [headers.join(","), ...rows.map((row) => row.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `cygrc_risk_register_export_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    setExportNotice(true);
    setTimeout(() => setExportNotice(false), 2500);
  };

  const handleAddRisk = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim() || !newOwner.trim()) return;

    const nextNumber = risksList.length + 1;
    const nextId = `RSK-${String(nextNumber).padStart(3, "0")}`;

    const newRisk: RiskItem = {
      id: nextId,
      name: newName.trim(),
      owner: newOwner.trim(),
      severity: newSeverity,
      status: newStatus,
    };

    setRisksList((prev) => [newRisk, ...prev]);
    setAddSuccess(true);
    setTimeout(() => {
      setAddSuccess(false);
      setIsAddModalOpen(false);
      setNewName("");
      setNewOwner("");
    }, 1200);
  };

  const handleUpdateRisk = (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingRisk) return;

    setRisksList((prev) =>
      prev.map((r) => (r.id === editingRisk.id ? editingRisk : r))
    );
    setEditSuccess(true);
    setTimeout(() => {
      setEditSuccess(false);
      setEditingRisk(null);
    }, 1000);
  };

  const handleDeleteRisk = (id: string) => {
    setRisksList((prev) => prev.filter((r) => r.id !== id));
    setEditingRisk(null);
  };

  return (
    <div className="space-y-6">
      {/* HEADER */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2">
            <div className="h-1 w-8 rounded-full bg-orange-500" />
            <span className="font-mono text-[9px] font-semibold tracking-[0.2em] text-orange-400">
              RISK_REGISTER
            </span>
          </div>

          <h2 className="text-2xl font-semibold tracking-tight text-white">
            Risk Register
          </h2>

          <p className="mt-1 text-sm text-zinc-500">
            Identify, monitor, and manage organizational risks.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setIsAddModalOpen(true)}
          className="flex w-fit items-center gap-2 rounded-xl bg-orange-500 px-4 py-2.5 text-sm font-semibold text-black shadow-lg shadow-orange-500/10 transition hover:bg-orange-400 active:scale-[0.98]"
        >
          <Plus size={17} />
          Register New Risk
        </button>
      </div>

      {/* REGISTER CARD */}
      <div className="overflow-hidden rounded-2xl border border-orange-500/15 bg-[#080807] shadow-[0_10px_40px_rgba(0,0,0,0.18)]">
        {/* TOOLBAR */}
        <div className="flex flex-col gap-4 border-b border-orange-500/10 p-5 lg:flex-row lg:items-center lg:justify-between">
          {/* SEARCH */}
          <div className="w-full lg:max-w-md">
            <div className="flex items-center gap-2 rounded-xl border border-zinc-800 bg-[#050505] px-3 py-2.5 transition focus-within:border-orange-500/40">
              <Search
                size={17}
                className="shrink-0 text-zinc-600"
              />

              <input
                type="text"
                value={filterValue}
                onChange={(event) => setFilterValue(event.target.value)}
                placeholder="Search risks by name, owner, severity, status..."
                className="w-full bg-transparent text-sm text-zinc-200 outline-none placeholder:text-zinc-600"
              />
              {filterValue && (
                <button
                  onClick={() => setFilterValue("")}
                  className="text-xs text-zinc-500 hover:text-zinc-300"
                >
                  <X size={14} />
                </button>
              )}
            </div>
          </div>

          {/* ACTIONS */}
          <div className="relative flex items-center gap-2">
            <button
              type="button"
              onClick={() => setIsFilterOpen(!isFilterOpen)}
              className={`flex items-center gap-2 rounded-xl border px-3.5 py-2.5 text-xs font-semibold transition ${
                activeFiltersCount > 0
                  ? "border-orange-500 bg-orange-500/10 text-orange-400"
                  : "border-zinc-800 bg-[#050505] text-zinc-400 hover:border-orange-500/20 hover:text-orange-400"
              }`}
            >
              <Filter size={14} />
              <span>Filters</span>
              {activeFiltersCount > 0 && (
                <span className="flex h-4 w-4 items-center justify-center rounded-full bg-orange-500 text-[10px] font-bold text-black">
                  {activeFiltersCount}
                </span>
              )}
              <ChevronDown
                size={14}
                className={`transition-transform ${isFilterOpen ? "rotate-180" : ""}`}
              />
            </button>

            <button
              type="button"
              onClick={handleExportCSV}
              className="flex items-center gap-2 rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-xs font-semibold text-zinc-400 transition hover:border-emerald-500/20 hover:text-emerald-400"
            >
              <Download size={15} />
              {exportNotice ? "Exported!" : "Export CSV"}
            </button>

            {/* FILTER DROPDOWN MENU */}
            <AnimatePresence>
              {isFilterOpen && (
                <motion.div
                  initial={{ opacity: 0, y: 8, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 8, scale: 0.95 }}
                  className="absolute right-0 top-12 z-30 w-72 rounded-xl border border-orange-500/20 bg-[#0c0d12] p-4 shadow-2xl"
                >
                  <div className="flex items-center justify-between border-b border-zinc-800 pb-2.5">
                    <span className="text-xs font-semibold text-zinc-200">
                      Filter Risks
                    </span>
                    {(severityFilter !== "All" || statusFilter !== "All") && (
                      <button
                        onClick={() => {
                          setSeverityFilter("All");
                          setStatusFilter("All");
                        }}
                        className="text-[11px] text-orange-400 hover:underline"
                      >
                        Reset All
                      </button>
                    )}
                  </div>

                  <div className="mt-3 space-y-3">
                    <div>
                      <label className="text-[11px] font-medium text-zinc-400">
                        Severity
                      </label>
                      <div className="mt-1 flex flex-wrap gap-1.5">
                        {["All", "Critical", "High", "Medium", "Low"].map((s) => (
                          <button
                            key={s}
                            onClick={() => setSeverityFilter(s)}
                            className={`rounded-lg px-2.5 py-1 text-[11px] font-semibold transition ${
                              severityFilter === s
                                ? "bg-orange-500 text-black font-bold"
                                : "border border-zinc-800 bg-black/40 text-zinc-400 hover:text-zinc-200"
                            }`}
                          >
                            {s}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="text-[11px] font-medium text-zinc-400">
                        Status
                      </label>
                      <div className="mt-1 flex flex-wrap gap-1.5">
                        {["All", "Open", "Mitigating", "Resolved", "Accepted"].map((st) => (
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

        {/* ACTIVE FILTER PILLS */}
        {(activeFiltersCount > 0 || filterValue) && (
          <div className="flex flex-wrap items-center gap-2 border-b border-orange-500/10 bg-orange-500/[0.02] px-5 py-2.5 text-xs">
            <span className="text-[11px] text-zinc-500">Active filters:</span>
            {filterValue && (
              <span className="flex items-center gap-1 rounded-md bg-zinc-800 px-2 py-0.5 text-zinc-300 text-[11px]">
                Search: &quot;{filterValue}&quot;
                <button onClick={() => setFilterValue("")} className="hover:text-white">
                  <X size={11} />
                </button>
              </span>
            )}
            {severityFilter !== "All" && (
              <span className="flex items-center gap-1 rounded-md bg-zinc-800 px-2 py-0.5 text-orange-400 text-[11px]">
                Severity: {severityFilter}
                <button onClick={() => setSeverityFilter("All")} className="hover:text-white">
                  <X size={11} />
                </button>
              </span>
            )}
            {statusFilter !== "All" && (
              <span className="flex items-center gap-1 rounded-md bg-zinc-800 px-2 py-0.5 text-emerald-400 text-[11px]">
                Status: {statusFilter}
                <button onClick={() => setStatusFilter("All")} className="hover:text-white">
                  <X size={11} />
                </button>
              </span>
            )}
            <button
              onClick={() => {
                setFilterValue("");
                setSeverityFilter("All");
                setStatusFilter("All");
              }}
              className="text-[11px] text-zinc-500 hover:text-orange-400 ml-auto"
            >
              Clear all
            </button>
          </div>
        )}

        {/* TABLE */}
        <div className="overflow-x-auto p-5">
          <div className="overflow-hidden rounded-xl border border-orange-500/10">
            <table className="min-w-full text-sm">
              <thead className="bg-[#111111]">
                <tr>
                  {columns.map((column) => (
                    <th
                      key={column}
                      className="whitespace-nowrap px-4 py-3.5 text-left font-mono text-[9px] font-semibold tracking-[0.15em] text-zinc-500"
                    >
                      {column}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {filteredRisks.length === 0 ? (
                  <tr>
                    <td
                      colSpan={columns.length}
                      className="px-4 py-12 text-center"
                    >
                      <ShieldAlert
                        size={30}
                        className="mx-auto mb-3 text-zinc-700"
                      />

                      <p className="text-sm text-zinc-500">
                        No risks found
                      </p>

                      {(filterValue || activeFiltersCount > 0) && (
                        <p className="mt-1 text-xs text-zinc-600">
                          Try adjusting or clearing your filters.
                        </p>
                      )}
                    </td>
                  </tr>
                ) : (
                  filteredRisks.map((risk) => (
                    <tr
                      key={risk.id}
                      className="border-t border-orange-500/10 transition hover:bg-orange-500/[0.025]"
                    >
                      {/* ID */}
                      <td className="whitespace-nowrap px-4 py-4">
                        <span className="font-mono text-xs font-semibold text-orange-400">
                          {risk.id}
                        </span>
                      </td>

                      {/* RISK NAME */}
                      <td className="px-4 py-4">
                        <div className="min-w-[220px]">
                          <p className="font-medium text-zinc-200">
                            {risk.name}
                          </p>
                          <p className="mt-1 text-[10px] text-zinc-600">
                            Organizational risk
                          </p>
                        </div>
                      </td>

                      {/* OWNER */}
                      <td className="whitespace-nowrap px-4 py-4 text-zinc-400">
                        {risk.owner}
                      </td>

                      {/* SEVERITY */}
                      <td className="whitespace-nowrap px-4 py-4">
                        <SeverityChip severity={risk.severity} />
                      </td>

                      {/* STATUS */}
                      <td className="whitespace-nowrap px-4 py-4">
                        <StatusChip status={risk.status} />
                      </td>

                      {/* ACTION */}
                      <td className="whitespace-nowrap px-4 py-4">
                        <button
                          type="button"
                          onClick={() => setEditingRisk({ ...risk })}
                          className="inline-flex items-center gap-1.5 rounded-lg border border-zinc-800 bg-[#050505] px-3 py-1.5 text-xs font-medium text-zinc-400 transition hover:border-orange-500/30 hover:text-orange-400"
                        >
                          <Pencil size={13} />
                          Edit
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* FOOTER */}
        <div className="flex flex-col gap-2 border-t border-orange-500/10 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
          <span className="text-xs text-zinc-600">
            Total{" "}
            <span className="font-medium text-zinc-400">
              {filteredRisks.length}
            </span>{" "}
            of {risksList.length} Risks
          </span>

          <div className="flex items-center gap-4 text-xs text-zinc-600">
            <span>
              Page <span className="text-zinc-400">1</span> of{" "}
              <span className="text-zinc-400">1</span>
            </span>
          </div>
        </div>
      </div>

      {/* ========================================================
          MODAL: REGISTER NEW RISK
      ======================================================== */}
      <AnimatePresence>
        {isAddModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsAddModalOpen(false)}
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
                    <h3 className="text-lg font-bold text-white">Register New Risk</h3>
                    <p className="text-xs text-zinc-400">Add entry to the organizational risk register</p>
                  </div>
                </div>
                <button
                  onClick={() => setIsAddModalOpen(false)}
                  className="rounded-lg p-1.5 text-zinc-400 hover:bg-zinc-800 hover:text-white"
                >
                  <X size={18} />
                </button>
              </div>

              {addSuccess ? (
                <div className="py-8 text-center">
                  <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400">
                    <CheckCircle2 size={32} />
                  </div>
                  <h4 className="mt-4 text-base font-semibold text-white">Risk Registered!</h4>
                  <p className="mt-1 text-xs text-zinc-400">The risk entry has been added to the register.</p>
                </div>
              ) : (
                <form onSubmit={handleAddRisk} className="mt-4 space-y-4">
                  <div>
                    <label className="text-xs font-semibold text-zinc-300">Risk Name *</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Sensitive Data Exposure via API"
                      value={newName}
                      onChange={(e) => setNewName(e.target.value)}
                      className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-zinc-300">Risk Owner *</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. SecOps Lead / Jane Doe"
                      value={newOwner}
                      onChange={(e) => setNewOwner(e.target.value)}
                      className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="text-xs font-semibold text-zinc-300">Severity</label>
                      <select
                        value={newSeverity}
                        onChange={(e) => setNewSeverity(e.target.value as RiskItem["severity"])}
                        className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                      >
                        <option value="Critical">Critical</option>
                        <option value="High">High</option>
                        <option value="Medium">Medium</option>
                        <option value="Low">Low</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-xs font-semibold text-zinc-300">Status</label>
                      <select
                        value={newStatus}
                        onChange={(e) => setNewStatus(e.target.value as RiskItem["status"])}
                        className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                      >
                        <option value="Open">Open</option>
                        <option value="Mitigating">Mitigating</option>
                        <option value="Resolved">Resolved</option>
                        <option value="Accepted">Accepted</option>
                      </select>
                    </div>
                  </div>

                  <div className="flex items-center justify-end gap-2 pt-4">
                    <button
                      type="button"
                      onClick={() => setIsAddModalOpen(false)}
                      className="rounded-xl border border-zinc-800 px-4 py-2 text-xs font-semibold text-zinc-400 hover:bg-zinc-800"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="flex items-center gap-1.5 rounded-xl bg-orange-500 px-4 py-2 text-xs font-semibold text-black transition hover:bg-orange-400 shadow-md shadow-orange-500/20"
                    >
                      <Plus size={14} />
                      Register Risk
                    </button>
                  </div>
                </form>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ========================================================
          MODAL: EDIT RISK
      ======================================================== */}
      <AnimatePresence>
        {editingRisk && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setEditingRisk(null)}
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
                    <Pencil size={18} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Edit Risk {editingRisk.id}</h3>
                    <p className="text-xs text-zinc-400">Update risk details, severity, and mitigation status</p>
                  </div>
                </div>
                <button
                  onClick={() => setEditingRisk(null)}
                  className="rounded-lg p-1.5 text-zinc-400 hover:bg-zinc-800 hover:text-white"
                >
                  <X size={18} />
                </button>
              </div>

              {editSuccess ? (
                <div className="py-8 text-center">
                  <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400">
                    <CheckCircle2 size={32} />
                  </div>
                  <h4 className="mt-4 text-base font-semibold text-white">Risk Updated!</h4>
                  <p className="mt-1 text-xs text-zinc-400">Changes saved to register.</p>
                </div>
              ) : (
                <form onSubmit={handleUpdateRisk} className="mt-4 space-y-4">
                  <div>
                    <label className="text-xs font-semibold text-zinc-300">Risk Name *</label>
                    <input
                      type="text"
                      required
                      value={editingRisk.name}
                      onChange={(e) =>
                        setEditingRisk({ ...editingRisk, name: e.target.value })
                      }
                      className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-zinc-300">Risk Owner *</label>
                    <input
                      type="text"
                      required
                      value={editingRisk.owner}
                      onChange={(e) =>
                        setEditingRisk({ ...editingRisk, owner: e.target.value })
                      }
                      className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="text-xs font-semibold text-zinc-300">Severity</label>
                      <select
                        value={editingRisk.severity}
                        onChange={(e) =>
                          setEditingRisk({
                            ...editingRisk,
                            severity: e.target.value as RiskItem["severity"],
                          })
                        }
                        className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                      >
                        <option value="Critical">Critical</option>
                        <option value="High">High</option>
                        <option value="Medium">Medium</option>
                        <option value="Low">Low</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-xs font-semibold text-zinc-300">Status</label>
                      <select
                        value={editingRisk.status}
                        onChange={(e) =>
                          setEditingRisk({
                            ...editingRisk,
                            status: e.target.value as RiskItem["status"],
                          })
                        }
                        className="mt-1 w-full rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-orange-500/50"
                      >
                        <option value="Open">Open</option>
                        <option value="Mitigating">Mitigating</option>
                        <option value="Resolved">Resolved</option>
                        <option value="Accepted">Accepted</option>
                      </select>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-4">
                    <button
                      type="button"
                      onClick={() => handleDeleteRisk(editingRisk.id)}
                      className="flex items-center gap-1.5 text-xs text-red-400 hover:text-red-300 transition"
                    >
                      <Trash2 size={14} />
                      Delete Risk
                    </button>

                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => setEditingRisk(null)}
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
    </div>
  );
}

/* ---------------------------------------------
SEVERITY CHIP
--------------------------------------------- */

function SeverityChip({
severity,
}: {
severity: string;
}) {
if (severity === "Critical") {
return ( <Chip
     size="sm"
     className="border border-red-500/20 bg-red-500/10 text-red-400"
   >
Critical </Chip>
);
}

if (severity === "High") {
return ( <Chip
     size="sm"
     className="border border-orange-500/20 bg-orange-500/10 text-orange-400"
   >
High </Chip>
);
}

if (severity === "Medium") {
return ( <Chip
     size="sm"
     className="border border-yellow-500/20 bg-yellow-500/10 text-yellow-400"
   >
Medium </Chip>
);
}

return ( <Chip
   size="sm"
   className="border border-emerald-500/20 bg-emerald-500/10 text-emerald-400"
 >
Low </Chip>
);
}

/* ---------------------------------------------
STATUS CHIP
--------------------------------------------- */

function StatusChip({
status,
}: {
status: string;
}) {
if (status === "Resolved") {
return ( <Chip
     size="sm"
     className="border border-emerald-500/20 bg-emerald-500/10 text-emerald-400"
   >
Resolved </Chip>
);
}

if (status === "Open") {
return ( <Chip
     size="sm"
     className="border border-orange-500/20 bg-orange-500/10 text-orange-400"
   >
Open </Chip>
);
}

if (status === "Mitigating") {
return ( <Chip
     size="sm"
     className="border border-blue-500/20 bg-blue-500/10 text-blue-400"
   >
Mitigating </Chip>
);
}

return ( <Chip
   size="sm"
   className="border border-zinc-700 bg-zinc-800/50 text-zinc-400"
 >
Accepted </Chip>
);
}
