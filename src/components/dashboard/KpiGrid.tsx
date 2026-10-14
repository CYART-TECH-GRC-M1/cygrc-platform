import MetricCard from "../ui/MetricCard";

const metrics = [
  { title: "Compliance Score", value: "82%", delta: "+2%" },
  { title: "Open Risks", value: 14, delta: "4 critical" },
  { title: "Pending Audits", value: 3, delta: "1 overdue" },
  { title: "Evidence Uploaded", value: 27, delta: "+6 this week" },
];

export default function KpiGrid() {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {metrics.map((metric) => (
        <MetricCard key={metric.title} {...metric} />
      ))}
    </div>
  );
}
