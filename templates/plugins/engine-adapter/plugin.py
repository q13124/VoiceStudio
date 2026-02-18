"""Engine adapter plugin template."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from adapter import EngineAdapter
from app.core.plugins_api import Plugin

logger = logging.getLogger(__name__)


class SynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    language: str = "en"
    reference_audio: Optional[str] = None
    options: Optional[dict[str, Any]] = None


class SynthesizeResponse(BaseModel):
    ok: bool
    sample_rate: Optional[int] = None
    samples: Optional[list[float]] = None
    message: Optional[str] = None


class {{CLASS_NAME}}EnginePlugin(Plugin):
    """Plugin adapter for the {{DISPLAY_NAME}} engine.

    Wraps :class:`EngineAdapter` and exposes ``POST /synthesize``,
    ``GET /voices``, and ``GET /health`` endpoints.
    """

    def __init__(self, plugin_dir: Path):
        super().__init__(plugin_dir)
        self._adapter = EngineAdapter()
        self.router = APIRouter(prefix="/api/plugin/{{PLUGIN_NAME}}", tags=["{{PLUGIN_NAME}}"])

    def register(self, app) -> None:
        self.router.post("/synthesize")(self.synthesize)
        self.router.get("/voices")(self.voices)
        self.router.get("/health")(self.health)
        app.include_router(self.router)

    def initialize(self) -> None:
        if self._adapter.initialize():
            super().initialize()

    def cleanup(self) -> None:
        self._adapter.cleanup()
        super().cleanup()

    async def synthesize(self, request: SynthesizeRequest) -> SynthesizeResponse:
        audio = self._adapter.synthesize(
            text=request.text,
            language=request.language,
            reference_audio=request.reference_audio,
            **(request.options or {}),
        )
        if audio is None:
            return SynthesizeResponse(ok=False, message="Synthesis failed")
        return SynthesizeResponse(
            ok=True,
            sample_rate=self._adapter.sample_rate,
            samples=audio.tolist(),
        )

    async def voices(self):
        return self._adapter.list_voices()

    async def health(self):
        return self._adapter.health()


def register(app, plugin_dir: Path):
    """Plugin entry point called by the plugin loader."""
    try:
        plugin = {{CLASS_NAME}}EnginePlugin(plugin_dir)
        plugin.register(app)
        plugin.initialize()
        return plugin
    except Exception as e:
        logger.exception("Failed to register plugin %s: %s", plugin_dir.name, e)
        raise
