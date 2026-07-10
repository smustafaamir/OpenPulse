import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import * as dashboardsApi from "@/api/dashboards";
import { listEvents } from "@/api/events";
import { ConnectionStatus } from "@/components/layout/ConnectionStatus";
import { LiveEventFeed } from "@/components/dashboard/LiveEventFeed";
import { PriceChart } from "@/components/dashboard/PriceChart";
import { StatisticsPanel } from "@/components/dashboard/StatisticsPanel";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useEventsWebSocket } from "@/hooks/useEventsWebSocket";
import type { DashboardLayout } from "@/types/dashboard";
import type { EventResponse } from "@/types/event";

const DEFAULT_LAYOUT: DashboardLayout = {
  widgets: ["feed", "chart", "stats"],
  selectedSymbol: "BTC",
};

const MARKET_SYMBOLS = ["BTC", "ETH"];

function isMarketQuote(event: EventResponse): boolean {
  return (
    event.source.toLowerCase() === "binance" &&
    event.event_type === "price" &&
    MARKET_SYMBOLS.includes(event.symbol)
  );
}

export function DashboardPage() {
  const queryClient = useQueryClient();
  const [selectedSymbol, setSelectedSymbol] = useState("BTC");
  const { events, status, setInitialEvents } = useEventsWebSocket(true);

  const bootstrapQuery = useQuery({
    queryKey: ["events", "dashboard-bootstrap"],
    queryFn: () =>
      listEvents({
        limit: 100,
        source: "binance",
        event_type: "price",
      }),
  });

  const dashboardsQuery = useQuery({
    queryKey: ["dashboards"],
    queryFn: dashboardsApi.listDashboards,
  });

  const saveLayoutMutation = useMutation({
    mutationFn: async (layout: DashboardLayout) => {
      const dashboards = dashboardsQuery.data ?? [];
      if (dashboards.length === 0) {
        return dashboardsApi.createDashboard({
          name: "Main Dashboard",
          layout,
        });
      }
      return dashboardsApi.updateDashboard(dashboards[0].id, { layout });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboards"] });
    },
  });

  useEffect(() => {
    if (bootstrapQuery.data?.items) {
      setInitialEvents(bootstrapQuery.data.items.filter(isMarketQuote));
    }
  }, [bootstrapQuery.data, setInitialEvents]);

  useEffect(() => {
    const dashboards = dashboardsQuery.data;
    if (!dashboards || dashboards.length === 0) {
      return;
    }
    const layout = dashboards[0].layout as unknown as DashboardLayout;
    if (layout.selectedSymbol && MARKET_SYMBOLS.includes(layout.selectedSymbol)) {
      setSelectedSymbol(layout.selectedSymbol);
    }
  }, [dashboardsQuery.data]);

  const marketEvents = useMemo(
    () => events.filter(isMarketQuote),
    [events],
  );

  const handleSymbolChange = (symbol: string) => {
    setSelectedSymbol(symbol);
    const layout: DashboardLayout = {
      ...DEFAULT_LAYOUT,
      selectedSymbol: symbol,
    };
    saveLayoutMutation.mutate(layout);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="display-title text-white">Dashboard</h2>
          <p className="mt-1 text-sm leading-relaxed text-slate-400">
            Live Binance spot quotes — BTC & ETH
          </p>
        </div>
        <ConnectionStatus status={status} />
      </div>

      <StatisticsPanel events={marketEvents} />

      <div className="grid gap-6 xl:grid-cols-2">
        <Card
          title="Market Tape"
          action={
            <span className="text-xs text-slate-500">
              {marketEvents.length} ticks
            </span>
          }
        >
          <LiveEventFeed events={marketEvents} />
        </Card>

        <Card
          title="Price Chart"
          action={
            <div className="flex items-center gap-2">
              <label className="text-xs text-slate-400" htmlFor="symbol-select">
                Pair
              </label>
              <select
                id="symbol-select"
                value={selectedSymbol}
                onChange={(e) => handleSymbolChange(e.target.value)}
                className="field-control press-feedback"
              >
                {MARKET_SYMBOLS.map((symbol) => (
                  <option key={symbol} value={symbol}>
                    {symbol}/USDT
                  </option>
                ))}
              </select>
            </div>
          }
        >
          <PriceChart events={marketEvents} symbol={selectedSymbol} />
        </Card>
      </div>

      {saveLayoutMutation.isError && (
        <p className="text-sm text-rose-400">Failed to save dashboard layout.</p>
      )}
      {dashboardsQuery.isLoading && (
        <p className="text-sm text-slate-500">Loading dashboard configuration...</p>
      )}
      {!dashboardsQuery.isLoading && (dashboardsQuery.data?.length ?? 0) === 0 && (
        <Button
          onClick={() => saveLayoutMutation.mutate(DEFAULT_LAYOUT)}
          disabled={saveLayoutMutation.isPending}
        >
          Create default dashboard
        </Button>
      )}
    </div>
  );
}
