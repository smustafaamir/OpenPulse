"""Mock data collector for local development."""

import asyncio
import random
from collections.abc import AsyncIterator
from datetime import UTC, datetime

from app.collectors.base import BaseCollector
from app.schemas.event import EventCreate

SYMBOLS = ("BTC", "ETH", "SPY", "NVDA")
EVENT_TYPES = ("price", "volume")
CRYPTO_SYMBOLS = frozenset({"BTC", "ETH"})


def _asset_class(symbol: str) -> str:
    """Return asset class metadata for a mock symbol."""
    return "crypto" if symbol in CRYPTO_SYMBOLS else "equity"


class MockCollector(BaseCollector):
    """Generate random market-like events every second."""

    source = "mock"

    async def collect(self) -> AsyncIterator[EventCreate]:
        """Yield one random event per second indefinitely."""
        while True:
            symbol = random.choice(SYMBOLS)
            event_type = random.choice(EVENT_TYPES)
            if event_type == "price":
                payload = {
                    "price": round(random.uniform(10, 100_000), 2),
                    "currency": "USD",
                    "change_24h_pct": round(random.uniform(-5, 5), 2),
                }
            else:
                payload = {"volume": round(random.uniform(100, 1_000_000), 2)}
            yield EventCreate(
                source=self.source,
                event_type=event_type,
                symbol=symbol,
                timestamp=datetime.now(UTC),
                importance=random.randint(1, 5),
                payload=payload,
                metadata={
                    "collector": "mock",
                    "asset_class": _asset_class(symbol),
                    "display_symbol": symbol,
                },
            )
            await asyncio.sleep(1)
