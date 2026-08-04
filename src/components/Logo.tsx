"use client";
import React from "react";

export default function Logo({ className }: { className?: string }) {
  return (
    <div className={className} aria-hidden>
      <svg width="40" height="40" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="48" height="48" rx="8" fill="#0b1220" />
        <path d="M12 34L22 14L30 34" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
        <circle cx="36" cy="12" r="4" fill="#94a3b8" />
      </svg>
    </div>
  );
}
