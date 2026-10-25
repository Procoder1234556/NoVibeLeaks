const SEVERITY_ICONS: Record<string, string> = {
  critical: "●",
  high: "▲",
  medium: "◆",
  low: "○",
};

export function SeverityBadge({ severity }: { severity: string }) {
  const map: Record<string, string> = {
    critical: "bg-red-900/80 text-red-100",
    high: "bg-orange-900/70 text-orange-100",
    medium: "bg-yellow-900/60 text-yellow-100",
    low: "bg-slate-700 text-slate-200",
  };
  const cls = map[severity] ?? map.low;
  const icon = SEVERITY_ICONS[severity] ?? SEVERITY_ICONS.low;

  return (
    <span
      className={`inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs font-medium uppercase ${cls}`}
    >
      <span aria-hidden="true">{icon}</span>
      {severity}
    </span>
  );
}
