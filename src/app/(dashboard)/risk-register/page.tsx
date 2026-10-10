"use client";

import { useState } from "react";
import { Chip } from "@heroui/react";
import {
Search,
ChevronDown,
Download,
Plus,
Pencil,
ShieldAlert,
} from "lucide-react";

const risks = [
{
id: "RSK-001",
name: "Data Breach via Phishing",
owner: "John Doe",
severity: "Critical",
status: "Mitigating",
},
{
id: "RSK-002",
name: "Unpatched Server Vulnerabilities",
owner: "Sarah Connor",
severity: "High",
status: "Open",
},
{
id: "RSK-003",
name: "Lack of MFA on Admin Panel",
owner: "IT Security",
severity: "Medium",
status: "Resolved",
},
{
id: "RSK-004",
name: "Third-party Vendor Compliance",
owner: "Procurement",
severity: "Low",
status: "Accepted",
},
];

const columns = [
"ID",
"RISK NAME",
"OWNER",
"SEVERITY",
"STATUS",
"ACTIONS",
];

export default function RiskRegister() {
const [filterValue, setFilterValue] = useState("");

const filteredRisks = risks.filter((risk) =>
`${risk.id} ${risk.name} ${risk.owner} ${risk.severity} ${risk.status}`
.toLowerCase()
.includes(filterValue.toLowerCase())
);

return ( <div className="space-y-6">
{/* HEADER */} <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"> <div> <div className="mb-2 flex items-center gap-2"> <div className="h-1 w-8 rounded-full bg-orange-500" />


        <span className="font-mono text-[9px] font-semibold tracking-[0.2em] text-orange-400">
          RISK_REGISTER
        </span>
      </div>

      <h2 className="text-2xl font-semibold tracking-tight text-white">
        Risk Register
      </h2>

      <p className="mt-1 text-sm text-zinc-500">
        Identify, monitor, and manage organizational risks.
      </p>
    </div>

    <button
      type="button"
      className="flex w-fit items-center gap-2 rounded-xl bg-orange-500 px-4 py-2.5 text-sm font-semibold text-black shadow-lg shadow-orange-500/10 transition hover:bg-orange-400 active:scale-[0.98]"
    >
      <Plus size={17} />
      Register New Risk
    </button>
  </div>

  {/* REGISTER CARD */}
  <div className="overflow-hidden rounded-2xl border border-orange-500/15 bg-[#080807] shadow-[0_10px_40px_rgba(0,0,0,0.18)]">
    {/* TOOLBAR */}
    <div className="flex flex-col gap-4 border-b border-orange-500/10 p-5 lg:flex-row lg:items-center lg:justify-between">
      {/* SEARCH */}
      <div className="w-full lg:max-w-md">
        <div className="flex items-center gap-2 rounded-xl border border-zinc-800 bg-[#050505] px-3 py-2.5 transition focus-within:border-orange-500/40">
          <Search
            size={17}
            className="shrink-0 text-zinc-600"
          />

          <input
            type="text"
            value={filterValue}
            onChange={(event) =>
              setFilterValue(event.target.value)
            }
            placeholder="Search risks..."
            className="w-full bg-transparent text-sm text-zinc-200 outline-none placeholder:text-zinc-600"
          />
        </div>
      </div>

      {/* ACTIONS */}
      <div className="flex gap-2">
        <button
          type="button"
          className="hidden items-center gap-2 rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-xs font-semibold text-zinc-400 transition hover:border-orange-500/20 hover:text-orange-400 sm:flex"
        >
          <span>Filters</span>
          <ChevronDown size={14} />
        </button>

        <button
          type="button"
          className="flex items-center gap-2 rounded-xl border border-zinc-800 bg-[#050505] px-3.5 py-2.5 text-xs font-semibold text-zinc-400 transition hover:border-emerald-500/20 hover:text-emerald-400"
        >
          <Download size={15} />
          Export CSV
        </button>
      </div>
    </div>

    {/* TABLE */}
    <div className="overflow-x-auto p-5">
      <div className="overflow-hidden rounded-xl border border-orange-500/10">
        <table className="min-w-full text-sm">
          <thead className="bg-[#111111]">
            <tr>
              {columns.map((column) => (
                <th
                  key={column}
                  className="whitespace-nowrap px-4 py-3.5 text-left font-mono text-[9px] font-semibold tracking-[0.15em] text-zinc-500"
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {filteredRisks.length === 0 ? (
              <tr>
                <td
                  colSpan={columns.length}
                  className="px-4 py-12 text-center"
                >
                  <ShieldAlert
                    size={30}
                    className="mx-auto mb-3 text-zinc-700"
                  />

                  <p className="text-sm text-zinc-500">
                    No risks found
                  </p>

                  {filterValue && (
                    <p className="mt-1 text-xs text-zinc-700">
                      Try a different search term.
                    </p>
                  )}
                </td>
              </tr>
            ) : (
              filteredRisks.map((risk) => (
                <tr
                  key={risk.id}
                  className="border-t border-orange-500/10 transition hover:bg-orange-500/[0.025]"
                >
                  {/* ID */}
                  <td className="whitespace-nowrap px-4 py-4">
                    <span className="font-mono text-xs font-semibold text-orange-400">
                      {risk.id}
                    </span>
                  </td>

                  {/* RISK NAME */}
                  <td className="px-4 py-4">
                    <div className="min-w-[220px]">
                      <p className="font-medium text-zinc-200">
                        {risk.name}
                      </p>

                      <p className="mt-1 text-[10px] text-zinc-600">
                        Organizational risk
                      </p>
                    </div>
                  </td>

                  {/* OWNER */}
                  <td className="whitespace-nowrap px-4 py-4 text-zinc-400">
                    {risk.owner}
                  </td>

                  {/* SEVERITY */}
                  <td className="whitespace-nowrap px-4 py-4">
                    <SeverityChip severity={risk.severity} />
                  </td>

                  {/* STATUS */}
                  <td className="whitespace-nowrap px-4 py-4">
                    <StatusChip status={risk.status} />
                  </td>

                  {/* ACTION */}
                  <td className="whitespace-nowrap px-4 py-4">
                    <button
                      type="button"
                      className="inline-flex items-center gap-1.5 rounded-lg border border-zinc-800 bg-[#050505] px-3 py-1.5 text-xs font-medium text-zinc-400 transition hover:border-orange-500/30 hover:text-orange-400"
                    >
                      <Pencil size={13} />
                      Edit
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>

    {/* FOOTER */}
    <div className="flex flex-col gap-2 border-t border-orange-500/10 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
      <span className="text-xs text-zinc-600">
        Total{" "}
        <span className="font-medium text-zinc-400">
          {filteredRisks.length}
        </span>{" "}
        Risks
      </span>

      <div className="flex items-center gap-4 text-xs text-zinc-600">
        <span>
          Page{" "}
          <span className="text-zinc-400">1</span>{" "}
          of{" "}
          <span className="text-zinc-400">10</span>
        </span>
      </div>
    </div>
  </div>
</div>


);
}

/* ---------------------------------------------
SEVERITY CHIP
--------------------------------------------- */

function SeverityChip({
severity,
}: {
severity: string;
}) {
if (severity === "Critical") {
return ( <Chip
     size="sm"
     className="border border-red-500/20 bg-red-500/10 text-red-400"
   >
Critical </Chip>
);
}

if (severity === "High") {
return ( <Chip
     size="sm"
     className="border border-orange-500/20 bg-orange-500/10 text-orange-400"
   >
High </Chip>
);
}

if (severity === "Medium") {
return ( <Chip
     size="sm"
     className="border border-yellow-500/20 bg-yellow-500/10 text-yellow-400"
   >
Medium </Chip>
);
}

return ( <Chip
   size="sm"
   className="border border-emerald-500/20 bg-emerald-500/10 text-emerald-400"
 >
Low </Chip>
);
}

/* ---------------------------------------------
STATUS CHIP
--------------------------------------------- */

function StatusChip({
status,
}: {
status: string;
}) {
if (status === "Resolved") {
return ( <Chip
     size="sm"
     className="border border-emerald-500/20 bg-emerald-500/10 text-emerald-400"
   >
Resolved </Chip>
);
}

if (status === "Open") {
return ( <Chip
     size="sm"
     className="border border-orange-500/20 bg-orange-500/10 text-orange-400"
   >
Open </Chip>
);
}

if (status === "Mitigating") {
return ( <Chip
     size="sm"
     className="border border-blue-500/20 bg-blue-500/10 text-blue-400"
   >
Mitigating </Chip>
);
}

return ( <Chip
   size="sm"
   className="border border-zinc-700 bg-zinc-800/50 text-zinc-400"
 >
Accepted </Chip>
);
}
