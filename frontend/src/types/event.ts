export interface EventResponse {
  id: string;
  organization_id: string;
  source: string;
  event_type: string;
  symbol: string;
  timestamp: string;
  importance: number;
  payload: Record<string, unknown>;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface EventListResponse {
  items: EventResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface EventQueryParams {
  symbol?: string;
  source?: string;
  event_type?: string;
  start?: string;
  end?: string;
  limit?: number;
  offset?: number;
}

export interface WsEventMessage {
  type: "event";
  data: EventResponse;
}
