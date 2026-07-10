"""Collector registry tests."""

import pytest

from app.collectors.binance import BinanceCollector
from app.collectors.mock import MockCollector
from app.collectors.registry import CollectorRegistry
from app.core.config import Settings, get_settings


def _settings(**overrides: str) -> Settings:
    base = {
        "database_url": "postgresql+asyncpg://openpulse:openpulse@localhost:5432/openpulse",
        "redis_url": "redis://localhost:6379/0",
        "jwt_secret": "test-secret",
    }
    base.update(overrides)
    return Settings(**base)


def test_registry_mock_only() -> None:
    """COLLECTORS=mock enables a single collector."""
    registry = CollectorRegistry(_settings(collectors="mock"))
    collectors = registry.get_enabled()
    assert len(collectors) == 1
    assert isinstance(collectors[0], MockCollector)


def test_registry_mock_and_binance() -> None:
    """COLLECTORS=mock,binance enables both collectors."""
    registry = CollectorRegistry(_settings(collectors="mock,binance"))
    collectors = registry.get_enabled()
    assert len(collectors) == 2
    assert isinstance(collectors[0], MockCollector)
    assert isinstance(collectors[1], BinanceCollector)


def test_registry_ignores_unknown_collector() -> None:
    """Unknown collector names are skipped."""
    registry = CollectorRegistry(_settings(collectors="mock,unknown,binance"))
    collectors = registry.get_enabled()
    assert len(collectors) == 2
    assert {c.source for c in collectors} == {"mock", "binance"}


def test_registry_raises_when_no_valid_collectors() -> None:
    """Empty collector list after filtering raises at startup."""
    registry = CollectorRegistry(_settings(collectors="unknown,also-unknown"))
    with pytest.raises(RuntimeError, match="No valid collectors"):
        registry.get_enabled()


def test_collector_list_dedupes_and_lowercases() -> None:
    """collector_list normalizes configured names."""
    get_settings.cache_clear()
    settings = _settings(collectors=" Mock ,BINANCE,mock ")
    assert settings.collector_list == ["mock", "binance"]
