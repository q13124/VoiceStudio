"""
Video Creator Engine for VoiceStudio
Video creation from images and audio using Video Creator (prakashdk)

Compatible with:
- Python 3.10+
- moviepy 1.0.3+
- PIL/Pillow 9.0.0+
"""

import hashlib
import logging
import os
import shutil
import tempfile
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Import base protocol
try:
    from .protocols import EngineProtocol
except ImportError:
    from .base import EngineProtocol

logger = logging.getLogger(__name__)

# Required imports
try:
    from moviepy.editor import (
        AudioFileClip,
        ImageClip,
        concatenate_audioclips,
        concatenate_videoclips,
    )

    HAS_MOVIEPY = True
except ImportError:
    HAS_MOVIEPY = False
    logger.warning("moviepy not installed. Install with: pip install moviepy>=1.0.3")


class VideoCreatorEngine(EngineProtocol):
    """
    Video Creator Engine for creating videos from images and audio.

    Supports:
    - Video from images and audio
    - Image slideshow creation
    - Audio synchronization
    - Transition effects
    - Image sequencing
    """

    def __init__(
        self,
        device: Optional[str] = None,
        gpu: bool = True,
        enable_cache: bool = True,
        cache_size: int = 100,
        batch_size: int = 4,
    ):
        """
        Initialize Video Creator engine.

        Args:
            device: Device to use (not used,
                kept for protocol compatibility)
            gpu: Whether to use GPU (not used,
                kept for protocol compatibility)
            enable_cache: Enable LRU generation cache
            cache_size: Maximum cache size
            batch_size: Default batch size for parallel processing
        """
        if not HAS_MOVIEPY:
            raise ImportError(
                "moviepy not installed. " "Install with: pip install moviepy>=1.0.3"
            )

        super().__init__(device=device, gpu=gpu)

        # Performance optimizations
        self.enable_cache = enable_cache
        self.cache_size = max(cache_size, 200)  # Increased default cache size
        self.batch_size = max(batch_size, 8)  # Increased default batch size
        self._generation_cache: OrderedDict[str, str] = OrderedDict()
        self._temp_dir = None  # Reusable temp directory
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
        }
        # Image clip pool for reuse (limited pool size)
        self._clip_pool: Dict[str, object] = {}
        self._max_pool_size = 20

    def initialize(self) -> bool:
        """Initialize the Video Creator engine."""
        try:
            if self._initialized:
                return True

            logger.info("Initializing Video Creator engine")

            # Create reusable temp directory
            # (using temp file manager if available)
            try:
                from ..utils.temp_file_manager import get_temp_file_manager

                temp_manager = get_temp_file_manager()
                self._temp_dir = temp_manager.create_temp_directory(
                    prefix="video_creator_", owner="video_creator_engine"
                )
                logger.debug(
                    f"Created temp directory via manager: " f"{self._temp_dir}"
                )
            except Exception as e:
                logger.debug(f"Temp file manager not available, using tempfile: {e}")
                self._temp_dir = tempfile.mkdtemp(prefix="video_creator_")
                logger.debug(f"Created temp directory: {self._temp_dir}")

            self._initialized = True
            logger.info("Video Creator engine initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Video Creator engine: {e}")
            self._initialized = False
            return False

    def cleanup(self):
        """Clean up resources and free memory (enhanced)."""
        try:
            # Clear cache
            if self.enable_cache:
                self._generation_cache.clear()
                self._cache_stats = {"hits": 0, "misses": 0}

            # Cleanup image clip pool
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
                    from ..utils.temp_file_manager import get_temp_file_manager

                    temp_manager = get_temp_file_manager()
                    temp_manager.remove_temp_file(self._temp_dir, force=True)
                    logger.debug(
                        f"Removed temp directory via manager: {self._temp_dir}"
                    )
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
            logger.info("Video Creator engine cleaned up")

        except Exception as e:
            logger.error(f"Error during Video Creator cleanup: {e}")

    def create_video_from_images(
        self,
        image_paths: List[Union[str, Path]],
        audio_path: Optional[Union[str, Path]] = None,
        output_path: Optional[Union[str, Path]] = None,
        duration_per_image: float = 3.0,
        fps: int = 30,
        transition: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Create video from images and optional audio.

        Args:
            image_paths: List of image file paths
            audio_path: Path to audio file (optional)
            output_path: Path to save output video
            duration_per_image: Duration to show each image (seconds)
            fps: Frames per second for output
            transition: Transition effect ('fade', 'crossfade', None)
            **kwargs: Additional parameters

        Returns:
            Path to created video
        """
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError(
                    "Engine not initialized. " "Call initialize() first."
                )

        try:
            # Validate inputs
            if not image_paths:
                raise ValueError("No image paths provided")

            # Check cache (LRU) - optimized
            if self.enable_cache:
                cache_key = self._get_cache_key(
                    "create_video",
                    image_paths,
                    audio_path,
                    duration_per_image,
                    fps,
                    transition,
                    **kwargs,
                )
                if cache_key in self._generation_cache:
                    cached_path = self._generation_cache[cache_key]
                    if os.path.exists(cached_path):
                        logger.debug("Using cached Video Creator generation result")
                        # LRU update
                        self._generation_cache.move_to_end(cache_key)
                        self._cache_stats["hits"] += 1
                        return cached_path
                    else:
                        del self._generation_cache[cache_key]
                else:
                    self._cache_stats["misses"] += 1

            logger.info(f"Creating video from {len(image_paths)} images")

            # Create image clips
            clips = []
            for img_path in image_paths:
                clip = ImageClip(str(img_path), duration=duration_per_image)
                clips.append(clip)

            # Apply transitions if specified
            if transition == "fade":
                clips = [clip.fadein(0.5).fadeout(0.5) for clip in clips]
            elif transition == "crossfade":
                # Crossfade between clips
                for i in range(len(clips) - 1):
                    clips[i] = clips[i].fadeout(0.5)
                    clips[i + 1] = clips[i + 1].fadein(0.5)

            # Concatenate clips
            if len(clips) > 1:
                video = concatenate_videoclips(clips, method="compose")
            else:
                video = clips[0]

            # Add audio if provided
            audio = None
            if audio_path:
                audio = AudioFileClip(str(audio_path))
                # Match audio duration to video
                if audio.duration > video.duration:
                    audio = audio.subclip(0, video.duration)
                elif audio.duration < video.duration:
                    # Loop audio if shorter
                    loops = int(video.duration / audio.duration) + 1
                    audio = concatenate_audioclips([audio] * loops).subclip(
                        0, video.duration
                    )

                video = video.set_audio(audio)

            # Set FPS
            video = video.set_fps(fps)

            # Generate output path (use temp dir if available)
            if output_path is None:
                if self._temp_dir:
                    output_dir = self._temp_dir
                else:
                    output_dir = os.path.join(
                        os.getenv("TEMP", "C:\\Temp"),
                        "VoiceStudio",
                        "video_creator_output",
                    )
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, "created_video.mp4")

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write video
            video.write_videofile(
                str(output_path),
                codec="libx264",
                audio_codec="aac" if audio_path else None,
                fps=fps,
                **kwargs,
            )

            # Cleanup
            video.close()
            if audio:
                audio.close()
            for clip in clips:
                clip.close()

            # Cache result if successful (LRU)
            if self.enable_cache:
                self._cache_result(cache_key, str(output_path))

            logger.info(f"Video created successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error creating video: {e}")
            raise RuntimeError(f"Failed to create video: {e}")

    def create_slideshow(
        self,
        image_paths: List[Union[str, Path]],
        audio_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        fps: int = 30,
        **kwargs,
    ) -> str:
        """
        Create synchronized slideshow from images and audio.

        Args:
            image_paths: List of image file paths
            audio_path: Path to audio file
            output_path: Path to save output video
            fps: Frames per second for output
            **kwargs: Additional parameters

        Returns:
            Path to created slideshow video
        """
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError(
                    "Engine not initialized. " "Call initialize() first."
                )

        try:
            # Load audio to get duration
            audio = AudioFileClip(str(audio_path))
            audio_duration = audio.duration
            audio.close()  # Close immediately to free memory

            # Calculate duration per image
            duration_per_image = audio_duration / len(image_paths)

            logger.info(
                f"Creating slideshow: {len(image_paths)} images, "
                f"{audio_duration:.2f}s audio"
            )

            # Create video with synchronized timing
            return self.create_video_from_images(
                image_paths=image_paths,
                audio_path=audio_path,
                output_path=output_path,
                duration_per_image=duration_per_image,
                fps=fps,
                transition="crossfade",
                **kwargs,
            )

        except Exception as e:
            logger.error(f"Error creating slideshow: {e}")
            raise RuntimeError(f"Failed to create slideshow: {e}")

    def batch_create_videos(
        self,
        videos: List[
            Tuple[
                List[Union[str, Path]],
                Optional[Union[str, Path]],
                Optional[Union[str, Path]],
                Optional[Dict],
            ]
        ],
        batch_size: Optional[int] = None,
    ) -> List[str]:
        """
        Create multiple videos in batch with parallel processing.

        Args:
            videos: List of tuples (image_paths, audio_path,
                output_path, kwargs)
            batch_size: Number of parallel creations
                (default: self.batch_size)

        Returns:
            List of output paths
        """
        if not self._initialized:
            if not self.initialize():
                return []

        actual_batch_size = batch_size if batch_size is not None else self.batch_size

        def create_single(args):
            image_paths, audio_path, output_path, kwargs = args
            try:
                # Record processing time if metrics available
                start_time = time.perf_counter()
                result = self.create_video_from_images(
                    image_paths=image_paths,
                    audio_path=audio_path,
                    output_path=output_path,
                    **(kwargs if kwargs else {}),
                )
                # Record metrics if available
                duration = time.perf_counter() - start_time
                try:
                    from .performance_metrics import get_engine_metrics

                    metrics = get_engine_metrics()
                    metrics.record_synthesis_time(
                        "video_creator", duration, cached=False
                    )
                except Exception:
                    logger.debug(
                        "Performance metrics unavailable for video_creator batch create."
                    )
                return result
            except Exception as e:
                logger.error(f"Batch video creation failed: {e}")
                # Record error if metrics available
                try:
                    from .performance_metrics import get_engine_metrics

                    metrics = get_engine_metrics()
                    metrics.record_error("video_creator", "creation_error")
                except Exception:
                    ...
                return None

        # Optimize batch processing with better chunking
        results = []
        for i in range(0, len(videos), actual_batch_size):
            batch_videos = videos[i : i + actual_batch_size]

            with ThreadPoolExecutor(max_workers=actual_batch_size) as executor:
                batch_results = list(executor.map(create_single, batch_videos))
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
        """Cache generation result with LRU eviction."""
        # Remove if already exists
        if cache_key in self._generation_cache:
            self._generation_cache.move_to_end(cache_key)  # LRU update
            return

        # Add new result
        self._generation_cache[cache_key] = output_path
        self._generation_cache.move_to_end(cache_key)  # LRU update

        # Evict oldest if cache full
        if len(self._generation_cache) > self.cache_size:
            oldest_key, oldest_path = self._generation_cache.popitem(last=False)
            logger.debug(f"Evicted from cache: {oldest_key[:8]}")

    def get_cache_stats(self) -> Dict[str, Union[int, float, str]]:
        """Get cache statistics (enhanced)."""
        total_requests = self._cache_stats["hits"] + self._cache_stats["misses"]
        hit_rate = (
            (self._cache_stats["hits"] / total_requests * 100)
            if total_requests > 0
            else 0.0
        )
        return {
            "cache_size": len(self._generation_cache),
            "max_cache_size": self.cache_size,
            "cache_enabled": self.enable_cache,
            "cache_hits": self._cache_stats["hits"],
            "cache_misses": self._cache_stats["misses"],
            "cache_hit_rate": f"{hit_rate:.2f}%",
        }

    def get_info(self) -> Dict:
        """Get engine information (enhanced)."""
        info = super().get_info()
        info.update(
            {
                "engine_type": "video_creation",
                "has_moviepy": HAS_MOVIEPY,
                "cache_enabled": self.enable_cache,
                "cache_size": len(self._generation_cache),
                "max_cache_size": self.cache_size,
                "batch_size": self.batch_size,
                "clip_pool_size": len(self._clip_pool),
                "max_pool_size": self._max_pool_size,
                "cache_stats": self.get_cache_stats(),
            }
        )
        return info


def create_video_creator_engine(
    device: Optional[str] = None,
    gpu: bool = True,
) -> VideoCreatorEngine:
    """
    Create and initialize Video Creator engine.

    Args:
        device: Device to use (not used, kept for compatibility)
        gpu: Whether to use GPU (not used, kept for compatibility)

    Returns:
        Initialized VideoCreatorEngine instance
    """
    engine = VideoCreatorEngine(device=device, gpu=gpu)
    engine.initialize()
    return engine
