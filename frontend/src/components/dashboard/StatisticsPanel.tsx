import { Card } from "@/components/ui/Card";
import type { EventResponse } from "@/types/event";
import {
  formatMarketTime,
  formatPercent,
  formatPrice,
  percentToneClass,
} from "@/utils/formatMarket";

interface StatisticsPanelProps {
  events: EventResponse[];
}

const TRACKED_SYMBOLS = ["BTC", "ETH"] as const;

function latestBySymbol(events: EventResponse[]): Map<string, EventResponse> {
  const latest = new Map<string, EventResponse>();
  for (const event of events) {
    if (!latest.has(event.symbol)) {
      latest.set(event.symbol, event);
    }
  }
  return latest;
}

function ticksPerMinute(events: EventResponse[]): number {
  if (events.length < 2) {
    return events.length;
  }
  const newest = new Date(events[0].timestamp).getTime();
  const oldest = new Date(events[events.length - 1].timestamp).getTime();
  const minutes = Math.max((newest - oldest) / 60_000, 1 / 60);
  return Math.round(events.length / minutes);
}

export function StatisticsPanel({ events }: StatisticsPanelProps) {
  const latest = latestBySymbol(events);

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {TRACKED_SYMBOLS.map((symbol) => {
        const quote = latest.get(symbol);
        const change = quote ? formatPercent(quote.payload.change_24h_pct) : null;
        return (
          <Card key={symbol}>
            <p className="text-sm font-medium tracking-wide text-slate-400">
              {symbol}/USDT
            </p>
            {quote && change ? (
              <>
                <p className="stat-value mt-2 text-white">
                  {formatPrice(quote.payload.price, "USD")}
                </p>
                <p className={`mt-1 text-sm font-medium tabular-nums ${percentToneClass(change.tone)}`}>
                  {change.text}
                </p>
                <p className="mt-2 text-xs text-slate-500">
                  Updated {formatMarketTime(quote.timestamp)}
                </p>
              </>
            ) : (
              <p className="mt-2 text-sm text-slate-500">No quote yet</p>
            )}
          </Card>
        );
      })}
      <Card>
        <p className="text-sm tracking-wide text-slate-400">Ticks / minute</p>
        <p className="stat-value mt-2 text-white">{ticksPerMinute(events)}</p>
        <p className="mt-2 text-xs text-slate-500">
          {events.length} ticks in window
        </p>
      </Card>
      <Card>
        <p className="text-sm tracking-wide text-slate-400">Feed</p>
        <p className="mt-2 text-lg font-semibold text-emerald-300">Binance Live</p>
        <p className="mt-2 text-xs text-slate-500">Spot ticker · BTC & ETH</p>
      </Card>
    </div>
  );
}
