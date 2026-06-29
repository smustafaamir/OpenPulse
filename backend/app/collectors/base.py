"""Collector base interface."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.schemas.event import EventCreate


class BaseCollector(ABC):
    """Abstract data collector that yields events."""

    source: str

    @abstractmethod
    def collect(self) -> AsyncIterator[EventCreate]:
        """Yield events without touching the database."""
        raise NotImplementedError
