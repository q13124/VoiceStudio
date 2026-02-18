"""Piper engine adapter plugin."""

from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

from adapter import PiperEngineAdapter
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.engines.engine_registry import register_engine
from app.core.plugins_api import Plugin


class SynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    language: str = "en"
    voice: Optional[str] = None
    options: Optional[dict[str, Any]] = None


class SynthesizeResponse(BaseModel):
    ok: bool
    sample_rate: Optional[int] = None
    samples: Optional[list[float]] = None
    message: Optional[str] = None


class PiperEnginePlugin(Plugin):
    """Plugin adapter for the Piper fast-inference TTS engine.

    Wraps :class:`PiperEngineAdapter` and registers the engine in the
    global engine registry on initialization.  Exposes ``POST /synthesize``,
    ``GET /voices``, and ``GET /health``.
    """

    def __init__(self, plugin_dir: Path):
        super().__init__(plugin_dir)
        self._adapter = PiperEngineAdapter()
        self.router = APIRouter(prefix="/api/plugin/engine_piper", tags=["engine_piper"])

    def register(self, app) -> None:
        self.router.post("/synthesize")(self.synthesize)
        self.router.get("/voices")(self.voices)
        self.router.get("/health")(self.health)
        app.include_router(self.router)

    def initialize(self) -> None:
        if self._adapter.initialize():
            mod = importlib.import_module("app.core.engines.piper_engine")
            engine_cls = mod.PiperEngine
            register_engine("piper_plugin_adapter", engine_cls, {"source": "plugin"})
            super().initialize()

    def cleanup(self) -> None:
        self._adapter.cleanup()
        super().cleanup()

    async def synthesize(self, request: SynthesizeRequest) -> SynthesizeResponse:
        audio = self._adapter.synthesize(
            text=request.text,
            language=request.language,
            voice=request.voice,
            options=request.options,
        )
        if audio is None:
            return SynthesizeResponse(ok=False, message="Synthesis failed")
        return SynthesizeResponse(ok=True, sample_rate=self._adapter.sample_rate, samples=audio.tolist())

    async def voices(self):
        return self._adapter.list_voices()

    async def health(self):
        return self._adapter.health()


def register(app, plugin_dir: Path):
    try:
        plugin = PiperEnginePlugin(plugin_dir)
        plugin.register(app)
        plugin.initialize()
        return plugin
    except Exception as e:
        logger.exception("Failed to register plugin %s: %s", plugin_dir.name, e)
        raise
