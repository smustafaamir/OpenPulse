import { WS_BASE } from "@/config";
import type { EventResponse, WsEventMessage } from "@/types/event";

export type ConnectionStatus = "connecting" | "connected" | "disconnected" | "error";

export interface EventsSocketOptions {
  token: string;
  onEvent: (event: EventResponse) => void;
  onStatusChange: (status: ConnectionStatus) => void;
}

const MAX_BACKOFF_MS = 30_000;
const INITIAL_BACKOFF_MS = 1_000;

export class EventsSocket {
  private socket: WebSocket | null = null;
  private closed = false;
  private backoffMs = INITIAL_BACKOFF_MS;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private readonly options: EventsSocketOptions;
  private bufferedEvents: EventResponse[] = [];

  constructor(options: EventsSocketOptions) {
    this.options = options;
  }

  connect(): void {
    this.closed = false;
    this.openSocket();
  }

  disconnect(): void {
    this.closed = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.socket?.close();
    this.socket = null;
    this.options.onStatusChange("disconnected");
  }

  drainBuffer(): EventResponse[] {
    const events = [...this.bufferedEvents];
    this.bufferedEvents = [];
    return events;
  }

  private openSocket(): void {
    if (this.closed) {
      return;
    }

    this.options.onStatusChange("connecting");
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const base = WS_BASE || `${protocol}//${window.location.host}`;
    const url = `${base}/ws/events?token=${encodeURIComponent(this.options.token)}`;
    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      this.backoffMs = INITIAL_BACKOFF_MS;
      this.options.onStatusChange("connected");
      const buffered = this.drainBuffer();
      for (const event of buffered) {
        this.options.onEvent(event);
      }
    };

    this.socket.onmessage = (message) => {
      try {
        const payload = JSON.parse(message.data as string) as WsEventMessage;
        if (payload.type === "event") {
          if (this.socket?.readyState === WebSocket.OPEN) {
            this.options.onEvent(payload.data);
          } else {
            this.bufferedEvents.push(payload.data);
          }
        }
      } catch {
        // ignore malformed messages
      }
    };

    this.socket.onerror = () => {
      this.options.onStatusChange("error");
    };

    this.socket.onclose = () => {
      this.socket = null;
      if (!this.closed) {
        this.options.onStatusChange("disconnected");
        this.scheduleReconnect();
      }
    };
  }

  private scheduleReconnect(): void {
    if (this.closed) {
      return;
    }
    this.reconnectTimer = setTimeout(() => {
      this.openSocket();
      this.backoffMs = Math.min(this.backoffMs * 2, MAX_BACKOFF_MS);
    }, this.backoffMs);
  }

  bufferEvent(event: EventResponse): void {
    this.bufferedEvents.push(event);
  }
}
