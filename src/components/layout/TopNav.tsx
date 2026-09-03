"use client";

import {
  Search,
  Bell,
  Sparkles,
  Moon,
  Plus,
} from "lucide-react";

export default function TopNav() {
  return (
    <header className="sticky top-0 z-40 flex h-16 items-center justify-between border-b border-orange-500/10 bg-[#090712]/95 px-6 backdrop-blur-xl">

      {/* Search */}
      <div className="flex flex-1 items-center">
        <div className="flex w-full max-w-md items-center gap-3 rounded-full border border-orange-500/20 bg-[#141126] px-4 py-2">
          <Search
            size={18}
            className="text-zinc-500"
          />

          <input
            type="text"
            placeholder="Search risks, controls, assets..."
            className="w-full bg-transparent text-sm text-white placeholder:text-zinc-500 outline-none"
          />
        </div>
      </div>

      {/* Right */}
      <div className="ml-6 flex items-center gap-3">

        {/* AI Assistant */}
        <button
          type="button"
          className="hidden items-center gap-2 rounded-full bg-gradient-to-r from-orange-500 to-emerald-500 px-5 py-2 text-sm font-semibold text-white transition hover:scale-105 md:flex"
        >
          <Sparkles size={16} />
          AI Assistant
        </button>

        {/* Add */}
        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-full border border-orange-500/20 bg-[#141126] text-zinc-300 transition hover:border-orange-400"
        >
          <Plus size={18} />
        </button>

        {/* Theme */}
        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-full border border-orange-500/20 bg-[#141126] text-zinc-300"
        >
          <Moon size={18} />
        </button>

        {/* Notifications */}
        <div className="relative">
          <button
            type="button"
            className="flex h-10 w-10 items-center justify-center rounded-full border border-orange-500/20 bg-[#141126] text-zinc-300"
          >
            <Bell size={18} />
          </button>

          <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
            3
          </span>
        </div>

      </div>

    </header>
  );
}