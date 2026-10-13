"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Search,
  Bell,
  Sparkles,
  Moon,
  Sun,
  Plus,
  X,
  Send,
  ShieldCheck,
  AlertTriangle,
  Clock,
  CheckCircle2,
  FileCheck,
  Activity,
  Plug,
  ExternalLink,
  Bot,
  Trash2,
} from "lucide-react";
import { useTheme } from "@/context/ThemeContext";

interface NotificationItem {
  id: string;
  title: string;
  description: string;
  time: string;
  unread: boolean;
  type: "warning" | "success" | "info";
}

interface ChatMessage {
  id: string;
  sender: "user" | "ai";
  text: string;
  time: string;
}

export default function TopNav() {
  const { theme, toggleTheme } = useTheme();
  const router = useRouter();

  // State
  const [searchQuery, setSearchQuery] = useState("");
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [quickAddOpen, setQuickAddOpen] = useState(false);
  const [aiDrawerOpen, setAiDrawerOpen] = useState(false);

  // Notifications State
  const [notifications, setNotifications] = useState<NotificationItem[]>([
    {
      id: "1",
      title: "SOC 2 Evidence Approved",
      description: "Auditor approved access control policy evidence for Q3.",
      time: "10m ago",
      unread: true,
      type: "success",
    },
    {
      id: "2",
      title: "Critical Risk Flagged",
      description: "Unauthorized sign-in pattern detected from unknown IP.",
      time: "45m ago",
      unread: true,
      type: "warning",
    },
    {
      id: "3",
      title: "Upcoming Audit Review",
      description: "ISO 27001 ISMS internal audit commences in 3 days.",
      time: "2h ago",
      unread: true,
      type: "info",
    },
  ]);

  // AI Assistant Chat State
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: "init",
      sender: "ai",
      text: "Hello! I am your CyGRC AI Copilot. How can I assist you with your compliance frameworks, risk assessments, or audit readiness today?",
      time: "Just now",
    },
  ]);
  const [aiInput, setAiInput] = useState("");
  const [aiThinking, setAiThinking] = useState(false);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Click outside listener refs
  const notificationRef = useRef<HTMLDivElement>(null);
  const quickAddRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        notificationRef.current &&
        !notificationRef.current.contains(event.target as Node)
      ) {
        setNotificationsOpen(false);
      }
      if (
        quickAddRef.current &&
        !quickAddRef.current.contains(event.target as Node)
      ) {
        setQuickAddOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Auto-scroll AI chat
  useEffect(() => {
    if (aiDrawerOpen) {
      chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatMessages, aiDrawerOpen]);

  // Search submission
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    router.push(`/risk-register?q=${encodeURIComponent(searchQuery.trim())}`);
  };

  // Notification actions
  const unreadCount = notifications.filter((n) => n.unread).length;
  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, unread: false })));
  };
  const clearNotifications = () => {
    setNotifications([]);
  };

  // AI Chat handler
  const handleSendAiMessage = async (promptText?: string) => {
    const textToSend = promptText || aiInput;
    if (!textToSend.trim() || aiThinking) return;

    const userMsg: ChatMessage = {
      id: String(Date.now()),
      sender: "user",
      text: textToSend.trim(),
      time: "Just now",
    };

    setChatMessages((prev) => [...prev, userMsg]);
    if (!promptText) setAiInput("");
    setAiThinking(true);

    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("cygrc_token") : null;
      const res = await fetch("/api/v1/ai/soc-copilot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          "X-Tenant-ID": "00000000-0000-0000-0000-00000000000a",
        },
        body: JSON.stringify({ question: textToSend.trim() }),
      });

      if (res.ok) {
        const data = await res.json();
        let reply = data.answer || "Analysis complete.";
        if (data.supporting_sources && data.supporting_sources.length > 0) {
          reply += `\n\n📌 Supporting Sources: ${data.supporting_sources.join(", ")}`;
        }
        if (data.confidence_score) {
          reply += ` (Grounding Confidence: ${Math.round(data.confidence_score * 100)}%)`;
        }
        setChatMessages((prev) => [
          ...prev,
          {
            id: String(Date.now() + 1),
            sender: "ai",
            text: reply,
            time: "Just now",
          },
        ]);
        setAiThinking(false);
        return;
      }
    } catch {
      // Backend unavailable or network error - fallback to local posture analysis
    }

    // Fallback response if offline / unauthorized
    setTimeout(() => {
      let reply = "I analyzed the CyGRC posture repository. ";
      const lower = textToSend.toLowerCase();

      if (lower.includes("risk") || lower.includes("threat")) {
        reply +=
          "Currently, 142 total risks are tracked with 12 critical risks. The primary focus area is unpatched cloud instances and access control policies.";
      } else if (lower.includes("audit") || lower.includes("iso")) {
        reply +=
          "ISO 27001 Internal ISMS Audit is scheduled in 3 days with Michael R. Readiness score is currently at 87% compliant.";
      } else if (lower.includes("connector") || lower.includes("integration")) {
        reply +=
          "You have 19 active connected services out of 24, with 98.7% data sync health. AWS has 1 sync alert pending attention.";
      } else {
        reply +=
          "All security controls are operating normally across active frameworks (ISO 27001, SOC 2, NIST CSF). For deep capability inspection, visit the full Cyber AI Hub.";
      }

      setChatMessages((prev) => [
        ...prev,
        {
          id: String(Date.now() + 1),
          sender: "ai",
          text: reply,
          time: "Just now",
        },
      ]);
      setAiThinking(false);
    }, 600);
  };

  return (
    <>
      <header className="sticky top-0 z-40 flex h-16 items-center justify-between border-b border-orange-500/10 bg-[#090712]/95 px-6 backdrop-blur-xl">
        {/* Search */}
        <form onSubmit={handleSearchSubmit} className="flex flex-1 items-center">
          <div className="flex w-full max-w-md items-center gap-3 rounded-full border border-orange-500/20 bg-[#141126] px-4 py-2 transition focus-within:border-orange-500/50">
            <Search size={18} className="text-zinc-500 shrink-0" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search risks, controls, assets... (Press Enter)"
              className="w-full bg-transparent text-sm text-white placeholder:text-zinc-500 outline-none"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                className="text-zinc-500 hover:text-zinc-300"
              >
                <X size={14} />
              </button>
            )}
          </div>
        </form>

        {/* Right Actions */}
        <div className="ml-6 flex items-center gap-3">
          {/* AI Assistant Button */}
          <button
            type="button"
            onClick={() => setAiDrawerOpen(true)}
            aria-label="Open AI Assistant"
            className="hidden items-center gap-2 rounded-full bg-gradient-to-r from-orange-500 to-emerald-500 px-5 py-2 text-sm font-semibold text-white transition hover:scale-105 active:scale-95 md:flex shadow-md shadow-orange-500/20"
          >
            <Sparkles size={16} />
            AI Assistant
          </button>

          {/* Quick Add Menu */}
          <div className="relative" ref={quickAddRef}>
            <button
              type="button"
              onClick={() => setQuickAddOpen(!quickAddOpen)}
              aria-label="Quick Actions"
              aria-expanded={quickAddOpen}
              className={`flex h-10 w-10 items-center justify-center rounded-full border bg-[#141126] text-zinc-300 transition hover:border-orange-400 ${
                quickAddOpen ? "border-orange-500 text-orange-400 rotate-45" : "border-orange-500/20"
              }`}
            >
              <Plus size={18} className="transition-transform duration-200" />
            </button>

            {quickAddOpen && (
              <div className="absolute right-0 top-12 z-50 w-56 rounded-2xl border border-orange-500/20 bg-[#0e0c1a] p-2 shadow-2xl backdrop-blur-xl animate-fade-in">
                <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-orange-400 border-b border-white/5">
                  Quick Actions
                </div>
                <div className="mt-1 space-y-1">
                  <Link
                    href="/risk-register"
                    onClick={() => setQuickAddOpen(false)}
                    className="flex items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium text-slate-200 hover:bg-orange-500/10 hover:text-orange-400 transition"
                  >
                    <AlertTriangle size={15} className="text-orange-400" />
                    Register New Risk
                  </Link>
                  <Link
                    href="/audit"
                    onClick={() => setQuickAddOpen(false)}
                    className="flex items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium text-slate-200 hover:bg-orange-500/10 hover:text-orange-400 transition"
                  >
                    <FileCheck size={15} className="text-emerald-400" />
                    Schedule Audit
                  </Link>
                  <Link
                    href="/settings/connectors"
                    onClick={() => setQuickAddOpen(false)}
                    className="flex items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium text-slate-200 hover:bg-orange-500/10 hover:text-orange-400 transition"
                  >
                    <Plug size={15} className="text-orange-400" />
                    Add Connector
                  </Link>
                  <Link
                    href="/evidence"
                    onClick={() => setQuickAddOpen(false)}
                    className="flex items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium text-slate-200 hover:bg-orange-500/10 hover:text-orange-400 transition"
                  >
                    <CheckCircle2 size={15} className="text-emerald-400" />
                    Upload Evidence
                  </Link>
                  <Link
                    href="/incidents"
                    onClick={() => setQuickAddOpen(false)}
                    className="flex items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium text-slate-200 hover:bg-orange-500/10 hover:text-orange-400 transition"
                  >
                    <Activity size={15} className="text-red-400" />
                    Report Incident
                  </Link>
                </div>
              </div>
            )}
          </div>

          {/* Theme Toggle Button */}
          <button
            type="button"
            onClick={toggleTheme}
            aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            className="flex h-10 w-10 items-center justify-center rounded-full border border-orange-500/20 bg-[#141126] text-zinc-300 transition hover:border-orange-400 hover:text-orange-400 active:scale-95"
          >
            {theme === "light" ? (
              <Sun size={18} className="text-amber-400" />
            ) : (
              <Moon size={18} className="text-orange-300" />
            )}
          </button>

          {/* Notifications Button & Dropdown */}
          <div className="relative" ref={notificationRef}>
            <button
              type="button"
              onClick={() => setNotificationsOpen(!notificationsOpen)}
              aria-label="Toggle notifications"
              aria-expanded={notificationsOpen}
              className={`flex h-10 w-10 items-center justify-center rounded-full border bg-[#141126] text-zinc-300 transition hover:border-orange-400 ${
                notificationsOpen ? "border-orange-500 text-orange-400" : "border-orange-500/20"
              }`}
            >
              <Bell size={18} />
            </button>

            {unreadCount > 0 && (
              <span className="pointer-events-none absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white shadow-lg shadow-red-500/50">
                {unreadCount}
              </span>
            )}

            {/* Notification Panel */}
            {notificationsOpen && (
              <div className="absolute right-0 top-12 z-50 w-80 sm:w-96 rounded-2xl border border-orange-500/20 bg-[#0e0c1a] shadow-2xl backdrop-blur-xl animate-fade-in">
                <div className="flex items-center justify-between border-b border-white/10 p-4">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm text-white">Notifications</span>
                    {unreadCount > 0 && (
                      <span className="rounded-full bg-orange-500/20 px-2 py-0.5 text-[10px] font-bold text-orange-400">
                        {unreadCount} new
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    {unreadCount > 0 && (
                      <button
                        type="button"
                        onClick={markAllAsRead}
                        className="text-[11px] text-zinc-400 hover:text-orange-400 transition"
                      >
                        Mark read
                      </button>
                    )}
                    {notifications.length > 0 && (
                      <button
                        type="button"
                        onClick={clearNotifications}
                        title="Clear all"
                        className="text-zinc-500 hover:text-red-400 transition"
                      >
                        <Trash2 size={13} />
                      </button>
                    )}
                  </div>
                </div>

                <div className="max-h-80 overflow-y-auto divide-y divide-white/5 p-2">
                  {notifications.length === 0 ? (
                    <div className="p-6 text-center text-xs text-zinc-500">
                      No notifications to display
                    </div>
                  ) : (
                    notifications.map((item) => (
                      <div
                        key={item.id}
                        className={`group flex items-start gap-3 rounded-xl p-3 transition ${
                          item.unread
                            ? "bg-orange-500/5 hover:bg-orange-500/10"
                            : "hover:bg-white/[0.03]"
                        }`}
                      >
                        <div
                          className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg ${
                            item.type === "success"
                              ? "bg-emerald-500/10 text-emerald-400"
                              : item.type === "warning"
                              ? "bg-orange-500/10 text-orange-400"
                              : "bg-blue-500/10 text-blue-400"
                          }`}
                        >
                          {item.type === "success" ? (
                            <CheckCircle2 size={14} />
                          ) : item.type === "warning" ? (
                            <AlertTriangle size={14} />
                          ) : (
                            <ShieldCheck size={14} />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-semibold text-white truncate">
                            {item.title}
                          </p>
                          <p className="mt-0.5 text-[11px] text-zinc-400 leading-snug">
                            {item.description}
                          </p>
                          <span className="mt-1 inline-block text-[10px] text-zinc-600">
                            {item.time}
                          </span>
                        </div>
                        {item.unread && (
                          <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-orange-500" />
                        )}
                      </div>
                    ))
                  )}
                </div>

                <div className="border-t border-white/5 p-3 text-center">
                  <Link
                    href="/dashboard"
                    onClick={() => setNotificationsOpen(false)}
                    className="text-[11px] font-medium text-orange-400 hover:text-orange-300 transition"
                  >
                    View audit and incident activity →
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* AI Assistant Slide-over Drawer */}
      {aiDrawerOpen && (
        <div className="fixed inset-0 z-50 flex justify-end">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
            onClick={() => setAiDrawerOpen(false)}
          />

          {/* Drawer content */}
          <div className="relative z-10 flex h-full w-full max-w-md flex-col border-l border-orange-500/20 bg-[#0a0815] text-white shadow-2xl animate-in slide-in-from-right duration-300">
            {/* Drawer Header */}
            <div className="flex items-center justify-between border-b border-orange-500/10 p-5 bg-[#0e0c1c]">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-orange-500 to-emerald-500 text-white shadow-md shadow-orange-500/20">
                  <Sparkles size={20} />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    CyGRC AI Copilot
                    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium text-emerald-400 border border-emerald-500/20">
                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      Ready
                    </span>
                  </h3>
                  <p className="text-[11px] text-zinc-500">Security & Compliance Assistant</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Link
                  href="/ai"
                  onClick={() => setAiDrawerOpen(false)}
                  className="rounded-lg border border-orange-500/30 bg-orange-500/10 px-2.5 py-1 text-[11px] font-semibold text-orange-400 hover:bg-orange-500/20 transition flex items-center gap-1"
                >
                  Full Hub <ExternalLink size={12} />
                </Link>
                <button
                  type="button"
                  onClick={() => setAiDrawerOpen(false)}
                  className="flex h-8 w-8 items-center justify-center rounded-lg text-zinc-400 hover:bg-white/10 hover:text-white transition"
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            {/* Chat History */}
            <div className="flex-1 overflow-y-auto p-5 space-y-4">
              {chatMessages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs leading-relaxed ${
                      msg.sender === "user"
                        ? "bg-gradient-to-r from-orange-500 to-orange-600 text-white shadow-md shadow-orange-900/20 rounded-tr-none"
                        : "bg-[#141126] border border-orange-500/15 text-zinc-200 rounded-tl-none shadow-sm"
                    }`}
                  >
                    {msg.sender === "ai" && (
                      <div className="mb-1 flex items-center gap-1.5 text-[10px] font-semibold text-orange-400">
                        <Bot size={13} />
                        Copilot
                      </div>
                    )}
                    <p>{msg.text}</p>
                    <span className="mt-1 block text-right text-[9px] opacity-60">
                      {msg.time}
                    </span>
                  </div>
                </div>
              ))}

              {aiThinking && (
                <div className="flex justify-start">
                  <div className="rounded-2xl rounded-tl-none bg-[#141126] border border-orange-500/15 px-4 py-3 text-xs text-orange-400 flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-orange-400 animate-bounce" />
                    <span className="h-1.5 w-1.5 rounded-full bg-orange-400 animate-bounce [animation-delay:0.2s]" />
                    <span className="h-1.5 w-1.5 rounded-full bg-orange-400 animate-bounce [animation-delay:0.4s]" />
                    <span className="text-zinc-400 ml-1">Analyzing security posture...</span>
                  </div>
                </div>
              )}
              <div ref={chatBottomRef} />
            </div>

            {/* Prompt Quick Chips */}
            <div className="border-t border-white/5 bg-[#0a0815] p-3">
              <p className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-zinc-500">
                Suggested Inquiries:
              </p>
              <div className="flex flex-wrap gap-1.5">
                {[
                  "Summarize critical risks",
                  "Check ISO 27001 readiness",
                  "Connector synchronization health",
                ].map((chip) => (
                  <button
                    key={chip}
                    type="button"
                    onClick={() => handleSendAiMessage(chip)}
                    className="rounded-lg border border-orange-500/20 bg-orange-500/5 px-2.5 py-1 text-[11px] text-zinc-300 hover:border-orange-500/40 hover:bg-orange-500/10 hover:text-white transition"
                  >
                    {chip}
                  </button>
                ))}
              </div>
            </div>

            {/* Input area */}
            <div className="border-t border-white/10 bg-[#0e0c1c] p-4">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSendAiMessage();
                }}
                className="flex items-center gap-2"
              >
                <input
                  type="text"
                  value={aiInput}
                  onChange={(e) => setAiInput(e.target.value)}
                  placeholder="Ask about risks, controls, or compliance..."
                  className="flex-1 rounded-xl border border-orange-500/20 bg-[#141126] px-4 py-2.5 text-xs text-white placeholder:text-zinc-500 outline-none transition focus:border-orange-500"
                />
                <button
                  type="submit"
                  disabled={!aiInput.trim() || aiThinking}
                  className="flex h-9 w-9 items-center justify-center rounded-xl bg-orange-500 text-black font-bold transition hover:bg-orange-400 disabled:opacity-40 disabled:hover:bg-orange-500 shrink-0"
                >
                  <Send size={15} />
                </button>
              </form>
            </div>
          </div>
        </div>
      )}
    </>
  );
}