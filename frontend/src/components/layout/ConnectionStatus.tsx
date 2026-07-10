import type { ConnectionStatus } from "@/websocket/eventsSocket";

const statusStyles: Record<ConnectionStatus, string> = {
  connecting: "bg-amber-500/20 text-amber-300 border-amber-500/40",
  connected: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
  disconnected: "bg-slate-500/20 text-slate-300 border-slate-500/40",
  error: "bg-rose-500/20 text-rose-300 border-rose-500/40",
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
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium ${statusStyles[status]}`}
    >
      <span
        className={`h-2 w-2 rounded-full ${
          status === "connected"
            ? "bg-emerald-400 animate-pulse"
            : status === "connecting"
              ? "bg-amber-400 animate-pulse"
              : "bg-slate-400"
        }`}
      />
      {statusLabels[status]}
    </span>
  );
}
