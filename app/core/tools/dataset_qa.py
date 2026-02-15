"""
Dataset QA Module for VoiceStudio
Dataset quality assurance and validation

Compatible with:
- Python 3.10+
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Import audio utilities
try:
    from app.core.audio.audio_utils import (
        analyze_voice_characteristics,
        detect_silence,
        resample_audio,
    )
    from app.core.audio.enhanced_quality_metrics import EnhancedQualityMetrics

    HAS_AUDIO_UTILS = True
except ImportError:
    HAS_AUDIO_UTILS = False
    logger.warning("Audio utilities not available")

# Try to import librosa
try:
    import librosa
    import numpy as np

    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    logger.warning("librosa not available. Some QA checks will be limited.")


class DatasetQA:
    """
    Dataset QA for quality assurance and validation.

    Supports:
    - Audio file validation
    - Quality checks
    - Format validation
    - Duration checks
    - Sample rate validation
    - Silence detection
    - Duplicate detection
    - Dataset statistics
    """

    def __init__(
        self,
        min_duration: float = 1.0,
        max_duration: float = 30.0,
        min_sample_rate: int = 16000,
        max_silence_ratio: float = 0.5,
        quality_threshold: float = 0.5,
    ):
        """
        Initialize Dataset QA.

        Args:
            min_duration: Minimum audio duration in seconds
            max_duration: Maximum audio duration in seconds
            min_sample_rate: Minimum sample rate in Hz
            max_silence_ratio: Maximum ratio of silence allowed
            quality_threshold: Minimum quality score threshold
        """
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.min_sample_rate = min_sample_rate
        self.max_silence_ratio = max_silence_ratio
        self.quality_threshold = quality_threshold

        self.quality_metrics = None
        if HAS_AUDIO_UTILS:
            try:
                self.quality_metrics = EnhancedQualityMetrics()
            except Exception as e:
                logger.warning(f"Failed to initialize quality metrics: {e}")

    def validate_audio_file(
        self, audio_path: str | Path, check_quality: bool = True
    ) -> dict[str, Any]:
        """
        Validate a single audio file.

        Args:
            audio_path: Path to audio file
            check_quality: Whether to perform quality checks

        Returns:
            Dictionary with validation results
        """
        audio_path = Path(audio_path)
        results = {
            "file": str(audio_path),
            "valid": False,
            "errors": [],
            "warnings": [],
            "metadata": {},
            "quality_score": None,
        }

        # Check file exists
        if not audio_path.exists():
            results["errors"].append("File does not exist")
            return results

        # Check file extension
        valid_extensions = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac"}
        if audio_path.suffix.lower() not in valid_extensions:
            results["warnings"].append(
                f"Unusual file extension: {audio_path.suffix}"
            )

        # Load and analyze audio
        if HAS_LIBROSA:
            try:
                audio, sr = librosa.load(str(audio_path), sr=None)
                duration = len(audio) / sr

                results["metadata"] = {
                    "sample_rate": sr,
                    "duration": duration,
                    "channels": 1 if len(audio.shape) == 1 else audio.shape[1],
                    "samples": len(audio),
                }

                # Check duration
                if duration < self.min_duration:
                    results["errors"].append(
                        f"Duration too short: {duration:.2f}s < {self.min_duration}s"
                    )
                elif duration > self.max_duration:
                    results["warnings"].append(
                        f"Duration long: {duration:.2f}s > {self.max_duration}s"
                    )

                # Check sample rate
                if sr < self.min_sample_rate:
                    results["errors"].append(
                        f"Sample rate too low: {sr}Hz < {self.min_sample_rate}Hz"
                    )

                # Check for silence
                if HAS_AUDIO_UTILS:
                    try:
                        silence_regions = detect_silence(audio, sr)
                        silence_duration = sum(
                            end - start for start, end in silence_regions
                        )
                        silence_ratio = silence_duration / duration if duration > 0 else 0.0

                        if silence_ratio > self.max_silence_ratio:
                            results["warnings"].append(
                                f"High silence ratio: {silence_ratio:.2%} > {self.max_silence_ratio:.2%}"
                            )
                    except Exception as e:
                        logger.warning(f"Silence detection failed: {e}")

                # Quality check
                if check_quality and self.quality_metrics:
                    try:
                        quality = self.quality_metrics.calculate_all(
                            audio, sr, include_advanced=False
                        )
                        quality_score = quality.get("overall_quality_score", 0.0)
                        results["quality_score"] = quality_score

                        if quality_score < self.quality_threshold:
                            results["warnings"].append(
                                f"Low quality score: {quality_score:.3f} < {self.quality_threshold}"
                            )
                    except Exception as e:
                        logger.warning(f"Quality check failed: {e}")

            except Exception as e:
                results["errors"].append(f"Failed to load audio: {e!s}")
        else:
            results["warnings"].append(
                "librosa not available, limited validation"
            )

        # File is valid if no errors
        results["valid"] = len(results["errors"]) == 0

        return results

    def validate_dataset(
        self,
        dataset_path: str | Path,
        audio_extensions: list[str] | None = None,
        recursive: bool = True,
        check_quality: bool = True,
    ) -> dict[str, Any]:
        """
        Validate an entire dataset.

        Args:
            dataset_path: Path to dataset directory
            audio_extensions: List of audio file extensions to check
            recursive: Whether to search recursively
            check_quality: Whether to perform quality checks

        Returns:
            Dictionary with dataset validation results
        """
        dataset_path = Path(dataset_path)
        if audio_extensions is None:
            audio_extensions = [".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac"]

        results = {
            "dataset_path": str(dataset_path),
            "timestamp": datetime.utcnow().isoformat(),
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "file_results": [],
            "statistics": {},
            "errors": [],
            "warnings": [],
        }

        if not dataset_path.exists():
            results["errors"].append("Dataset path does not exist")
            return results

        if not dataset_path.is_dir():
            results["errors"].append("Dataset path is not a directory")
            return results

        # Find all audio files
        audio_files = []
        if recursive:
            for ext in audio_extensions:
                audio_files.extend(dataset_path.rglob(f"*{ext}"))
        else:
            for ext in audio_extensions:
                audio_files.extend(dataset_path.glob(f"*{ext}"))

        results["total_files"] = len(audio_files)

        # Validate each file
        valid_count = 0
        invalid_count = 0
        durations = []
        sample_rates = []
        quality_scores = []

        for audio_file in audio_files:
            file_result = self.validate_audio_file(audio_file, check_quality)
            results["file_results"].append(file_result)

            if file_result["valid"]:
                valid_count += 1
            else:
                invalid_count += 1

            # Collect statistics
            if file_result.get("metadata"):
                meta = file_result["metadata"]
                if "duration" in meta:
                    durations.append(meta["duration"])
                if "sample_rate" in meta:
                    sample_rates.append(meta["sample_rate"])

            if file_result.get("quality_score") is not None:
                quality_scores.append(file_result["quality_score"])

        results["valid_files"] = valid_count
        results["invalid_files"] = invalid_count

        # Calculate statistics
        if durations:
            results["statistics"]["duration"] = {
                "min": min(durations),
                "max": max(durations),
                "mean": sum(durations) / len(durations),
                "total": sum(durations),
            }

        if sample_rates:
            results["statistics"]["sample_rate"] = {
                "min": min(sample_rates),
                "max": max(sample_rates),
                "unique": list(set(sample_rates)),
            }

        if quality_scores:
            results["statistics"]["quality"] = {
                "min": min(quality_scores),
                "max": max(quality_scores),
                "mean": sum(quality_scores) / len(quality_scores),
            }

        # Overall warnings
        if invalid_count > 0:
            results["warnings"].append(
                f"{invalid_count} invalid files found in dataset"
            )

        if valid_count == 0:
            results["errors"].append("No valid audio files found in dataset")

        return results

    def check_duplicates(
        self, dataset_path: str | Path, recursive: bool = True
    ) -> dict[str, Any]:
        """
        Check for duplicate audio files in dataset.

        Args:
            dataset_path: Path to dataset directory
            recursive: Whether to search recursively

        Returns:
            Dictionary with duplicate detection results
        """
        dataset_path = Path(dataset_path)
        results = {
            "dataset_path": str(dataset_path),
            "total_files": 0,
            "duplicates": [],
            "unique_files": 0,
        }

        if not dataset_path.exists() or not dataset_path.is_dir():
            return results

        # Find all audio files
        audio_extensions = [".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac"]
        audio_files = []
        if recursive:
            for ext in audio_extensions:
                audio_files.extend(dataset_path.rglob(f"*{ext}"))
        else:
            for ext in audio_extensions:
                audio_files.extend(dataset_path.glob(f"*{ext}"))

        results["total_files"] = len(audio_files)

        # Simple duplicate detection by file size and name
        # In a full implementation, would use audio fingerprinting
        file_sizes = {}
        for audio_file in audio_files:
            size = audio_file.stat().st_size
            if size not in file_sizes:
                file_sizes[size] = []
            file_sizes[size].append(str(audio_file))

        # Find duplicates (same size)
        duplicates = []
        for size, files in file_sizes.items():
            if len(files) > 1:
                duplicates.append({"size": size, "files": files})

        results["duplicates"] = duplicates
        results["unique_files"] = len(audio_files) - sum(
            len(dup["files"]) - 1 for dup in duplicates
        )

        return results

    def generate_report(
        self, validation_results: dict[str, Any], output_path: str | Path | None = None
    ) -> str:
        """
        Generate QA report.

        Args:
            validation_results: Results from validate_dataset
            output_path: Optional output file path

        Returns:
            Report text
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("Dataset QA Report")
        report_lines.append("=" * 80)
        report_lines.append(f"Dataset: {validation_results.get('dataset_path', 'N/A')}")
        report_lines.append(f"Generated: {validation_results.get('timestamp', 'N/A')}")
        report_lines.append("")

        # Summary
        report_lines.append("Summary")
        report_lines.append("-" * 80)
        report_lines.append(f"Total Files: {validation_results.get('total_files', 0)}")
        report_lines.append(f"Valid Files: {validation_results.get('valid_files', 0)}")
        report_lines.append(f"Invalid Files: {validation_results.get('invalid_files', 0)}")
        report_lines.append("")

        # Statistics
        if validation_results.get("statistics"):
            stats = validation_results["statistics"]
            report_lines.append("Statistics")
            report_lines.append("-" * 80)
            if "duration" in stats:
                dur = stats["duration"]
                report_lines.append(f"Duration: {dur.get('min', 0):.2f}s - {dur.get('max', 0):.2f}s (mean: {dur.get('mean', 0):.2f}s)")
                report_lines.append(f"Total Duration: {dur.get('total', 0):.2f}s")
            if "sample_rate" in stats:
                sr = stats["sample_rate"]
                report_lines.append(f"Sample Rate: {sr.get('min', 0)}Hz - {sr.get('max', 0)}Hz")
                report_lines.append(f"Unique Sample Rates: {sr.get('unique', [])}")
            if "quality" in stats:
                qual = stats["quality"]
                report_lines.append(f"Quality Score: {qual.get('min', 0):.3f} - {qual.get('max', 0):.3f} (mean: {qual.get('mean', 0):.3f})")
            report_lines.append("")

        # Errors and warnings
        if validation_results.get("errors"):
            report_lines.append("Errors")
            report_lines.append("-" * 80)
            for error in validation_results["errors"]:
                report_lines.append(f"  - {error}")
            report_lines.append("")

        if validation_results.get("warnings"):
            report_lines.append("Warnings")
            report_lines.append("-" * 80)
            for warning in validation_results["warnings"]:
                report_lines.append(f"  - {warning}")
            report_lines.append("")

        report_text = "\n".join(report_lines)

        # Save to file if requested
        if output_path:
            output_path = Path(output_path)
            output_path.write_text(report_text, encoding="utf-8")
            logger.info(f"Report saved to: {output_path}")

        return report_text


def create_dataset_qa(
    min_duration: float = 1.0,
    max_duration: float = 30.0,
    min_sample_rate: int = 16000,
    max_silence_ratio: float = 0.5,
    quality_threshold: float = 0.5,
) -> DatasetQA:
    """
    Factory function to create a Dataset QA instance.

    Args:
        min_duration: Minimum audio duration in seconds
        max_duration: Maximum audio duration in seconds
        min_sample_rate: Minimum sample rate in Hz
        max_silence_ratio: Maximum ratio of silence allowed
        quality_threshold: Minimum quality score threshold

    Returns:
        Initialized DatasetQA instance
    """
    return DatasetQA(
        min_duration=min_duration,
        max_duration=max_duration,
        min_sample_rate=min_sample_rate,
        max_silence_ratio=max_silence_ratio,
        quality_threshold=quality_threshold,
    )

