"use client";
import React from "react";

type Activity = {
  id: string;
  time: string;
  user: string;
  action: string;
  status?: string;
};

const sample: Activity[] = [
  { id: "1", time: "2026-07-22 10:12", user: "alice@corp.com", action: "Uploaded evidence: firewall-log.zip", status: "Uploaded" },
  { id: "2", time: "2026-07-22 09:48", user: "bob@corp.com", action: "Marked audit as pending", status: "Pending" },
  { id: "3", time: "2026-07-21 18:02", user: "carol@corp.com", action: "Closed risk: CVE-2026-1234", status: "Closed" },
];

export default function ActivityTable() {
  return (
    <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/60">
      <table className="w-full min-w-[640px] table-auto">
        <thead className="bg-slate-950/40">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">Time</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">User</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">Action</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">Status</th>
          </tr>
        </thead>
        <tbody>
          {sample.map((a) => (
            <tr key={a.id} className="border-t border-slate-800">
              <td className="px-4 py-3 text-sm text-slate-300">{a.time}</td>
              <td className="px-4 py-3 text-sm text-slate-200">{a.user}</td>
              <td className="px-4 py-3 text-sm text-slate-300">{a.action}</td>
              <td className="px-4 py-3 text-sm text-slate-300">{a.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
