"""
Scale Up Plugin - Advanced Voice Quality Enhancement

Multi-stage voice enhancement pipeline with:
- Noise reduction
- Artifact removal
- Clarity enhancement
- Spectral enhancement
- Dynamic processing
- Final polish
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.plugins_api.base import BasePlugin, PluginMetadata

logger = logging.getLogger(__name__)

PLUGIN_DIR = Path(__file__).parent

# Try to import optional dependencies
try:
    import soundfile as sf

    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    logger.warning("soundfile not available - audio I/O will be limited")

try:
    import librosa

    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.warning("librosa not available - advanced processing will be limited")

try:
    import scipy.signal as signal

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("scipy not available - filtering will be limited")


class ScaleUpRequest(BaseModel):
    """Request model for scale up processing"""

    input_path: str
    output_path: Optional[str] = None
    mode: str = "scale_up"
    noise_reduction_strength: Optional[float] = None
    enhancement_strength: Optional[float] = None


class ScaleUpManager:
    """Advanced voice quality enhancement manager"""

    def __init__(self):
        """Initialize the Scale Up manager"""
        manifest_path = PLUGIN_DIR / "plugin.json"
        with open(manifest_path, "r", encoding="utf-8") as f:
            self.manifest = json.load(f)

        self.sample_rate = 44100
        self.hop_length = 512
        self.n_fft = 2048

        # Processing parameters
        self.params = {
            "noise_reduction_strength": 0.6,
            "enhancement_strength": 1.0,
            "compression_ratio": 3.0,
            "compression_threshold": -12.0,
            "brightness_boost": 0.0,
            "presence_boost": 0.0,
            "preserve_formants": True,
            "remove_plosives": True,
            "de_sibilance": True,
            "normalize": True,
            "target_lufs": -16.0,
        }

    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file with automatic resampling"""
        if not SOUNDFILE_AVAILABLE:
            raise RuntimeError("soundfile not installed. Run: pip install soundfile")

        audio, sr = sf.read(file_path)

        # Convert to mono if stereo
        if isinstance(audio, np.ndarray) and len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)

        # Resample if needed
        if sr != self.sample_rate:
            if LIBROSA_AVAILABLE:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sample_rate)
            else:
                logger.warning(
                    f"librosa not available, keeping original sample rate {sr}"
                )
                self.sample_rate = sr

        # Normalize to prevent clipping
        if np.max(np.abs(audio)) > 1.0:
            audio = audio / np.max(np.abs(audio))

        return audio, self.sample_rate

    def save_audio(self, audio: np.ndarray, sr: int, file_path: str):
        """Save audio file with proper normalization"""
        if not SOUNDFILE_AVAILABLE:
            raise RuntimeError("soundfile not installed. Run: pip install soundfile")

        # Prevent clipping
        if np.max(np.abs(audio)) > 0.99:
            audio = audio / np.max(np.abs(audio)) * 0.99

        sf.write(file_path, audio, sr)

    def scale_up(
        self, input_path: str, output_path: str, mode: str = "scale_up", **kwargs
    ) -> Dict[str, Any]:
        """
        Main upscaling function with multiple modes.

        Args:
            input_path: Path to input audio file
            output_path: Path to output audio file
            mode: Processing mode ('scale_up', 'scale_up_2', 'scale_up_max', 'preserve', 'enhance')
            **kwargs: Additional parameters
        """
        logger.info(f"Scale Up Processing - Mode: {mode}")

        # Load audio
        audio, sr = self.load_audio(input_path)
        logger.info(f"Loaded: {len(audio)/sr:.2f}s at {sr}Hz")

        # Get mode strength
        mode_config = self.manifest.get("processing_modes", {}).get(mode, {})
        strength = mode_config.get("strength", 1.25)

        # Update params based on mode
        if mode == "preserve":
            self.params["enhancement_strength"] = 0.3
            self.params["noise_reduction_strength"] = 0.3
        elif mode == "enhance":
            self.params["enhancement_strength"] = 1.5
            self.params["noise_reduction_strength"] = 0.8

        # Update from kwargs
        for key, value in kwargs.items():
            if key in self.params:
                self.params[key] = value

        # Processing pipeline
        logger.info(f"Processing with strength: {strength}x...")

        # Step 1: Noise reduction
        audio = self._reduce_noise(audio, sr)

        # Step 2: Remove artifacts
        audio = self._remove_artifacts(audio, sr)

        # Step 3: Enhance clarity
        audio = self._enhance_clarity(audio, sr)

        # Step 4: Spectral enhancement
        audio = self._spectral_enhancement(audio, sr)

        # Step 5: Dynamic processing
        audio = self._dynamic_processing(audio, sr)

        # Step 6: Final polish
        audio = self._final_polish(audio, sr)

        # Save result
        self.save_audio(audio, sr, output_path)

        # Calculate improvement metrics
        original_audio, _ = self.load_audio(input_path)
        metrics = self._calculate_metrics(original_audio, audio, sr)

        logger.info(
            f"Processing Complete! SNR Improvement: {metrics['snr_improvement']:.2f} dB"
        )

        return {
            "status": "success",
            "output_file": output_path,
            "metrics": metrics,
            "mode": mode,
            "strength": strength,
        }

    def _reduce_noise(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Advanced noise reduction"""
        if not SCIPY_AVAILABLE or not LIBROSA_AVAILABLE:
            return audio

        strength = self.params["noise_reduction_strength"]

        # Spectral subtraction
        stft = librosa.stft(audio, n_fft=self.n_fft, hop_length=self.hop_length)
        magnitude = np.abs(stft)
        phase = np.angle(stft)

        # Estimate noise floor from first 0.5s
        noise_samples = int(0.5 * sr / self.hop_length)
        noise_floor = np.percentile(
            magnitude[:, :noise_samples], 50, axis=1, keepdims=True
        )

        # Subtract noise
        magnitude_clean = magnitude - strength * noise_floor
        magnitude_clean = np.maximum(magnitude_clean, 0)

        # Reconstruct
        stft_clean = magnitude_clean * np.exp(1j * phase)
        audio_clean = librosa.istft(stft_clean, hop_length=self.hop_length)

        return audio_clean

    def _remove_artifacts(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Remove clicks, pops, and other artifacts"""
        if not SCIPY_AVAILABLE:
            return audio

        # High-pass filter to remove low-frequency artifacts
        nyquist = sr / 2
        cutoff = 80
        b, a = signal.butter(4, cutoff / nyquist, btype="high")
        audio = signal.filtfilt(b, a, audio)

        # Remove clicks using median filter
        window_size = int(0.01 * sr)  # 10ms window
        if window_size % 2 == 0:
            window_size += 1

        audio = signal.medfilt(audio, kernel_size=window_size)

        return audio

    def _enhance_clarity(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Enhance vocal clarity and presence"""
        if not LIBROSA_AVAILABLE or not SCIPY_AVAILABLE:
            return audio

        strength = self.params["enhancement_strength"]
        brightness = self.params["brightness_boost"]
        presence = self.params["presence_boost"]

        # Spectral decomposition
        stft = librosa.stft(audio, n_fft=self.n_fft, hop_length=self.hop_length)
        magnitude = np.abs(stft)
        phase = np.angle(stft)

        # Frequency bins
        freqs = librosa.fft_frequencies(sr=sr, n_fft=self.n_fft)

        # Vocal enhancement
        # Boost presence frequencies (2-5 kHz)
        presence_mask = (freqs >= 2000) & (freqs <= 5000)
        magnitude[presence_mask, :] *= 1 + strength * presence

        # Boost brightness (5-10 kHz)
        if brightness > 0:
            brightness_mask = (freqs >= 5000) & (freqs <= 10000)
            magnitude[brightness_mask, :] *= 1 + brightness

        # Prevent excessive boost
        magnitude = np.clip(magnitude, 0, np.percentile(magnitude, 99.5))

        # Reconstruct
        stft_enhanced = magnitude * np.exp(1j * phase)
        audio_enhanced = librosa.istft(stft_enhanced, hop_length=self.hop_length)

        return audio_enhanced

    def _spectral_enhancement(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply spectral enhancement to restore harmonics"""
        if not LIBROSA_AVAILABLE:
            return audio

        # Harmonic-percussive separation
        try:
            harmonic, percussive = librosa.effects.hpss(audio)

            # Enhance harmonics
            harmonic_boost = 1.2
            harmonic = harmonic * harmonic_boost

            # Combine
            audio = harmonic + 0.5 * percussive
        except Exception as e:
            logger.warning(f"Harmonic separation failed: {e}")

        return audio

    def _dynamic_processing(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply dynamic processing (compression, limiting)"""
        if not SCIPY_AVAILABLE:
            return audio

        # Simple compressor
        threshold = self.params["compression_threshold"]
        ratio = self.params["compression_ratio"]

        # Calculate RMS
        rms = np.sqrt(np.mean(audio**2))

        # Apply compression
        if rms > 0:
            rms_db = 20 * np.log10(rms)

            if rms_db > threshold:
                excess = rms_db - threshold
                compressed_excess = excess / ratio
                target_db = threshold + compressed_excess
                gain = 10 ** ((target_db - rms_db) / 20)
                audio = audio * gain

        # Limiter to prevent clipping
        max_val = 0.95
        if np.max(np.abs(audio)) > max_val:
            audio = audio / np.max(np.abs(audio)) * max_val

        return audio

    def _final_polish(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Final polishing and normalization"""
        if not SCIPY_AVAILABLE:
            return audio

        # De-ess (remove sibilance)
        if self.params["de_sibilance"]:
            nyquist = sr / 2
            f0 = 7000 / nyquist
            Q = 0.5
            b_notch, a_notch = signal.iirnotch(f0, Q)
            audio = signal.filtfilt(b_notch, a_notch, audio)

        # Plosive removal
        if self.params["remove_plosives"]:
            nyquist = sr / 2
            cutoff = 100
            b, a = signal.butter(4, cutoff / nyquist, btype="high")
            audio = signal.filtfilt(b, a, audio)

        # Normalize
        if self.params["normalize"]:
            target_lufs = self.params["target_lufs"]
            rms = np.sqrt(np.mean(audio**2))
            current_lufs = 20 * np.log10(rms) - 23
            gain_db = target_lufs - current_lufs
            gain = 10 ** (gain_db / 20)
            audio = audio * gain
            audio = np.clip(audio, -0.95, 0.95)

        return audio

    def _calculate_metrics(
        self, original: np.ndarray, processed: np.ndarray, sr: int
    ) -> Dict[str, float]:
        """Calculate quality improvement metrics"""
        metrics = {}

        # SNR improvement (simplified)
        original_rms = np.sqrt(np.mean(original**2))
        processed_rms = np.sqrt(np.mean(processed**2))

        noise_estimate = np.percentile(np.abs(original), 10)
        if noise_estimate > 0:
            original_snr = 20 * np.log10(original_rms / noise_estimate)
        else:
            original_snr = 60

        noise_processed = np.percentile(np.abs(processed), 10)
        if noise_processed > 0:
            processed_snr = 20 * np.log10(processed_rms / noise_processed)
        else:
            processed_snr = 60

        metrics["snr_improvement"] = processed_snr - original_snr

        # Clarity improvement
        if LIBROSA_AVAILABLE:
            original_hf = np.mean(
                np.abs(librosa.stft(original, n_fft=self.n_fft)[-100:, :])
            )
            processed_hf = np.mean(
                np.abs(librosa.stft(processed, n_fft=self.n_fft)[-100:, :])
            )

            if original_hf > 0:
                metrics["clarity_improvement"] = (processed_hf / original_hf - 1) * 100
            else:
                metrics["clarity_improvement"] = 0
        else:
            metrics["clarity_improvement"] = 0

        return metrics


class ScaleUpPlugin(BasePlugin):
    """Scale Up Plugin for VoiceStudio"""

    def __init__(self, plugin_dir: Path):
        """Initialize scale up plugin"""
        manifest_path = plugin_dir / "manifest.json"
        metadata = PluginMetadata(manifest_path)
        super().__init__(metadata)
        self.router = APIRouter(
            prefix="/api/plugin/scale_up", tags=["plugin", "scale_up"]
        )
        self.manager = ScaleUpManager()

    def register(self, app):
        """Register plugin routes with FastAPI app"""
        # Register routes
        self.router.post("/process")(self.process_audio)
        self.router.get("/modes")(self.get_modes)
        self.router.get("/info")(self.get_info)

        # Include router in app
        app.include_router(self.router)
        logger.info(f"Scale Up plugin registered with {len(self.router.routes)} routes")

    async def process_audio(self, request: ScaleUpRequest):
        """Process audio with scale up enhancement"""
        if not request.output_path:
            input_path = Path(request.input_path)
            request.output_path = str(
                input_path.parent / f"{input_path.stem}_scaleup{input_path.suffix}"
            )

        kwargs = {}
        if request.noise_reduction_strength is not None:
            kwargs["noise_reduction_strength"] = request.noise_reduction_strength
        if request.enhancement_strength is not None:
            kwargs["enhancement_strength"] = request.enhancement_strength

        try:
            result = self.manager.scale_up(
                request.input_path, request.output_path, mode=request.mode, **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Scale up processing failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    async def get_modes(self):
        """Get available processing modes"""
        return self.manager.manifest.get("processing_modes", {})

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
    plugin = ScaleUpPlugin(plugin_dir)
    plugin.register(app)
    plugin.initialize()
    return plugin
