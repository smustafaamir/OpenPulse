"""Binance spot ticker collector."""

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from datetime import UTC, datetime

import websockets

from app.collectors.base import BaseCollector
from app.core.config import Settings
from app.schemas.event import EventCreate

logger = logging.getLogger(__name__)

MAX_BACKOFF_SECONDS = 30
INITIAL_BACKOFF_SECONDS = 1


def symbol_to_stream(symbol: str) -> str:
    """Map base symbol to Binance combined stream name."""
    return f"{symbol.lower()}usdt@ticker"


def parse_ticker_message(
    message: str | bytes, symbols: list[str]
) -> EventCreate | None:
    """Parse a Binance combined-stream ticker message into an EventCreate."""
    if isinstance(message, bytes):
        message = message.decode()
    payload = json.loads(message)
    data = payload.get("data", payload)
    if not isinstance(data, dict):
        return None

    pair = str(data.get("s", "")).upper()
    if not pair.endswith("USDT"):
        return None

    base_symbol = pair.removesuffix("USDT")
    if base_symbol not in symbols:
        return None

    last_price = float(data["c"])
    change_pct = float(data.get("P", 0))
    event_time_ms = int(data.get("E", 0))
    timestamp = (
        datetime.fromtimestamp(event_time_ms / 1000, tz=UTC)
        if event_time_ms
        else datetime.now(UTC)
    )

    return EventCreate(
        source="binance",
        event_type="price",
        symbol=base_symbol,
        timestamp=timestamp,
        importance=3,
        payload={
            "price": last_price,
            "currency": "USD",
            "pair": pair,
            "change_24h_pct": change_pct,
        },
        metadata={
            "collector": "binance",
            "stream": symbol_to_stream(base_symbol),
            "asset_class": "crypto",
            "display_symbol": base_symbol,
        },
    )


class BinanceCollector(BaseCollector):
    """Stream spot ticker prices from Binance."""

    source = "binance"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._symbols = settings.binance_symbol_list

    def _stream_url(self) -> str:
        """Build combined stream WebSocket URL."""
        streams = "/".join(symbol_to_stream(symbol) for symbol in self._symbols)
        base = self._settings.binance_ws_url.rstrip("/")
        if "stream?" in base:
            return f"{base}streams={streams}"
        return f"{base}?streams={streams}"

    async def collect(self) -> AsyncIterator[EventCreate]:
        """Yield ticker events with reconnect backoff."""
        backoff = INITIAL_BACKOFF_SECONDS
        while True:
            try:
                async for event in self._consume_stream():
                    yield event
                    backoff = INITIAL_BACKOFF_SECONDS
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception(
                    "Binance collector error; reconnecting in %ss", backoff
                )
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, MAX_BACKOFF_SECONDS)

    async def _consume_stream(self) -> AsyncIterator[EventCreate]:
        """Connect and yield parsed events until disconnect."""
        url = self._stream_url()
        logger.info("Connecting to Binance stream: %s", url)
        async with websockets.connect(url, ping_interval=20, ping_timeout=20) as ws:
            async for message in ws:
                event = parse_ticker_message(message, self._symbols)
                if event is not None:
                    yield event
