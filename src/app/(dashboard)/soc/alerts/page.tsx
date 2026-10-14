"use client";

import { useEffect, useState } from "react";
import {
  AlertTriangle,
  ShieldAlert,
  CheckCircle2,
  Clock,
  Filter,
  Plus,
  RefreshCw,
  Search,
  Eye,
  SlidersHorizontal,
  ChevronRight,
  Terminal,
  Activity,
} from "lucide-react";

interface Alert {
  alert_id: string;
  title: string;
  source: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  status: "NEW" | "TRIAGED" | "IN_PROGRESS" | "CLOSED" | "ESCALATED";
  description: string;
  raw_payload?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export default function SOCAlertQueuePage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [severityFilter, setSeverityFilter] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  // Form State
  const [newTitle, setNewTitle] = useState("");
  const [newSource, setNewSource] = useState("Wazuh SIEM");
  const [newSeverity, setNewSeverity] = useState("HIGH");
  const [newDescription, setNewDescription] = useState("");

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      let url = "/api/v1/alerts";
      const params = new URLSearchParams();
      if (statusFilter !== "ALL") params.append("status", statusFilter);
      if (severityFilter !== "ALL") params.append("severity", severityFilter);
      if (params.toString()) url += `?${params.toString()}`;

      const res = await fetch(url, {
        headers: {
          "X-Tenant-ID": "00000000-0000-0000-0000-00000000000a",
        },
      });
      if (res.ok) {
        const data = await res.json();
        setAlerts(data);
      }
    } catch (err) {
      console.error("Failed to fetch alerts", err);
    } finally {
      setLoading(false);
    }
  };

  const [streamConnected, setStreamConnected] = useState(false);

  useEffect(() => {
    fetchAlerts();
  }, [statusFilter, severityFilter]);

  // Connect to backend Server-Sent Events stream for real-time alert updates
  useEffect(() => {
    if (typeof window === "undefined") return;
    const sse = new EventSource("/api/v1/alerts/stream");

    sse.onopen = () => {
      setStreamConnected(true);
    };

    sse.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data && data.alert_id) {
          setAlerts((prev) => {
            if (prev.some((a) => a.alert_id === data.alert_id)) return prev;
            return [data, ...prev];
          });
        }
      } catch (err) {
        // Keepalive comment / heartbeat
      }
    };

    sse.onerror = () => {
      setStreamConnected(false);
    };

    return () => {
      sse.close();
    };
  }, []);

  const handleCreateAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch("/api/v1/alerts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Tenant-ID": "00000000-0000-0000-0000-00000000000a",
        },
        body: JSON.stringify({
          title: newTitle || "Suspicious PowerShell Execution",
          source: newSource,
          severity: newSeverity,
          description: newDescription || "Encoded PowerShell command executed from temp directory.",
          raw_payload: { rule_id: 60100, agent_name: "win-srv-02", level: 12 },
        }),
      });

      if (res.ok) {
        setIsCreateOpen(false);
        setNewTitle("");
        setNewDescription("");
        fetchAlerts();
      }
    } catch (err) {
      console.error("Error creating alert", err);
    }
  };

  const handleUpdateStatus = async (alert_id: string, newStatus: string) => {
    try {
      const res = await fetch(`/api/v1/alerts/${alert_id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Tenant-ID": "00000000-0000-0000-0000-00000000000a",
        },
        body: JSON.stringify({ status: newStatus }),
      });
      if (res.ok) {
        fetchAlerts();
        if (selectedAlert && selectedAlert.alert_id === alert_id) {
          setSelectedAlert((prev) => (prev ? { ...prev, status: newStatus as any } : null));
        }
      }
    } catch (err) {
      console.error("Failed to update status", err);
    }
  };

  const [feedSuccess, setFeedSuccess] = useState<string | null>(null);

  const handleFeedToGRC = async (alert: Alert) => {
    try {
      const res = await fetch("/api/v1/alerts/feed-control-evidence", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Tenant-ID": "00000000-0000-0000-0000-00000000000a",
        },
        body: JSON.stringify({
          alert_id: alert.alert_id,
          title: alert.title,
          severity: alert.severity,
          control_id: "A.5.1",
        }),
      });
      if (res.ok) {
        setFeedSuccess(`Successfully mapped to GRC Control A.5.1 as automated evidence!`);
        setTimeout(() => setFeedSuccess(null), 4000);
      }
    } catch (err) {
      console.error("Failed to feed alert to GRC", err);
    }
  };

  const filteredAlerts = alerts.filter((a) => {
    if (!searchQuery) return true;
    return (
      a.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.source.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (a.description && a.description.toLowerCase().includes(searchQuery.toLowerCase()))
    );
  });

  // Calculate metrics
  const totalCount = alerts.length;
  const criticalCount = alerts.filter((a) => a.severity === "CRITICAL" || a.severity === "HIGH").length;
  const newCount = alerts.filter((a) => a.status === "NEW").length;
  const triagedCount = alerts.filter((a) => a.status === "TRIAGED" || a.status === "IN_PROGRESS").length;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between rounded-2xl border border-slate-800 bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/40 p-6 shadow-xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-rose-500/10 text-rose-500 ring-1 ring-rose-500/20">
              <ShieldAlert className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">SOC Alert Queue</h1>
              <p className="text-xs text-slate-400">
                Real-time SIEM Alert Ingestion & Triage Queue (Wazuh & Sigma Integrations)
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900/90 px-3 py-2 text-xs">
            <span className={`h-2.5 w-2.5 rounded-full ${streamConnected ? "bg-emerald-400 animate-pulse" : "bg-amber-400"}`} />
            <span className="font-medium text-slate-300">
              {streamConnected ? "Live SSE Active" : "Reconnecting SSE..."}
            </span>
          </div>

          <button
            onClick={fetchAlerts}
            className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900/80 px-4 py-2.5 text-xs font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin text-indigo-400" : ""}`} />
            Refresh
          </button>

          <button
            onClick={() => setIsCreateOpen(true)}
            className="flex items-center gap-2 rounded-xl bg-slate-800 border border-indigo-500/30 px-4 py-2.5 text-xs font-semibold text-indigo-300 shadow-lg hover:bg-slate-750 transition"
          >
            <Plus className="h-4 w-4" />
            Simulate Security Alert
          </button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Total Alerts</span>
            <Activity className="h-4 w-4 text-indigo-400" />
          </div>
          <p className="mt-3 text-3xl font-extrabold text-white">{totalCount}</p>
          <p className="mt-1 text-[11px] text-slate-500">Active ingestion stream</p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">High / Critical</span>
            <AlertTriangle className="h-4 w-4 text-rose-500" />
          </div>
          <p className="mt-3 text-3xl font-extrabold text-rose-400">{criticalCount}</p>
          <p className="mt-1 text-[11px] text-rose-500/80 font-medium">Requires immediate analyst triage</p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">New (Untriaged)</span>
            <Clock className="h-4 w-4 text-amber-400" />
          </div>
          <p className="mt-3 text-3xl font-extrabold text-amber-400">{newCount}</p>
          <p className="mt-1 text-[11px] text-slate-500">Awaiting SOC initial review</p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Triaged / In-Progress</span>
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          </div>
          <p className="mt-3 text-3xl font-extrabold text-emerald-400">{triagedCount}</p>
          <p className="mt-1 text-[11px] text-slate-500">Active analyst investigation</p>
        </div>
      </div>

      {/* Queue Filters & Controls */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between rounded-2xl border border-slate-800 bg-slate-900/40 p-4">
        <div className="flex flex-1 items-center gap-3">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search alert title, source, or payload..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-xl border border-slate-800 bg-slate-950 py-2.5 pl-10 pr-4 text-xs text-white placeholder-slate-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-slate-500" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="rounded-xl border border-slate-800 bg-slate-950 py-2.5 px-3 text-xs text-slate-300 focus:border-indigo-500 focus:outline-none"
            >
              <option value="ALL">All Statuses</option>
              <option value="NEW">New</option>
              <option value="TRIAGED">Triaged</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="CLOSED">Closed</option>
              <option value="ESCALATED">Escalated</option>
            </select>

            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="rounded-xl border border-slate-800 bg-slate-950 py-2.5 px-3 text-xs text-slate-300 focus:border-indigo-500 focus:outline-none"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Alert Queue Table */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 bg-slate-950/80 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              <tr>
                <th className="px-6 py-4">Severity</th>
                <th className="px-6 py-4">Alert Title</th>
                <th className="px-6 py-4">Source Engine</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Timestamp</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500">
                    <RefreshCw className="mx-auto h-6 w-6 animate-spin text-indigo-500 mb-2" />
                    Loading SOC alert stream...
                  </td>
                </tr>
              ) : filteredAlerts.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500">
                    No alerts found matching current filters. Click "Simulate Alert Ingestion" to generate test data.
                  </td>
                </tr>
              ) : (
                filteredAlerts.map((alert) => (
                  <tr key={alert.alert_id} className="hover:bg-slate-800/40 transition">
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[10px] font-bold ${
                          alert.severity === "CRITICAL"
                            ? "bg-rose-500/15 text-rose-400 ring-1 ring-rose-500/30"
                            : alert.severity === "HIGH"
                            ? "bg-orange-500/15 text-orange-400 ring-1 ring-orange-500/30"
                            : alert.severity === "MEDIUM"
                            ? "bg-amber-500/15 text-amber-400 ring-1 ring-amber-500/30"
                            : "bg-emerald-500/15 text-emerald-400 ring-1 ring-emerald-500/30"
                        }`}
                      >
                        <span className="h-1.5 w-1.5 rounded-full bg-current"></span>
                        {alert.severity}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-semibold text-slate-100">{alert.title}</p>
                        <p className="text-[11px] text-slate-400 line-clamp-1">{alert.description || "No description provided"}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4 font-mono text-[11px] text-slate-400">
                      <span className="flex items-center gap-1.5">
                        <Terminal className="h-3.5 w-3.5 text-slate-500" />
                        {alert.source}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center rounded-lg px-2 py-1 text-[10px] font-medium border ${
                          alert.status === "NEW"
                            ? "border-amber-500/30 bg-amber-500/10 text-amber-300"
                            : alert.status === "TRIAGED"
                            ? "border-indigo-500/30 bg-indigo-500/10 text-indigo-300"
                            : alert.status === "IN_PROGRESS"
                            ? "border-blue-500/30 bg-blue-500/10 text-blue-300"
                            : alert.status === "ESCALATED"
                            ? "border-rose-500/30 bg-rose-500/10 text-rose-300"
                            : "border-slate-700 bg-slate-800 text-slate-400"
                        }`}
                      >
                        {alert.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-[11px] text-slate-400">
                      {new Date(alert.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => setSelectedAlert(alert)}
                          className="flex items-center gap-1 rounded-lg border border-slate-800 bg-slate-950 px-2.5 py-1 text-[11px] text-slate-300 hover:border-slate-700 hover:text-white transition"
                        >
                          <Eye className="h-3.5 w-3.5" />
                          View
                        </button>
                        {alert.status === "NEW" && (
                          <button
                            onClick={() => handleUpdateStatus(alert.alert_id, "TRIAGED")}
                            className="rounded-lg bg-indigo-600/80 px-2.5 py-1 text-[11px] font-medium text-white hover:bg-indigo-600 transition"
                          >
                            Triage
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Alert Details Modal Drawer */}
      {selectedAlert && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-2xl rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
            <div className="flex items-start justify-between border-b border-slate-800 pb-4">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">Alert Payload Inspector</span>
                <h3 className="text-lg font-bold text-white mt-1">{selectedAlert.title}</h3>
              </div>
              <button
                onClick={() => setSelectedAlert(null)}
                className="rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="mt-4 space-y-4 text-xs text-slate-300">
              <div className="grid grid-cols-2 gap-4 rounded-xl bg-slate-950 p-4 border border-slate-800">
                <div>
                  <span className="text-slate-500">Alert ID:</span>
                  <p className="font-mono text-slate-200 truncate">{selectedAlert.alert_id}</p>
                </div>
                <div>
                  <span className="text-slate-500">Source:</span>
                  <p className="font-medium text-slate-200">{selectedAlert.source}</p>
                </div>
                <div>
                  <span className="text-slate-500">Severity:</span>
                  <p className="font-bold text-rose-400">{selectedAlert.severity}</p>
                </div>
                <div>
                  <span className="text-slate-500">Status:</span>
                  <p className="font-semibold text-indigo-400">{selectedAlert.status}</p>
                </div>
              </div>

              <div>
                <span className="text-slate-400 font-medium">Description:</span>
                <p className="mt-1 rounded-xl bg-slate-950 p-3 border border-slate-800 text-slate-300">
                  {selectedAlert.description || "No description"}
                </p>
              </div>

              <div>
                <span className="text-slate-400 font-medium">Raw Payload (JSON):</span>
                <pre className="mt-1 max-h-48 overflow-y-auto rounded-xl bg-slate-950 p-3 font-mono text-[11px] text-emerald-400 border border-slate-800">
                  {JSON.stringify(selectedAlert.raw_payload || {}, null, 2)}
                </pre>
              </div>
            </div>

            {feedSuccess && (
              <div className="mt-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 p-2.5 text-xs text-emerald-400 font-medium">
                ✓ {feedSuccess}
              </div>
            )}

            <div className="mt-6 flex items-center justify-end gap-3 border-t border-slate-800 pt-4">
              <button
                onClick={() => handleFeedToGRC(selectedAlert)}
                className="rounded-xl border border-indigo-500/30 bg-indigo-500/10 px-3.5 py-2 text-xs font-semibold text-indigo-300 hover:bg-indigo-500/20 transition flex items-center gap-1.5"
              >
                <Activity className="h-3.5 w-3.5" />
                Feed to GRC Control (A.5.1)
              </button>

              <button
                onClick={() => handleUpdateStatus(selectedAlert.alert_id, "CLOSED")}
                className="rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-300 hover:bg-slate-700 hover:text-white"
              >
                Close Alert
              </button>

              <button
                onClick={() => handleUpdateStatus(selectedAlert.alert_id, "ESCALATED")}
                className="rounded-xl bg-rose-600 px-4 py-2 text-xs font-semibold text-white hover:bg-rose-500 shadow-lg shadow-rose-500/20"
              >
                Escalate to DFIR Case
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Ingest Alert Simulation Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <form onSubmit={handleCreateAlert} className="w-full max-w-lg rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white">Simulate Wazuh SIEM Alert Ingestion</h3>

            <div>
              <label className="text-xs font-medium text-slate-400">Alert Title</label>
              <input
                type="text"
                required
                placeholder="e.g., Wazuh: Encoded PowerShell Command Execution"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                className="mt-1 w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white focus:border-indigo-500 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-medium text-slate-400">Source</label>
                <input
                  type="text"
                  value={newSource}
                  onChange={(e) => setNewSource(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-400">Severity</label>
                <select
                  value={newSeverity}
                  onChange={(e) => setNewSeverity(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white focus:border-indigo-500 focus:outline-none"
                >
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                  <option value="CRITICAL">Critical</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-xs font-medium text-slate-400">Description</label>
              <textarea
                rows={3}
                placeholder="Detailed alert context..."
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                className="mt-1 w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white focus:border-indigo-500 focus:outline-none"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setIsCreateOpen(false)}
                className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-2 text-xs text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500"
              >
                Ingest Alert
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
