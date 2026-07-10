import { useQuery } from "@tanstack/react-query";
import { FormEvent, useState } from "react";
import { listEvents } from "@/api/events";
import { EventsTable } from "@/components/events/EventsTable";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import type { EventQueryParams } from "@/types/event";

const PAGE_SIZE = 25;

export function EventsPage() {
  const [filters, setFilters] = useState<EventQueryParams>({
    limit: PAGE_SIZE,
    offset: 0,
  });
  const [draft, setDraft] = useState({
    symbol: "",
    source: "",
    event_type: "",
    start: "",
    end: "",
  });

  const eventsQuery = useQuery({
    queryKey: ["events", filters],
    queryFn: () => listEvents(filters),
  });

  const handleFilterSubmit = (event: FormEvent) => {
    event.preventDefault();
    setFilters({
      symbol: draft.symbol || undefined,
      source: draft.source || undefined,
      event_type: draft.event_type || undefined,
      start: draft.start ? new Date(draft.start).toISOString() : undefined,
      end: draft.end ? new Date(draft.end).toISOString() : undefined,
      limit: PAGE_SIZE,
      offset: 0,
    });
  };

  const handleClear = () => {
    setDraft({ symbol: "", source: "", event_type: "", start: "", end: "" });
    setFilters({ limit: PAGE_SIZE, offset: 0 });
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-white">Events</h2>
        <p className="text-sm text-slate-400">
          Query historical events with filters and pagination
        </p>
      </div>

      <Card title="Filters">
        <form
          className="grid gap-4 md:grid-cols-2 xl:grid-cols-3"
          onSubmit={handleFilterSubmit}
        >
          <Input
            label="Symbol"
            value={draft.symbol}
            onChange={(e) => setDraft((prev) => ({ ...prev, symbol: e.target.value }))}
            placeholder="BTC"
          />
          <Input
            label="Source"
            value={draft.source}
            onChange={(e) => setDraft((prev) => ({ ...prev, source: e.target.value }))}
            placeholder="mock"
          />
          <Input
            label="Event type"
            value={draft.event_type}
            onChange={(e) =>
              setDraft((prev) => ({ ...prev, event_type: e.target.value }))
            }
            placeholder="price"
          />
          <Input
            label="Start"
            type="datetime-local"
            value={draft.start}
            onChange={(e) => setDraft((prev) => ({ ...prev, start: e.target.value }))}
          />
          <Input
            label="End"
            type="datetime-local"
            value={draft.end}
            onChange={(e) => setDraft((prev) => ({ ...prev, end: e.target.value }))}
          />
          <div className="flex items-end gap-2">
            <Button type="submit">Apply filters</Button>
            <Button type="button" variant="secondary" onClick={handleClear}>
              Clear
            </Button>
          </div>
        </form>
      </Card>

      <Card title="Event history">
        {eventsQuery.isLoading ? (
          <p className="text-sm text-slate-500">Loading events...</p>
        ) : eventsQuery.isError ? (
          <p className="text-sm text-rose-400">Failed to load events.</p>
        ) : (
          <EventsTable
            events={eventsQuery.data?.items ?? []}
            total={eventsQuery.data?.total ?? 0}
            limit={filters.limit ?? PAGE_SIZE}
            offset={filters.offset ?? 0}
            onPageChange={(offset) =>
              setFilters((current) => ({
                ...current,
                offset,
              }))
            }
          />
        )}
      </Card>
    </div>
  );
}
