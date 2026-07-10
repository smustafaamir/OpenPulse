import type { EventResponse } from "@/types/event";
import {
  formatMarketTime,
  formatPercent,
  formatPrice,
  formatTradingPair,
  percentBadgeClass,
} from "@/utils/formatMarket";

interface LiveEventFeedProps {
  events: EventResponse[];
}

function payloadCurrency(payload: Record<string, unknown>): string {
  return typeof payload.currency === "string" ? payload.currency : "USD";
}

export function LiveEventFeed({ events }: LiveEventFeedProps) {
  return (
    <div className="max-h-[420px] overflow-y-auto rounded-lg glass-inset">
      <table className="min-w-full text-left text-sm">
        <thead className="sticky top-0 z-10 glass-chrome text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-4 py-3 font-medium">Time</th>
            <th className="px-4 py-3 font-medium">Pair</th>
            <th className="px-4 py-3 text-right font-medium">Last</th>
            <th className="px-4 py-3 text-right font-medium">24h</th>
          </tr>
        </thead>
        <tbody className="font-mono text-[13px]">
          {events.length === 0 ? (
            <tr>
              <td colSpan={4} className="px-4 py-10 text-center font-sans text-slate-500">
                Waiting for live market data…
              </td>
            </tr>
          ) : (
            events.map((event) => {
              const change = formatPercent(event.payload.change_24h_pct);
              const currency = payloadCurrency(event.payload);
              return (
                <tr
                  key={event.id}
                  className="border-t border-white/5 transition-colors hover:bg-white/[0.03]"
                >
                  <td className="whitespace-nowrap px-4 py-2.5 tabular-nums text-slate-400">
                    {formatMarketTime(event.timestamp)}
                  </td>
                  <td className="whitespace-nowrap px-4 py-2.5">
                    <span className="font-sans font-semibold text-slate-100">
                      {formatTradingPair(event.symbol, event.payload)}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-4 py-2.5 text-right tabular-nums text-base font-medium text-white">
                    {formatPrice(event.payload.price, currency)}
                  </td>
                  <td className="whitespace-nowrap px-4 py-2.5 text-right">
                    <span
                      className={`inline-block min-w-[4.5rem] rounded-md px-2 py-0.5 text-right text-xs font-semibold tabular-nums ring-1 ring-inset ${percentBadgeClass(change.tone)}`}
                    >
                      {change.text}
                    </span>
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}
