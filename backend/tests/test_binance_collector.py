"""Binance collector tests."""

import json
from datetime import UTC, datetime

from app.collectors.binance import parse_ticker_message

SAMPLE_TICKER = {
    "stream": "btcusdt@ticker",
    "data": {
        "e": "24hrTicker",
        "E": 1_700_000_000_000,
        "s": "BTCUSDT",
        "c": "43250.50",
        "P": "2.35",
    },
}


def test_parse_ticker_message_returns_event_create() -> None:
    """Parse sample Binance ticker JSON into EventCreate fields."""
    message = json.dumps(SAMPLE_TICKER)
    event = parse_ticker_message(message, ["BTC", "ETH"])
    assert event is not None
    assert event.source == "binance"
    assert event.event_type == "price"
    assert event.symbol == "BTC"
    assert event.payload["price"] == 43250.50
    assert event.payload["currency"] == "USD"
    assert event.payload["change_24h_pct"] == 2.35
    assert event.metadata["asset_class"] == "crypto"
    assert event.metadata["collector"] == "binance"
    assert event.timestamp == datetime.fromtimestamp(1_700_000_000_000 / 1000, tz=UTC)


def test_parse_ticker_message_ignores_unconfigured_symbol() -> None:
    """Symbols outside the configured list are skipped."""
    message = json.dumps(
        {
            "stream": "solusdt@ticker",
            "data": {"s": "SOLUSDT", "c": "100", "P": "1.0", "E": 1},
        }
    )
    assert parse_ticker_message(message, ["BTC", "ETH"]) is None


def test_parse_ticker_message_handles_bytes() -> None:
    """Parser accepts bytes payloads from the websocket client."""
    message = json.dumps(SAMPLE_TICKER).encode()
    event = parse_ticker_message(message, ["BTC"])
    assert event is not None
    assert event.symbol == "BTC"
