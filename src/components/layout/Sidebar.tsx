"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useNavigation } from "@/context/NavigationContext";
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
  Sparkles,
  ShieldAlert,
  FolderKanban,
  Crosshair,
  Binary,
  X,
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
    section: "Cyber Defense",
    items: [
      {
        label: "Alert Queue",
        icon: ShieldAlert,
        path: "/soc/alerts",
      },
      {
        label: "Incident Cases",
        icon: FolderKanban,
        path: "/soc/cases",
      },
      {
        label: "VAPT Findings",
        icon: Crosshair,
        path: "/vapt/findings",
      },
      {
        label: "DFIR Forensics",
        icon: Binary,
        path: "/dfir/investigation",
      },
      {
        label: "Cyber AI Hub",
        icon: Sparkles,
        path: "/ai",
      },
    ],
  },
  {
    section: "GRC Modules",
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
        label: "Evidence Vault",
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
  const { mobileSidebarOpen, closeMobileSidebar } = useNavigation();

  const isItemActive = (path: string) => {
    if (path === "/dashboard") return pathname === "/dashboard";
    return pathname === path || (pathname ? pathname.startsWith(path + "/") : false);
  };

  const renderNavList = (isMobile = false) => (
    <nav className="flex-1 overflow-y-auto px-2 py-4">
      {navItems.map((group) => (
        <div key={group.section} className="mb-6">
          {(!collapsed || isMobile) && (
            <h3
              className="
                mb-2 px-3
                text-[10px]
                font-bold
                uppercase
                tracking-[0.16em]
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
              const active = isItemActive(item.path);

              return (
                <li key={item.path}>
                  <Link
                    href={item.path}
                    onClick={() => {
                      if (isMobile) closeMobileSidebar();
                    }}
                    className={`
                      group relative flex items-center
                      rounded-xl border-l-2
                      text-sm font-medium
                      transition-all duration-200
                      ${
                        active
                          ? "border-orange-500 bg-orange-500/10 text-orange-400 font-semibold dark:bg-orange-500/15 dark:text-orange-400"
                          : "border-transparent text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/60 dark:hover:text-white"
                      }
                      ${
                        collapsed && !isMobile
                          ? "justify-center px-3 py-2.5"
                          : "gap-3 px-3 py-2.5"
                      }
                    `}
                  >
                    <Icon
                      size={18}
                      strokeWidth={2}
                      className={`
                        shrink-0 transition-transform duration-200
                        group-hover:scale-105
                        ${active ? "text-orange-400" : ""}
                      `}
                    />

                    {(!collapsed || isMobile) && (
                      <span className="truncate">{item.label}</span>
                    )}

                    {/* COLLAPSED TOOLTIP (Desktop only) */}
                    {collapsed && !isMobile && (
                      <span
                        className="
                          pointer-events-none
                          absolute left-full z-50 ml-3
                          whitespace-nowrap
                          rounded-lg
                          border border-slate-700
                          bg-slate-900
                          px-3 py-1.5
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
  );

  return (
    <>
      {/* =========================================================
          MOBILE DRAWER BACKDROP & SIDEBAR
      ========================================================== */}
      {mobileSidebarOpen && (
        <div
          className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm md:hidden animate-fade-in"
          onClick={closeMobileSidebar}
          aria-hidden="true"
        />
      )}

      <aside
        className={`
          fixed inset-y-0 left-0 z-50 flex w-72 flex-col
          border-r border-slate-800 bg-[#090712] text-slate-100
          shadow-2xl transition-transform duration-300 ease-in-out md:hidden
          ${mobileSidebarOpen ? "translate-x-0" : "-translate-x-full"}
        `}
      >
        {/* Mobile Header */}
        <div className="flex h-16 items-center justify-between border-b border-slate-800 px-5">
          <LogoFull className="h-8 w-auto" />
          <button
            type="button"
            onClick={closeMobileSidebar}
            aria-label="Close navigation menu"
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-800 bg-slate-900 text-slate-400 hover:text-white transition"
          >
            <X size={18} />
          </button>
        </div>

        {/* Mobile Navigation List */}
        {renderNavList(true)}

        {/* Mobile Bottom Security Area */}
        <div className="border-t border-slate-800 p-4">
          <div className="flex items-center gap-3 rounded-xl bg-slate-900/80 p-3 border border-slate-800/60">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-orange-500/10 text-orange-400">
              <ShieldCheck size={18} />
            </div>
            <div className="min-w-0">
              <p className="truncate text-xs font-semibold text-slate-200">
                CyGRC Security
              </p>
              <p className="truncate text-[10px] text-slate-400">
                Enterprise Defense Platform
              </p>
            </div>
          </div>
        </div>
      </aside>

      {/* =========================================================
          DESKTOP SIDEBAR
      ========================================================== */}
      <aside
        className={`
          sticky top-0 z-40 hidden md:flex h-screen flex-col
          border-r border-slate-200 bg-white
          dark:border-slate-800 dark:bg-slate-950
          transition-all duration-300
          ${collapsed ? "w-20" : "w-64"}
        `}
      >
        {/* DESKTOP LOGO */}
        <div
          className={`
            flex h-16 items-center border-b
            border-slate-200 dark:border-slate-800
            ${collapsed ? "justify-center px-3" : "justify-between px-5"}
          `}
        >
          {collapsed ? (
            <Logo className="h-8 w-8" />
          ) : (
            <LogoFull className="h-8 w-auto" />
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
              py-2.5
              dark:border-slate-800
            "
          >
            <button
              type="button"
              onClick={() => setCollapsed(false)}
              aria-label="Expand sidebar"
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
              <ChevronRight size={18} />
            </button>
          </div>
        )}

        {/* DESKTOP NAVIGATION LIST */}
        {renderNavList(false)}

        {/* DESKTOP BOTTOM SECURITY AREA */}
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
                  className="text-orange-500"
                />
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <div
                  className="
                    flex h-9 w-9 items-center
                    justify-center
                    rounded-lg
                    bg-orange-500/10
                  "
                >
                  <ShieldCheck
                    size={18}
                    className="text-orange-500"
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
                    Enterprise Defense
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </aside>
    </>
  );
}