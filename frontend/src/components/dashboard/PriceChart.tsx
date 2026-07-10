import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { EventResponse } from "@/types/event";
import { formatMarketTime, formatPrice } from "@/utils/formatMarket";

interface PriceChartProps {
  events: EventResponse[];
  symbol?: string;
}

function extractPrice(event: EventResponse): number | null {
  const price = event.payload.price;
  return typeof price === "number" ? price : null;
}

export function PriceChart({ events, symbol }: PriceChartProps) {
  const priceEvents = events
    .filter((event) => event.event_type === "price")
    .filter((event) => (symbol ? event.symbol === symbol : true))
    .map((event) => ({
      time: formatMarketTime(event.timestamp),
      price: extractPrice(event),
      currency:
        typeof event.payload.currency === "string" ? event.payload.currency : "USD",
      pair: `${event.symbol}/USDT`,
    }))
    .filter((point) => point.price !== null)
    .reverse();

  return (
    <div className="h-72 w-full">
      {priceEvents.length === 0 ? (
        <div className="flex h-full items-center justify-center text-sm text-slate-500">
          No price data for {symbol ?? "selected pair"} yet
        </div>
      ) : (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={priceEvents}>
            <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
            <XAxis
              dataKey="time"
              stroke="#64748b"
              tick={{ fontSize: 11, fontFamily: "ui-monospace, monospace" }}
              minTickGap={32}
            />
            <YAxis
              stroke="#64748b"
              tick={{ fontSize: 11, fontFamily: "ui-monospace, monospace" }}
              tickFormatter={(value: number) => formatPrice(value)}
              domain={["auto", "auto"]}
              width={88}
            />
            <Tooltip
              contentStyle={{
                background: "#0f172a",
                border: "1px solid #334155",
                borderRadius: "8px",
                fontFamily: "ui-monospace, monospace",
                fontSize: "13px",
              }}
              labelFormatter={(label) => `Time ${label}`}
              formatter={(value: number, _name, item) => {
                const currency =
                  typeof item.payload.currency === "string"
                    ? item.payload.currency
                    : "USD";
                return [formatPrice(value, currency), item.payload.pair];
              }}
            />
            <Line
              type="monotone"
              dataKey="price"
              stroke="#38bdf8"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
