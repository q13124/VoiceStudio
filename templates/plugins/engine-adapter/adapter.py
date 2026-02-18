"""Engine adapter template."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

# Replace with your concrete engine class import.
from app.core.engines.protocols import EngineProtocol


class EngineAdapter:
    """Thin adapter that wraps an existing EngineProtocol implementation.

    Override ``SAMPLE_RATE`` with the engine's native output sample rate.
    """

    #: Default output sample rate; override per-engine.
    SAMPLE_RATE: int = 22050

    def __init__(self, engine: EngineProtocol):
        self._engine = engine

    @property
    def sample_rate(self) -> int:
        """Return the engine's native output sample rate."""
        return getattr(self._engine, "sample_rate", self.SAMPLE_RATE)

    def initialize(self) -> bool:
        return bool(self._engine.initialize())

    def cleanup(self) -> None:
        self._engine.cleanup()

    def synthesize(self, text: str, **kwargs: Any) -> np.ndarray | None:
        result = self._engine.synthesize(text=text, **kwargs)
        if isinstance(result, tuple):
            return result[0]
        return result

    def list_voices(self) -> list[dict[str, Any]]:
        """Return available voices from the engine, or an empty list."""
        if hasattr(self._engine, "list_voices"):
            return self._engine.list_voices()
        return []

    def health(self) -> dict[str, Any]:
        if hasattr(self._engine, "health_check"):
            return self._engine.health_check()
        return {"status": "unknown"}
