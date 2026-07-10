import type { EventResponse } from "@/types/event";

interface LiveEventFeedProps {
  events: EventResponse[];
}

export function LiveEventFeed({ events }: LiveEventFeedProps) {
  return (
    <div className="max-h-[420px] overflow-y-auto rounded-lg border border-slate-800">
      <table className="min-w-full text-left text-sm">
        <thead className="sticky top-0 bg-slate-900 text-slate-400">
          <tr>
            <th className="px-3 py-2">Time</th>
            <th className="px-3 py-2">Symbol</th>
            <th className="px-3 py-2">Type</th>
            <th className="px-3 py-2">Source</th>
            <th className="px-3 py-2">Payload</th>
          </tr>
        </thead>
        <tbody>
          {events.length === 0 ? (
            <tr>
              <td colSpan={5} className="px-3 py-8 text-center text-slate-500">
                Waiting for events...
              </td>
            </tr>
          ) : (
            events.map((event) => (
              <tr key={event.id} className="border-t border-slate-800/80">
                <td className="px-3 py-2 text-slate-400">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </td>
                <td className="px-3 py-2 font-medium text-slate-100">{event.symbol}</td>
                <td className="px-3 py-2 text-slate-300">{event.event_type}</td>
                <td className="px-3 py-2 text-slate-300">{event.source}</td>
                <td className="px-3 py-2 text-slate-400">
                  {JSON.stringify(event.payload)}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
