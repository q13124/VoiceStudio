"""
Base Adapter.

Task 3.2.4: Port/adapter pattern for external services.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class Adapter(ABC):
    """
    Base class for infrastructure adapters.

    Adapters bridge domain/application layers to
    external infrastructure (databases, APIs, etc.).
    """

    def __init__(self, name: str | None = None):
        """
        Initialize adapter.

        Args:
            name: Adapter name for logging
        """
        self._name = name or self.__class__.__name__
        self._connected = False
        self._logger = logging.getLogger(f"infrastructure.{self._name}")

    @property
    def name(self) -> str:
        """Get adapter name."""
        return self._name

    @property
    def is_connected(self) -> bool:
        """Check if adapter is connected."""
        return self._connected

    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the external service.

        Returns:
            True if connected successfully
        """
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from the external service.

        Returns:
            True if disconnected successfully
        """
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """
        Check health of the external service.

        Returns:
            Health status dict
        """
        pass

    async def __aenter__(self) -> Adapter:
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect()
