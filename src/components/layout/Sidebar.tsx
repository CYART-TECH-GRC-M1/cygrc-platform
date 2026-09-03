"use client";

import { useState } from "react";
import Link from "next/link";
import { Logo, LogoFull } from "@/components/Logo";
import {
  LayoutDashboard,
  ShieldCheck,
  AlertTriangle,
  ClipboardCheck,
  FileCheck,
  Boxes,
  Activity,
  FileBarChart,
  Users,
  Plug,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

const navItems = [
  {
    section: "Main",
    items: [
      {
        label: "Dashboard",
        icon: LayoutDashboard,
        path: "/dashboard",
      },
    ],
  },
  {
    section: "Modules",
    items: [
      {
        label: "Governance",
        icon: ShieldCheck,
        path: "/governance",
      },
      {
        label: "Risk Management",
        icon: AlertTriangle,
        path: "/risk-register",
      },
      {
        label: "Compliance",
        icon: ClipboardCheck,
        path: "/compliance",
      },
      {
        label: "Audit",
        icon: FileCheck,
        path: "/audit",
      },
      {
        label: "Evidence",
        icon: Boxes,
        path: "/evidence",
      },
      {
        label: "Incidents",
        icon: Activity,
        path: "/incidents",
      },
      {
        label: "Reports",
        icon: FileBarChart,
        path: "/reports",
      },
    ],
  },
  {
    section: "Administration",
    items: [
      {
        label: "Users & Teams",
        icon: Users,
        path: "/users",
      },
      {
        label: "Connectors",
        icon: Plug,
        path: "/settings/connectors",
      },
      {
        label: "Settings",
        icon: Settings,
        path: "/settings",
      },
    ],
  },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`
        sticky top-0 z-40 flex h-screen flex-col
        border-r
        border-slate-200 bg-white
        dark:border-slate-800 dark:bg-slate-950
        transition-all duration-300
        ${collapsed ? "w-20" : "w-64"}
      `}
    >
      {/* LOGO */}
      <div
        className={`
          flex h-20 items-center border-b
          border-slate-200 dark:border-slate-800
          ${collapsed ? "justify-center px-3" : "justify-between px-5"}
        `}
      >
        {collapsed ? (
          <Logo className="h-9 w-9" />
        ) : (
          <LogoFull className="h-9 w-auto" />
        )}

        {!collapsed && (
          <button
            type="button"
            onClick={() => setCollapsed(true)}
            aria-label="Collapse sidebar"
            className="
              flex h-8 w-8 items-center justify-center
              rounded-lg
              text-slate-500
              transition
              hover:bg-slate-100
              hover:text-slate-900
              dark:hover:bg-slate-800
              dark:hover:text-white
            "
          >
            <ChevronLeft size={18} />
          </button>
        )}
      </div>

      {/* EXPAND BUTTON */}
      {collapsed && (
        <div
          className="
            flex justify-center
            border-b border-slate-200
            py-3
            dark:border-slate-800
          "
        >
          <button
            type="button"
            onClick={() => setCollapsed(false)}
            aria-label="Expand sidebar"
            className="
              flex h-9 w-9 items-center justify-center
              rounded-lg
              text-slate-500
              transition
              hover:bg-slate-100
              hover:text-slate-900
              dark:hover:bg-slate-800
              dark:hover:text-white
            "
          >
            <ChevronRight size={18} />
          </button>
        </div>
      )}

      {/* NAVIGATION */}
      <nav className="flex-1 overflow-y-auto px-2 py-5">
        {navItems.map((group) => (
          <div key={group.section} className="mb-7">
            {!collapsed && (
              <h3
                className="
                  mb-2 px-3
                  text-[11px]
                  font-semibold
                  uppercase
                  tracking-[0.12em]
                  text-slate-400
                  dark:text-slate-500
                "
              >
                {group.section}
              </h3>
            )}

            <ul className="space-y-1">
              {group.items.map((item) => {
                const Icon = item.icon;

                return (
                  <li key={item.label}>
                    <Link
                      href={item.path}
                      className={`
                        group relative flex items-center
                        rounded-xl
                        text-sm font-medium
                        text-slate-600
                        transition-all duration-200
                        hover:bg-slate-100
                        hover:text-slate-900
                        dark:text-slate-300
                        dark:hover:bg-slate-800
                        dark:hover:text-white
                        ${
                          collapsed
                            ? "justify-center px-3 py-3"
                            : "gap-3 px-3 py-2.5"
                        }
                      `}
                    >
                      <Icon
                        size={20}
                        strokeWidth={2}
                        className="
                          shrink-0
                          transition-transform duration-200
                          group-hover:scale-105
                        "
                      />

                      {!collapsed && (
                        <span className="truncate">
                          {item.label}
                        </span>
                      )}

                      {/* COLLAPSED TOOLTIP */}
                      {collapsed && (
                        <span
                          className="
                            pointer-events-none
                            absolute left-full z-50 ml-3
                            whitespace-nowrap
                            rounded-lg
                            border border-slate-700
                            bg-slate-900
                            px-3 py-2
                            text-xs font-medium
                            text-white
                            opacity-0
                            shadow-xl
                            transition-opacity duration-200
                            group-hover:opacity-100
                          "
                        >
                          {item.label}
                        </span>
                      )}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* BOTTOM SECURITY AREA */}
      <div
        className="
          border-t
          border-slate-200
          p-3
          dark:border-slate-800
        "
      >
        <div
          className={`
            rounded-xl
            bg-slate-50
            dark:bg-slate-900
            ${collapsed ? "p-2" : "p-3"}
          `}
        >
          {collapsed ? (
            <div className="flex justify-center">
              <ShieldCheck
                size={20}
                className="text-violet-500"
              />
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <div
                className="
                  flex h-9 w-9 items-center
                  justify-center
                  rounded-lg
                  bg-violet-500/10
                "
              >
                <ShieldCheck
                  size={18}
                  className="text-violet-500"
                />
              </div>

              <div className="min-w-0">
                <p
                  className="
                    truncate
                    text-xs font-semibold
                    text-slate-700
                    dark:text-slate-200
                  "
                >
                  CyGRC Security
                </p>

                <p
                  className="
                    truncate
                    text-[10px]
                    text-slate-400
                  "
                >
                  Enterprise Platform
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}