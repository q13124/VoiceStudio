"""XTTS v2 engine adapter plugin."""

from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import Any, Optional

from adapter import XttsEngineAdapter
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.engines.engine_registry import register_engine
from app.core.plugins_api import Plugin

logger = logging.getLogger(__name__)


class SynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    reference_audio: str = Field(..., min_length=1)
    language: str = "en"
    options: Optional[dict[str, Any]] = None


class SynthesizeResponse(BaseModel):
    ok: bool
    sample_rate: Optional[int] = None
    samples: Optional[list[float]] = None
    message: Optional[str] = None


class XttsEnginePlugin(Plugin):
    """Plugin adapter for the XTTS v2 voice-cloning TTS engine.

    Wraps :class:`XttsEngineAdapter` and registers the engine in the
    global engine registry on initialization.  Exposes ``POST /synthesize``,
    ``GET /voices``, and ``GET /health``.
    """

    def __init__(self, plugin_dir: Path):
        super().__init__(plugin_dir)
        self._adapter = XttsEngineAdapter()
        self.router = APIRouter(prefix="/api/plugin/engine_xtts_v2", tags=["engine_xtts_v2"])

    def register(self, app) -> None:
        self.router.post("/synthesize")(self.synthesize)
        self.router.get("/voices")(self.voices)
        self.router.get("/health")(self.health)
        app.include_router(self.router)

    def initialize(self) -> None:
        if self._adapter.initialize():
            mod = importlib.import_module("app.core.engines.xtts_engine")
            engine_cls = mod.XTTSEngine
            register_engine("xtts_plugin_adapter", engine_cls, {"source": "plugin"})
            super().initialize()

    def cleanup(self) -> None:
        self._adapter.cleanup()
        super().cleanup()

    async def synthesize(self, request: SynthesizeRequest) -> SynthesizeResponse:
        audio = self._adapter.synthesize(
            text=request.text,
            reference_audio=request.reference_audio,
            language=request.language,
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
        plugin = XttsEnginePlugin(plugin_dir)
        plugin.register(app)
        plugin.initialize()
        return plugin
    except Exception as e:
        logger.exception("Failed to register plugin %s: %s", plugin_dir.name, e)
        raise
