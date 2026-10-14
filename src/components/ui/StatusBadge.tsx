type StatusBadgeProps = {
  status: string;
  tone?: "default" | "success" | "warning" | "danger";
};

export default function StatusBadge({ status, tone = "default" }: StatusBadgeProps) {
  const tones: Record<NonNullable<StatusBadgeProps["tone"]>, string> = {
    default: "bg-slate-800 text-slate-200",
    success: "bg-emerald-500/10 text-emerald-300",
    warning: "bg-amber-500/10 text-amber-300",
    danger: "bg-rose-500/10 text-rose-300",
  };

  return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${tones[tone]}`}>{status}</span>;
}
