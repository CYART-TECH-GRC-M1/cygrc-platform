"use client";

import { Fingerprint } from "lucide-react";
import { motion } from "framer-motion";

interface LogoProps {
  size?: number;
  className?: string;
}

export function Logo({
  size = 40,
  className = "",
}: LogoProps) {
  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: "spring", stiffness: 200 }}
      className={`relative flex items-center justify-center rounded-2xl bg-gradient-to-br from-orange-500 to-emerald-500 shadow-lg ${className}`}
      style={{
        width: size,
        height: size,
      }}
    >
      <Fingerprint
        className="text-white"
        size={size * 0.6}
        strokeWidth={2.5}
      />
    </motion.div>
  );
}

export function LogoFull({
  className = "",
}: {
  className?: string;
}) {
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <Logo size={40} />

      <div className="flex flex-col leading-none">
        <span className="text-xl font-bold text-white">
          CyGRC
        </span>

        <span className="text-[10px] text-slate-400">
          Governance • Risk • Compliance
        </span>
      </div>
    </div>
  );
}