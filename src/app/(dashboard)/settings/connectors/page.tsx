"use client";

import React, { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Plug,
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ArrowUpRight,
  ShieldCheck,
  Database,
  Cloud,
  Server,
  KeyRound,
  RefreshCw,
  Settings2,
  Activity,
  Clock3,
  Code2,
  MessageSquare,
  X,
  Check,
  Globe,
  Trash2,
  Sliders,
  Shield,
  Zap,
} from "lucide-react";

/* =========================================================
   CONNECTOR DATA & TYPES
========================================================= */

interface Connector {
  id: string;
  name: string;
  description: string;
  category: "Cloud" | "Identity" | "Development" | "ITSM" | "Communication" | "Security";
  icon: React.ElementType;
  iconColor: string;
  iconBg: string;
  status: "Connected" | "Needs Attention" | "Disconnected";
  lastSync: string;
  records: string;
  health: number;
  endpoint?: string;
  syncFrequency?: string;
}

const initialConnectors: Connector[] = [
  {
    id: "conn-azure",
    name: "Microsoft Azure",
    description: "Cloud infrastructure and identity management",
    category: "Cloud",
    icon: Cloud,
    iconColor: "text-orange-400",
    iconBg: "bg-orange-500/10",
    status: "Connected",
    lastSync: "2 minutes ago",
    records: "12,482",
    health: 99,
    endpoint: "https://management.azure.com",
    syncFrequency: "Every 15 minutes",
  },
  {
    id: "conn-github",
    name: "GitHub Enterprise",
    description: "Repositories, secret scanning, and security findings",
    category: "Development",
    icon: Code2,
    iconColor: "text-green-400",
    iconBg: "bg-green-500/10",
    status: "Connected",
    lastSync: "5 minutes ago",
    records: "8,921",
    health: 98,
    endpoint: "https://api.github.com",
    syncFrequency: "Every 15 minutes",
  },
  {
    id: "conn-slack",
    name: "Slack",
    description: "Security notifications, incident triage, and alerts",
    category: "Communication",
    icon: MessageSquare,
    iconColor: "text-green-400",
    iconBg: "bg-green-500/10",
    status: "Connected",
    lastSync: "8 minutes ago",
    records: "3,284",
    health: 97,
    endpoint: "https://slack.com/api",
    syncFrequency: "Hourly",
  },
  {
    id: "conn-aws",
    name: "Amazon Web Services (AWS)",
    description: "Cloud resources, IAM, and configuration monitoring",
    category: "Cloud",
    icon: Cloud,
    iconColor: "text-orange-400",
    iconBg: "bg-orange-500/10",
    status: "Needs Attention",
    lastSync: "42 minutes ago",
    records: "16,204",
    health: 74,
    endpoint: "https://aws.amazon.com",
    syncFrequency: "Every 15 minutes",
  },
  {
    id: "conn-jira",
    name: "Jira Software",
    description: "Remediation tickets and audit action workflows",
    category: "Development",
    icon: Database,
    iconColor: "text-green-400",
    iconBg: "bg-green-500/10",
    status: "Connected",
    lastSync: "12 minutes ago",
    records: "6,721",
    health: 96,
    endpoint: "https://atlassian.net",
    syncFrequency: "Hourly",
  },
  {
    id: "conn-entra",
    name: "Microsoft Entra ID",
    description: "Enterprise identity, SSO, and access monitoring",
    category: "Identity",
    icon: KeyRound,
    iconColor: "text-orange-400",
    iconBg: "bg-orange-500/10",
    status: "Connected",
    lastSync: "3 minutes ago",
    records: "4,831",
    health: 100,
    endpoint: "https://graph.microsoft.com",
    syncFrequency: "Every 5 minutes",
  },
  {
    id: "conn-servicenow",
    name: "ServiceNow",
    description: "ITSM incident and change management workflows",
    category: "ITSM",
    icon: Server,
    iconColor: "text-green-400",
    iconBg: "bg-green-500/10",
    status: "Disconnected",
    lastSync: "Yesterday",
    records: "2,194",
    health: 0,
    endpoint: "https://service-now.com",
    syncFrequency: "Daily",
  },
  {
    id: "conn-okta",
    name: "Okta Workforce",
    description: "Workforce identity, user lifecycle, and MFA policies",
    category: "Identity",
    icon: ShieldCheck,
    iconColor: "text-orange-400",
    iconBg: "bg-orange-500/10",
    status: "Connected",
    lastSync: "7 minutes ago",
    records: "7,412",
    health: 99,
    endpoint: "https://okta.com",
    syncFrequency: "Every 15 minutes",
  },
];

const availableConnectorPresets = [
  {
    name: "Google Cloud Platform (GCP)",
    description: "GCP projects, IAM roles, and Cloud Asset inventory",
    category: "Cloud" as const,
    icon: Cloud,
    iconColor: "text-orange-400",
    iconBg: "bg-orange-500/10",
    defaultEndpoint: "https://cloudasset.googleapis.com",
  },
  {
    name: "CrowdStrike Falcon",
    description: "Endpoint detection, threat telemetry, and host coverage",
    category: "Security" as const,
    icon: Shield,
    iconColor: "text-red-400",
    iconBg: "bg-red-500/10",
    defaultEndpoint: "https://api.crowdstrike.com",
  },
  {
    name: "Datadog",
    description: "Infrastructure monitoring, audit logs, and security signals",
    category: "ITSM" as const,
    icon: Server,
    iconColor: "text-purple-400",
    iconBg: "bg-purple-500/10",
    defaultEndpoint: "https://api.datadoghq.com",
  },
  {
    name: "GitLab",
    description: "Source code repositories, pipelines, and dependency scanning",
    category: "Development" as const,
    icon: Code2,
    iconColor: "text-green-400",
    iconBg: "bg-green-500/10",
    defaultEndpoint: "https://gitlab.com/api/v4",
  },
  {
    name: "PagerDuty",
    description: "Incident escalation and on-call alerting integrations",
    category: "Communication" as const,
    icon: Zap,
    iconColor: "text-emerald-400",
    iconBg: "bg-emerald-500/10",
    defaultEndpoint: "https://api.pagerduty.com",
  },
];

/* =========================================================
   STAT CARD
========================================================= */

function StatCard({
  title,
  value,
  change,
  description,
  icon: Icon,
  color,
}: {
  title: string;
  value: string;
  change: string;
  description: string;
  icon: React.ElementType;
  color: string;
}) {
  const colors: Record<string, string> = {
    orange: "bg-orange-500/10 text-orange-400 border-orange-500/20",
    green: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  };

  return (
    <motion.div
      whileHover={{ y: -3 }}
      transition={{ duration: 0.2 }}
      className="relative overflow-hidden rounded-xl border border-white/[0.08] bg-[#0b0d0c] p-6 shadow-[0_8px_30px_rgba(0,0,0,0.25)]"
    >
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-orange-500/30 to-transparent" />

      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-400">{title}</p>
          <motion.p
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-3 text-3xl font-bold tracking-tight text-white"
          >
            {value}
          </motion.p>
        </div>

        <div
          className={`flex h-12 w-12 items-center justify-center rounded-xl border ${colors[color]}`}
        >
          <Icon size={22} strokeWidth={2} />
        </div>
      </div>

      <div className="mt-5 flex items-center gap-2 text-xs">
        <span
          className={
            color === "orange"
              ? "font-semibold text-orange-400"
              : "font-semibold text-emerald-400"
          }
        >
          ↗ {change}
        </span>
        <span className="text-slate-500">{description}</span>
      </div>
    </motion.div>
  );
}

/* =========================================================
   STATUS BADGE
========================================================= */

function StatusBadge({ status }: { status: string }) {
  if (status === "Connected") {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400">
        <CheckCircle2 size={13} />
        Connected
      </span>
    );
  }

  if (status === "Needs Attention") {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full border border-orange-500/20 bg-orange-500/10 px-3 py-1 text-xs font-medium text-orange-400">
        <AlertTriangle size={13} />
        Needs Attention
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-red-500/20 bg-red-500/10 px-3 py-1 text-xs font-medium text-red-400">
      <XCircle size={13} />
      Disconnected
    </span>
  );
}

/* =========================================================
   MAIN COMPONENT
========================================================= */

export default function ConnectorsPage() {
  // State
  const [connectors, setConnectors] = useState<Connector[]>(initialConnectors);
  const [selectedCategory, setSelectedCategory] = useState<string>("All Connectors");
  const [searchQuery, setSearchQuery] = useState("");
  const [filterNeedsAttention, setFilterNeedsAttention] = useState(false);

  // Modals state
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [configureConnector, setConfigureConnector] = useState<Connector | null>(null);
  const [feedback, setFeedback] = useState<{
    type: "success" | "info" | "warning";
    message: string;
  } | null>(null);

  // Add Connector Form State
  const [newConnectorType, setNewConnectorType] = useState<string>("custom");
  const [newConnectorName, setNewConnectorName] = useState("");
  const [newConnectorCategory, setNewConnectorCategory] = useState<Connector["category"]>("Cloud");
  const [newConnectorEndpoint, setNewConnectorEndpoint] = useState("");
  const [newConnectorSyncFreq, setNewConnectorSyncFreq] = useState("Every 15 minutes");
  const [newConnectorToken, setNewConnectorToken] = useState("");
  const [addFormError, setAddFormError] = useState("");

  // Categories with dynamic counts
  const categories = useMemo(() => {
    const list = [
      "All Connectors",
      "Cloud",
      "Identity",
      "Development",
      "ITSM",
      "Communication",
      "Security",
    ];

    return list.map((catName) => {
      const count =
        catName === "All Connectors"
          ? connectors.length
          : connectors.filter((c) => c.category === catName).length;
      return { name: catName, count };
    });
  }, [connectors]);

  // Filtered connectors based on Category, Live Search, and Attention Filter
  const filteredConnectors = useMemo(() => {
    return connectors.filter((connector) => {
      // Category filter
      const matchesCategory =
        selectedCategory === "All Connectors" ||
        connector.category === selectedCategory;

      // Search query filter
      const q = searchQuery.toLowerCase().trim();
      const matchesSearch =
        !q ||
        connector.name.toLowerCase().includes(q) ||
        connector.description.toLowerCase().includes(q) ||
        connector.category.toLowerCase().includes(q) ||
        connector.status.toLowerCase().includes(q);

      // Attention only filter
      const matchesAttention = !filterNeedsAttention || connector.status === "Needs Attention";

      return matchesCategory && matchesSearch && matchesAttention;
    });
  }, [connectors, selectedCategory, searchQuery, filterNeedsAttention]);

  // Dynamic statistics
  const stats = useMemo(() => {
    const total = connectors.length;
    const connected = connectors.filter((c) => c.status === "Connected").length;
    const needsAttention = connectors.filter((c) => c.status === "Needs Attention").length;
    const avgHealth =
      total > 0
        ? Math.round(connectors.reduce((acc, curr) => acc + curr.health, 0) / total)
        : 0;

    return [
      {
        title: "Total Connectors",
        value: String(total),
        change: `+${total - 8 >= 0 ? total - 8 : 0} custom`,
        description: "active integrations",
        icon: Plug,
        color: "orange",
      },
      {
        title: "Connected",
        value: String(connected),
        change: `${total > 0 ? Math.round((connected / total) * 100) : 0}%`,
        description: "healthy connections",
        icon: CheckCircle2,
        color: "green",
      },
      {
        title: "Needs Attention",
        value: String(needsAttention),
        change: needsAttention > 0 ? `${needsAttention} alerts` : "None",
        description: "require administrative review",
        icon: AlertTriangle,
        color: "orange",
      },
      {
        title: "Connector Health",
        value: `${avgHealth}%`,
        change: "Overall",
        description: "health average score",
        icon: RefreshCw,
        color: "green",
      },
    ];
  }, [connectors]);

  // Handle Preset Selection in Add Modal
  const handleSelectPreset = (presetName: string) => {
    const preset = availableConnectorPresets.find((p) => p.name === presetName);
    if (preset) {
      setNewConnectorType(preset.name);
      setNewConnectorName(preset.name);
      setNewConnectorCategory(preset.category);
      setNewConnectorEndpoint(preset.defaultEndpoint);
    } else {
      setNewConnectorType("custom");
      setNewConnectorName("");
      setNewConnectorEndpoint("");
    }
  };

  // Handle Add Connector Submit
  const handleCreateConnector = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newConnectorName.trim()) {
      setAddFormError("Service name is required.");
      return;
    }

    const preset = availableConnectorPresets.find((p) => p.name === newConnectorType);

    const newConn: Connector = {
      id: `conn-${Date.now()}`,
      name: newConnectorName.trim(),
      description:
        preset?.description ||
        `Custom ${newConnectorCategory} integration for enterprise security sync.`,
      category: newConnectorCategory,
      icon: preset?.icon || Plug,
      iconColor: preset?.iconColor || "text-orange-400",
      iconBg: preset?.iconBg || "bg-orange-500/10",
      status: "Connected",
      lastSync: "Just now",
      records: "100",
      health: 100,
      endpoint: newConnectorEndpoint || "https://api.internal.corp",
      syncFrequency: newConnectorSyncFreq,
    };

    setConnectors((prev) => [newConn, ...prev]);
    setAddModalOpen(false);
    setNewConnectorName("");
    setNewConnectorEndpoint("");
    setNewConnectorToken("");
    setAddFormError("");

    setFeedback({
      type: "success",
      message: `Connector "${newConn.name}" created and connected successfully (simulated client-side integration).`,
    });
  };

  // Handle Configure Modal Save
  const handleSaveConfiguration = (updated: Connector) => {
    setConnectors((prev) =>
      prev.map((c) => (c.id === updated.id ? updated : c))
    );
    setConfigureConnector(null);
    setFeedback({
      type: "success",
      message: `Configuration saved for "${updated.name}".`,
    });
  };

  // Handle Trigger Sync
  const handleSyncNow = (id: string) => {
    setConnectors((prev) =>
      prev.map((c) => {
        if (c.id === id) {
          return {
            ...c,
            lastSync: "Just now",
            health: c.status === "Disconnected" ? 95 : Math.min(100, c.health + 5),
            status: c.status === "Disconnected" ? "Connected" : c.status,
          };
        }
        return c;
      })
    );
    if (configureConnector?.id === id) {
      setConfigureConnector((curr) =>
        curr
          ? {
              ...curr,
              lastSync: "Just now",
              health: Math.min(100, curr.health + 5),
              status: curr.status === "Disconnected" ? "Connected" : curr.status,
            }
          : null
      );
    }
    setFeedback({
      type: "info",
      message: "Sync triggered. Security telemetry refreshed successfully.",
    });
  };

  // Handle Delete / Disconnect
  const handleDeleteConnector = (id: string, name: string) => {
    setConnectors((prev) => prev.filter((c) => c.id !== id));
    setConfigureConnector(null);
    setFeedback({
      type: "warning",
      message: `Connector "${name}" was disconnected and removed.`,
    });
  };

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#050606] text-white">
      {/* BACKGROUND GLOW */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -right-40 top-20 h-96 w-96 rounded-full bg-orange-500/[0.04] blur-3xl" />
        <div className="absolute bottom-0 left-1/3 h-96 w-96 rounded-full bg-emerald-500/[0.035] blur-3xl" />
        <div className="absolute left-0 top-1/2 h-80 w-80 rounded-full bg-orange-500/[0.025] blur-3xl" />
      </div>

      <div className="relative space-y-7 p-6 lg:p-9">
        {/* FEEDBACK BANNER */}
        <AnimatePresence>
          {feedback && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className={`flex items-center justify-between rounded-xl border p-4 text-xs font-medium shadow-lg backdrop-blur-md ${
                feedback.type === "success"
                  ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
                  : feedback.type === "warning"
                  ? "border-red-500/30 bg-red-500/10 text-red-300"
                  : "border-orange-500/30 bg-orange-500/10 text-orange-300"
              }`}
            >
              <div className="flex items-center gap-2.5">
                {feedback.type === "success" ? (
                  <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
                ) : feedback.type === "warning" ? (
                  <AlertTriangle size={16} className="text-red-400 shrink-0" />
                ) : (
                  <RefreshCw size={16} className="text-orange-400 shrink-0" />
                )}
                <span>{feedback.message}</span>
              </div>
              <button
                type="button"
                onClick={() => setFeedback(null)}
                className="text-white/60 hover:text-white transition ml-3"
              >
                <X size={15} />
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* HEADER */}
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col justify-between gap-5 xl:flex-row xl:items-center"
        >
          <div>
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-orange-500/20 bg-orange-500/10 text-orange-400">
                <Plug size={22} />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-white">
                  Connectors
                </h1>
                <p className="mt-1 text-sm text-slate-400">
                  Connect CYGRC with your cloud, identity, and security ecosystem.
                </p>
              </div>
            </div>
          </div>

          {/* ADD CONNECTOR BUTTON */}
          <button
            type="button"
            onClick={() => setAddModalOpen(true)}
            className="flex h-10 items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-orange-500 to-orange-600 px-5 text-sm font-semibold text-black shadow-lg shadow-orange-900/20 transition hover:from-orange-400 hover:to-orange-500 active:scale-95"
          >
            <Plus size={17} />
            Add Connector
          </button>
        </motion.div>

        {/* STATISTICS */}
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.08 }}
            >
              <StatCard {...stat} />
            </motion.div>
          ))}
        </div>

        {/* MAIN GRID */}
        <div className="grid gap-6 xl:grid-cols-[240px_minmax(0,1fr)]">
          {/* CATEGORIES SIDEBAR */}
          <motion.aside
            initial={{ opacity: 0, x: -15 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.25 }}
            className="h-fit rounded-xl border border-white/[0.08] bg-[#0b0d0c] p-4"
          >
            <div className="mb-4 px-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Categories
              </p>
            </div>

            <div className="space-y-1">
              {categories.map((category) => {
                const isActive = selectedCategory === category.name;
                return (
                  <button
                    key={category.name}
                    type="button"
                    onClick={() => setSelectedCategory(category.name)}
                    className={`flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-left text-sm transition ${
                      isActive
                        ? "bg-orange-500/15 text-orange-400 font-semibold border border-orange-500/30"
                        : "text-slate-400 hover:bg-white/[0.04] hover:text-white"
                    }`}
                  >
                    <span>{category.name}</span>
                    <span
                      className={`rounded-md px-2 py-0.5 text-[10px] ${
                        isActive
                          ? "bg-orange-500/20 text-orange-300 font-bold"
                          : "bg-white/[0.04] text-slate-600"
                      }`}
                    >
                      {category.count}
                    </span>
                  </button>
                );
              })}
            </div>

            <div className="my-5 h-px bg-white/[0.06]" />

            {/* HEALTH SUMMARY */}
            <div className="rounded-lg border border-orange-500/10 bg-orange-500/[0.04] p-3">
              <div className="flex items-center gap-2">
                <Activity size={15} className="text-orange-400" />
                <span className="text-xs font-semibold text-slate-300">
                  Connector Health
                </span>
              </div>

              <div className="mt-3 flex items-end justify-between">
                <span className="text-2xl font-bold text-white">96.4%</span>
                <span className="text-[10px] font-medium text-emerald-400">
                  Healthy
                </span>
              </div>

              <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/[0.06]">
                <div className="h-full w-[96%] rounded-full bg-gradient-to-r from-orange-500 to-emerald-500" />
              </div>
            </div>
          </motion.aside>

          {/* CONNECTOR SECTION */}
          <motion.section
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="overflow-hidden rounded-xl border border-white/[0.08] bg-[#0b0d0c]"
          >
            {/* TOOLBAR */}
            <div className="flex flex-col gap-4 border-b border-white/[0.07] p-5 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <h2 className="text-lg font-semibold text-white">
                  Connected Services
                </h2>
                <p className="mt-1 text-sm text-slate-500">
                  Showing {filteredConnectors.length} of {connectors.length} configured services.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                {/* LIVE SEARCH */}
                <div className="flex h-9 items-center gap-2 rounded-lg border border-white/10 bg-[#050606] px-3 focus-within:border-orange-500/50 transition">
                  <Search size={15} className="text-slate-500 shrink-0" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search connectors..."
                    className="w-40 sm:w-48 bg-transparent text-xs text-white outline-none placeholder:text-slate-600"
                  />
                  {searchQuery && (
                    <button
                      type="button"
                      onClick={() => setSearchQuery("")}
                      className="text-slate-500 hover:text-white"
                    >
                      <X size={12} />
                    </button>
                  )}
                </div>

                {/* FILTER BY ATTENTION */}
                <button
                  type="button"
                  onClick={() => setFilterNeedsAttention(!filterNeedsAttention)}
                  className={`flex h-9 items-center gap-2 rounded-lg border px-3 text-xs transition ${
                    filterNeedsAttention
                      ? "border-orange-500/50 bg-orange-500/10 text-orange-400 font-semibold"
                      : "border-white/10 bg-[#050606] text-slate-400 hover:border-orange-500/20 hover:text-orange-400"
                  }`}
                >
                  <Filter size={14} />
                  {filterNeedsAttention ? "Needs Attention Only" : "Filter"}
                </button>
              </div>
            </div>

            {/* CONNECTOR CARDS GRID */}
            <div className="grid gap-4 p-5 md:grid-cols-2">
              {filteredConnectors.length === 0 ? (
                <div className="col-span-2 flex flex-col items-center justify-center p-12 text-center border border-dashed border-white/10 rounded-2xl">
                  <Plug size={36} className="text-slate-600 mb-3" />
                  <p className="text-sm font-semibold text-slate-300">
                    No connectors found
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    Try adjusting your search query or selected category filter.
                  </p>
                  <button
                    type="button"
                    onClick={() => {
                      setSearchQuery("");
                      setSelectedCategory("All Connectors");
                      setFilterNeedsAttention(false);
                    }}
                    className="mt-4 rounded-lg bg-white/5 border border-white/10 px-3 py-1.5 text-xs text-orange-400 hover:bg-orange-500/10 transition"
                  >
                    Reset all filters
                  </button>
                </div>
              ) : (
                filteredConnectors.map((connector, index) => {
                  const Icon = connector.icon;

                  return (
                    <motion.div
                      key={connector.id}
                      initial={{ opacity: 0, y: 12 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.05 * index }}
                      whileHover={{ y: -2 }}
                      className="group relative overflow-hidden rounded-xl border border-white/[0.07] bg-[#080a09] p-5 transition hover:border-orange-500/20 hover:shadow-[0_8px_30px_rgba(249,115,22,0.06)]"
                    >
                      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-orange-500/50 to-transparent opacity-0 transition group-hover:opacity-100" />

                      {/* CARD HEADER */}
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                          <div
                            className={`flex h-11 w-11 items-center justify-center rounded-xl ${connector.iconBg} ${connector.iconColor}`}
                          >
                            <Icon size={22} />
                          </div>
                          <div>
                            <h3 className="text-sm font-semibold text-white">
                              {connector.name}
                            </h3>
                            <p className="mt-1 text-[11px] text-slate-500">
                              {connector.category}
                            </p>
                          </div>
                        </div>

                        <button
                          type="button"
                          onClick={() => setConfigureConnector(connector)}
                          title="Connector Options"
                          className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-500 transition hover:bg-white/[0.05] hover:text-orange-400"
                        >
                          <MoreHorizontal size={17} />
                        </button>
                      </div>

                      {/* DESCRIPTION */}
                      <p className="mt-4 text-xs leading-5 text-slate-400">
                        {connector.description}
                      </p>

                      {/* STATUS */}
                      <div className="mt-4 flex items-center justify-between">
                        <StatusBadge status={connector.status} />
                        <span className="text-[10px] text-slate-500 font-mono">
                          {connector.syncFrequency || "Every 15m"}
                        </span>
                      </div>

                      {/* HEALTH */}
                      <div className="mt-5">
                        <div className="mb-2 flex items-center justify-between">
                          <span className="text-[11px] text-slate-500">
                            Connection health
                          </span>
                          <span
                            className={`text-[11px] font-semibold ${
                              connector.health >= 90
                                ? "text-emerald-400"
                                : connector.health > 0
                                ? "text-orange-400"
                                : "text-red-400"
                            }`}
                          >
                            {connector.health}%
                          </span>
                        </div>

                        <div className="h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
                          <div
                            style={{ width: `${connector.health}%` }}
                            className={`h-full rounded-full transition-all duration-500 ${
                              connector.health >= 90
                                ? "bg-emerald-500"
                                : connector.health > 0
                                ? "bg-orange-500"
                                : "bg-red-500"
                            }`}
                          />
                        </div>
                      </div>

                      {/* FOOTER */}
                      <div className="mt-5 flex items-center justify-between border-t border-white/[0.05] pt-4">
                        <div>
                          <p className="text-[10px] uppercase tracking-wider text-slate-500">
                            Last sync
                          </p>
                          <div className="mt-1 flex items-center gap-1.5">
                            <Clock3 size={12} className="text-slate-500" />
                            <span className="text-[11px] text-slate-300">
                              {connector.lastSync}
                            </span>
                          </div>
                        </div>

                        <div className="text-right">
                          <p className="text-[10px] uppercase tracking-wider text-slate-500">
                            Records
                          </p>
                          <p className="mt-1 text-xs font-semibold text-slate-300 font-mono">
                            {connector.records}
                          </p>
                        </div>
                      </div>

                      {/* CARD ACTIONS */}
                      <div className="mt-4 flex gap-2">
                        <button
                          type="button"
                          onClick={() => setConfigureConnector(connector)}
                          className="flex h-8 flex-1 items-center justify-center gap-1.5 rounded-lg border border-white/[0.07] bg-white/[0.02] text-[11px] font-medium text-slate-300 transition hover:border-orange-500/30 hover:bg-orange-500/[0.06] hover:text-orange-400 active:scale-[0.98]"
                        >
                          <Settings2 size={13} />
                          Configure
                        </button>

                        <button
                          type="button"
                          onClick={() => handleSyncNow(connector.id)}
                          title="Trigger Sync"
                          className="flex h-8 w-9 items-center justify-center rounded-lg border border-white/[0.07] bg-white/[0.02] text-slate-400 transition hover:border-emerald-500/30 hover:bg-emerald-500/[0.06] hover:text-emerald-400 active:scale-[0.98]"
                        >
                          <RefreshCw size={13} />
                        </button>
                      </div>
                    </motion.div>
                  );
                })
              )}
            </div>

            {/* FOOTER */}
            <div className="flex items-center justify-between border-t border-white/[0.06] px-5 py-4">
              <p className="text-xs text-slate-500">
                Showing{" "}
                <span className="text-slate-300">{filteredConnectors.length}</span>{" "}
                of{" "}
                <span className="text-slate-300">{connectors.length}</span>{" "}
                connectors
              </p>

              <button
                type="button"
                onClick={() => {
                  setSelectedCategory("All Connectors");
                  setSearchQuery("");
                  setFilterNeedsAttention(false);
                }}
                className="flex items-center gap-1.5 text-xs font-medium text-orange-400 transition hover:text-orange-300"
              >
                View all connectors
                <ArrowUpRight size={14} />
              </button>
            </div>
          </motion.section>
        </div>
      </div>

      {/* =========================================================
          ADD CONNECTOR MODAL
      ========================================================= */}
      {addModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="fixed inset-0 bg-black/75 backdrop-blur-sm"
            onClick={() => setAddModalOpen(false)}
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="relative z-10 w-full max-w-lg overflow-hidden rounded-2xl border border-orange-500/20 bg-[#0e0c1a] text-white shadow-2xl"
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-white/10 p-5 bg-[#141126]">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-orange-500/10 text-orange-400 border border-orange-500/20">
                  <Plus size={20} />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">
                    Add New Connector
                  </h3>
                  <p className="text-xs text-slate-400">
                    Connect an external service to synchronize security telemetry.
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setAddModalOpen(false)}
                className="rounded-lg p-1 text-slate-400 hover:bg-white/10 hover:text-white"
              >
                <X size={18} />
              </button>
            </div>

            {/* Modal Form */}
            <form onSubmit={handleCreateConnector} className="p-5 space-y-4">
              {addFormError && (
                <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-300 flex items-center gap-2">
                  <AlertTriangle size={14} className="shrink-0" />
                  <span>{addFormError}</span>
                </div>
              )}

              {/* Service Preset Selection */}
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                  Select Ecosystem Service
                </label>
                <div className="grid grid-cols-2 gap-2 max-h-36 overflow-y-auto pr-1">
                  {availableConnectorPresets.map((preset) => (
                    <button
                      key={preset.name}
                      type="button"
                      onClick={() => handleSelectPreset(preset.name)}
                      className={`flex items-center gap-2 rounded-xl border p-2.5 text-left text-xs transition ${
                        newConnectorType === preset.name
                          ? "border-orange-500 bg-orange-500/10 text-orange-400 font-semibold"
                          : "border-white/10 bg-white/[0.02] text-slate-300 hover:border-white/20 hover:bg-white/[0.05]"
                      }`}
                    >
                      <preset.icon size={16} className={preset.iconColor} />
                      <span className="truncate">{preset.name}</span>
                    </button>
                  ))}
                  <button
                    type="button"
                    onClick={() => handleSelectPreset("custom")}
                    className={`flex items-center gap-2 rounded-xl border p-2.5 text-left text-xs transition ${
                      newConnectorType === "custom"
                        ? "border-orange-500 bg-orange-500/10 text-orange-400 font-semibold"
                        : "border-white/10 bg-white/[0.02] text-slate-300 hover:border-white/20 hover:bg-white/[0.05]"
                    }`}
                  >
                    <Plug size={16} className="text-orange-400" />
                    <span>Custom REST Service</span>
                  </button>
                </div>
              </div>

              {/* Connector Name */}
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Integration Name
                </label>
                <input
                  type="text"
                  value={newConnectorName}
                  onChange={(e) => {
                    setNewConnectorName(e.target.value);
                    if (addFormError) setAddFormError("");
                  }}
                  placeholder="e.g. AWS Production US-East"
                  className="w-full rounded-xl border border-white/10 bg-[#07060f] px-3.5 py-2.5 text-xs text-white placeholder:text-slate-600 outline-none focus:border-orange-500/50"
                />
              </div>

              {/* Category & Frequency */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Category
                  </label>
                  <select
                    value={newConnectorCategory}
                    onChange={(e) =>
                      setNewConnectorCategory(
                        e.target.value as Connector["category"]
                      )
                    }
                    className="w-full rounded-xl border border-white/10 bg-[#07060f] px-3 py-2.5 text-xs text-white outline-none focus:border-orange-500/50"
                  >
                    <option value="Cloud">Cloud</option>
                    <option value="Identity">Identity</option>
                    <option value="Development">Development</option>
                    <option value="ITSM">ITSM</option>
                    <option value="Communication">Communication</option>
                    <option value="Security">Security</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Sync Schedule
                  </label>
                  <select
                    value={newConnectorSyncFreq}
                    onChange={(e) => setNewConnectorSyncFreq(e.target.value)}
                    className="w-full rounded-xl border border-white/10 bg-[#07060f] px-3 py-2.5 text-xs text-white outline-none focus:border-orange-500/50"
                  >
                    <option value="Every 5 minutes">Every 5 minutes</option>
                    <option value="Every 15 minutes">Every 15 minutes</option>
                    <option value="Hourly">Hourly</option>
                    <option value="Daily">Daily</option>
                  </select>
                </div>
              </div>

              {/* Endpoint */}
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  API Endpoint / Host URI
                </label>
                <input
                  type="text"
                  value={newConnectorEndpoint}
                  onChange={(e) => setNewConnectorEndpoint(e.target.value)}
                  placeholder="https://api.provider.com/v1"
                  className="w-full rounded-xl border border-white/10 bg-[#07060f] px-3.5 py-2.5 text-xs text-white placeholder:text-slate-600 outline-none focus:border-orange-500/50 font-mono"
                />
              </div>

              {/* Mock Token field with Security Disclaimer */}
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Access Key / API Token (Prototype Simulation)
                </label>
                <input
                  type="password"
                  value={newConnectorToken}
                  onChange={(e) => setNewConnectorToken(e.target.value)}
                  placeholder="••••••••••••••••••••••••"
                  className="w-full rounded-xl border border-white/10 bg-[#07060f] px-3.5 py-2.5 text-xs text-white placeholder:text-slate-600 outline-none focus:border-orange-500/50 font-mono"
                />
                <p className="mt-1 text-[11px] text-slate-500">
                  Demo mode: Simulation only. No credentials are saved or transmitted to remote servers.
                </p>
              </div>

              {/* Modal Actions */}
              <div className="flex items-center justify-end gap-3 pt-3 border-t border-white/10">
                <button
                  type="button"
                  onClick={() => setAddModalOpen(false)}
                  className="rounded-xl border border-white/10 px-4 py-2.5 text-xs font-semibold text-slate-400 hover:text-white hover:bg-white/5 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-xl bg-orange-500 px-5 py-2.5 text-xs font-semibold text-black hover:bg-orange-400 transition shadow-lg shadow-orange-500/20 active:scale-95"
                >
                  Connect Service
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}

      {/* =========================================================
          CONFIGURE CONNECTOR MODAL
      ========================================================= */}
      {configureConnector && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="fixed inset-0 bg-black/75 backdrop-blur-sm"
            onClick={() => setConfigureConnector(null)}
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="relative z-10 w-full max-w-lg overflow-hidden rounded-2xl border border-orange-500/20 bg-[#0e0c1a] text-white shadow-2xl"
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-white/10 p-5 bg-[#141126]">
              <div className="flex items-center gap-3">
                <div
                  className={`flex h-10 w-10 items-center justify-center rounded-xl ${configureConnector.iconBg} ${configureConnector.iconColor}`}
                >
                  <configureConnector.icon size={20} />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    {configureConnector.name}
                    <StatusBadge status={configureConnector.status} />
                  </h3>
                  <p className="text-xs text-slate-400">
                    Integration settings and sync controls
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setConfigureConnector(null)}
                className="rounded-lg p-1 text-slate-400 hover:bg-white/10 hover:text-white"
              >
                <X size={18} />
              </button>
            </div>

            {/* Content Form */}
            <div className="p-5 space-y-4">
              {/* Status Switcher */}
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                  Connection Status
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(["Connected", "Needs Attention", "Disconnected"] as const).map(
                    (st) => (
                      <button
                        key={st}
                        type="button"
                        onClick={() =>
                          setConfigureConnector({
                            ...configureConnector,
                            status: st,
                            health: st === "Connected" ? 98 : st === "Needs Attention" ? 65 : 0,
                          })
                        }
                        className={`rounded-xl border py-2 text-xs font-medium transition ${
                          configureConnector.status === st
                            ? st === "Connected"
                              ? "border-emerald-500 bg-emerald-500/10 text-emerald-400 font-bold"
                              : st === "Needs Attention"
                              ? "border-orange-500 bg-orange-500/10 text-orange-400 font-bold"
                              : "border-red-500 bg-red-500/10 text-red-400 font-bold"
                            : "border-white/10 bg-white/[0.02] text-slate-400 hover:border-white/20"
                        }`}
                      >
                        {st}
                      </button>
                    )
                  )}
                </div>
              </div>

              {/* Endpoint */}
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  API Endpoint Host
                </label>
                <input
                  type="text"
                  value={configureConnector.endpoint || "https://api.service.com"}
                  onChange={(e) =>
                    setConfigureConnector({
                      ...configureConnector,
                      endpoint: e.target.value,
                    })
                  }
                  className="w-full rounded-xl border border-white/10 bg-[#07060f] px-3.5 py-2.5 text-xs text-white outline-none focus:border-orange-500/50 font-mono"
                />
              </div>

              {/* Sync Schedule */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Sync Schedule
                  </label>
                  <select
                    value={configureConnector.syncFrequency || "Every 15 minutes"}
                    onChange={(e) =>
                      setConfigureConnector({
                        ...configureConnector,
                        syncFrequency: e.target.value,
                      })
                    }
                    className="w-full rounded-xl border border-white/10 bg-[#07060f] px-3 py-2.5 text-xs text-white outline-none focus:border-orange-500/50"
                  >
                    <option value="Every 5 minutes">Every 5 minutes</option>
                    <option value="Every 15 minutes">Every 15 minutes</option>
                    <option value="Hourly">Hourly</option>
                    <option value="Daily">Daily</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Last Health Metric
                  </label>
                  <div className="flex h-10 items-center justify-between rounded-xl border border-white/10 bg-[#07060f] px-3 text-xs">
                    <span className="text-slate-400">Score</span>
                    <span className="font-bold text-emerald-400">
                      {configureConnector.health}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Description
                </label>
                <textarea
                  rows={2}
                  value={configureConnector.description}
                  onChange={(e) =>
                    setConfigureConnector({
                      ...configureConnector,
                      description: e.target.value,
                    })
                  }
                  className="w-full rounded-xl border border-white/10 bg-[#07060f] p-3 text-xs text-white outline-none focus:border-orange-500/50 resize-none"
                />
              </div>

              {/* Quick Actions (Sync Now & Delete) */}
              <div className="flex items-center justify-between border-t border-white/10 pt-4">
                <button
                  type="button"
                  onClick={() =>
                    handleDeleteConnector(
                      configureConnector.id,
                      configureConnector.name
                    )
                  }
                  className="flex items-center gap-1.5 text-xs font-semibold text-red-400 hover:text-red-300 transition"
                >
                  <Trash2 size={14} />
                  Disconnect Service
                </button>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => handleSyncNow(configureConnector.id)}
                    className="flex items-center gap-1.5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-xs font-medium text-emerald-400 hover:bg-emerald-500/20 transition"
                  >
                    <RefreshCw size={13} />
                    Sync Now
                  </button>

                  <button
                    type="button"
                    onClick={() => handleSaveConfiguration(configureConnector)}
                    className="rounded-xl bg-orange-500 px-4 py-2 text-xs font-semibold text-black hover:bg-orange-400 transition"
                  >
                    Save Changes
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </main>
  );
}