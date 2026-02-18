"""
Example Audio Effect Plugin for VoiceStudio

This plugin demonstrates the unified plugin architecture with:
- Audio effect processing (normalize, amplify, fade, trim)
- Permission-based security model
- Plugin settings and configuration
- Health checks and lifecycle management

Phase 1 Reference Implementation
"""

import asyncio
import io
import logging
import os
import struct
import tempfile
import wave
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field

from app.core.plugins_api.base import BasePlugin, PluginMetadata

logger = logging.getLogger(__name__)


# ============================================================================
# Models
# ============================================================================

class EffectType(str, Enum):
    """Available audio effect types."""
    NORMALIZE = "normalize"
    AMPLIFY = "amplify"
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    TRIM = "trim"
    SILENCE_DETECTION = "silence_detection"


class EffectRequest(BaseModel):
    """Request model for applying an audio effect."""
    effect: EffectType
    parameters: Dict[str, Any] = Field(default_factory=dict)


class EffectResult(BaseModel):
    """Result of applying an audio effect."""
    success: bool
    effect: str
    message: str
    output_path: Optional[str] = None
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PluginSettings(BaseModel):
    """Plugin configuration settings."""
    default_normalization_level: float = -3.0
    preserve_original_files: bool = True
    output_format: str = "wav"
    sample_rate: int = 44100


class HealthStatus(BaseModel):
    """Plugin health check response."""
    healthy: bool
    plugin_id: str
    version: str
    uptime_seconds: float
    effects_available: List[str]
    last_operation: Optional[str] = None
    error_count: int = 0


# ============================================================================
# Audio Processing Functions
# ============================================================================

def load_wav(file_path: Path) -> Tuple[np.ndarray, int, int]:
    """
    Load a WAV file and return audio data, sample rate, and channels.
    
    Returns:
        Tuple of (audio_data as float32 normalized, sample_rate, num_channels)
    """
    with wave.open(str(file_path), 'rb') as wav_file:
        n_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sample_rate = wav_file.getframerate()
        n_frames = wav_file.getnframes()
        
        raw_data = wav_file.readframes(n_frames)
        
        # Convert bytes to numpy array based on sample width
        if sample_width == 1:
            dtype = np.uint8
            max_val = 255.0
        elif sample_width == 2:
            dtype = np.int16
            max_val = 32767.0
        elif sample_width == 4:
            dtype = np.int32
            max_val = 2147483647.0
        else:
            raise ValueError(f"Unsupported sample width: {sample_width}")
        
        audio = np.frombuffer(raw_data, dtype=dtype).astype(np.float32)
        
        # Normalize to [-1.0, 1.0]
        if sample_width == 1:
            audio = (audio - 128.0) / 128.0
        else:
            audio = audio / max_val
        
        # Reshape for multi-channel
        if n_channels > 1:
            audio = audio.reshape(-1, n_channels)
        
        return audio, sample_rate, n_channels


def save_wav(file_path: Path, audio: np.ndarray, sample_rate: int, n_channels: int = 1):
    """Save audio data to a WAV file."""
    # Ensure audio is in correct shape
    if audio.ndim == 1 and n_channels > 1:
        audio = audio.reshape(-1, n_channels)
    elif audio.ndim == 2 and n_channels == 1:
        audio = audio.flatten()
    
    # Clip and convert to int16
    audio = np.clip(audio, -1.0, 1.0)
    audio_int = (audio * 32767.0).astype(np.int16)
    
    with wave.open(str(file_path), 'wb') as wav_file:
        wav_file.setnchannels(n_channels)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int.tobytes())


def normalize_audio(audio: np.ndarray, target_db: float = -3.0) -> np.ndarray:
    """
    Normalize audio to target peak level in dB.
    
    Args:
        audio: Input audio array
        target_db: Target peak level in dB (e.g., -3.0)
    
    Returns:
        Normalized audio array
    """
    peak = np.max(np.abs(audio))
    if peak < 1e-6:
        return audio
    
    target_linear = 10 ** (target_db / 20.0)
    gain = target_linear / peak
    
    return audio * gain


def amplify_audio(audio: np.ndarray, gain_db: float) -> np.ndarray:
    """
    Apply gain to audio in dB.
    
    Args:
        audio: Input audio array
        gain_db: Gain in dB (positive = louder, negative = quieter)
    
    Returns:
        Amplified audio array
    """
    gain_linear = 10 ** (gain_db / 20.0)
    return audio * gain_linear


def apply_fade(
    audio: np.ndarray,
    sample_rate: int,
    fade_type: str = "in",
    duration_ms: float = 500.0,
    curve: str = "linear"
) -> np.ndarray:
    """
    Apply fade in or fade out to audio.
    
    Args:
        audio: Input audio array
        sample_rate: Sample rate in Hz
        fade_type: 'in' or 'out'
        duration_ms: Fade duration in milliseconds
        curve: 'linear', 'exponential', or 'logarithmic'
    
    Returns:
        Audio with fade applied
    """
    n_samples = int(sample_rate * duration_ms / 1000.0)
    n_samples = min(n_samples, len(audio))
    
    # Create fade curve
    t = np.linspace(0, 1, n_samples)
    
    if curve == "exponential":
        envelope = t ** 2
    elif curve == "logarithmic":
        envelope = np.sqrt(t)
    else:  # linear
        envelope = t
    
    if fade_type == "out":
        envelope = 1.0 - envelope
    
    # Apply fade
    result = audio.copy()
    
    if fade_type == "in":
        if audio.ndim == 1:
            result[:n_samples] *= envelope
        else:
            result[:n_samples] *= envelope[:, np.newaxis]
    else:  # fade out
        if audio.ndim == 1:
            result[-n_samples:] *= envelope
        else:
            result[-n_samples:] *= envelope[:, np.newaxis]
    
    return result


def trim_audio(
    audio: np.ndarray,
    sample_rate: int,
    start_ms: float = 0.0,
    end_ms: Optional[float] = None
) -> np.ndarray:
    """
    Trim audio to specified time range.
    
    Args:
        audio: Input audio array
        sample_rate: Sample rate in Hz
        start_ms: Start time in milliseconds
        end_ms: End time in milliseconds (None = end of audio)
    
    Returns:
        Trimmed audio array
    """
    start_sample = int(sample_rate * start_ms / 1000.0)
    
    if end_ms is not None:
        end_sample = int(sample_rate * end_ms / 1000.0)
    else:
        end_sample = len(audio)
    
    start_sample = max(0, min(start_sample, len(audio)))
    end_sample = max(start_sample, min(end_sample, len(audio)))
    
    return audio[start_sample:end_sample]


def detect_silence(
    audio: np.ndarray,
    sample_rate: int,
    threshold_db: float = -40.0,
    min_silence_ms: float = 500.0
) -> List[Tuple[float, float]]:
    """
    Detect silent regions in audio.
    
    Args:
        audio: Input audio array
        sample_rate: Sample rate in Hz
        threshold_db: Silence threshold in dB
        min_silence_ms: Minimum silence duration in ms
    
    Returns:
        List of (start_ms, end_ms) tuples for silent regions
    """
    # Convert to mono if stereo
    if audio.ndim == 2:
        mono = np.mean(audio, axis=1)
    else:
        mono = audio
    
    # Calculate amplitude envelope (simple RMS in windows)
    window_size = int(sample_rate * 0.01)  # 10ms windows
    n_windows = len(mono) // window_size
    
    threshold_linear = 10 ** (threshold_db / 20.0)
    min_silence_samples = int(sample_rate * min_silence_ms / 1000.0)
    
    silent_regions = []
    in_silence = False
    silence_start = 0
    
    for i in range(n_windows):
        window = mono[i * window_size:(i + 1) * window_size]
        rms = np.sqrt(np.mean(window ** 2))
        
        if rms < threshold_linear:
            if not in_silence:
                in_silence = True
                silence_start = i * window_size
        else:
            if in_silence:
                silence_end = i * window_size
                if (silence_end - silence_start) >= min_silence_samples:
                    start_ms = silence_start / sample_rate * 1000.0
                    end_ms = silence_end / sample_rate * 1000.0
                    silent_regions.append((start_ms, end_ms))
                in_silence = False
    
    # Check for trailing silence
    if in_silence:
        silence_end = len(mono)
        if (silence_end - silence_start) >= min_silence_samples:
            start_ms = silence_start / sample_rate * 1000.0
            end_ms = silence_end / sample_rate * 1000.0
            silent_regions.append((start_ms, end_ms))
    
    return silent_regions


# ============================================================================
# Plugin Implementation
# ============================================================================

class ExampleAudioEffectPlugin(BasePlugin):
    """Example audio effect plugin implementation."""

    def __init__(self, plugin_dir: Path):
        """Initialize the plugin."""
        manifest_path = plugin_dir / "manifest.json"
        metadata = PluginMetadata(manifest_path)
        super().__init__(metadata)
        
        self.plugin_dir = plugin_dir
        self.router = APIRouter(
            prefix="/api/plugin/example_audio_effect",
            tags=["plugin", "audio", "effects"]
        )
        self.settings = PluginSettings()
        self._start_time = asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0
        self._last_operation: Optional[str] = None
        self._error_count = 0

    def register(self, app):
        """Register plugin routes with FastAPI app."""
        # Register effect endpoints
        self.router.post("/apply", response_model=EffectResult)(self.apply_effect)
        self.router.post("/normalize", response_model=EffectResult)(self.normalize)
        self.router.post("/amplify", response_model=EffectResult)(self.amplify)
        self.router.post("/fade", response_model=EffectResult)(self.fade)
        self.router.post("/trim", response_model=EffectResult)(self.trim)
        self.router.post("/detect-silence")(self.detect_silence_endpoint)
        
        # Info endpoints
        self.router.get("/info")(self.info)
        self.router.get("/health", response_model=HealthStatus)(self.health_check)
        self.router.get("/effects")(self.list_effects)
        self.router.get("/settings", response_model=PluginSettings)(self.get_settings)
        self.router.put("/settings", response_model=PluginSettings)(self.update_settings)
        
        app.include_router(self.router)
        logger.info(f"ExampleAudioEffect plugin registered with {len(self.router.routes)} routes")

    async def apply_effect(self, request: EffectRequest):
        """Apply a generic effect based on the request."""
        effect_handlers = {
            EffectType.NORMALIZE: self._apply_normalize,
            EffectType.AMPLIFY: self._apply_amplify,
            EffectType.FADE_IN: self._apply_fade_in,
            EffectType.FADE_OUT: self._apply_fade_out,
            EffectType.TRIM: self._apply_trim,
            EffectType.SILENCE_DETECTION: self._apply_silence_detection,
        }
        
        handler = effect_handlers.get(request.effect)
        if not handler:
            raise HTTPException(status_code=400, detail=f"Unknown effect: {request.effect}")
        
        try:
            result = await handler(request.parameters)
            self._last_operation = request.effect.value
            return result
        except Exception as e:
            self._error_count += 1
            logger.exception(f"Error applying effect {request.effect}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def normalize(
        self,
        file: UploadFile = File(...),
        target_db: float = Query(-3.0, ge=-20.0, le=0.0)
    ):
        """Normalize audio to target peak level."""
        import time
        start = time.time()
        
        temp_input_path = temp_output_path = None
        try:
            content = await file.read()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=self.plugin_dir) as tmp_in:
                temp_input_path = Path(tmp_in.name)
                tmp_in.write(content)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=self.plugin_dir) as tmp_out:
                temp_output_path = Path(tmp_out.name)
            audio, sr, channels = load_wav(temp_input_path)
            processed = normalize_audio(audio, target_db)
            save_wav(temp_output_path, processed, sr, channels)
            duration = (time.time() - start) * 1000
            self._last_operation = "normalize"
            return EffectResult(
                success=True,
                effect="normalize",
                message=f"Normalized audio to {target_db} dB",
                output_path=str(temp_output_path),
                duration_ms=duration,
                metadata={
                    "target_db": target_db,
                    "sample_rate": sr,
                    "channels": channels
                }
            )
        except Exception as e:
            self._error_count += 1
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            for p in (temp_input_path, temp_output_path):
                if p and p.exists():
                    try:
                        os.unlink(p)
                    except OSError:
                        # SAFETY: Best-effort cleanup of temp files; failures
                        # are expected (file locked, already deleted, etc.)
                        pass

    async def amplify(
        self,
        file: UploadFile = File(...),
        gain_db: float = Query(0.0, ge=-40.0, le=40.0)
    ):
        """Apply gain to audio."""
        import time
        start = time.time()
        
        temp_input_path = temp_output_path = None
        try:
            content = await file.read()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=self.plugin_dir) as tmp_in:
                temp_input_path = Path(tmp_in.name)
                tmp_in.write(content)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=self.plugin_dir) as tmp_out:
                temp_output_path = Path(tmp_out.name)
            audio, sr, channels = load_wav(temp_input_path)
            processed = amplify_audio(audio, gain_db)
            save_wav(temp_output_path, processed, sr, channels)
            duration = (time.time() - start) * 1000
            self._last_operation = "amplify"
            return EffectResult(
                success=True,
                effect="amplify",
                message=f"Applied {gain_db} dB gain",
                output_path=str(temp_output_path),
                duration_ms=duration,
                metadata={"gain_db": gain_db}
            )
        except Exception as e:
            self._error_count += 1
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            for p in (temp_input_path, temp_output_path):
                if p and p.exists():
                    try:
                        os.unlink(p)
                    except OSError:
                        # SAFETY: Best-effort cleanup of temp files; failures
                        # are expected (file locked, already deleted, etc.)
                        pass

    async def fade(
        self,
        file: UploadFile = File(...),
        fade_type: str = Query("in", regex="^(in|out)$"),
        duration_ms: float = Query(500.0, ge=10.0, le=10000.0),
        curve: str = Query("linear", regex="^(linear|exponential|logarithmic)$")
    ):
        """Apply fade in or fade out."""
        import time
        start = time.time()
        
        temp_input_path = temp_output_path = None
        try:
            content = await file.read()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=self.plugin_dir) as tmp_in:
                temp_input_path = Path(tmp_in.name)
                tmp_in.write(content)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=self.plugin_dir) as tmp_out:
                temp_output_path = Path(tmp_out.name)
            audio, sr, channels = load_wav(temp_input_path)
            processed = apply_fade(audio, sr, fade_type, duration_ms, curve)
            save_wav(temp_output_path, processed, sr, channels)
            proc_duration = (time.time() - start) * 1000
            self._last_operation = f"fade_{fade_type}"
            return EffectResult(
                success=True,
                effect=f"fade_{fade_type}",
                message=f"Applied {duration_ms}ms {curve} fade {fade_type}",
                output_path=str(temp_output_path),
                duration_ms=proc_duration,
                metadata={
                    "fade_type": fade_type,
                    "fade_duration_ms": duration_ms,
                    "curve": curve
                }
            )
        except Exception as e:
            self._error_count += 1
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            for p in (temp_input_path, temp_output_path):
                if p and p.exists():
                    try:
                        os.unlink(p)
                    except OSError:
                        # SAFETY: Best-effort cleanup of temp files; failures
                        # are expected (file locked, already deleted, etc.)
                        pass

    async def trim(
        self,
        file: UploadFile = File(...),
        start_ms: float = Query(0.0, ge=0.0),
        end_ms: Optional[float] = Query(None, ge=0.0)
    ):
        """Trim audio to specified time range."""
        import time
        start = time.time()
        
        temp_input_path = temp_output_path = None
        try:
            content = await file.read()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=self.plugin_dir) as tmp_in:
                temp_input_path = Path(tmp_in.name)
                tmp_in.write(content)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=self.plugin_dir) as tmp_out:
                temp_output_path = Path(tmp_out.name)
            audio, sr, channels = load_wav(temp_input_path)
            processed = trim_audio(audio, sr, start_ms, end_ms)
            save_wav(temp_output_path, processed, sr, channels)
            proc_duration = (time.time() - start) * 1000
            self._last_operation = "trim"
            return EffectResult(
                success=True,
                effect="trim",
                message=f"Trimmed audio from {start_ms}ms to {end_ms or 'end'}",
                output_path=str(temp_output_path),
                duration_ms=proc_duration,
                metadata={
                    "start_ms": start_ms,
                    "end_ms": end_ms,
                    "output_duration_ms": len(processed) / sr * 1000
                }
            )
        except Exception as e:
            self._error_count += 1
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            for p in (temp_input_path, temp_output_path):
                if p and p.exists():
                    try:
                        os.unlink(p)
                    except OSError:
                        # SAFETY: Best-effort cleanup of temp files; failures
                        # are expected (file locked, already deleted, etc.)
                        pass

    async def detect_silence_endpoint(
        self,
        file: UploadFile = File(...),
        threshold_db: float = Query(-40.0, ge=-80.0, le=0.0),
        min_silence_ms: float = Query(500.0, ge=100.0)
    ):
        """Detect silent regions in audio."""
        temp_input_path = None
        try:
            content = await file.read()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=self.plugin_dir) as tmp_in:
                temp_input_path = Path(tmp_in.name)
                tmp_in.write(content)
            audio, sr, channels = load_wav(temp_input_path)
            silent_regions = detect_silence(audio, sr, threshold_db, min_silence_ms)
            self._last_operation = "silence_detection"
            return {
                "regions": [
                    {"start_ms": start, "end_ms": end}
                    for start, end in silent_regions
                ],
                "count": len(silent_regions),
                "threshold_db": threshold_db,
                "min_silence_ms": min_silence_ms
            }
        except Exception as e:
            self._error_count += 1
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if temp_input_path and temp_input_path.exists():
                try:
                    os.unlink(temp_input_path)
                except OSError:
                    # SAFETY: Best-effort cleanup of temp files; failures
                    # are expected (file locked, already deleted, etc.)
                    pass

    async def info(self):
        """Get plugin information."""
        return self.get_info()

    async def health_check(self):
        """Check plugin health status."""
        import time
        
        try:
            loop = asyncio.get_event_loop()
            current_time = loop.time() if loop.is_running() else time.time()
            uptime = current_time - self._start_time if self._start_time > 0 else 0
        except Exception:
            uptime = 0
        
        return HealthStatus(
            healthy=True,
            plugin_id="example_audio_effect",
            version="1.0.0",
            uptime_seconds=uptime,
            effects_available=[e.value for e in EffectType],
            last_operation=self._last_operation,
            error_count=self._error_count
        )

    async def list_effects(self):
        """List available audio effects."""
        return {
            "effects": [
                {
                    "id": "normalize",
                    "name": "Normalize",
                    "description": "Normalize audio to target peak level",
                    "parameters": {
                        "target_db": {"type": "number", "default": -3.0, "min": -20.0, "max": 0.0}
                    }
                },
                {
                    "id": "amplify",
                    "name": "Amplify",
                    "description": "Apply gain to audio",
                    "parameters": {
                        "gain_db": {"type": "number", "default": 0.0, "min": -40.0, "max": 40.0}
                    }
                },
                {
                    "id": "fade_in",
                    "name": "Fade In",
                    "description": "Apply fade in effect",
                    "parameters": {
                        "duration_ms": {"type": "number", "default": 500.0},
                        "curve": {"type": "string", "enum": ["linear", "exponential", "logarithmic"]}
                    }
                },
                {
                    "id": "fade_out",
                    "name": "Fade Out",
                    "description": "Apply fade out effect",
                    "parameters": {
                        "duration_ms": {"type": "number", "default": 500.0},
                        "curve": {"type": "string", "enum": ["linear", "exponential", "logarithmic"]}
                    }
                },
                {
                    "id": "trim",
                    "name": "Trim",
                    "description": "Trim audio to specified time range",
                    "parameters": {
                        "start_ms": {"type": "number", "default": 0.0},
                        "end_ms": {"type": "number", "default": None}
                    }
                },
                {
                    "id": "silence_detection",
                    "name": "Silence Detection",
                    "description": "Detect silent regions in audio",
                    "parameters": {
                        "threshold_db": {"type": "number", "default": -40.0},
                        "min_silence_ms": {"type": "number", "default": 500.0}
                    }
                }
            ]
        }

    async def get_settings(self):
        """Get current plugin settings."""
        return self.settings

    async def update_settings(self, settings: PluginSettings):
        """Update plugin settings."""
        self.settings = settings
        return self.settings

    # Private helper methods for apply_effect
    async def _apply_normalize(self, params: Dict[str, Any]) -> EffectResult:
        target_db = params.get("target_db", self.settings.default_normalization_level)
        input_path = params.get("input_path")
        
        if not input_path:
            raise ValueError("input_path is required")
        
        audio, sr, channels = load_wav(Path(input_path))
        processed = normalize_audio(audio, target_db)
        
        output_path = self.plugin_dir / "output.wav"
        save_wav(output_path, processed, sr, channels)
        
        return EffectResult(
            success=True,
            effect="normalize",
            message=f"Normalized to {target_db} dB",
            output_path=str(output_path)
        )

    async def _apply_amplify(self, params: Dict[str, Any]) -> EffectResult:
        gain_db = params.get("gain_db", 0.0)
        input_path = params.get("input_path")
        
        if not input_path:
            raise ValueError("input_path is required")
        
        audio, sr, channels = load_wav(Path(input_path))
        processed = amplify_audio(audio, gain_db)
        
        output_path = self.plugin_dir / "output.wav"
        save_wav(output_path, processed, sr, channels)
        
        return EffectResult(
            success=True,
            effect="amplify",
            message=f"Applied {gain_db} dB gain",
            output_path=str(output_path)
        )

    async def _apply_fade_in(self, params: Dict[str, Any]) -> EffectResult:
        duration_ms = params.get("duration_ms", 500.0)
        curve = params.get("curve", "linear")
        input_path = params.get("input_path")
        
        if not input_path:
            raise ValueError("input_path is required")
        
        audio, sr, channels = load_wav(Path(input_path))
        processed = apply_fade(audio, sr, "in", duration_ms, curve)
        
        output_path = self.plugin_dir / "output.wav"
        save_wav(output_path, processed, sr, channels)
        
        return EffectResult(
            success=True,
            effect="fade_in",
            message=f"Applied {duration_ms}ms fade in",
            output_path=str(output_path)
        )

    async def _apply_fade_out(self, params: Dict[str, Any]) -> EffectResult:
        duration_ms = params.get("duration_ms", 500.0)
        curve = params.get("curve", "linear")
        input_path = params.get("input_path")
        
        if not input_path:
            raise ValueError("input_path is required")
        
        audio, sr, channels = load_wav(Path(input_path))
        processed = apply_fade(audio, sr, "out", duration_ms, curve)
        
        output_path = self.plugin_dir / "output.wav"
        save_wav(output_path, processed, sr, channels)
        
        return EffectResult(
            success=True,
            effect="fade_out",
            message=f"Applied {duration_ms}ms fade out",
            output_path=str(output_path)
        )

    async def _apply_trim(self, params: Dict[str, Any]) -> EffectResult:
        start_ms = params.get("start_ms", 0.0)
        end_ms = params.get("end_ms")
        input_path = params.get("input_path")
        
        if not input_path:
            raise ValueError("input_path is required")
        
        audio, sr, channels = load_wav(Path(input_path))
        processed = trim_audio(audio, sr, start_ms, end_ms)
        
        output_path = self.plugin_dir / "output.wav"
        save_wav(output_path, processed, sr, channels)
        
        return EffectResult(
            success=True,
            effect="trim",
            message=f"Trimmed from {start_ms}ms to {end_ms or 'end'}",
            output_path=str(output_path)
        )

    async def _apply_silence_detection(self, params: Dict[str, Any]) -> EffectResult:
        threshold_db = params.get("threshold_db", -40.0)
        min_silence_ms = params.get("min_silence_ms", 500.0)
        input_path = params.get("input_path")
        
        if not input_path:
            raise ValueError("input_path is required")
        
        audio, sr, channels = load_wav(Path(input_path))
        silent_regions = detect_silence(audio, sr, threshold_db, min_silence_ms)
        
        return EffectResult(
            success=True,
            effect="silence_detection",
            message=f"Found {len(silent_regions)} silent regions",
            metadata={
                "regions": [
                    {"start_ms": start, "end_ms": end}
                    for start, end in silent_regions
                ]
            }
        )


# ============================================================================
# Plugin Entry Point
# ============================================================================

def register(app, plugin_dir: Path):
    """
    Register the plugin with the FastAPI app.
    
    This function is called by the plugin loader.
    
    Args:
        app: FastAPI application instance
        plugin_dir: Path to plugin directory
    
    Returns:
        Plugin instance
    """
    plugin = ExampleAudioEffectPlugin(plugin_dir)
    plugin.register(app)
    plugin.initialize()
    logger.info(f"Example Audio Effect plugin v1.0.0 loaded from {plugin_dir}")
    return plugin
