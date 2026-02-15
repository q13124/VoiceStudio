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
    EngineCapability,
    EngineStatus,
    IEmotionEngine,
    IEnginePort,
    ISynthesisEngine,
    ITranscriptionEngine,
    ITranslationEngine,
    IVoiceConversionEngine,
)

__all__ = [
    "EngineCapability",
    "EngineStatus",
    "IEmotionEngine",
    "IEnginePort",
    "ISynthesisEngine",
    "ITranscriptionEngine",
    "ITranslationEngine",
    "IVoiceConversionEngine",
]
