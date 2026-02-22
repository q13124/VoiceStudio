"""
Engine Registry

Centralized registry of all available engines for easy discovery and management.
"""

from __future__ import annotations

import importlib
import logging

from .protocols import EngineProtocol

logger = logging.getLogger(__name__)


class EngineRegistry:
    """
    Centralized registry for all engines.

    Provides discovery, loading, and management of engines.
    """

    def __init__(self):
        """Initialize engine registry."""
        self._engines: dict[str, type[EngineProtocol]] = {}
        self._engine_metadata: dict[str, dict] = {}

    def register_engine(
        self,
        name: str,
        engine_class: type[EngineProtocol],
        metadata: dict | None = None,
    ):
        """
        Register an engine.

        Args:
            name: Engine name
            engine_class: Engine class
            metadata: Optional metadata (description, capabilities, etc.)
        """
        if not issubclass(engine_class, EngineProtocol):
            raise TypeError("Engine class must inherit from EngineProtocol")

        self._engines[name] = engine_class
        self._engine_metadata[name] = metadata or {}

        logger.info(f"Registered engine: {name}")

    def get_engine_class(self, name: str) -> type[EngineProtocol] | None:
        """
        Get engine class by name.

        Args:
            name: Engine name

        Returns:
            Engine class or None
        """
        return self._engines.get(name)

    def list_engines(self) -> list[str]:
        """
        List all registered engine names.

        Returns:
            List of engine names
        """
        return list(self._engines.keys())

    def get_engine_metadata(self, name: str) -> dict:
        """
        Get engine metadata.

        Args:
            name: Engine name

        Returns:
            Metadata dictionary
        """
        return self._engine_metadata.get(name, {})

    def discover_engines_from_module(self, module_name: str = "app.core.engines"):
        """
        Automatically discover and register engines from module.

        Args:
            module_name: Module to search for engines
        """
        try:
            module = importlib.import_module(module_name)

            # Look for engine classes
            for name in dir(module):
                obj = getattr(module, name)
                if (
                    isinstance(obj, type)
                    and issubclass(obj, EngineProtocol)
                    and obj != EngineProtocol
                ):
                    # Extract engine name from class name
                    engine_name = name.lower().replace("engine", "").replace("_", "")
                    self.register_engine(engine_name, obj)

        except Exception as e:
            logger.error(f"Failed to discover engines from {module_name}: {e}")

    def get_all_engines(self) -> dict[str, type[EngineProtocol]]:
        """
        Get all registered engines.

        Returns:
            Dictionary of engine names to classes
        """
        return self._engines.copy()


# Global registry instance
_global_registry = EngineRegistry()


def get_engine_registry() -> EngineRegistry:
    """Get global engine registry."""
    return _global_registry


def register_engine(name: str, engine_class: type[EngineProtocol], metadata: dict | None = None):
    """Register an engine in the global registry."""
    _global_registry.register_engine(name, engine_class, metadata)


def list_all_engines() -> list[str]:
    """List all registered engines."""
    return _global_registry.list_engines()


# Export
__all__ = [
    "EngineRegistry",
    "get_engine_registry",
    "list_all_engines",
    "register_engine",
]
