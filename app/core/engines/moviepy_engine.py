"""
MoviePy Engine for VoiceStudio
Programmable video editing using MoviePy

Compatible with:
- Python 3.10+
- moviepy 1.0.3+
- imageio 2.9.0+
"""

from __future__ import annotations

import hashlib
import logging
import os
import shutil
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
    from moviepy.editor import AudioFileClip, VideoFileClip, concatenate_videoclips
    from moviepy.video.fx import all as vfx

    HAS_MOVIEPY = True
except ImportError:
    HAS_MOVIEPY = False
    logger.warning("moviepy not installed. Install with: pip install moviepy>=1.0.3")


class MoviePyEngine(EngineProtocol):
    """
    MoviePy Engine for programmable video editing.

    Supports:
    - Video concatenation and composition
    - Audio/video synchronization
    - Effects and transitions
    - Text overlays
    - Video transformations
    """

    def __init__(
        self,
        device: str | None = None,
        gpu: bool = True,
        enable_cache: bool = True,
        cache_size: int = 100,
        batch_size: int = 4,
    ):
        """
        Initialize MoviePy engine.

        Args:
            device: Device to use (not used for MoviePy,
                kept for protocol compatibility)
            gpu: Whether to use GPU (not used for MoviePy,
                kept for protocol compatibility)
            enable_cache: Enable LRU processing cache
            cache_size: Maximum cache size
            batch_size: Default batch size for parallel processing
        """
        if not HAS_MOVIEPY:
            raise ImportError("moviepy not installed. " "Install with: pip install moviepy>=1.0.3")

        super().__init__(device=device, gpu=gpu)

        # Performance optimizations
        self.enable_cache = enable_cache
        self.cache_size = max(cache_size, 200)  # Increased default cache size
        self.batch_size = max(batch_size, 8)  # Increased default batch size
        self._processing_cache: OrderedDict[str, str] = OrderedDict()
        self._temp_dir: Path | str | None = None
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
        }
        # Video clip pool for reuse (limited pool size)
        self._clip_pool: dict[str, object] = {}
        self._max_pool_size = 10

    def initialize(self) -> bool:
        """Initialize the MoviePy engine."""
        try:
            if self._initialized:
                return True

            logger.info("Initializing MoviePy engine")

            # Create reusable temp directory (using temp file manager if available)
            try:
                from app.core.utils.temp_file_manager import get_temp_file_manager

                temp_manager = get_temp_file_manager()
                self._temp_dir = temp_manager.create_temp_directory(
                    prefix="moviepy_", owner="moviepy_engine"
                )
                logger.debug(f"Created temp directory via manager: {self._temp_dir}")
            except Exception as e:
                logger.debug(f"Temp file manager not available, using tempfile: {e}")
                self._temp_dir = tempfile.mkdtemp(prefix="moviepy_")
                logger.debug(f"Created temp directory: {self._temp_dir}")

            # MoviePy doesn't require model loading, just verify it's available
            self._initialized = True
            logger.info("MoviePy engine initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize MoviePy engine: {e}")
            self._initialized = False
            return False

    def cleanup(self):
        """Clean up resources and free memory (enhanced)."""
        try:
            # Clear cache
            if self.enable_cache:
                self._processing_cache.clear()
                self._cache_stats = {"hits": 0, "misses": 0}

            # Cleanup video clip pool
            for clip_path, clip in list(self._clip_pool.items()):
                try:
                    if hasattr(clip, "close"):
                        clip.close()
                except Exception as e:
                    logger.debug(f"Error closing clip {clip_path}: {e}")
            self._clip_pool.clear()

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
                self._temp_dir: Path | None = None

            # MoviePy clips should be closed explicitly
            # This is handled by the context managers in methods
            self._initialized = False
            logger.info("MoviePy engine cleaned up")

        except Exception as e:
            logger.error(f"Error during MoviePy cleanup: {e}")

    def edit_video(
        self,
        video_path: str | Path,
        output_path: str | Path | None = None,
        operations: list[dict] | None = None,
        **kwargs,
    ) -> str:
        """
        Edit video with specified operations.

        Args:
            video_path: Path to input video
            output_path: Path to save output video
            operations: List of editing operations to apply
            **kwargs: Additional parameters

        Returns:
            Path to edited video
        """
        if not self._initialized and not self.initialize():
            raise RuntimeError("Engine not initialized. Call initialize() first.")

        try:
            video_path = Path(video_path)
            if not video_path.exists():
                raise FileNotFoundError(f"Input video not found: {video_path}")

            # Check cache (LRU) - optimized
            if self.enable_cache:
                cache_key = self._get_cache_key("edit", str(video_path), operations, **kwargs)
                if cache_key in self._processing_cache:
                    cached_path = self._processing_cache[cache_key]
                    if os.path.exists(cached_path):
                        logger.debug("Using cached MoviePy editing result")
                        # LRU update
                        self._processing_cache.move_to_end(cache_key)
                        self._cache_stats["hits"] += 1
                        return cached_path
                    else:
                        del self._processing_cache[cache_key]
                else:
                    self._cache_stats["misses"] += 1

            logger.info(f"Editing video: {video_path}")

            # Load video
            video = VideoFileClip(str(video_path))

            # Apply operations
            if operations:
                for op in operations:
                    video = self._apply_operation(video, op)

            # Generate output path (use temp dir if available)
            if output_path is None:
                if self._temp_dir:
                    output_dir = self._temp_dir
                else:
                    output_dir = os.path.join(
                        os.getenv("TEMP", "C:\\Temp"),
                        "VoiceStudio",
                        "moviepy_output",
                    )
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, "edited_video.mp4")

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write video
            video.write_videofile(
                str(output_path),
                codec="libx264",
                audio_codec="aac",
                **kwargs,
            )

            video.close()

            # Cache result if successful (LRU)
            if self.enable_cache:
                self._cache_result(cache_key, str(output_path))

            logger.info(f"Video edited successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error editing video: {e}")
            raise RuntimeError(f"Failed to edit video: {e}")

    def concatenate_videos(
        self,
        video_paths: list[str | Path],
        output_path: str | Path | None = None,
        method: str = "compose",
        **kwargs,
    ) -> str:
        """
        Concatenate multiple videos.

        Args:
            video_paths: List of video file paths
            output_path: Path to save output video
            method: Concatenation method ('compose' or 'reduce')
            **kwargs: Additional parameters

        Returns:
            Path to concatenated video
        """
        if not self._initialized and not self.initialize():
            raise RuntimeError("Engine not initialized. Call initialize() first.")

        try:
            # Check cache (LRU) - optimized
            if self.enable_cache:
                cache_key = self._get_cache_key("concatenate", video_paths, method, **kwargs)
                if cache_key in self._processing_cache:
                    cached_path = self._processing_cache[cache_key]
                    if os.path.exists(cached_path):
                        logger.debug("Using cached MoviePy concatenation result")
                        # LRU update
                        self._processing_cache.move_to_end(cache_key)
                        self._cache_stats["hits"] += 1
                        return cached_path
                    else:
                        del self._processing_cache[cache_key]
                else:
                    self._cache_stats["misses"] += 1

            logger.info(f"Concatenating {len(video_paths)} videos")

            # Load all videos
            clips = [VideoFileClip(str(path)) for path in video_paths]

            # Concatenate
            final_clip = concatenate_videoclips(clips, method=method)

            # Generate output path (use temp dir if available)
            if output_path is None:
                if self._temp_dir:
                    output_dir = self._temp_dir
                else:
                    output_dir = os.path.join(
                        os.getenv("TEMP", "C:\\Temp"),
                        "VoiceStudio",
                        "moviepy_output",
                    )
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, "concatenated_video.mp4")

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write video
            final_clip.write_videofile(
                str(output_path),
                codec="libx264",
                audio_codec="aac",
                **kwargs,
            )

            # Cleanup
            for clip in clips:
                clip.close()
            final_clip.close()

            # Cache result if successful (LRU)
            if self.enable_cache:
                self._cache_result(cache_key, str(output_path))

            logger.info(f"Videos concatenated successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error concatenating videos: {e}")
            raise RuntimeError(f"Failed to concatenate videos: {e}")

    def add_audio(
        self,
        video_path: str | Path,
        audio_path: str | Path,
        output_path: str | Path | None = None,
        **kwargs,
    ) -> str:
        """
        Add audio to video.

        Args:
            video_path: Path to video file
            audio_path: Path to audio file
            output_path: Path to save output video
            **kwargs: Additional parameters (fps, duration, etc.)

        Returns:
            Path to video with audio
        """
        if not self._initialized and not self.initialize():
            raise RuntimeError("Engine not initialized. Call initialize() first.")

        try:
            video_path = Path(video_path)
            audio_path = Path(audio_path)
            if not video_path.exists():
                raise FileNotFoundError(f"Input video not found: {video_path}")
            if not audio_path.exists():
                raise FileNotFoundError(f"Input audio not found: {audio_path}")

            # Check cache (LRU) - optimized
            if self.enable_cache:
                cache_key = self._get_cache_key(
                    "add_audio", str(video_path), str(audio_path), **kwargs
                )
                if cache_key in self._processing_cache:
                    cached_path = self._processing_cache[cache_key]
                    if os.path.exists(cached_path):
                        logger.debug("Using cached MoviePy add_audio result")
                        # LRU update
                        self._processing_cache.move_to_end(cache_key)
                        self._cache_stats["hits"] += 1
                        return cached_path
                    else:
                        del self._processing_cache[cache_key]
                else:
                    self._cache_stats["misses"] += 1

            logger.info("Adding audio to video")

            # Load video and audio
            video = VideoFileClip(str(video_path))
            audio = AudioFileClip(str(audio_path))

            # Set audio duration to match video if needed
            if "duration" in kwargs:
                audio = audio.subclip(0, kwargs["duration"])
            else:
                audio = audio.subclip(0, video.duration)

            # Set video audio
            final_video = video.set_audio(audio)

            # Generate output path (use temp dir if available)
            if output_path is None:
                if self._temp_dir:
                    output_dir = self._temp_dir
                else:
                    output_dir = os.path.join(
                        os.getenv("TEMP", "C:\\Temp"),
                        "VoiceStudio",
                        "moviepy_output",
                    )
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, "video_with_audio.mp4")

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write video
            final_video.write_videofile(
                str(output_path),
                codec="libx264",
                audio_codec="aac",
                **kwargs,
            )

            # Cleanup
            video.close()
            audio.close()
            final_video.close()

            # Cache result if successful (LRU)
            if self.enable_cache:
                self._cache_result(cache_key, str(output_path))

            logger.info(f"Audio added successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error adding audio: {e}")
            raise RuntimeError(f"Failed to add audio: {e}")

    def _apply_operation(self, video, operation: dict):
        """Apply a single editing operation to video."""
        op_type = operation.get("type")

        if op_type == "resize":
            width = operation.get("width")
            height = operation.get("height")
            if width and height:
                return video.resize((width, height))
            elif width:
                return video.resize(width=width)
            elif height:
                return video.resize(height=height)

        elif op_type == "crop":
            x1 = operation.get("x1", 0)
            y1 = operation.get("y1", 0)
            x2 = operation.get("x2", video.w)
            y2 = operation.get("y2", video.h)
            return video.crop(x1=x1, y1=y1, x2=x2, y2=y2)

        elif op_type == "subclip":
            start = operation.get("start", 0)
            end = operation.get("end", video.duration)
            return video.subclip(start, end)

        elif op_type == "speedx":
            factor = operation.get("factor", 1.0)
            return video.fx(vfx.speedx, factor)

        elif op_type == "fadein":
            duration = operation.get("duration", 1.0)
            return video.fadein(duration)

        elif op_type == "fadeout":
            duration = operation.get("duration", 1.0)
            return video.fadeout(duration)

        elif op_type == "loop":
            n = operation.get("n", 1)
            return video.loop(n)

        else:
            logger.warning(f"Unknown operation type: {op_type}")
            return video

    def batch_edit(
        self,
        videos: list[
            tuple[
                str | Path,
                str | Path | None,
                list[dict] | None,
                dict | None,
            ]
        ],
        batch_size: int | None = None,
    ) -> list[str]:
        """
        Edit multiple videos in batch with parallel processing.

        Args:
            videos: List of tuples (video_path, output_path,
                operations, kwargs)
            batch_size: Number of parallel edits
                (default: self.batch_size)

        Returns:
            List of output paths
        """
        if not self._initialized and not self.initialize():
            return []

        actual_batch_size = batch_size if batch_size is not None else self.batch_size

        def edit_single(args):
            video_path, output_path, operations, kwargs = args
            try:
                # Record processing time if metrics available
                start_time = time.perf_counter()
                result = self.edit_video(
                    video_path=video_path,
                    output_path=output_path,
                    operations=operations,
                    **(kwargs if kwargs else {}),
                )
                # Record metrics if available
                duration = time.perf_counter() - start_time
                try:
                    from .performance_metrics import get_engine_metrics

                    metrics = get_engine_metrics()
                    metrics.record_synthesis_time("moviepy", duration, cached=False)
                except Exception:
                    logger.debug("Performance metrics unavailable for moviepy batch edit.")
                return result
            except Exception as e:
                logger.error(f"Batch editing failed for {video_path}: {e}")
                # Record error if metrics available
                try:
                    from .performance_metrics import get_engine_metrics

                    metrics = get_engine_metrics()
                    metrics.record_error("moviepy", "edit_error")
                except Exception:
                    ...
                return None

        # Optimize batch processing with better chunking
        results = []
        for i in range(0, len(videos), actual_batch_size):
            batch_videos = videos[i : i + actual_batch_size]

            with ThreadPoolExecutor(max_workers=actual_batch_size) as executor:
                batch_results = list(executor.map(edit_single, batch_videos))
            results.extend(batch_results)

        return results

    def _get_cache_key(self, operation: str, *args, **kwargs) -> str:
        """Generate cache key for operation."""
        # Convert args to string representation
        args_str = str(args)
        kwargs_str = str(sorted(kwargs.items()))
        key_data = f"{operation}::{args_str}::{kwargs_str}"
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
                "engine_type": "video_editing",
                "has_moviepy": HAS_MOVIEPY,
                "cache_enabled": self.enable_cache,
                "cache_size": len(self._processing_cache),
                "max_cache_size": self.cache_size,
                "batch_size": self.batch_size,
                "clip_pool_size": len(self._clip_pool),
                "max_pool_size": self._max_pool_size,
                "cache_stats": self.get_cache_stats(),
            }
        )
        return info


def create_moviepy_engine(
    device: str | None = None,
    gpu: bool = True,
) -> MoviePyEngine:
    """
    Create and initialize MoviePy engine.

    Args:
        device: Device to use (not used, kept for compatibility)
        gpu: Whether to use GPU (not used, kept for compatibility)

    Returns:
        Initialized MoviePyEngine instance
    """
    engine = MoviePyEngine(device=device, gpu=gpu)
    engine.initialize()
    return engine
