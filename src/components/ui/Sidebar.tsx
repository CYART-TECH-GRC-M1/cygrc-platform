"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { Logo, LogoFull } from "@/components/Logo";

import {
  Home,
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
        label: "Home",
        icon: Home,
        path: "/",
      },
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
  const pathname = usePathname();

  return (
    <aside
      className={
        collapsed
          ? "sticky top-0 z-50 flex h-screen w-[78px] flex-col border-r border-[#26322d] bg-[#080d0b]"
          : "sticky top-0 z-50 flex h-screen w-[260px] flex-col border-r border-[#26322d] bg-[#080d0b]"
      }
    >
      {/* Logo */}

      <div
        className={
          collapsed
            ? "flex h-[76px] items-center justify-center border-b border-[#202a26]"
            : "flex h-[76px] items-center justify-between border-b border-[#202a26] px-5"
        }
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
            className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-500 hover:bg-orange-500/10 hover:text-orange-400"
          >
            <ChevronLeft size={18} />
          </button>
        )}
      </div>

      {/* Expand */}

      {collapsed && (
        <div className="flex justify-center border-b border-[#202a26] py-3">
          <button
            type="button"
            onClick={() => setCollapsed(false)}
            className="flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 hover:bg-orange-500/10 hover:text-orange-400"
          >
            <ChevronRight size={18} />
          </button>
        </div>
      )}

      {/* Navigation */}

      <nav className="flex-1 overflow-y-auto px-3 py-5">
        {navItems.map((group) => (
          <div key={group.section} className="mb-7">
            {!collapsed && (
              <div className="mb-2 px-3 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-600">
                {group.section}
              </div>
            )}

            <ul className="space-y-1">
              {group.items.map((item) => {
                const Icon = item.icon;

                const isActive =
                  item.path === "/"
                    ? pathname === "/"
                    : pathname === item.path ||
                      pathname.startsWith(item.path + "/");

                return (
                  <li key={item.label}>
                    <Link
                      href={item.path}
                      className={
                        isActive
                          ? collapsed
                            ? "relative flex h-11 items-center justify-center rounded-xl border border-orange-500/20 bg-gradient-to-r from-orange-500/20 to-emerald-500/10 text-white"
                            : "relative flex items-center gap-3 rounded-xl border border-orange-500/20 bg-gradient-to-r from-orange-500/20 via-orange-500/5 to-emerald-500/10 px-3 py-2.5 text-white"
                          : collapsed
                            ? "group relative flex h-11 items-center justify-center rounded-xl border border-transparent text-slate-400 hover:border-orange-500/10 hover:bg-white/[0.03] hover:text-white"
                            : "group relative flex items-center gap-3 rounded-xl border border-transparent px-3 py-2.5 text-slate-400 hover:border-orange-500/10 hover:bg-white/[0.03] hover:text-white"
                      }
                    >
                      {isActive && (
                        <span className="absolute left-0 top-1/2 h-6 w-[3px] -translate-y-1/2 rounded-r-full bg-gradient-to-b from-orange-400 to-emerald-400" />
                      )}

                      <Icon
                        size={20}
                        strokeWidth={2}
                        className={
                          isActive
                            ? "shrink-0 text-orange-400"
                            : "shrink-0 text-slate-500 group-hover:text-orange-400"
                        }
                      />

                      {!collapsed && (
                        <span
                          className={
                            isActive
                              ? "font-semibold text-white"
                              : "font-medium"
                          }
                        >
                          {item.label}
                        </span>
                      )}

                      {!collapsed && isActive && (
                        <span className="ml-auto h-1.5 w-1.5 rounded-full bg-emerald-400" />
                      )}

                      {collapsed && (
                        <span className="pointer-events-none absolute left-full z-50 ml-3 whitespace-nowrap rounded-lg border border-[#34413b] bg-[#0d1411] px-3 py-2 text-xs text-white opacity-0 shadow-xl group-hover:opacity-100">
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

      {/* Security */}

      <div className="border-t border-[#202a26] p-3">
        <div className="rounded-xl border border-emerald-500/10 bg-emerald-500/[0.04] p-3">
          {collapsed ? (
            <div className="flex justify-center">
              <ShieldCheck
                size={18}
                className="text-emerald-400"
              />
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500/10">
                <ShieldCheck
                  size={18}
                  className="text-emerald-400"
                />
              </div>

              <div>
                <p className="text-xs font-semibold text-slate-200">
                  Security Active
                </p>

                <div className="mt-1 flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />

                  <p className="text-[10px] text-slate-500">
                    Enterprise Protected
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}