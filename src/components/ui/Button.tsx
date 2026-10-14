"use client";
import React from "react";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  loading?: boolean;
  variant?: "primary" | "ghost";
};

export default function Button({ loading, className = "", variant = "primary", children, ...rest }: ButtonProps) {
  const base = "inline-flex items-center justify-center rounded-2xl px-6 py-3 text-sm font-semibold transition";
  const styles =
    variant === "primary"
      ? "bg-slate-100 text-slate-950 hover:bg-slate-200"
      : "border border-slate-800 bg-transparent text-slate-100 hover:bg-slate-900";

  return (
    <button className={`${base} ${styles} ${className}`} {...rest}>
      {loading ? "Loading..." : children}
    </button>
  );
}
