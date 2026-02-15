"""
Engine Hooks System
Pre and post hooks for engine lifecycle events
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class HookRegistry:
    """Registry for engine hooks."""

    def __init__(self):
        self.pre_hooks: dict[str, list[Callable]] = {}
        self.post_hooks: dict[str, list[Callable]] = {}
        self._register_builtin_hooks()

    def _register_builtin_hooks(self):
        """Register built-in hooks."""
        self.register_pre_hook("ensure_models", self._ensure_models)
        self.register_pre_hook("prepare_workspace", self._prepare_workspace)
        self.register_post_hook("collect_artifacts", self._collect_artifacts)
        self.register_post_hook("thumbnail", self._thumbnail)

    def register_pre_hook(self, name: str, func: Callable):
        """Register a pre-hook."""
        if name not in self.pre_hooks:
            self.pre_hooks[name] = []
        self.pre_hooks[name].append(func)
        logger.debug(f"Registered pre-hook: {name}")

    def register_post_hook(self, name: str, func: Callable):
        """Register a post-hook."""
        if name not in self.post_hooks:
            self.post_hooks[name] = []
        self.post_hooks[name].append(func)
        logger.debug(f"Registered post-hook: {name}")

    def execute_pre_hooks(self, hook_names: list[str], context: dict[str, Any]) -> bool:
        """
        Execute pre-hooks.

        Args:
            hook_names: List of hook names to execute
            context: Context dictionary

        Returns:
            True if all hooks succeeded, False otherwise
        """
        for hook_name in hook_names:
            if hook_name not in self.pre_hooks:
                logger.warning(f"Pre-hook not found: {hook_name}")
                continue

            for hook_func in self.pre_hooks[hook_name]:
                try:
                    logger.info(f"Executing pre-hook: {hook_name}")
                    result = hook_func(context)
                    if result is False:
                        logger.error(f"Pre-hook {hook_name} failed")
                        return False
                except Exception as e:
                    logger.error(f"Pre-hook {hook_name} raised exception: {e}")
                    return False

        return True

    def execute_post_hooks(self, hook_names: list[str], context: dict[str, Any]) -> bool:
        """
        Execute post-hooks.

        Args:
            hook_names: List of hook names to execute
            context: Context dictionary

        Returns:
            True if all hooks succeeded, False otherwise
        """
        for hook_name in hook_names:
            if hook_name not in self.post_hooks:
                logger.warning(f"Post-hook not found: {hook_name}")
                continue

            for hook_func in self.post_hooks[hook_name]:
                try:
                    logger.info(f"Executing post-hook: {hook_name}")
                    result = hook_func(context)
                    if result is False:
                        logger.error(f"Post-hook {hook_name} failed")
                        return False
                except Exception as e:
                    logger.error(f"Post-hook {hook_name} raised exception: {e}")
                    return False

        return True

    # Built-in hooks

    def _ensure_models(self, context: dict[str, Any]) -> bool:
        """Ensure required models are downloaded."""
        manifest = context.get("manifest", {})
        model_paths = manifest.get("model_paths", {})

        for _path_key, path_value in model_paths.items():
            # Expand environment variables
            path = os.path.expandvars(path_value)
            path_obj = Path(path)

            if not path_obj.exists():
                logger.warning(f"Model path does not exist: {path}")
                # Could trigger model download here
                # For now, just warn
                # return False  # Uncomment to fail if models missing

        return True

    def _prepare_workspace(self, context: dict[str, Any]) -> bool:
        """Prepare workspace directories."""
        manifest = context.get("manifest", {})
        workspace_root = context.get("workspace_root", ".")

        # Create required directories
        required_dirs = manifest.get("workspace", {}).get("directories", [])

        for dir_path in required_dirs:
            # Expand environment variables
            dir_path = os.path.expandvars(dir_path)
            dir_obj = Path(workspace_root) / dir_path
            dir_obj.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Prepared workspace directory: {dir_obj}")

        return True

    def _collect_artifacts(self, context: dict[str, Any]) -> bool:
        """Collect artifacts from job execution."""
        output_path = context.get("output_path")
        artifacts = context.get("artifacts", [])

        if not output_path:
            return True  # No output to collect

        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Move/copy artifacts to output directory
        for artifact in artifacts:
            source = Path(artifact.get("source"))
            target = output_dir / artifact.get("target", source.name)

            if source.exists():
                # Copy artifact
                import shutil
                shutil.copy2(source, target)
                logger.debug(f"Collected artifact: {source} -> {target}")

        return True

    def _thumbnail(self, context: dict[str, Any]) -> bool:
        """
        Generate thumbnail for output based on file type.

        Supports:
        - Audio files: Generate waveform thumbnail
        - Image files: Generate resized thumbnail
        - Video files: Extract frame thumbnail
        """
        output_path = context.get("output_path")

        if not output_path:
            return True  # No output to thumbnail

        output_file = Path(output_path)
        if not output_file.exists():
            logger.warning(f"Output file not found for thumbnail: {output_path}")
            return True

        # Determine thumbnail path
        thumbnail_dir = output_file.parent / "thumbnails"
        thumbnail_dir.mkdir(parents=True, exist_ok=True)
        thumbnail_path = thumbnail_dir / f"{output_file.stem}_thumb.png"

        try:
            file_ext = output_file.suffix.lower()

            # Audio files - generate waveform
            if file_ext in ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac']:
                return self._generate_audio_thumbnail(output_file, thumbnail_path)

            # Image files - generate resized thumbnail
            elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
                return self._generate_image_thumbnail(output_file, thumbnail_path)

            # Video files - extract frame
            elif file_ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']:
                return self._generate_video_thumbnail(output_file, thumbnail_path)

            else:
                logger.debug(f"Thumbnail generation not supported for file type: {file_ext}")
                return True

        except Exception as e:
            logger.warning(f"Failed to generate thumbnail for {output_path}: {e}")
            return True  # Don't fail the hook if thumbnail generation fails

    def _generate_audio_thumbnail(self, audio_path: Path, thumbnail_path: Path) -> bool:
        """Generate waveform thumbnail for audio file."""
        try:
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            import matplotlib.pyplot as plt

            # Try loading audio
            try:
                import librosa
                audio, sr = librosa.load(str(audio_path), sr=None, duration=30)  # Limit to 30s
            except ImportError:
                try:
                    import soundfile as sf
                    audio, sr = sf.read(str(audio_path))
                    # Limit to 30 seconds
                    max_samples = int(sr * 30)
                    if len(audio) > max_samples:
                        audio = audio[:max_samples]
                except ImportError:
                    logger.warning("No audio library available for thumbnail generation")
                    return True

            # Generate waveform
            fig, ax = plt.subplots(figsize=(4, 2), dpi=100)
            ax.plot(audio, linewidth=0.5, color='blue')
            ax.axis('off')
            ax.set_xlim(0, len(audio))
            fig.tight_layout(pad=0)

            # Save thumbnail
            fig.savefig(str(thumbnail_path), bbox_inches='tight', pad_inches=0, dpi=100)
            plt.close(fig)

            logger.debug(f"Generated audio thumbnail: {thumbnail_path}")
            return True

        except Exception as e:
            logger.warning(f"Failed to generate audio thumbnail: {e}")
            return True

    def _generate_image_thumbnail(self, image_path: Path, thumbnail_path: Path) -> bool:
        """Generate resized thumbnail for image file."""
        try:
            from PIL import Image

            # Open image
            img = Image.open(str(image_path))

            # Calculate thumbnail size (max 200x200, maintain aspect ratio)
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)

            # Save thumbnail
            img.save(str(thumbnail_path), 'PNG')

            logger.debug(f"Generated image thumbnail: {thumbnail_path}")
            return True

        except ImportError:
            logger.debug("PIL/Pillow not available for image thumbnail generation")
            return True
        except Exception as e:
            logger.warning(f"Failed to generate image thumbnail: {e}")
            return True

    def _generate_video_thumbnail(self, video_path: Path, thumbnail_path: Path) -> bool:
        """Extract frame thumbnail from video file."""
        try:
            # Try using imageio-ffmpeg or opencv
            try:
                import imageio
                reader = imageio.get_reader(str(video_path))
                # Get frame at 1 second (or first frame if video is shorter)
                frame = reader.get_data(0)
                reader.close()

                # Save as image
                from PIL import Image
                img = Image.fromarray(frame)
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                img.save(str(thumbnail_path), 'PNG')

                logger.debug(f"Generated video thumbnail: {thumbnail_path}")
                return True

            except ImportError:
                try:
                    import cv2
                    cap = cv2.VideoCapture(str(video_path))
                    ret, frame = cap.read()
                    cap.release()

                    if ret:
                        # Convert BGR to RGB
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                        # Resize
                        height, width = frame_rgb.shape[:2]
                        max_size = 200
                        if width > height:
                            new_width = max_size
                            new_height = int(height * (max_size / width))
                        else:
                            new_height = max_size
                            new_width = int(width * (max_size / height))

                        frame_resized = cv2.resize(frame_rgb, (new_width, new_height))

                        # Save
                        from PIL import Image
                        img = Image.fromarray(frame_resized)
                        img.save(str(thumbnail_path), 'PNG')

                        logger.debug(f"Generated video thumbnail: {thumbnail_path}")
                        return True

                except ImportError:
                    logger.debug("No video library available for thumbnail generation")
                    return True

        except Exception as e:
            logger.warning(f"Failed to generate video thumbnail: {e}")
            return True


# Global hook registry
_hook_registry: HookRegistry | None = None


def get_hook_registry() -> HookRegistry:
    """Get or create global hook registry."""
    global _hook_registry
    if _hook_registry is None:
        _hook_registry = HookRegistry()
    return _hook_registry

