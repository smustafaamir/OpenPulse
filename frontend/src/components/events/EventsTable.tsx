import type { EventResponse } from "@/types/event";

interface EventsTableProps {
  events: EventResponse[];
  total: number;
  limit: number;
  offset: number;
  onPageChange: (offset: number) => void;
}

export function EventsTable({
  events,
  total,
  limit,
  offset,
  onPageChange,
}: EventsTableProps) {
  const page = Math.floor(offset / limit) + 1;
  const totalPages = Math.max(Math.ceil(total / limit), 1);

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto rounded-lg border border-slate-800">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-900 text-slate-400">
            <tr>
              <th className="px-3 py-2">Timestamp</th>
              <th className="px-3 py-2">Symbol</th>
              <th className="px-3 py-2">Type</th>
              <th className="px-3 py-2">Source</th>
              <th className="px-3 py-2">Importance</th>
              <th className="px-3 py-2">Payload</th>
            </tr>
          </thead>
          <tbody>
            {events.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-3 py-8 text-center text-slate-500">
                  No events found
                </td>
              </tr>
            ) : (
              events.map((event) => (
                <tr key={event.id} className="border-t border-slate-800/80">
                  <td className="px-3 py-2 text-slate-400">
                    {new Date(event.timestamp).toLocaleString()}
                  </td>
                  <td className="px-3 py-2 font-medium text-slate-100">{event.symbol}</td>
                  <td className="px-3 py-2 text-slate-300">{event.event_type}</td>
                  <td className="px-3 py-2 text-slate-300">{event.source}</td>
                  <td className="px-3 py-2 text-slate-300">{event.importance}</td>
                  <td className="px-3 py-2 text-slate-400">
                    {JSON.stringify(event.payload)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <div className="flex items-center justify-between text-sm text-slate-400">
        <span>
          Page {page} of {totalPages} ({total} total)
        </span>
        <div className="flex gap-2">
          <button
            type="button"
            disabled={offset === 0}
            onClick={() => onPageChange(Math.max(offset - limit, 0))}
            className="rounded-lg border border-slate-700 px-3 py-1 disabled:opacity-40"
          >
            Previous
          </button>
          <button
            type="button"
            disabled={offset + limit >= total}
            onClick={() => onPageChange(offset + limit)}
            className="rounded-lg border border-slate-700 px-3 py-1 disabled:opacity-40"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
