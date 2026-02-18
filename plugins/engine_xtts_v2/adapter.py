"""XTTS adapter wrapping the existing XTTS engine implementation."""

from __future__ import annotations

import importlib
from typing import Any, Optional

import numpy as np


class XttsEngineAdapter:
    """Adapter wrapping the XTTS v2 engine for plugin-based synthesis."""

    #: Native output sample rate for XTTS v2.
    SAMPLE_RATE: int = 22050

    def __init__(self, engine_cls=None) -> None:
        if engine_cls is None:
            module = importlib.import_module("app.core.engines.xtts_engine")
            engine_cls = module.XTTSEngine
        self._engine = engine_cls()

    @property
    def sample_rate(self) -> int:
        """Return the engine's native output sample rate."""
        return getattr(self._engine, "sample_rate", self.SAMPLE_RATE)

    def initialize(self) -> bool:
        return bool(self._engine.initialize())

    def cleanup(self) -> None:
        self._engine.cleanup()

    def synthesize(
        self,
        text: str,
        reference_audio: str,
        language: str = "en",
        options: Optional[dict[str, Any]] = None,
    ) -> Optional[np.ndarray]:
        opts = options or {}
        result = self._engine.synthesize(
            text=text,
            speaker_wav=reference_audio,
            language=language,
            **opts,
        )
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
