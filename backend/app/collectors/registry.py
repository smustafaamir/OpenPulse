"""Collector registry for config-driven enablement."""

import logging

from app.collectors.base import BaseCollector
from app.collectors.binance import BinanceCollector
from app.collectors.mock import MockCollector
from app.core.config import Settings

logger = logging.getLogger(__name__)

_COLLECTOR_FACTORIES: dict[str, type[BaseCollector]] = {
    "mock": MockCollector,
    "binance": BinanceCollector,
}


class CollectorRegistry:
    """Resolve enabled collectors from application settings."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def get_enabled(self) -> list[BaseCollector]:
        """Return instantiated collectors for configured names."""
        collectors: list[BaseCollector] = []
        for name in self._settings.collector_list:
            factory = _COLLECTOR_FACTORIES.get(name)
            if factory is None:
                logger.warning("Unknown collector %r — skipping", name)
                continue
            if name == "binance":
                collectors.append(BinanceCollector(self._settings))
            else:
                collectors.append(factory())
        if not collectors:
            msg = "No valid collectors enabled; check COLLECTORS setting"
            raise RuntimeError(msg)
        return collectors
