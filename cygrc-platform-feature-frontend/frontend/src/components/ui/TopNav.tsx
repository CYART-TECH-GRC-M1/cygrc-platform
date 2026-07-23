"use client";
import React from "react";
import Link from "next/link";
import ThemeToggle from "./ThemeToggle";

export default function TopNav() {
  return (
    <header className="sticky top-0 z-20 flex w-full items-center justify-between gap-4 rounded-t-xl border-b border-[var(--border)] bg-[var(--surface)] px-4 py-3 backdrop-blur">
      <div className="flex items-center gap-4">
        <button className="md:hidden rounded-md p-2 text-slate-300 hover:bg-slate-800">Menu</button>
        <h3 className="text-lg font-semibold text-white">GRC Dashboard</h3>
      </div>

      <div className="flex items-center gap-3">
        <input
          placeholder="Search activities"
          className="hidden rounded-lg border border-slate-800 bg-slate-900/60 px-3 py-2 text-sm text-slate-200 placeholder:text-slate-500 md:block"
        />
        <ThemeToggle />
        <Link href="#" className="rounded-full bg-slate-800/50 px-3 py-2 text-sm text-slate-200 hover:bg-slate-800">
          Notifications
        </Link>
        <Link href="#" className="rounded-full bg-slate-800/50 px-3 py-2 text-sm text-slate-200 hover:bg-slate-800">
          Account
        </Link>
      </div>
    </header>
  );
}
