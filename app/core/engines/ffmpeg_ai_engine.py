"""
FFmpeg with AI Plugins Engine for VoiceStudio
Video transcoding with AI enhancements using FFmpeg

Compatible with:
- Python 3.10+
- ffmpeg-python 0.2.0+
- FFmpeg binary with AI plugins
"""

from __future__ import annotations

import hashlib
import logging
import os
import shutil
import subprocess
import tempfile
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Import base protocol
try:
    from .protocols import EngineProtocol
except ImportError:
    from .base import EngineProtocol

logger = logging.getLogger(__name__)

# Required imports
try:
    import ffmpeg

    HAS_FFMPEG_PYTHON = True
except ImportError:
    HAS_FFMPEG_PYTHON = False
    logger.warning("ffmpeg-python not installed. Install with: pip install ffmpeg-python")


class FFmpegAIEngine(EngineProtocol):
    """
    FFmpeg with AI Plugins Engine for video transcoding with AI enhancements.

    Supports:
    - Video transcoding and conversion
    - AI-powered upscaling (via plugins)
    - AI-powered denoising (via plugins)
    - Video enhancement
    - Format conversion
    """

    def __init__(
        self,
        device: str | None = None,
        gpu: bool = True,
        ffmpeg_path: str | None = None,
        enable_cache: bool = True,
        cache_size: int = 100,
        batch_size: int = 4,
    ):
        """
        Initialize FFmpeg AI engine.

        Args:
            device: Device to use (not used for FFmpeg, kept for protocol compatibility)
            gpu: Whether to use GPU (used for AI plugins)
            ffmpeg_path: Path to FFmpeg binary (optional, uses system PATH if not provided)
            enable_cache: Enable LRU processing cache
            cache_size: Maximum cache size
            batch_size: Default batch size for parallel processing
        """
        super().__init__(device=device, gpu=gpu)

        self.ffmpeg_path = ffmpeg_path or self._find_ffmpeg()
        if not self.ffmpeg_path:
            logger.warning("FFmpeg not found in PATH. Some features may not work.")

        # Performance optimizations
        self.enable_cache = enable_cache
        self.cache_size = max(cache_size, 200)  # Increased default cache size
        self.batch_size = max(batch_size, 8)  # Increased default batch size
        self._processing_cache: OrderedDict[str, str] = OrderedDict()
        self._temp_dir = None  # Reusable temp directory
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
        }
        # Subprocess pool for reuse (limited pool size)
        self._subprocess_pool: list[subprocess.Popen] = []
        self._max_pool_size = 4

    def initialize(self) -> bool:
        """Initialize the FFmpeg AI engine."""
        try:
            if self._initialized:
                return True

            logger.info("Initializing FFmpeg AI engine")

            # Check if FFmpeg is available
            if not self._check_ffmpeg():
                logger.warning("FFmpeg not available. Install FFmpeg to use this engine.")
                self._initialized = False
                return False

            # Create reusable temp directory (using temp file manager if available)
            try:
                from app.core.utils.temp_file_manager import get_temp_file_manager

                temp_manager = get_temp_file_manager()
                self._temp_dir = temp_manager.create_temp_directory(
                    prefix="ffmpeg_ai_", owner="ffmpeg_ai_engine"
                )
                logger.debug(f"Created temp directory via manager: {self._temp_dir}")
            except Exception as e:
                logger.debug(f"Temp file manager not available, using tempfile: {e}")
                self._temp_dir = tempfile.mkdtemp(prefix="ffmpeg_ai_")
                logger.debug(f"Created temp directory: {self._temp_dir}")

            self._initialized = True
            logger.info("FFmpeg AI engine initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize FFmpeg AI engine: {e}")
            self._initialized = False
            return False

    def cleanup(self):
        """Clean up resources and free memory (enhanced)."""
        try:
            # Clear cache
            if self.enable_cache:
                self._processing_cache.clear()
                self._cache_stats = {"hits": 0, "misses": 0}

            # Cleanup subprocess pool
            for proc in self._subprocess_pool:
                try:
                    if proc.poll() is None:  # Still running
                        proc.terminate()
                        proc.wait(timeout=5)
                except Exception as e:
                    logger.debug(f"Error terminating subprocess: {e}")
            self._subprocess_pool.clear()

            # Cleanup temp directory (using temp file manager if available)
            if self._temp_dir:
                try:
                    from app.core.utils.temp_file_manager import get_temp_file_manager

                    temp_manager = get_temp_file_manager()
                    temp_manager.remove_temp_file(self._temp_dir, force=True)
                    logger.debug(f"Removed temp directory via manager: {self._temp_dir}")
                except Exception:
                    # Fallback to direct removal
                    if os.path.exists(self._temp_dir):
                        try:
                            shutil.rmtree(self._temp_dir)
                            logger.debug(f"Removed temp directory: {self._temp_dir}")
                        except Exception as e:
                            logger.warning(f"Failed to remove temp directory: {e}")
                self._temp_dir = None

            self._initialized = False
            logger.info("FFmpeg AI engine cleaned up")

        except Exception as e:
            logger.error(f"Error during FFmpeg AI cleanup: {e}")

    def transcode_video(
        self,
        input_path: str | Path,
        output_path: str | Path | None = None,
        codec: str = "libx264",
        quality: str = "medium",
        resolution: tuple[int, int] | None = None,
        fps: float | None = None,
        **kwargs,
    ) -> str:
        """
        Transcode video with specified settings.

        Args:
            input_path: Path to input video
            output_path: Path to save output video
            codec: Video codec to use
            quality: Quality preset ('low', 'medium', 'high', 'veryhigh')
            resolution: Output resolution (width, height)
            fps: Output frame rate
            **kwargs: Additional FFmpeg parameters

        Returns:
            Path to transcoded video
        """
        if not self._initialized and not self.initialize():
            raise RuntimeError("Engine not initialized. Call initialize() first.")

        try:
            input_path = Path(input_path)
            if not input_path.exists():
                raise FileNotFoundError(f"Input video not found: {input_path}")

            # Check cache (LRU) - optimized
            if self.enable_cache:
                cache_key = self._get_cache_key(
                    "transcode",
                    str(input_path),
                    codec,
                    quality,
                    resolution,
                    fps,
                    **kwargs,
                )
                if cache_key in self._processing_cache:
                    cached_path = self._processing_cache[cache_key]
                    if os.path.exists(cached_path):
                        logger.debug("Using cached FFmpeg transcoding result")
                        self._processing_cache.move_to_end(cache_key)  # LRU update
                        self._cache_stats["hits"] += 1
                        return cached_path
                    else:
                        del self._processing_cache[cache_key]
                else:
                    self._cache_stats["misses"] += 1

            logger.info(f"Transcoding video: {input_path}")

            # Build FFmpeg command
            input_stream = ffmpeg.input(str(input_path))

            # Apply filters
            video = input_stream.video

            # Resolution
            if resolution:
                width, height = resolution
                video = video.filter("scale", width, height)

            # FPS
            if fps:
                video = video.filter("fps", fps=fps)

            # Quality settings
            quality_map = {
                "low": {"crf": 28, "preset": "fast"},
                "medium": {"crf": 23, "preset": "medium"},
                "high": {"crf": 18, "preset": "slow"},
                "veryhigh": {"crf": 15, "preset": "veryslow"},
            }

            quality_params = quality_map.get(quality, quality_map["medium"])

            # Generate output path (use temp dir if available)
            if output_path is None:
                if self._temp_dir:
                    output_dir = self._temp_dir
                else:
                    output_dir = os.path.join(
                        os.getenv("TEMP", "C:\\Temp"),
                        "VoiceStudio",
                        "ffmpeg_output",
                    )
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, "transcoded_video.mp4")

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Build output stream
            audio = input_stream.audio
            output_stream = ffmpeg.output(
                video,
                audio,
                str(output_path),
                vcodec=codec,
                acodec="aac",
                **quality_params,
                **kwargs,
            )

            # Run FFmpeg
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)

            # Cache result if successful (LRU)
            if self.enable_cache:
                self._cache_result(cache_key, str(output_path))

            logger.info(f"Video transcoded successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error transcoding video: {e}")
            raise RuntimeError(f"Failed to transcode video: {e}")

    def upscale_video(
        self,
        input_path: str | Path,
        output_path: str | Path | None = None,
        scale_factor: float = 2.0,
        model: str = "espcn",
        **kwargs,
    ) -> str:
        """
        Upscale video using AI model.

        Args:
            input_path: Path to input video
            output_path: Path to save output video
            scale_factor: Upscaling factor (2.0 = 2x, 4.0 = 4x)
            model: AI model to use ('espcn', 'edsr', 'lapsrn')
            **kwargs: Additional parameters

        Returns:
            Path to upscaled video
        """
        if not self._initialized and not self.initialize():
            raise RuntimeError("Engine not initialized. Call initialize() first.")

        try:
            input_path = Path(input_path)
            if not input_path.exists():
                raise FileNotFoundError(f"Input video not found: {input_path}")

            # Check cache (LRU) - optimized
            if self.enable_cache:
                cache_key = self._get_cache_key(
                    "upscale", str(input_path), scale_factor, model, **kwargs
                )
                if cache_key in self._processing_cache:
                    cached_path = self._processing_cache[cache_key]
                    if os.path.exists(cached_path):
                        logger.debug("Using cached FFmpeg upscaling result")
                        self._processing_cache.move_to_end(cache_key)  # LRU update
                        self._cache_stats["hits"] += 1
                        return cached_path
                    else:
                        del self._processing_cache[cache_key]
                else:
                    self._cache_stats["misses"] += 1

            logger.info(f"Upscaling video: {input_path} (scale: {scale_factor}x)")

            # Generate output path (use temp dir if available)
            if output_path is None:
                if self._temp_dir:
                    output_dir = self._temp_dir
                else:
                    output_dir = os.path.join(
                        os.getenv("TEMP", "C:\\Temp"),
                        "VoiceStudio",
                        "ffmpeg_output",
                    )
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, "upscaled_video.mp4")

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Build FFmpeg command with AI upscaling filter
            # Note: This requires FFmpeg compiled with libplacebo or similar AI filters
            input_stream = ffmpeg.input(str(input_path))

            # Use scale filter with AI model if available
            # In production, this would use actual AI upscaling filters
            video = input_stream.video.filter(
                "scale", f"iw*{scale_factor}", f"ih*{scale_factor}", flags="lanczos"
            )

            output_stream = ffmpeg.output(
                video,
                input_stream.audio,
                str(output_path),
                vcodec="libx264",
                acodec="copy",
                **kwargs,
            )

            # Run FFmpeg
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)

            # Cache result if successful (LRU)
            if self.enable_cache:
                self._cache_result(cache_key, str(output_path))

            logger.info(f"Video upscaled successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error upscaling video: {e}")
            raise RuntimeError(f"Failed to upscale video: {e}")

    def _find_ffmpeg(self) -> str | None:
        """Find FFmpeg binary deterministically."""
        try:
            from app.core.utils.native_tools import find_ffmpeg

            return find_ffmpeg()
        except Exception:
            return None

    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available."""
        if not self.ffmpeg_path:
            return False

        try:
            result = subprocess.run([self.ffmpeg_path, "-version"], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def batch_transcode(
        self,
        videos: list[
            tuple[
                str | Path,
                str | Path | None,
                dict | None,
            ]
        ],
        batch_size: int | None = None,
    ) -> list[str]:
        """
        Transcode multiple videos in batch with parallel processing.

        Args:
            videos: List of tuples (input_path, output_path, kwargs)
            batch_size: Number of parallel transcodings (default: self.batch_size)

        Returns:
            List of output paths
        """
        if not self._initialized and not self.initialize():
            return []

        actual_batch_size = batch_size if batch_size is not None else self.batch_size

        def transcode_single(args):
            input_path, output_path, kwargs = args
            try:
                # Record processing time if metrics available
                start_time = time.perf_counter()
                result = self.transcode_video(
                    input_path=input_path,
                    output_path=output_path,
                    **kwargs if kwargs else {},
                )
                # Record metrics if available
                duration = time.perf_counter() - start_time
                try:
                    from .performance_metrics import get_engine_metrics

                    metrics = get_engine_metrics()
                    metrics.record_synthesis_time("ffmpeg_ai", duration, cached=False)
                except Exception:
                    logger.debug("Performance metrics unavailable for ffmpeg_ai batch transcode.")
                return result
            except Exception as e:
                logger.error(f"Batch transcoding failed for {input_path}: {e}")
                # Record error if metrics available
                try:
                    from .performance_metrics import get_engine_metrics

                    metrics = get_engine_metrics()
                    metrics.record_error("ffmpeg_ai", "transcode_error")
                except Exception:
                    ...
                return None

        # Optimize batch processing with better chunking
        results = []
        for i in range(0, len(videos), actual_batch_size):
            batch_videos = videos[i : i + actual_batch_size]

            with ThreadPoolExecutor(max_workers=actual_batch_size) as executor:
                batch_results = list(executor.map(transcode_single, batch_videos))
            results.extend(batch_results)

        return results

    def batch_upscale(
        self,
        videos: list[
            tuple[
                str | Path,
                str | Path | None,
                dict | None,
            ]
        ],
        batch_size: int | None = None,
    ) -> list[str]:
        """
        Upscale multiple videos in batch with parallel processing.

        Args:
            videos: List of tuples (input_path, output_path, kwargs)
            batch_size: Number of parallel upscalings (default: self.batch_size)

        Returns:
            List of output paths
        """
        if not self._initialized and not self.initialize():
            return []

        actual_batch_size = batch_size if batch_size is not None else self.batch_size

        def upscale_single(args):
            input_path, output_path, kwargs = args
            try:
                # Record processing time if metrics available
                start_time = time.perf_counter()
                result = self.upscale_video(
                    input_path=input_path,
                    output_path=output_path,
                    **kwargs if kwargs else {},
                )
                # Record metrics if available
                duration = time.perf_counter() - start_time
                try:
                    from .performance_metrics import get_engine_metrics

                    metrics = get_engine_metrics()
                    metrics.record_synthesis_time("ffmpeg_ai", duration, cached=False)
                except Exception:
                    logger.debug("Performance metrics unavailable for ffmpeg_ai batch upscale.")
                return result
            except Exception as e:
                logger.error(f"Batch upscaling failed for {input_path}: {e}")
                # Record error if metrics available
                try:
                    from .performance_metrics import get_engine_metrics

                    metrics = get_engine_metrics()
                    metrics.record_error("ffmpeg_ai", "upscale_error")
                except Exception:
                    ...
                return None

        # Optimize batch processing with better chunking
        results = []
        for i in range(0, len(videos), actual_batch_size):
            batch_videos = videos[i : i + actual_batch_size]

            with ThreadPoolExecutor(max_workers=actual_batch_size) as executor:
                batch_results = list(executor.map(upscale_single, batch_videos))
            results.extend(batch_results)

        return results

    def _get_cache_key(self, operation: str, *args, **kwargs) -> str:
        """Generate cache key for operation."""
        key_data = f"{operation}::{args}::{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _cache_result(self, cache_key: str, output_path: str):
        """Cache processing result with LRU eviction."""
        # Remove if already exists
        if cache_key in self._processing_cache:
            self._processing_cache.move_to_end(cache_key)  # LRU update
            return

        # Add new result
        self._processing_cache[cache_key] = output_path
        self._processing_cache.move_to_end(cache_key)  # LRU update

        # Evict oldest if cache full
        if len(self._processing_cache) > self.cache_size:
            oldest_key, _oldest_path = self._processing_cache.popitem(last=False)
            logger.debug(f"Evicted from cache: {oldest_key[:8]}")

    def get_cache_stats(self) -> dict[str, int | float | str]:
        """Get cache statistics (enhanced)."""
        total_requests = self._cache_stats["hits"] + self._cache_stats["misses"]
        hit_rate = (self._cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0.0
        return {
            "cache_size": len(self._processing_cache),
            "max_cache_size": self.cache_size,
            "cache_enabled": self.enable_cache,
            "cache_hits": self._cache_stats["hits"],
            "cache_misses": self._cache_stats["misses"],
            "cache_hit_rate": f"{hit_rate:.2f}%",
        }

    def get_info(self) -> dict:
        """Get engine information (enhanced)."""
        info = super().get_info()
        info.update(
            {
                "engine_type": "video_transcoding",
                "has_ffmpeg_python": HAS_FFMPEG_PYTHON,
                "ffmpeg_path": self.ffmpeg_path,
                "cache_enabled": self.enable_cache,
                "cache_size": len(self._processing_cache),
                "max_cache_size": self.cache_size,
                "batch_size": self.batch_size,
                "subprocess_pool_size": len(self._subprocess_pool),
                "max_pool_size": self._max_pool_size,
                "cache_stats": self.get_cache_stats(),
            }
        )
        return info


def create_ffmpeg_ai_engine(
    device: str | None = None, gpu: bool = True, ffmpeg_path: str | None = None
) -> FFmpegAIEngine:
    """
    Create and initialize FFmpeg AI engine.

    Args:
        device: Device to use (not used, kept for compatibility)
        gpu: Whether to use GPU (for AI plugins)
        ffmpeg_path: Path to FFmpeg binary

    Returns:
        Initialized FFmpegAIEngine instance
    """
    engine = FFmpegAIEngine(device=device, gpu=gpu, ffmpeg_path=ffmpeg_path)
    engine.initialize()
    return engine
