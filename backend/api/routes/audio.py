"""
Audio Analysis Routes

Endpoints for audio visualization data: waveforms, spectrograms, and meters.
Provides downsampled data optimized for real-time rendering in the UI.
"""

import logging
import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from pydantic import BaseModel

from ..optimization import cache_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/audio", tags=["audio"])

# Import audio utilities
try:
    import librosa
    import soundfile as sf

    HAS_AUDIO_LIBS = True
except ImportError:
    HAS_AUDIO_LIBS = False
    logger.warning(
        "librosa/soundfile not available. Audio analysis endpoints will be limited."
    )


class WaveformData(BaseModel):
    """Waveform data for rendering."""

    samples: List[float]
    sample_rate: int
    duration: float
    channels: int
    width: int
    mode: str  # "peak" or "rms"


class SpectrogramFrame(BaseModel):
    """Single frame of spectrogram data."""

    time: float
    frequencies: List[float]


class SpectrogramData(BaseModel):
    """Spectrogram data for rendering."""

    frames: List[SpectrogramFrame]
    sample_rate: int
    fft_size: int
    hop_length: int
    width: int
    height: int


class AudioMeters(BaseModel):
    """Audio level meters data."""

    peak: float
    rms: float
    lufs: Optional[float] = None
    channels: List[Dict[str, float]] = []


class LoudnessData(BaseModel):
    """Loudness (LUFS) data for visualization."""

    times: List[float]
    lufs_values: List[float]
    integrated_lufs: Optional[float] = None
    peak_lufs: Optional[float] = None
    sample_rate: int
    duration: float


class RadarData(BaseModel):
    """Radar chart data for frequency domain visualization."""

    band_names: List[str]
    frequencies: List[float]
    magnitudes: List[float]
    phases: Optional[List[float]] = None
    sample_rate: int


class PhaseData(BaseModel):
    """Phase analysis data for visualization."""

    times: List[float]
    correlation: List[float]
    phase_difference: Optional[List[float]] = None
    stereo_width: Optional[List[float]] = None
    average_correlation: Optional[float] = None
    sample_rate: int
    duration: float


class RadarAxis(BaseModel):
    """Radar chart axis definition."""

    name: str
    max_value: float = 1.0
    min_value: float = 0.0


class RadarDataPoint(BaseModel):
    """Radar chart data point."""

    axis_name: str
    value: float  # Normalized 0.0-1.0


class RadarChartData(BaseModel):
    """Radar chart data for rendering."""

    axes: List[RadarAxis]
    points: List[RadarDataPoint]
    label: str = ""


def _get_audio_path(audio_id: str) -> Optional[str]:
    """Get audio file path from audio_id.

    Checks:
    1. Voice route temporary storage (_audio_storage)
    2. Project audio directories (by filename match)
    3. Direct filename match in project audio directories
    """
    # Check voice route storage
    from .voice import _audio_storage

    if audio_id in _audio_storage:
        path = _audio_storage[audio_id]
        if os.path.exists(path):
            return path

    # Check project audio storage
    # audio_id might be a filename (for project audio files)
    projects_dir = os.path.join(os.path.expanduser("~"), ".voicestudio", "projects")

    # First, try exact filename match
    for project_dir in Path(projects_dir).glob("*/audio/*"):
        if project_dir.is_file() and project_dir.name == audio_id:
            return str(project_dir)

    # Then try partial match (audio_id might be embedded in filename)
    for project_dir in Path(projects_dir).glob("*/audio/*"):
        if project_dir.is_file() and audio_id in project_dir.name:
            return str(project_dir)

    # Also check if audio_id is just a filename without path
    if not os.path.sep in audio_id and not os.path.altsep in audio_id:
        # It's just a filename, search all project audio directories
        for project_dir in Path(projects_dir).glob("*/audio/*"):
            if project_dir.is_file() and project_dir.name == audio_id:
                return str(project_dir)

    return None


def _downsample_waveform(
    audio: np.ndarray, sample_rate: int, target_width: int, mode: str = "peak"
) -> np.ndarray:
    """Downsample audio to target width for waveform rendering."""
    if not HAS_AUDIO_LIBS:
        # Fallback: simple downsampling
        if len(audio) <= target_width:
            return audio.tolist()

        step = len(audio) // target_width
        if mode == "peak":
            # Peak mode: take max absolute value in each bin
            downsampled = []
            for i in range(0, len(audio), step):
                chunk = audio[i : i + step]
                if len(chunk) > 0:
                    downsampled.append(float(np.max(np.abs(chunk))))
        else:
            # RMS mode: calculate RMS in each bin
            downsampled = []
            for i in range(0, len(audio), step):
                chunk = audio[i : i + step]
                if len(chunk) > 0:
                    rms = np.sqrt(np.mean(chunk**2))
                    downsampled.append(float(rms))

        return np.array(downsampled[:target_width])

    # Use librosa for better downsampling
    if mode == "peak":
        # Peak mode: take max absolute value
        hop_length = max(1, len(audio) // target_width)
        downsampled = []
        for i in range(0, len(audio), hop_length):
            chunk = audio[i : i + hop_length]
            if len(chunk) > 0:
                downsampled.append(float(np.max(np.abs(chunk))))
        return np.array(downsampled[:target_width])
    else:
        # RMS mode: use librosa's frame function
        hop_length = max(1, len(audio) // target_width)
        frames = librosa.util.frame(
            audio, frame_length=hop_length, hop_length=hop_length, axis=0
        )
        rms = np.sqrt(np.mean(frames**2, axis=0))
        return rms[:target_width]


@router.get("/waveform", response_model=WaveformData)
@cache_response(
    ttl=300
)  # Cache for 5 minutes (waveform data is static for a given audio file)
def get_waveform_data(
    audio_id: str = Query(..., description="Audio file identifier"),
    width: int = Query(1024, description="Target pixel width for downsampling"),
    mode: str = Query("peak", description="Waveform mode: 'peak' or 'rms'"),
) -> WaveformData:
    """
    Get downsampled waveform data for rendering.

    Returns waveform samples optimized for the specified width.
    """
    try:
        if not audio_id or not audio_id.strip():
            raise HTTPException(status_code=400, detail="Audio ID is required")
        if width <= 0:
            raise HTTPException(status_code=400, detail="Width must be greater than 0")
        if width > 10000:
            raise HTTPException(status_code=400, detail="Width cannot exceed 10000")

        if not HAS_AUDIO_LIBS:
            raise HTTPException(
                status_code=503,
                detail="Audio analysis libraries not available. Install librosa and soundfile.",
            )

        audio_path = _get_audio_path(audio_id)
        if not audio_path or not os.path.exists(audio_path):
            logger.warning(f"Audio file not found for waveform: {audio_id}")
            raise HTTPException(
                status_code=404, detail=f"Audio file not found: {audio_id}"
            )

        try:
            # Load audio file
            audio, sample_rate = sf.read(audio_path)

            # Handle stereo by converting to mono
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)

            # Calculate duration
            duration = len(audio) / sample_rate

            # Downsample waveform
            if mode not in ["peak", "rms"]:
                mode = "peak"

            downsampled = _downsample_waveform(audio, sample_rate, width, mode)

            return WaveformData(
                samples=downsampled.tolist(),
                sample_rate=sample_rate,
                duration=duration,
                channels=1,
                width=len(downsampled),
                mode=mode,
            )
        except Exception as e:
            logger.error(
                f"Failed to load or process audio for waveform {audio_id}: {str(e)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=500, detail=f"Failed to process audio: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error generating waveform data for {audio_id}: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to generate waveform data: {str(e)}"
        )


@router.get("/spectrogram", response_model=SpectrogramData)
@cache_response(
    ttl=300
)  # Cache for 5 minutes (spectrogram data is static for a given audio file)
def get_spectrogram_data(
    audio_id: str = Query(..., description="Audio file identifier"),
    width: int = Query(512, description="Target pixel width"),
    height: int = Query(256, description="Target pixel height (frequency bins)"),
) -> SpectrogramData:
    """
    Get FFT-based spectrogram data for rendering.

    Returns spectrogram frames optimized for the specified dimensions.
    """
    try:
        if not audio_id or not audio_id.strip():
            raise HTTPException(status_code=400, detail="Audio ID is required")
        if width <= 0:
            raise HTTPException(status_code=400, detail="Width must be greater than 0")
        if width > 5000:
            raise HTTPException(status_code=400, detail="Width cannot exceed 5000")
        if height <= 0:
            raise HTTPException(status_code=400, detail="Height must be greater than 0")
        if height > 2048:
            raise HTTPException(status_code=400, detail="Height cannot exceed 2048")

        if not HAS_AUDIO_LIBS:
            raise HTTPException(
                status_code=503,
                detail="Audio analysis libraries not available. Install librosa and soundfile.",
            )

        audio_path = _get_audio_path(audio_id)
        if not audio_path or not os.path.exists(audio_path):
            logger.warning(f"Audio file not found for spectrogram: {audio_id}")
            raise HTTPException(
                status_code=404, detail=f"Audio file not found: {audio_id}"
            )

        try:
            # Load audio file
            audio, sample_rate = sf.read(audio_path)

            # Handle stereo by converting to mono
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)

            # Calculate STFT parameters
            n_fft = 2048
            hop_length = max(1, len(audio) // width)

            # Compute STFT
            stft = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)
            magnitude = np.abs(stft)

            # Convert to dB
            magnitude_db = librosa.amplitude_to_db(magnitude, ref=np.max)

            # Normalize to 0-1 range
            magnitude_normalized = (magnitude_db + 80) / 80.0  # Assuming -80dB floor
            magnitude_normalized = np.clip(magnitude_normalized, 0, 1)

            # Downsample frequency bins to target height
            if magnitude_normalized.shape[0] > height:
                # Average adjacent bins
                step = magnitude_normalized.shape[0] // height
                downsampled = []
                for i in range(0, magnitude_normalized.shape[0], step):
                    chunk = magnitude_normalized[i : i + step, :]
                    if len(chunk) > 0:
                        downsampled.append(np.mean(chunk, axis=0))
                magnitude_normalized = np.array(downsampled)

            # Create frames
            frames = []
            time_per_frame = hop_length / sample_rate

            for i in range(magnitude_normalized.shape[1]):
                frames.append(
                    SpectrogramFrame(
                        time=i * time_per_frame,
                        frequencies=magnitude_normalized[:, i].tolist(),
                    )
                )

            return SpectrogramData(
                frames=frames,
                sample_rate=sample_rate,
                fft_size=n_fft,
                hop_length=hop_length,
                width=len(frames),
                height=magnitude_normalized.shape[0],
            )
        except Exception as e:
            logger.error(
                f"Failed to load or process audio for spectrogram {audio_id}: {str(e)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=500, detail=f"Failed to process audio: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error generating spectrogram data for {audio_id}: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to generate spectrogram data: {str(e)}"
        )


@router.get("/loudness", response_model=LoudnessData)
@cache_response(
    ttl=300
)  # Cache for 5 minutes (loudness data is static for a given audio file)
def get_loudness_data(
    audio_id: str = Query(..., description="Audio file identifier"),
    width: int = Query(1024, description="Target pixel width for downsampling"),
    block_size: float = Query(
        0.400, description="Block size in seconds for LUFS measurement"
    ),
) -> LoudnessData:
    """
    Get loudness (LUFS) data over time for visualization.

    Returns LUFS values calculated at regular intervals, optimized for the specified width.
    """
    try:
        if not audio_id or not audio_id.strip():
            raise HTTPException(status_code=400, detail="Audio ID is required")
        if width <= 0:
            raise HTTPException(status_code=400, detail="Width must be greater than 0")
        if width > 10000:
            raise HTTPException(status_code=400, detail="Width cannot exceed 10000")
        if block_size <= 0:
            raise HTTPException(
                status_code=400, detail="Block size must be greater than 0"
            )
        if block_size > 10.0:
            raise HTTPException(
                status_code=400, detail="Block size cannot exceed 10 seconds"
            )

        if not HAS_AUDIO_LIBS:
            raise HTTPException(
                status_code=503,
                detail="Audio analysis libraries not available. Install librosa and soundfile.",
            )

        # Try to import pyloudnorm
        try:
            import pyloudnorm as pyln

            HAS_PYLOUDNORM = True
        except ImportError:
            HAS_PYLOUDNORM = False
            logger.warning(
                "pyloudnorm not available. LUFS calculation will be approximated."
            )

        audio_path = _get_audio_path(audio_id)
        if not audio_path or not os.path.exists(audio_path):
            logger.warning(f"Audio file not found for loudness analysis: {audio_id}")
            raise HTTPException(
                status_code=404, detail=f"Audio file not found: {audio_id}"
            )

        try:
            # Load audio file
            audio, sample_rate = sf.read(audio_path)

            # Handle stereo by converting to mono for loudness measurement
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)

            # Calculate duration
            duration = len(audio) / sample_rate

            # Calculate number of blocks
            num_blocks = max(1, width)
            block_samples = max(1, int(sample_rate * block_size))
            hop_samples = max(1, len(audio) // num_blocks)

            times = []
            lufs_values = []

            if HAS_PYLOUDNORM:
                # Use pyloudnorm for accurate LUFS measurement
                meter = pyln.Meter(sample_rate, block_size=block_size)

                # Calculate LUFS for each block
                for i in range(0, len(audio), hop_samples):
                    block_end = min(i + block_samples, len(audio))
                    block_audio = audio[i:block_end]

                    if len(block_audio) < block_samples * 0.5:  # Skip incomplete blocks
                        break

                    try:
                        loudness = meter.integrated_loudness(block_audio)
                        if np.isnan(loudness) or np.isinf(loudness):
                            loudness = -70.0  # Default to very quiet
                    except Exception:
                        loudness = -70.0  # Default to very quiet

                    time_pos = i / sample_rate
                    times.append(time_pos)
                    lufs_values.append(float(loudness))
            else:
                # Fallback: approximate LUFS from RMS
                for i in range(0, len(audio), hop_samples):
                    block_end = min(i + hop_samples, len(audio))
                    block_audio = audio[i:block_end]

                    if len(block_audio) == 0:
                        break

                    # Calculate RMS
                    rms = np.sqrt(np.mean(block_audio**2))

                    # Approximate LUFS from RMS (rough conversion)
                    # LUFS ≈ 20 * log10(RMS) - 0.691 (approximate offset)
                    if rms > 1e-10:
                        lufs_approx = 20 * np.log10(rms) - 0.691
                        lufs_approx = max(
                            -70.0, min(0.0, lufs_approx)
                        )  # Clamp to reasonable range
                    else:
                        lufs_approx = -70.0

                    time_pos = i / sample_rate
                    times.append(time_pos)
                    lufs_values.append(float(lufs_approx))

            # Calculate integrated and peak LUFS
            integrated_lufs = None
            peak_lufs = None

            if HAS_PYLOUDNORM and len(audio) > 0:
                try:
                    meter = pyln.Meter(sample_rate)
                    integrated_lufs = float(meter.integrated_loudness(audio))
                    if np.isnan(integrated_lufs) or np.isinf(integrated_lufs):
                        integrated_lufs = None
                except Exception:
                    ...

            if len(lufs_values) > 0:
                peak_lufs = float(max(lufs_values))

            return LoudnessData(
                times=times,
                lufs_values=lufs_values,
                integrated_lufs=integrated_lufs,
                peak_lufs=peak_lufs,
                sample_rate=sample_rate,
                duration=duration,
            )
        except Exception as e:
            logger.error(
                f"Failed to load or process audio for loudness analysis {audio_id}: {str(e)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=500, detail=f"Failed to process audio: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error generating loudness data for {audio_id}: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to generate loudness data: {str(e)}"
        )


@router.get("/meters", response_model=AudioMeters)
@cache_response(ttl=1)  # Cache for 1 second (meters update very frequently)
def get_audio_meters(
    audio_id: str = Query(..., description="Audio file identifier")
) -> AudioMeters:
    """
    Get audio level meters data (peak, RMS, LUFS).

    Returns current audio levels for real-time meter updates.
    """
    try:
        if not audio_id or not audio_id.strip():
            raise HTTPException(status_code=400, detail="Audio ID is required")

        if not HAS_AUDIO_LIBS:
            raise HTTPException(
                status_code=503,
                detail="Audio analysis libraries not available. Install librosa and soundfile.",
            )

        audio_path = _get_audio_path(audio_id)
        if not audio_path or not os.path.exists(audio_path):
            logger.warning(f"Audio file not found for meters: {audio_id}")
            raise HTTPException(
                status_code=404, detail=f"Audio file not found: {audio_id}"
            )

        try:
            # Load audio file
            audio, sample_rate = sf.read(audio_path)

            # Handle multi-channel
            if len(audio.shape) == 1:
                audio = audio.reshape(-1, 1)

            num_channels = audio.shape[1]

            # Calculate peak and RMS per channel
            channels = []
            peak_values = []
            rms_values = []

            for ch in range(num_channels):
                channel_audio = audio[:, ch]
                peak = float(np.max(np.abs(channel_audio)))
                rms = float(np.sqrt(np.mean(channel_audio**2)))

                channels.append({"peak": peak, "rms": rms})
                peak_values.append(peak)
                rms_values.append(rms)

            # Overall peak and RMS
            overall_peak = float(np.max(peak_values))
            overall_rms = float(np.sqrt(np.mean([r**2 for r in rms_values])))

            # Calculate LUFS (simplified - use pyloudnorm if available)
            lufs = None
            try:
                import pyloudnorm as pyln

                meter = pyln.Meter(sample_rate)
                lufs = float(meter.integrated_loudness(audio))
            except (ImportError, Exception):
                # Fallback: estimate from RMS
                lufs = float(20 * np.log10(max(overall_rms, 1e-10)))

            return AudioMeters(
                peak=overall_peak, rms=overall_rms, lufs=lufs, channels=channels
            )
        except Exception as e:
            logger.error(
                f"Failed to load or process audio for meters {audio_id}: {str(e)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=500, detail=f"Failed to process audio: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error calculating audio meters for {audio_id}: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to calculate audio meters: {str(e)}"
        )


@router.get("/radar", response_model=RadarData)
@cache_response(
    ttl=300
)  # Cache for 5 minutes (radar data is static for a given audio file)
def get_radar_data(
    audio_id: str = Query(..., description="Audio file identifier")
) -> RadarData:
    """
    Get radar chart data for frequency domain visualization.

    Analyzes audio and returns frequency band magnitudes
    in a format suitable for radar chart rendering.
    """
    try:
        if not audio_id or not audio_id.strip():
            raise HTTPException(status_code=400, detail="Audio ID is required")

        if not HAS_AUDIO_LIBS:
            raise HTTPException(
                status_code=503,
                detail="Audio analysis libraries not available. Install librosa and soundfile.",
            )

        audio_path = _get_audio_path(audio_id)
        if not audio_path or not os.path.exists(audio_path):
            logger.warning(f"Audio file not found for radar analysis: {audio_id}")
            raise HTTPException(
                status_code=404, detail=f"Audio file not found: {audio_id}"
            )

        try:
            # Load audio file
            audio, sample_rate = sf.read(audio_path)

            # Convert to mono if stereo
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)

            # Compute FFT to get frequency domain representation
            n_fft = 2048
            hop_length = 512
            D = np.abs(librosa.stft(audio, n_fft=n_fft, hop_length=hop_length))

            # Average across time to get overall frequency spectrum
            avg_spectrum = np.mean(D, axis=1)

            # Define frequency bands (octave bands: 20Hz-20kHz)
            # Low: 20-250Hz, Low-Mid: 250-500Hz, Mid: 500-2kHz, High-Mid: 2-4kHz, High: 4-20kHz
            freq_bins = librosa.fft_frequencies(sr=sample_rate, n_fft=n_fft)

            # Define frequency bands
            band_ranges = [
                (20, 250),  # Low
                (250, 500),  # Low-Mid
                (500, 2000),  # Mid
                (2000, 4000),  # High-Mid
                (4000, 20000),  # High
            ]
            band_names = ["Low", "Low-Mid", "Mid", "High-Mid", "High"]

            magnitudes = []
            frequencies = []
            phases = []

            for (low_freq, high_freq), band_name in zip(band_ranges, band_names):
                # Find frequency bins in this range
                mask = (freq_bins >= low_freq) & (freq_bins <= high_freq)
                if np.any(mask):
                    # Average magnitude in this band
                    band_magnitude = np.mean(avg_spectrum[mask])
                    # Center frequency
                    center_freq = np.mean(freq_bins[mask])

                    # Normalize magnitude (0-1 range)
                    max_magnitude = np.max(avg_spectrum)
                    normalized_magnitude = (
                        float(band_magnitude / max_magnitude)
                        if max_magnitude > 0
                        else 0.0
                    )

                    magnitudes.append(normalized_magnitude)
                    frequencies.append(float(center_freq))
                    phases.append(0.0)  # Phase not computed for average spectrum

            # Normalize magnitudes to 0-1 range
            if magnitudes and max(magnitudes) > 0:
                max_mag = max(magnitudes)
                magnitudes = [m / max_mag for m in magnitudes]

            return RadarData(
                band_names=band_names,
                frequencies=frequencies,
                magnitudes=magnitudes,
                phases=phases if phases else None,
                sample_rate=sample_rate,
            )
        except Exception as e:
            logger.error(
                f"Failed to load or process audio for radar analysis {audio_id}: {str(e)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=500, detail=f"Failed to process audio: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error generating radar data for {audio_id}: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to generate radar data: {str(e)}"
        )


@router.get("/phase", response_model=PhaseData)
@cache_response(
    ttl=300
)  # Cache for 5 minutes (phase data is static for a given audio file)
def get_phase_data(
    audio_id: str = Query(..., description="Audio file identifier"),
    window_size: float = Query(
        0.1, description="Window size in seconds for phase analysis"
    ),
) -> PhaseData:
    """
    Get phase analysis data for visualization.

    Returns phase correlation, phase difference, and stereo width over time.
    """
    try:
        if not audio_id or not audio_id.strip():
            raise HTTPException(status_code=400, detail="Audio ID is required")
        if window_size <= 0:
            raise HTTPException(
                status_code=400, detail="Window size must be greater than 0"
            )
        if window_size > 5.0:
            raise HTTPException(
                status_code=400, detail="Window size cannot exceed 5 seconds"
            )

        if not HAS_AUDIO_LIBS:
            raise HTTPException(
                status_code=503,
                detail="Audio analysis libraries not available. Install librosa and soundfile.",
            )

        audio_path = _get_audio_path(audio_id)
        if not audio_path or not os.path.exists(audio_path):
            logger.warning(f"Audio file not found for phase analysis: {audio_id}")
            raise HTTPException(
                status_code=404, detail=f"Audio file not found: {audio_id}"
            )

        try:
            # Load audio file
            audio, sample_rate = sf.read(audio_path)
            duration = len(audio) / sample_rate

            # Handle mono vs stereo
            is_stereo = len(audio.shape) > 1 and audio.shape[1] >= 2
            if not is_stereo:
                # Convert mono to pseudo-stereo for analysis
                audio_stereo = np.column_stack([audio, audio])
            else:
                audio_stereo = audio[:, :2]  # Take first 2 channels

            left_channel = audio_stereo[:, 0]
            right_channel = audio_stereo[:, 1]

            # Calculate window samples
            window_samples = int(window_size * sample_rate)
            hop_samples = window_samples // 2  # 50% overlap
            num_windows = max(
                1, (len(left_channel) - window_samples) // hop_samples + 1
            )

            times = []
            correlations = []
            phase_differences = []
            stereo_widths = []

            for i in range(num_windows):
                start_idx = i * hop_samples
                end_idx = min(start_idx + window_samples, len(left_channel))

                if end_idx <= start_idx:
                    break

                left_window = left_channel[start_idx:end_idx]
                right_window = right_channel[start_idx:end_idx]

                # Calculate time for this window
                time_center = (start_idx + end_idx) / 2.0 / sample_rate
                times.append(float(time_center))

                # Calculate correlation
                # Normalize windows
                left_norm = left_window - np.mean(left_window)
                right_norm = right_window - np.mean(right_window)

                std_left = np.std(left_norm)
                std_right = np.std(right_norm)

                if std_left > 0 and std_right > 0:
                    correlation = np.corrcoef(left_norm, right_norm)[0, 1]
                    correlation = float(np.clip(correlation, -1.0, 1.0))
                else:
                    correlation = 0.0
                correlations.append(correlation)

                # Calculate phase difference using FFT
                left_fft = np.fft.rfft(left_window)
                right_fft = np.fft.rfft(right_window)

                # Get phase angles
                left_phase = np.angle(left_fft)
                right_phase = np.angle(right_fft)

                # Average phase difference (weighted by magnitude)
                magnitudes = np.abs(left_fft) + np.abs(right_fft)
                if np.sum(magnitudes) > 0:
                    phase_diff = np.sum(
                        (left_phase - right_phase) * magnitudes
                    ) / np.sum(magnitudes)
                    # Convert to degrees
                    phase_diff_degrees = float(np.degrees(phase_diff))
                    phase_diff_degrees = np.clip(phase_diff_degrees, -180, 180)
                else:
                    phase_diff_degrees = 0.0
                phase_differences.append(phase_diff_degrees)

                # Calculate stereo width (simplified: based on correlation)
                # Width of 1.0 = fully stereo (correlation = 0), 0.0 = mono (correlation = 1)
                stereo_width = float(1.0 - abs(correlation))
                stereo_widths.append(stereo_width)

            # Calculate average correlation
            avg_correlation = float(np.mean(correlations)) if correlations else None

            return PhaseData(
                times=times,
                correlation=correlations,
                phase_difference=phase_differences if phase_differences else None,
                stereo_width=stereo_widths if stereo_widths else None,
                average_correlation=avg_correlation,
                sample_rate=sample_rate,
                duration=float(duration),
            )
        except Exception as e:
            logger.error(
                f"Failed to load or process audio for phase analysis {audio_id}: {str(e)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=500, detail=f"Failed to process audio: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error generating phase data for {audio_id}: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to generate phase data: {str(e)}"
        )


# --- Audio Upload ---

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "audio_uploads")


class AudioUploadResponse(BaseModel):
    """Response from audio upload."""
    id: str
    filename: str
    path: str
    size: int
    content_type: Optional[str] = None


@router.post("/upload", response_model=AudioUploadResponse, status_code=201)
async def upload_audio(file: UploadFile = File(...)):
    """Upload an audio file for processing."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename or "audio.wav")[1] or ".wav"
    safe_filename = f"{file_id}{ext}"
    dest_path = os.path.join(UPLOAD_DIR, safe_filename)

    try:
        with open(dest_path, "wb") as out:
            content = await file.read()
            out.write(content)

        return AudioUploadResponse(
            id=file_id,
            filename=file.filename or safe_filename,
            path=dest_path,
            size=len(content),
            content_type=file.content_type,
        )
    except Exception as e:
        # Clean up on failure
        if os.path.exists(dest_path):
            os.remove(dest_path)
        logger.error(f"Audio upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
