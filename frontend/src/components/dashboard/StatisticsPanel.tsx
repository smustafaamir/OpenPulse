import { Card } from "@/components/ui/Card";
import type { EventResponse } from "@/types/event";

interface StatisticsPanelProps {
  events: EventResponse[];
}

function countUnique(values: string[]): number {
  return new Set(values).size;
}

function eventsPerMinute(events: EventResponse[]): number {
  if (events.length < 2) {
    return events.length;
  }
  const newest = new Date(events[0].timestamp).getTime();
  const oldest = new Date(events[events.length - 1].timestamp).getTime();
  const minutes = Math.max((newest - oldest) / 60_000, 1 / 60);
  return Math.round(events.length / minutes);
}

export function StatisticsPanel({ events }: StatisticsPanelProps) {
  const stats = [
    { label: "Events received", value: events.length },
    { label: "Events / minute", value: eventsPerMinute(events) },
    { label: "Sources", value: countUnique(events.map((event) => event.source)) },
    { label: "Symbols", value: countUnique(events.map((event) => event.symbol)) },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {stats.map((stat) => (
        <Card key={stat.label}>
          <p className="text-sm text-slate-400">{stat.label}</p>
          <p className="mt-2 text-3xl font-semibold text-white">{stat.value}</p>
        </Card>
      ))}
    </div>
  );
}
