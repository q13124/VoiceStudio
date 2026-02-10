"""
Backend Adapters Layer.

This package contains adapters that bridge the interface layer (ports)
to concrete implementations (engines, services).

Architecture Pattern:
    Routes → Interfaces (Ports) ← Adapters ← Concrete Engines

The adapters implement the port interfaces and delegate to the actual
engine implementations, providing:
- Dependency injection
- Lazy loading
- Error handling and graceful degradation
- Caching and resource management
"""

from backend.adapters.engine_adapter import (
    EngineAdapter,
    get_engine_service,
)

__all__ = [
    "EngineAdapter",
    "get_engine_service",
]
