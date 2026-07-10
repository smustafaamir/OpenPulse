interface SourceBadgeProps {
  source: string;
}

const SOURCE_STYLES: Record<string, string> = {
  mock: "bg-slate-700/50 text-slate-200 ring-slate-500/30 backdrop-blur-sm",
  binance: "bg-emerald-500/15 text-emerald-300 ring-emerald-500/30 backdrop-blur-sm",
};

export function SourceBadge({ source }: SourceBadgeProps) {
  const normalized = source.toLowerCase();
  const style =
    SOURCE_STYLES[normalized] ?? "bg-pulse-500/15 text-pulse-300 ring-pulse-500/30";

  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium capitalize ring-1 ring-inset ${style}`}
    >
      {source}
    </span>
  );
}
