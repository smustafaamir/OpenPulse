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

const DEFAULT_LAYOUT: DashboardLayout = {
  widgets: ["feed", "chart", "stats"],
  selectedSymbol: "BTC",
};

export function DashboardPage() {
  const queryClient = useQueryClient();
  const [selectedSymbol, setSelectedSymbol] = useState("BTC");
  const { events, status, setInitialEvents } = useEventsWebSocket(true);

  const bootstrapQuery = useQuery({
    queryKey: ["events", "dashboard-bootstrap"],
    queryFn: () => listEvents({ limit: 100 }),
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
      setInitialEvents(bootstrapQuery.data.items);
    }
  }, [bootstrapQuery.data, setInitialEvents]);

  useEffect(() => {
    const dashboards = dashboardsQuery.data;
    if (!dashboards || dashboards.length === 0) {
      return;
    }
    const layout = dashboards[0].layout as unknown as DashboardLayout;
    if (layout.selectedSymbol) {
      setSelectedSymbol(layout.selectedSymbol);
    }
  }, [dashboardsQuery.data]);

  const symbols = useMemo(
    () => Array.from(new Set(events.map((event) => event.symbol))).sort(),
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
          <h2 className="text-2xl font-semibold text-white">Dashboard</h2>
          <p className="text-sm text-slate-400">
            Live event intelligence for your organization
          </p>
        </div>
        <ConnectionStatus status={status} />
      </div>

      <StatisticsPanel events={events} />

      <div className="grid gap-6 xl:grid-cols-2">
        <Card
          title="Live Event Feed"
          action={
            <span className="text-xs text-slate-500">Newest {events.length} events</span>
          }
        >
          <LiveEventFeed events={events} />
        </Card>

        <Card
          title="Price Chart"
          action={
            <div className="flex items-center gap-2">
              <label className="text-xs text-slate-400" htmlFor="symbol-select">
                Symbol
              </label>
              <select
                id="symbol-select"
                value={selectedSymbol}
                onChange={(e) => handleSymbolChange(e.target.value)}
                className="rounded-lg border border-slate-700 bg-slate-900 px-2 py-1 text-sm"
              >
                {(symbols.length > 0 ? symbols : ["BTC", "ETH", "SPY", "NVDA"]).map(
                  (symbol) => (
                    <option key={symbol} value={symbol}>
                      {symbol}
                    </option>
                  ),
                )}
              </select>
            </div>
          }
        >
          <PriceChart events={events} symbol={selectedSymbol} />
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
