import { useCallback, useEffect, useRef, useState } from "react";
import { useAuthStore } from "@/stores/authStore";
import type { EventResponse } from "@/types/event";
import { EventsSocket, type ConnectionStatus } from "@/websocket/eventsSocket";

const MAX_EVENTS = 100;

export function useEventsWebSocket(enabled: boolean) {
  const accessToken = useAuthStore((state) => state.accessToken);
  const [events, setEvents] = useState<EventResponse[]>([]);
  const [status, setStatus] = useState<ConnectionStatus>("disconnected");
  const connectedRef = useRef(false);
  const pendingRef = useRef<EventResponse[]>([]);

  const addEvent = useCallback((event: EventResponse) => {
    setEvents((current) => [event, ...current].slice(0, MAX_EVENTS));
  }, []);

  const flushPending = useCallback(() => {
    const pending = pendingRef.current.splice(0);
    for (const event of pending) {
      addEvent(event);
    }
  }, [addEvent]);

  useEffect(() => {
    if (!enabled || !accessToken) {
      return;
    }

    const socket = new EventsSocket({
      token: accessToken,
      onEvent: (event) => {
        if (!connectedRef.current) {
          pendingRef.current.push(event);
          return;
        }
        addEvent(event);
      },
      onStatusChange: (nextStatus) => {
        connectedRef.current = nextStatus === "connected";
        setStatus(nextStatus);
        if (nextStatus === "connected") {
          flushPending();
          for (const event of socket.drainBuffer()) {
            addEvent(event);
          }
        }
      },
    });

    socket.connect();
    return () => {
      connectedRef.current = false;
      socket.disconnect();
    };
  }, [enabled, accessToken, addEvent, flushPending]);

  const setInitialEvents = useCallback((initial: EventResponse[]) => {
    setEvents(initial.slice(0, MAX_EVENTS));
  }, []);

  return { events, status, setInitialEvents };
}
