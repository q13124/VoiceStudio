"""
Optimized Audio Processing Pipeline

High-performance audio processing pipeline with parallel processing,
memory optimization, and batched operations.

Features:
- Parallel preprocessing for multiple files
- Memory-efficient processing
- Batch operations
- Caching of intermediate results
- Progress tracking
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    logger.warning("librosa not installed")

# Import audio utilities
try:
    from .audio_utils import (
        detect_silence,
        enhance_voice_quality,
        normalize_lufs,
        remove_artifacts,
        resample_audio,
    )
    from .enhanced_audio_enhancement import EnhancedAudioEnhancer
    from .enhanced_preprocessing import EnhancedPreprocessor
    HAS_AUDIO_MODULES = True
except ImportError:
    HAS_AUDIO_MODULES = False
    logger.warning("Audio modules not available")


class OptimizedAudioPipeline:
    """
    Optimized audio processing pipeline with parallel processing and memory optimization.

    Features:
    - Parallel processing for multiple files
    - Memory-efficient operations
    - Batch processing
    - Caching
    - Progress tracking
    """

    def __init__(
        self,
        sample_rate: int = 24000,
        max_workers: int | None = None,
        use_multiprocessing: bool = False,
        cache_size: int = 128,
    ):
        """
        Initialize optimized audio pipeline.

        Args:
            sample_rate: Target sample rate
            max_workers: Maximum parallel workers (None = auto)
            use_multiprocessing: Use ProcessPoolExecutor instead of ThreadPoolExecutor
            cache_size: LRU cache size for intermediate results
        """
        self.sample_rate = sample_rate
        self.max_workers = max_workers
        self.use_multiprocessing = use_multiprocessing
        self.cache_size = cache_size

        # Initialize processors
        self.preprocessor = EnhancedPreprocessor(
            sample_rate=sample_rate, target_sample_rate=sample_rate
        ) if HAS_AUDIO_MODULES else None
        self.enhancer = EnhancedAudioEnhancer(sample_rate=sample_rate) if HAS_AUDIO_MODULES else None

        # Cache for intermediate results
        self._cache: dict[str, np.ndarray] = {}

    def process_single(
        self,
        audio: np.ndarray,
        sample_rate: int,
        config: dict | None = None,
        enable_preprocessing: bool = True,
        enable_enhancement: bool = True,
        enable_postprocessing: bool = True,
    ) -> np.ndarray:
        """
        Process a single audio file with optimized pipeline.

        Args:
            audio: Input audio array
            sample_rate: Input sample rate
            config: Processing configuration
            enable_preprocessing: Enable preprocessing stage
            enable_enhancement: Enable enhancement stage
            enable_postprocessing: Enable post-processing stage

        Returns:
            Processed audio array
        """
        if config is None:
            config = {}

        processed = audio.copy()

        # Stage 1: Preprocessing
        if enable_preprocessing and self.preprocessor:
            try:
                preprocess_config = config.get("preprocessing", {})
                processed = self.preprocessor.preprocess(
                    processed, sample_rate=sample_rate, config=preprocess_config
                )
                sample_rate = self.sample_rate  # Preprocessor resamples to target
            except Exception as e:
                logger.warning(f"Preprocessing failed: {e}, continuing without preprocessing")

        # Stage 2: Enhancement
        if enable_enhancement and self.enhancer:
            try:
                enhance_config = config.get("enhancement", {})
                processed = self.enhancer.enhance(
                    processed, sample_rate=sample_rate, config=enhance_config
                )
            except Exception as e:
                logger.warning(f"Enhancement failed: {e}, continuing without enhancement")

        # Stage 3: Post-processing
        if enable_postprocessing:
            try:
                post_config = config.get("postprocessing", {})

                # Normalize if requested
                if post_config.get("normalize", True):
                    target_lufs = post_config.get("target_lufs", -23.0)
                    processed = normalize_lufs(processed, sample_rate, target_lufs=target_lufs)

                # Remove artifacts if requested
                if post_config.get("remove_artifacts", True):
                    processed = remove_artifacts(processed, sample_rate)

            except Exception as e:
                logger.warning(f"Post-processing failed: {e}, continuing without post-processing")

        return processed

    def process_batch(
        self,
        audio_files: list[np.ndarray | tuple[np.ndarray, int]],
        config: dict | None = None,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> list[np.ndarray]:
        """
        Process multiple audio files in parallel.

        Args:
            audio_files: List of audio arrays or (audio, sample_rate) tuples
            config: Processing configuration
            progress_callback: Optional callback(completed, total)

        Returns:
            List of processed audio arrays
        """
        if not audio_files:
            return []

        # Normalize input format
        normalized_inputs = []
        for item in audio_files:
            if isinstance(item, tuple):
                audio, sample_rate = item
            else:
                audio = item
                sample_rate = self.sample_rate
            normalized_inputs.append((audio, sample_rate))

        # Determine executor type
        executor_class = ProcessPoolExecutor if self.use_multiprocessing else ThreadPoolExecutor
        max_workers = self.max_workers or min(len(normalized_inputs), 4)

        results = [None] * len(normalized_inputs)

        with executor_class(max_workers=max_workers) as executor:
            # Submit all tasks
            futures = {
                executor.submit(
                    self.process_single,
                    audio,
                    sample_rate,
                    config,
                ): idx
                for idx, (audio, sample_rate) in enumerate(normalized_inputs)
            }

            # Collect results
            completed = 0
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    results[idx] = future.result()
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, len(normalized_inputs))
                except Exception as e:
                    logger.error(f"Failed to process audio {idx}: {e}")
                    # Use original audio as fallback
                    results[idx] = normalized_inputs[idx][0]

        return results

    def process_file(
        self,
        file_path: str | Path,
        output_path: str | Path | None = None,
        config: dict | None = None,
    ) -> np.ndarray:
        """
        Process audio file from disk.

        Args:
            file_path: Input file path
            output_path: Optional output file path
            config: Processing configuration

        Returns:
            Processed audio array
        """
        if not HAS_LIBROSA:
            raise ImportError("librosa is required for file processing")

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        # Load audio
        audio, sample_rate = librosa.load(str(file_path), sr=None, mono=False)

        # Process
        processed = self.process_single(audio, sample_rate, config)

        # Save if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                import soundfile as sf
                sf.write(str(output_path), processed.T, self.sample_rate)
            except ImportError:
                logger.warning("soundfile not available, cannot save audio")

        return processed

    def process_files_parallel(
        self,
        file_paths: list[str | Path],
        output_dir: str | Path | None = None,
        config: dict | None = None,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> list[np.ndarray]:
        """
        Process multiple audio files in parallel from disk.

        Args:
            file_paths: List of input file paths
            output_dir: Optional output directory
            config: Processing configuration
            progress_callback: Optional callback(completed, total)

        Returns:
            List of processed audio arrays
        """
        if not HAS_LIBROSA:
            raise ImportError("librosa is required for file processing")

        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

        # Load all files first (can be parallelized)
        def load_file(file_path: Path) -> tuple[np.ndarray, int]:
            audio, sample_rate = librosa.load(str(file_path), sr=None, mono=False)
            return audio, sample_rate

        max_workers = self.max_workers or min(len(file_paths), 4)
        executor_class = ProcessPoolExecutor if self.use_multiprocessing else ThreadPoolExecutor

        # Load files in parallel
        loaded_audio = []
        with executor_class(max_workers=max_workers) as executor:
            futures = {
                executor.submit(load_file, Path(fp)): idx
                for idx, fp in enumerate(file_paths)
            }

            loaded_audio = [None] * len(file_paths)
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    loaded_audio[idx] = future.result()
                except Exception as e:
                    logger.error(f"Failed to load file {file_paths[idx]}: {e}")
                    loaded_audio[idx] = None

        # Filter out failed loads
        valid_audio = [(audio, sr) for audio, sr in loaded_audio if audio is not None]

        # Process in parallel
        processed = self.process_batch(valid_audio, config, progress_callback)

        # Save if output directory provided
        if output_dir:
            try:
                import soundfile as sf
                for idx, (file_path, processed_audio) in enumerate(zip(file_paths, processed, strict=False)):
                    if processed_audio is not None:
                        output_path = output_dir / Path(file_path).name
                        sf.write(str(output_path), processed_audio.T, self.sample_rate)
            except ImportError:
                logger.warning("soundfile not available, cannot save audio")

        return processed

    def optimize_memory(self):
        """Optimize memory usage by clearing caches."""
        self._cache.clear()
        if hasattr(self, 'preprocessor') and self.preprocessor:
            # Clear any caches in preprocessor
            ...
        if hasattr(self, 'enhancer') and self.enhancer:
            # Clear any caches in enhancer
            ...
        logger.debug("Memory optimization: caches cleared")


# Factory function
def create_optimized_pipeline(
    sample_rate: int = 24000,
    max_workers: int | None = None,
    use_multiprocessing: bool = False,
) -> OptimizedAudioPipeline:
    """
    Create optimized audio processing pipeline.

    Args:
        sample_rate: Target sample rate
        max_workers: Maximum parallel workers
        use_multiprocessing: Use multiprocessing instead of threading

    Returns:
        OptimizedAudioPipeline instance
    """
    return OptimizedAudioPipeline(
        sample_rate=sample_rate,
        max_workers=max_workers,
        use_multiprocessing=use_multiprocessing,
    )


# Export
__all__ = ["OptimizedAudioPipeline", "create_optimized_pipeline"]

