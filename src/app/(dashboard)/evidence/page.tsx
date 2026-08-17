"use client";

import React, { useRef, useState } from "react";
import { motion } from "framer-motion";
import {
FileCheck2,
UploadCloud,
Files,
ShieldCheck,
Clock3,
ArrowUpRight,
FileText,
Image as ImageIcon,
Archive,
X,
CheckCircle2,
AlertCircle,
Trash2,
Download,
Search,
} from "lucide-react";

const stats = [
{
title: "TOTAL EVIDENCE",
value: "4,521",
change: "+12%",
text: "vs last month",
icon: Files,
color: "orange",
},
{
title: "VERIFIED EVIDENCE",
value: "3,842",
change: "+8%",
text: "successfully verified",
icon: ShieldCheck,
color: "green",
},
{
title: "PENDING REVIEW",
value: "426",
change: "-5%",
text: "awaiting verification",
icon: Clock3,
color: "orange",
},
{
title: "EVIDENCE COVERAGE",
value: "87%",
change: "+4%",
text: "compliance coverage",
icon: FileCheck2,
color: "green",
},
];

type EvidenceStatus = "Verified" | "Pending" | "Rejected";

type EvidenceItem = {
id: number;
name: string;
framework: string;
type: string;
size: string;
status: EvidenceStatus;
updated: string;
};

const initialEvidence: EvidenceItem[] = [
{
id: 1,
name: "ISO 27001 Security Policy.pdf",
framework: "ISO 27001",
type: "PDF",
size: "2.4 MB",
status: "Verified",
updated: "Today",
},
{
id: 2,
name: "SOC 2 Access Control.docx",
framework: "SOC 2",
type: "DOCX",
size: "1.8 MB",
status: "Pending",
updated: "Yesterday",
},
{
id: 3,
name: "Risk Assessment Report.pdf",
framework: "ISO 27001",
type: "PDF",
size: "4.2 MB",
status: "Verified",
updated: "2 days ago",
},
{
id: 4,
name: "Security Awareness Training.png",
framework: "SOC 2",
type: "PNG",
size: "856 KB",
status: "Verified",
updated: "3 days ago",
},
];

export default function EvidencePage() {
const fileInputRef = useRef<HTMLInputElement>(null);

const [evidence, setEvidence] =
useState<EvidenceItem[]>(initialEvidence);

const [search, setSearch] = useState("");
const [isDragging, setIsDragging] = useState(false);
const [uploading, setUploading] = useState(false);

const handleFiles = (files: FileList | File[]) => {
const selectedFiles = Array.from(files);

if (!selectedFiles.length) return;

setUploading(true);

setTimeout(() => {
  const newEvidence: EvidenceItem[] = selectedFiles.map(
    (file, index) => ({
      id: Date.now() + index,
      name: file.name,
      framework: "Pending Assignment",
      type:
        file.name.split(".").pop()?.toUpperCase() || "FILE",
      size: formatFileSize(file.size),
      status: "Pending",
      updated: "Just now",
    })
  );

  setEvidence((current) => [
    ...newEvidence,
    ...current,
  ]);

  setUploading(false);
}, 700);


};

const handleFileChange = (
event: React.ChangeEvent<HTMLInputElement>
) => {
if (event.target.files) {
handleFiles(event.target.files);
}

event.target.value = "";

};

const handleDrop = (
event: React.DragEvent<HTMLDivElement>
) => {
event.preventDefault();
setIsDragging(false);

if (event.dataTransfer.files) {
  handleFiles(event.dataTransfer.files);
}


};

const removeEvidence = (id: number) => {
setEvidence((current) =>
current.filter((item) => item.id !== id)
);
};

const filteredEvidence = evidence.filter((item) =>
`${item.name} ${item.framework} ${item.type} ${item.status}`
.toLowerCase()
.includes(search.toLowerCase())
);

return ( <div className="min-h-full space-y-6">
{/* PAGE HEADER */}


  <motion.div
    initial={{ opacity: 0, y: -12 }}
    animate={{ opacity: 1, y: 0 }}
    className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between"
  >
    <div>
      <div className="mb-2 flex items-center gap-2">
        <div className="h-1 w-8 rounded-full bg-orange-500" />

        <span className="font-mono text-[10px] font-semibold tracking-[0.25em] text-orange-400">
          CYGRC / EVIDENCE
        </span>
      </div>

      <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
        Evidence Management
      </h1>

      <p className="mt-2 text-sm text-zinc-500">
        Upload, organize, and manage compliance evidence.
      </p>
    </div>

    <button
      type="button"
      onClick={() => fileInputRef.current?.click()}
      className="flex w-fit items-center gap-2 rounded-xl bg-orange-500 px-5 py-3 text-sm font-semibold text-black shadow-lg shadow-orange-500/20 transition hover:bg-orange-400 active:scale-[0.98]"
    >
      <UploadCloud size={18} />
      Upload Evidence
    </button>

    <input
      ref={fileInputRef}
      type="file"
      multiple
      className="hidden"
      accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg,.zip"
      onChange={handleFileChange}
    />
  </motion.div>

  {/* KPI CARDS */}

  <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
    {stats.map((stat, index) => {
      const Icon = stat.icon;
      const orange = stat.color === "orange";

      return (
        <motion.div
          key={stat.title}
          initial={{
            opacity: 0,
            y: 15,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          transition={{
            delay: index * 0.08,
          }}
          whileHover={{
            y: -4,
          }}
          className={`rounded-2xl border bg-[#080807] p-6 shadow-[0_10px_40px_rgba(0,0,0,0.18)] ${
            orange
              ? "border-orange-500/20 hover:border-orange-500/40"
              : "border-emerald-500/20 hover:border-emerald-500/40"
          } transition`}
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="font-mono text-[9px] tracking-[0.2em] text-zinc-500">
                {stat.title}
              </p>

              <h2 className="mt-3 text-3xl font-semibold text-white">
                {stat.value}
              </h2>
            </div>

            <div
              className={`flex h-11 w-11 items-center justify-center rounded-xl ${
                orange
                  ? "bg-orange-500/10 text-orange-400"
                  : "bg-emerald-500/10 text-emerald-400"
              }`}
            >
              <Icon size={22} />
            </div>
          </div>

          <div className="mt-4 flex gap-2 text-xs">
            <span
              className={
                stat.change.startsWith("-")
                  ? "font-semibold text-orange-400"
                  : "font-semibold text-emerald-400"
              }
            >
              {stat.change}
            </span>

            <span className="text-zinc-500">
              {stat.text}
            </span>
          </div>
        </motion.div>
      );
    })}
  </div>

  {/* UPLOAD + TIPS */}

  <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
    {/* UPLOAD AREA */}

    <motion.div
      initial={{
        opacity: 0,
        y: 15,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="xl:col-span-2"
    >
      <div className="h-full rounded-2xl border border-orange-500/15 bg-[#080807]">
        <div className="flex items-center justify-between border-b border-orange-500/10 p-6">
          <div>
            <p className="font-mono text-[9px] tracking-[0.2em] text-orange-500">
              EVIDENCE_INGESTION
            </p>

            <h2 className="mt-2 text-lg font-semibold text-white">
              Upload Evidence
            </h2>

            <p className="mt-1 text-sm text-zinc-500">
              Add documents and files required for compliance.
            </p>
          </div>

          <div className="hidden h-11 w-11 items-center justify-center rounded-xl bg-orange-500/10 text-orange-400 sm:flex">
            <UploadCloud size={21} />
          </div>
        </div>

        <div className="p-6">
          <div
            onDragOver={(event) => {
              event.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => {
              setIsDragging(false);
            }}
            onDrop={handleDrop}
            onClick={() =>
              fileInputRef.current?.click()
            }
            className={`group flex min-h-[230px] cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-8 text-center transition ${
              isDragging
                ? "border-orange-400 bg-orange-500/10"
                : "border-orange-500/20 bg-[#050505] hover:border-orange-500/40 hover:bg-orange-500/[0.03]"
            }`}
          >
            <motion.div
              animate={{
                y: isDragging ? -5 : [0, -4, 0],
              }}
              transition={{
                duration: 2,
                repeat: isDragging ? 0 : Infinity,
              }}
              className="flex h-16 w-16 items-center justify-center rounded-2xl bg-orange-500/10 text-orange-400"
            >
              <UploadCloud size={30} />
            </motion.div>

            <h3 className="mt-5 text-base font-semibold text-white">
              {uploading
                ? "Processing files..."
                : isDragging
                ? "Drop your files here"
                : "Drag & Drop files here"}
            </h3>

            <p className="mt-2 text-sm text-zinc-500">
              or click anywhere to browse files
            </p>

            <div className="mt-5 flex flex-wrap justify-center gap-2">
              {[
                "PDF",
                "DOC",
                "DOCX",
                "PNG",
                "JPG",
                "ZIP",
              ].map((type) => (
                <span
                  key={type}
                  className="rounded-lg border border-zinc-800 bg-zinc-900/60 px-2.5 py-1 font-mono text-[9px] text-zinc-500"
                >
                  {type}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </motion.div>

    {/* TIPS */}

    <motion.div
      initial={{
        opacity: 0,
        x: 15,
      }}
      animate={{
        opacity: 1,
        x: 0,
      }}
    >
      <div className="h-full rounded-2xl border border-emerald-500/15 bg-[#080807] p-6">
        <div className="mb-5 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400">
            <FileText size={21} />
          </div>

          <div>
            <p className="font-mono text-[9px] tracking-[0.2em] text-emerald-500">
              FILE_PROTOCOL
            </p>

            <h3 className="mt-1 font-semibold text-white">
              Upload Tips
            </h3>
          </div>
        </div>

        <div className="space-y-3">
          <Tip
            icon={FileText}
            title="Documents"
            text="PDF, DOC, DOCX and text files"
          />

          <Tip
            icon={ImageIcon}
            title="Images"
            text="PNG, JPG, JPEG and screenshots"
          />

          <Tip
            icon={Archive}
            title="Archives"
            text="ZIP and supported archive files"
          />
        </div>

        <div className="mt-5 rounded-xl border border-emerald-500/15 bg-emerald-500/5 p-4">
          <div className="flex gap-3">
            <ShieldCheck
              size={18}
              className="shrink-0 text-emerald-400"
            />

            <div>
              <p className="text-xs font-semibold text-emerald-400">
                SECURITY REMINDER
              </p>

              <p className="mt-1 text-xs leading-5 text-zinc-500">
                Upload only authorized evidence files.
              </p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  </div>

  {/* REPOSITORY */}

  <motion.div
    initial={{
      opacity: 0,
      y: 15,
    }}
    animate={{
      opacity: 1,
      y: 0,
    }}
  >
    <div className="rounded-2xl border border-orange-500/15 bg-[#080807]">
      <div className="flex flex-col gap-4 border-b border-orange-500/10 p-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="font-mono text-[9px] tracking-[0.2em] text-emerald-500">
            EVIDENCE_REPOSITORY
          </p>

          <h2 className="mt-2 text-lg font-semibold text-white">
            Evidence Repository
          </h2>

          <p className="mt-1 text-sm text-zinc-500">
            Browse and manage uploaded evidence.
          </p>
        </div>

        <div className="relative w-full sm:w-64">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-600"
          />

          <input
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
            placeholder="Search evidence..."
            className="w-full rounded-xl border border-zinc-800 bg-[#050505] py-2.5 pl-9 pr-3 text-xs text-white outline-none transition placeholder:text-zinc-600 focus:border-orange-500/40"
          />
        </div>
      </div>

      <div className="overflow-x-auto p-6">
        <div className="overflow-hidden rounded-xl border border-orange-500/10">
          <table className="w-full min-w-[850px]">
            <thead className="bg-[#111111]">
              <tr>
                <th className="p-4 text-left font-mono text-[9px] tracking-wider text-zinc-500">
                  FILE
                </th>

                <th className="p-4 text-left font-mono text-[9px] tracking-wider text-zinc-500">
                  FRAMEWORK
                </th>

                <th className="p-4 text-left font-mono text-[9px] tracking-wider text-zinc-500">
                  TYPE
                </th>

                <th className="p-4 text-left font-mono text-[9px] tracking-wider text-zinc-500">
                  SIZE
                </th>

                <th className="p-4 text-left font-mono text-[9px] tracking-wider text-zinc-500">
                  STATUS
                </th>

                <th className="p-4 text-left font-mono text-[9px] tracking-wider text-zinc-500">
                  UPDATED
                </th>

                <th className="p-4 text-right font-mono text-[9px] tracking-wider text-zinc-500">
                  ACTION
                </th>
              </tr>
            </thead>

            <tbody>
              {filteredEvidence.length === 0 ? (
                <tr>
                  <td
                    colSpan={7}
                    className="p-12 text-center"
                  >
                    <Files
                      size={32}
                      className="mx-auto mb-3 text-zinc-700"
                    />

                    <p className="text-sm text-zinc-500">
                      No evidence found
                    </p>
                  </td>
                </tr>
              ) : (
                filteredEvidence.map((item) => (
                  <tr
                    key={item.id}
                    className="border-t border-orange-500/10 transition hover:bg-orange-500/[0.025]"
                  >
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-orange-500/10 text-orange-400">
                          <FileText size={17} />
                        </div>

                        <div>
                          <p className="max-w-[260px] truncate text-sm font-medium text-zinc-200">
                            {item.name}
                          </p>

                          <p className="mt-1 text-[10px] text-zinc-600">
                            Evidence #{item.id}
                          </p>
                        </div>
                      </div>
                    </td>

                    <td className="p-4 text-sm text-zinc-400">
                      {item.framework}
                    </td>

                    <td className="p-4">
                      <span className="rounded-md bg-zinc-900 px-2 py-1 font-mono text-[9px] text-zinc-500">
                        {item.type}
                      </span>
                    </td>

                    <td className="p-4 text-sm text-zinc-500">
                      {item.size}
                    </td>

                    <td className="p-4">
                      <StatusBadge status={item.status} />
                    </td>

                    <td className="p-4 text-sm text-zinc-500">
                      {item.updated}
                    </td>

                    <td className="p-4">
                      <div className="flex justify-end gap-1">
                        <button
                          type="button"
                          title="Download"
                          className="rounded-lg p-2 text-zinc-600 transition hover:bg-emerald-500/10 hover:text-emerald-400"
                        >
                          <Download size={15} />
                        </button>

                        <button
                          type="button"
                          title="Delete"
                          onClick={() =>
                            removeEvidence(item.id)
                          }
                          className="rounded-lg p-2 text-zinc-600 transition hover:bg-red-500/10 hover:text-red-400"
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="flex flex-col gap-2 border-t border-orange-500/10 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-xs text-zinc-600">
          Showing{" "}
          <span className="text-zinc-400">
            {filteredEvidence.length}
          </span>{" "}
          evidence files
        </p>

        <button
          type="button"
          className="flex items-center gap-2 text-xs font-semibold tracking-wider text-orange-400 transition hover:text-orange-300"
        >
          VIEW ALL
          <ArrowUpRight size={15} />
        </button>
      </div>
    </div>
  </motion.div>
</div>


);
}

type TipProps = {
icon: React.ElementType;
title: string;
text: string;
};

function Tip({
icon: Icon,
title,
text,
}: TipProps) {
return ( <div className="flex items-center gap-3 rounded-xl border border-orange-500/10 bg-[#050505] p-4 transition hover:border-orange-500/20"> <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-orange-500/10 text-orange-400"> <Icon size={18} /> </div>

  <div>
    <p className="text-sm font-medium text-zinc-200">
      {title}
    </p>

    <p className="mt-1 text-xs text-zinc-500">
      {text}
    </p>
  </div>
</div>


);
}

function StatusBadge({
status,
}: {
status: EvidenceStatus;
}) {
if (status === "Verified") {
return ( <span className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-500/10 px-2.5 py-1.5 text-[10px] font-semibold text-emerald-400"> <CheckCircle2 size={12} />
Verified </span>
);
}

if (status === "Rejected") {
return ( <span className="inline-flex items-center gap-1.5 rounded-lg bg-red-500/10 px-2.5 py-1.5 text-[10px] font-semibold text-red-400"> <X size={12} />
Rejected </span>
);
}

return ( <span className="inline-flex items-center gap-1.5 rounded-lg bg-orange-500/10 px-2.5 py-1.5 text-[10px] font-semibold text-orange-400"> <AlertCircle size={12} />
Pending </span>
);
}

function formatFileSize(bytes: number) {
if (bytes === 0) return "0 Bytes";

const units = [
"Bytes",
"KB",
"MB",
"GB",
];

const index = Math.floor(
Math.log(bytes) / Math.log(1024)
);

return `${parseFloat(
    (bytes / Math.pow(1024, index)).toFixed(1)
  )} ${units[index]}`;
}
