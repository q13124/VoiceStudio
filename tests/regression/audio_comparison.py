"""
Audio Comparison Utilities for Golden Tests

Provides functions to compare generated audio against golden references
using quality metrics with configurable tolerances.
"""

import json
import logging
import wave
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# Try to import audio quality modules
try:
    from app.core.audio.enhanced_quality_metrics import EnhancedQualityAnalyzer

    HAS_QUALITY_ANALYZER = True
except ImportError:
    HAS_QUALITY_ANALYZER = False
    logger.debug("EnhancedQualityAnalyzer not available")


@dataclass
class ComparisonResult:
    """Result of comparing two audio files."""

    passed: bool
    metric_name: str
    expected: float
    actual: float
    tolerance: float
    difference: float
    message: str


@dataclass
class GoldenComparisonReport:
    """Complete report from golden test comparison."""

    test_id: str
    engine: str
    passed: bool
    results: list[ComparisonResult]
    golden_file: str
    generated_file: str | None
    timestamp: str
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "test_id": self.test_id,
            "engine": self.engine,
            "passed": self.passed,
            "results": [
                {
                    "metric": r.metric_name,
                    "expected": r.expected,
                    "actual": r.actual,
                    "tolerance": r.tolerance,
                    "difference": r.difference,
                    "passed": r.passed,
                    "message": r.message,
                }
                for r in self.results
            ],
            "golden_file": self.golden_file,
            "generated_file": self.generated_file,
            "timestamp": self.timestamp,
            "error": self.error,
        }


def load_golden_config(config_path: Path) -> dict[str, Any]:
    """Load golden test configuration."""
    if not config_path.exists():
        raise FileNotFoundError(f"Golden config not found: {config_path}")
    return json.loads(config_path.read_text(encoding="utf-8"))


def load_audio_as_numpy(audio_path: Path) -> tuple[np.ndarray, int]:
    """Load WAV file as numpy array and return with sample rate."""
    with wave.open(str(audio_path), "rb") as wav:
        sample_rate = wav.getframerate()
        n_channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        n_frames = wav.getnframes()

        raw_data = wav.readframes(n_frames)

    # Convert to numpy
    if sample_width == 1:
        dtype = np.uint8
    elif sample_width == 2:
        dtype = np.int16
    elif sample_width == 4:
        dtype = np.int32
    else:
        raise ValueError(f"Unsupported sample width: {sample_width}")

    audio = np.frombuffer(raw_data, dtype=dtype)

    # Convert to float32 normalized to [-1, 1]
    if dtype == np.uint8:
        audio = (audio.astype(np.float32) - 128) / 128
    else:
        audio = audio.astype(np.float32) / np.iinfo(dtype).max

    # Convert to mono if stereo
    if n_channels == 2:
        audio = audio.reshape(-1, 2).mean(axis=1)

    return audio, sample_rate


def calculate_metrics(audio: np.ndarray, sample_rate: int) -> dict[str, float]:
    """Calculate quality metrics for audio."""
    metrics = {}

    # Basic metrics
    rms = np.sqrt(np.mean(audio**2))
    metrics["rms"] = float(rms)

    # LUFS approximation (simplified K-weighted loudness)
    # Real LUFS requires proper K-weighting filter
    lufs = 20 * np.log10(rms + 1e-10) - 0.691
    metrics["lufs"] = float(lufs)

    # SNR estimation (assuming noise floor is lowest 10% energy)
    frame_size = int(0.025 * sample_rate)  # 25ms frames
    hop_size = int(0.010 * sample_rate)  # 10ms hop

    if len(audio) > frame_size:
        n_frames = (len(audio) - frame_size) // hop_size
        frame_energies = []
        for i in range(n_frames):
            start = i * hop_size
            frame = audio[start : start + frame_size]
            energy = np.sum(frame**2)
            frame_energies.append(energy)

        if frame_energies:
            sorted_energies = sorted(frame_energies)
            noise_floor = np.mean(sorted_energies[: max(1, len(sorted_energies) // 10)])
            signal_power = np.mean(sorted_energies[-len(sorted_energies) // 2 :])
            snr = 10 * np.log10((signal_power + 1e-10) / (noise_floor + 1e-10))
            metrics["snr_db"] = float(snr)

    if "snr_db" not in metrics:
        metrics["snr_db"] = 0.0

    # Spectral centroid
    if len(audio) > 0:
        fft = np.fft.rfft(audio)
        magnitude = np.abs(fft)
        freqs = np.fft.rfftfreq(len(audio), 1 / sample_rate)
        spectral_centroid = np.sum(freqs * magnitude) / (np.sum(magnitude) + 1e-10)
        metrics["spectral_centroid_hz"] = float(spectral_centroid)

    # Try enhanced quality analyzer
    if HAS_QUALITY_ANALYZER:
        try:
            analyzer = EnhancedQualityAnalyzer()
            enhanced = analyzer.analyze_audio(audio, sample_rate)
            if enhanced.get("mos"):
                metrics["mos"] = enhanced["mos"]
            if enhanced.get("similarity"):
                metrics["similarity"] = enhanced["similarity"]
        except Exception as e:
            logger.debug(f"Enhanced quality analysis failed: {e}")

    return metrics


def compare_metrics(
    actual_metrics: dict[str, float],
    expected_metrics: dict[str, float],
    tolerances: dict[str, float],
) -> list[ComparisonResult]:
    """Compare actual metrics against expected with tolerances."""
    results = []

    for metric_name, expected_value in expected_metrics.items():
        if metric_name not in actual_metrics:
            results.append(
                ComparisonResult(
                    passed=False,
                    metric_name=metric_name,
                    expected=expected_value,
                    actual=0.0,
                    tolerance=tolerances.get(metric_name, 0.0),
                    difference=expected_value,
                    message=f"Metric '{metric_name}' not found in actual results",
                )
            )
            continue

        actual_value = actual_metrics[metric_name]
        tolerance = tolerances.get(metric_name, 0.0)
        difference = abs(actual_value - expected_value)
        passed = difference <= tolerance

        results.append(
            ComparisonResult(
                passed=passed,
                metric_name=metric_name,
                expected=expected_value,
                actual=actual_value,
                tolerance=tolerance,
                difference=difference,
                message=(
                    f"{metric_name}: {actual_value:.4f} (expected {expected_value:.4f} "
                    f"± {tolerance}, diff: {difference:.4f})"
                ),
            )
        )

    return results


def compare_with_golden(
    generated_audio_path: Path,
    golden_audio_path: Path,
    golden_metadata_path: Path,
    tolerances: dict[str, float],
    test_id: str,
    engine: str,
) -> GoldenComparisonReport:
    """
    Compare generated audio against golden reference.

    Args:
        generated_audio_path: Path to generated audio file
        golden_audio_path: Path to golden reference audio
        golden_metadata_path: Path to golden metadata JSON
        tolerances: Metric tolerances
        test_id: Test case identifier
        engine: Engine name

    Returns:
        GoldenComparisonReport with comparison results
    """
    timestamp = datetime.utcnow().isoformat()

    # Check if golden files exist
    if not golden_audio_path.exists():
        return GoldenComparisonReport(
            test_id=test_id,
            engine=engine,
            passed=False,
            results=[],
            golden_file=str(golden_audio_path),
            generated_file=str(generated_audio_path) if generated_audio_path.exists() else None,
            timestamp=timestamp,
            error=f"Golden audio file not found: {golden_audio_path}",
        )

    if not golden_metadata_path.exists():
        return GoldenComparisonReport(
            test_id=test_id,
            engine=engine,
            passed=False,
            results=[],
            golden_file=str(golden_audio_path),
            generated_file=str(generated_audio_path) if generated_audio_path.exists() else None,
            timestamp=timestamp,
            error=f"Golden metadata file not found: {golden_metadata_path}",
        )

    if not generated_audio_path.exists():
        return GoldenComparisonReport(
            test_id=test_id,
            engine=engine,
            passed=False,
            results=[],
            golden_file=str(golden_audio_path),
            generated_file=None,
            timestamp=timestamp,
            error=f"Generated audio file not found: {generated_audio_path}",
        )

    try:
        # Load golden metadata
        golden_metadata = json.loads(golden_metadata_path.read_text(encoding="utf-8"))
        expected_metrics = golden_metadata.get("metrics", {})

        # Load and analyze generated audio
        generated_audio, sample_rate = load_audio_as_numpy(generated_audio_path)
        actual_metrics = calculate_metrics(generated_audio, sample_rate)

        # Compare metrics
        results = compare_metrics(actual_metrics, expected_metrics, tolerances)
        all_passed = all(r.passed for r in results)

        return GoldenComparisonReport(
            test_id=test_id,
            engine=engine,
            passed=all_passed,
            results=results,
            golden_file=str(golden_audio_path),
            generated_file=str(generated_audio_path),
            timestamp=timestamp,
        )

    except Exception as e:
        logger.exception(f"Error comparing with golden: {e}")
        return GoldenComparisonReport(
            test_id=test_id,
            engine=engine,
            passed=False,
            results=[],
            golden_file=str(golden_audio_path),
            generated_file=str(generated_audio_path) if generated_audio_path.exists() else None,
            timestamp=timestamp,
            error=str(e),
        )


def update_golden_metadata(
    audio_path: Path,
    metadata_path: Path,
    test_config: dict[str, Any],
    engine: str,
) -> dict[str, Any]:
    """
    Update golden metadata file with current metrics.

    Args:
        audio_path: Path to audio file
        metadata_path: Path to save metadata
        test_config: Test case configuration
        engine: Engine name

    Returns:
        Generated metadata dictionary
    """
    audio, sample_rate = load_audio_as_numpy(audio_path)
    metrics = calculate_metrics(audio, sample_rate)

    metadata = {
        "text": test_config.get("text", ""),
        "engine": engine,
        "voice_profile": test_config.get("voice_profile", "default"),
        "created_at": datetime.utcnow().isoformat(),
        "sample_rate": sample_rate,
        "duration_seconds": len(audio) / sample_rate,
        "metrics": metrics,
    }

    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    logger.info(f"Updated golden metadata: {metadata_path}")

    return metadata
