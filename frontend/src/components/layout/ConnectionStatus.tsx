import type { ConnectionStatus } from "@/websocket/eventsSocket";

const statusStyles: Record<ConnectionStatus, string> = {
  connecting: "bg-amber-500/15 text-amber-300 ring-amber-500/25",
  connected: "bg-emerald-500/15 text-emerald-300 ring-emerald-500/25",
  disconnected: "bg-slate-500/15 text-slate-300 ring-slate-500/25",
  error: "bg-rose-500/15 text-rose-300 ring-rose-500/25",
};

const statusLabels: Record<ConnectionStatus, string> = {
  connecting: "Connecting",
  connected: "Live",
  disconnected: "Disconnected",
  error: "Connection error",
};

interface ConnectionStatusProps {
  status: ConnectionStatus;
}

export function ConnectionStatus({ status }: ConnectionStatusProps) {
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium ring-1 ring-inset backdrop-blur-sm ${statusStyles[status]}`}
    >
      <span
        className={`h-2 w-2 rounded-full ${
          status === "connected"
            ? "bg-emerald-400 animate-pulse motion-reduce:animate-none"
            : status === "connecting"
              ? "bg-amber-400 animate-pulse motion-reduce:animate-none"
              : "bg-slate-400"
        }`}
      />
      {statusLabels[status]}
    </span>
  );
}
