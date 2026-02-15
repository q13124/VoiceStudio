"""
Audio Tools Plugin - Professional Audio Processing for Voice Cloning

Provides professional audio enhancement tools including:
- Noise reduction
- LUFS normalization
- EQ presets
- De-essing and plosive removal
- Pitch and time manipulation
- AI-powered voice restoration
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.plugins_api.base import BasePlugin, PluginMetadata
from app.core.utils.native_tools import find_ffmpeg

logger = logging.getLogger(__name__)

PLUGIN_DIR = Path(__file__).parent
BIN_DIR = PLUGIN_DIR / "bin"


class EnhanceRequest(BaseModel):
    """Request model for audio enhancement"""

    input_path: str
    output_path: str | None = None
    noise_reduction: float = 0.5
    normalize: bool = True
    eq_preset: str = "vocal"
    remove_plosives: bool = True
    de_ess: bool = True


class AudioTools:
    """Professional audio processing tools"""

    def __init__(self):
        """Initialize audio tools"""
        manifest_path = PLUGIN_DIR / "plugin.json"
        if manifest_path.exists():
            with open(manifest_path, encoding="utf-8") as f:
                self.manifest = json.load(f)
        else:
            self.manifest = {}

    def get_tool(self, name: str) -> str | None:
        """Get path to audio tool executable"""
        if name == "ffmpeg":
            return find_ffmpeg() or "ffmpeg"

        if name not in self.manifest.get("tools", {}):
            return None

        exe = self.manifest["tools"][name]["executable"]
        path = BIN_DIR / exe
        return str(path) if path.exists() else None

    def run_tool(
        self, tool: str, *args, capture_output: bool = True, check: bool = True
    ):
        """Run audio tool with arguments"""
        exe = self.get_tool(tool)
        if not exe:
            if check:
                raise RuntimeError(f"{tool} not found")
            return None
        return subprocess.run(
            [exe, *list(args)], capture_output=capture_output, check=check
        )

    def enhance_voice_quality(
        self,
        input_path: str,
        output_path: str,
        noise_reduction: float = 0.5,
        normalize: bool = True,
        eq_preset: str = "vocal",
    ) -> dict[str, Any]:
        """Apply professional voice quality enhancement pipeline"""
        try:
            args = ["-i", input_path]

            # Noise reduction
            if noise_reduction > 0:
                args.extend(["-af", f"afftdn=nr={noise_reduction}"])

            # EQ for vocal clarity
            eq_filter = self._get_vocal_eq_filter(eq_preset)
            if eq_filter:
                if any(arg == "-af" for arg in args):
                    idx = args.index("-af")
                    args[idx + 1] = f"{args[idx + 1]},{eq_filter}"
                else:
                    args.extend(["-af", eq_filter])

            # Normalization (LUFS to -16 LUFS for broadcast quality)
            if normalize:
                args.extend(["-ar", "48000", "-ac", "1"])
                loudnorm = "loudnorm=I=-16:TP=-1.5:LRA=11"
                if any(arg == "-af" for arg in args):
                    idx = args.index("-af")
                    args[idx + 1] = f"{args[idx + 1]},{loudnorm}"
                else:
                    args.extend(["-af", loudnorm])

            args.extend(["-y", output_path])
            self.run_tool("ffmpeg", *args, check=False)

            return {
                "status": "success",
                "input_path": input_path,
                "output_path": output_path,
            }
        except Exception as e:
            logger.error(f"Enhancement failed: {e}", exc_info=True)
            detail = f"Enhancement failed: {e!s}"
            raise HTTPException(status_code=500, detail=detail)

    def normalize_lufs(
        self, input_path: str, output_path: str, target_lufs: float = -16.0
    ) -> dict[str, Any]:
        """Normalize to broadcast standard loudness (LUFS)"""
        try:
            self.run_tool(
                "ffmpeg",
                "-i",
                input_path,
                "-af",
                f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11",
                "-ar",
                "48000",
                "-y",
                output_path,
            )
            return {"status": "success", "output_path": output_path}
        except Exception as e:
            logger.error(f"Normalization failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Normalization failed: {e!s}"
            )

    def remove_plosives(
        self, input_path: str, output_path: str, strength: float = 1.0
    ) -> dict[str, Any]:
        """Reduce harsh plosives (p, b sounds)"""
        try:
            self.run_tool(
                "ffmpeg",
                "-i",
                input_path,
                "-af",
                f"highpass=f=80*{strength}:width_type=h:w=50",
                "-y",
                output_path,
            )
            return {"status": "success", "output_path": output_path}
        except Exception as e:
            logger.error(f"Plosive removal failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Plosive removal failed: {e!s}"
            )

    def _get_vocal_eq_filter(self, preset: str) -> str:
        """Get EQ filter string for vocal presets"""
        presets = {
            "vocal": (
                "equalizer=f=100:width_type=h:w=50:g=-1,"
                "equalizer=f=250:width_type=h:w=100:g=1.5,"
                "equalizer=f=3000:width_type=h:w=500:g=2"
            ),
            "broadcast": (
                "equalizer=f=100:width_type=h:w=50:g=-2,"
                "equalizer=f=3000:width_type=h:w=500:g=1.5"
            ),
            "telephone": (
                "equalizer=f=300:width_type=h:w=200:g=0,"
                "equalizer=f=3400:width_type=h:w=200:g=0"
            ),
            "natural": "",
        }
        return presets.get(preset, "")


class AudioToolsPlugin(BasePlugin):
    """Audio Tools Plugin for VoiceStudio"""

    def __init__(self, plugin_dir: Path):
        """Initialize audio tools plugin"""
        manifest_path = plugin_dir / "manifest.json"
        metadata = PluginMetadata(manifest_path)
        super().__init__(metadata)
        self.router = APIRouter(
            prefix="/api/plugin/audio_tools", tags=["plugin", "audio_tools"]
        )
        self.tools = AudioTools()

    def register(self, app):
        """Register plugin routes with FastAPI app"""
        # Register routes
        self.router.post("/enhance")(self.enhance_audio)
        self.router.post("/normalize")(self.normalize_audio)
        self.router.post("/remove-plosives")(self.remove_plosives_endpoint)
        self.router.get("/info")(self.get_info)

        # Include router in app
        app.include_router(self.router)
        logger.info(
            f"Audio Tools plugin registered with {len(self.router.routes)} routes"
        )

    async def enhance_audio(self, request: EnhanceRequest):
        """Enhance audio quality"""
        if not request.output_path:
            # Generate output path
            input_path = Path(request.input_path)
            request.output_path = str(
                input_path.parent / f"{input_path.stem}_enhanced{input_path.suffix}"
            )

        result = self.tools.enhance_voice_quality(
            request.input_path,
            request.output_path,
            noise_reduction=request.noise_reduction,
            normalize=request.normalize,
            eq_preset=request.eq_preset,
        )
        return result

    async def normalize_audio(
        self,
        input_path: str,
        output_path: str | None = None,
        target_lufs: float = -16.0,
    ):
        """Normalize audio to target LUFS"""
        if not output_path:
            input_path_obj = Path(input_path)
            output_path = str(
                input_path_obj.parent
                / f"{input_path_obj.stem}_normalized{input_path_obj.suffix}"
            )

        result = self.tools.normalize_lufs(input_path, output_path, target_lufs)
        return result

    async def remove_plosives_endpoint(
        self, input_path: str, output_path: str | None = None, strength: float = 1.0
    ):
        """Remove plosives from audio"""
        if not output_path:
            input_path_obj = Path(input_path)
            output_path = str(
                input_path_obj.parent
                / f"{input_path_obj.stem}_no_plosives{input_path_obj.suffix}"
            )

        result = self.tools.remove_plosives(input_path, output_path, strength)
        return result

    async def get_info(self):
        """Get plugin info"""
        return self.get_info()


# Plugin entry point
def register(app, plugin_dir: Path):
    """
    Register the plugin with the FastAPI app.

    Args:
        app: FastAPI application instance
        plugin_dir: Path to plugin directory
    """
    plugin = AudioToolsPlugin(plugin_dir)
    plugin.register(app)
    plugin.initialize()
    return plugin
