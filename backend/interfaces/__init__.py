"""
Backend Interfaces Layer.

This package defines abstract interfaces (ports) for the backend services,
following Clean Architecture principles. Routes and application code should
depend on these interfaces, not on concrete implementations.

Architecture Pattern:
    Routes → Interfaces (Ports) ← Adapters ← Concrete Engines

Benefits:
    - Decouples routes from engine implementations
    - Enables dependency injection and testing
    - Allows swapping implementations without changing routes
    - Supports the Dependency Inversion Principle (DIP)
"""

from backend.interfaces.engine_port import (
    IEnginePort,
    ISynthesisEngine,
    ITranscriptionEngine,
    IVoiceConversionEngine,
    IEmotionEngine,
    ITranslationEngine,
    EngineCapability,
    EngineStatus,
)

__all__ = [
    "IEnginePort",
    "ISynthesisEngine",
    "ITranscriptionEngine",
    "IVoiceConversionEngine",
    "IEmotionEngine",
    "ITranslationEngine",
    "EngineCapability",
    "EngineStatus",
]
