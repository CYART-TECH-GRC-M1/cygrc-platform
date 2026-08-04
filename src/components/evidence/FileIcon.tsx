"use client";
import React from "react";

export default function FileIcon({ name }: { name: string }) {
  const ext = name.split('.').pop()?.toLowerCase();
  if (!ext) return <div className="h-8 w-8 rounded bg-slate-800" />;
  if (['png', 'jpg', 'jpeg', 'gif', 'webp'].includes(ext)) return <div className="flex h-8 w-8 items-center justify-center rounded bg-sky-800 text-sm font-semibold text-white">IMG</div>;
  if (['pdf'].includes(ext)) return <div className="flex h-8 w-8 items-center justify-center rounded bg-rose-700 text-sm font-semibold text-white">PDF</div>;
  if (['zip', 'tar', 'gz'].includes(ext)) return <div className="flex h-8 w-8 items-center justify-center rounded bg-amber-700 text-sm font-semibold text-white">ZIP</div>;
  if (['doc', 'docx'].includes(ext)) return <div className="flex h-8 w-8 items-center justify-center rounded bg-blue-700 text-sm font-semibold text-white">DOC</div>;
  return <div className="flex h-8 w-8 items-center justify-center rounded bg-slate-800 text-sm font-semibold text-white">FILE</div>;
}
