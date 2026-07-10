import { apiRequest } from "@/api/client";
import type { EventListResponse, EventQueryParams, EventResponse } from "@/types/event";

function toQueryString(params: EventQueryParams): string {
  const search = new URLSearchParams();
  if (params.symbol) search.set("symbol", params.symbol);
  if (params.source) search.set("source", params.source);
  if (params.event_type) search.set("event_type", params.event_type);
  if (params.start) search.set("start", params.start);
  if (params.end) search.set("end", params.end);
  if (params.limit !== undefined) search.set("limit", String(params.limit));
  if (params.offset !== undefined) search.set("offset", String(params.offset));
  const query = search.toString();
  return query ? `?${query}` : "";
}

export function listEvents(params: EventQueryParams = {}): Promise<EventListResponse> {
  return apiRequest<EventListResponse>(`/events${toQueryString(params)}`);
}

export function getEvent(eventId: string): Promise<EventResponse> {
  return apiRequest<EventResponse>(`/events/${eventId}`);
}
