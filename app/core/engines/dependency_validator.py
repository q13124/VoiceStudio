"""
Dependency Validator for Engine Initialization
Validates all required dependencies before engine use.
"""

import importlib
import importlib.util
import logging
import sys
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DependencyError(Exception):
    """Raised when a required dependency is missing."""

    def __init__(self, dependency: str, installation_instruction: str):
        self.dependency = dependency
        self.installation_instruction = installation_instruction
        super().__init__(
            f"Required dependency '{dependency}' is not installed. "
            f"Install with: {installation_instruction}"
        )


class DependencyValidator:
    """Validates engine dependencies before initialization."""

    # Engine dependency requirements
    ENGINE_DEPENDENCIES = {
        "xtts": {
            "required": [
                ("TTS", "coqui-tts==0.27.2"),
                ("torch", "torch>=2.0.0"),
                ("transformers", "transformers>=4.55.4"),
            ],
            "optional": [
                ("soundfile", "soundfile"),
                ("librosa", "librosa"),
            ],
        },
        "whisper": {
            "required": [
                ("faster_whisper", "faster-whisper==1.0.3"),
            ],
            "optional": [
                ("soundfile", "soundfile"),
            ],
        },
        "rvc": {
            "required": [
                ("torch", "torch>=2.0.0"),
                ("numpy", "numpy"),
            ],
            "optional": [
                ("librosa", "librosa"),
                ("soundfile", "soundfile"),
            ],
        },
        "deepfacelab": {
            "required": [
                ("cv2", "opencv-python>=4.5.0"),
                ("numpy", "numpy"),
                ("tensorflow", "tensorflow>=2.8.0"),
            ],
            "optional": [
                ("face_alignment", "face-alignment>=1.3.0"),
            ],
        },
        "fomm": {
            "required": [
                ("torch", "torch>=2.0.0"),
                ("cv2", "opencv-python>=4.5.0"),
                ("numpy", "numpy"),
            ],
            "optional": [
                ("face_alignment", "face-alignment>=1.3.0"),
            ],
        },
        "sadtalker": {
            "required": [
                ("torch", "torch>=2.0.0"),
                ("cv2", "opencv-python>=4.5.0"),
                ("PIL", "Pillow"),
                ("numpy", "numpy"),
            ],
            "optional": [
                ("face_alignment", "face-alignment>=1.3.0"),
            ],
        },
        "streaming": {
            "required": [
                ("numpy", "numpy"),
            ],
            "optional": [
                ("soundfile", "soundfile"),
                ("librosa", "librosa"),
            ],
        },
        "speaker_encoder": {
            "required": [
                ("numpy", "numpy"),
            ],
            "optional": [
                ("resemblyzer", "resemblyzer>=0.1.1"),
                ("speechbrain", "speechbrain>=0.5.0"),
            ],
        },
        "quality_metrics": {
            "required": [
                ("numpy", "numpy"),
            ],
            "optional": [
                ("librosa", "librosa"),
                ("torch", "torch>=2.0.0"),
                ("resemblyzer", "resemblyzer>=0.1.1"),
                ("speechbrain", "speechbrain>=0.5.0"),
            ],
        },
        # Add more engines as needed
    }

    @staticmethod
    def check_package(package_name: str, import_name: Optional[str] = None) -> bool:
        """
        Check if a package is installed.

        Args:
            package_name: Name of the package (for pip install)
            import_name: Name to use for import (defaults to package_name)

        Returns:
            True if package is installed, False otherwise
        """
        if import_name is None:
            import_name = package_name

        try:
            # Try to import the package
            importlib.import_module(import_name)
            return True
        except ImportError:
            # Check if it's available via importlib.util
            spec = importlib.util.find_spec(import_name)
            return spec is not None

    @staticmethod
    def validate_engine_dependencies(
        engine_name: str, raise_on_error: bool = True
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate all dependencies for an engine.

        Args:
            engine_name: Name of the engine to validate
            raise_on_error: If True, raise DependencyError on missing required deps

        Returns:
            Tuple of (all_valid, missing_required, missing_optional)
        """
        if engine_name not in DependencyValidator.ENGINE_DEPENDENCIES:
            logger.warning(f"Unknown engine '{engine_name}', skipping dependency validation")
            return True, [], []

        deps = DependencyValidator.ENGINE_DEPENDENCIES[engine_name]
        missing_required = []
        missing_optional = []

        # Check required dependencies
        for import_name, package_name in deps.get("required", []):
            if not DependencyValidator.check_package(package_name, import_name):
                missing_required.append((import_name, package_name))
                if raise_on_error:
                    raise DependencyError(import_name, f"pip install {package_name}")

        # Check optional dependencies
        for import_name, package_name in deps.get("optional", []):
            if not DependencyValidator.check_package(package_name, import_name):
                missing_optional.append((import_name, package_name))
                logger.debug(
                    f"Optional dependency '{import_name}' not installed for engine '{engine_name}'"
                )

        all_valid = len(missing_required) == 0

        if missing_required:
            error_msg = (
                f"Engine '{engine_name}' is missing required dependencies:\n"
                + "\n".join(
                    f"  - {name}: pip install {pkg}" for name, pkg in missing_required
                )
            )
            logger.error(error_msg)

        if missing_optional:
            warning_msg = (
                f"Engine '{engine_name}' is missing optional dependencies:\n"
                + "\n".join(
                    f"  - {name}: pip install {pkg}" for name, pkg in missing_optional
                )
            )
            logger.warning(warning_msg)

        return all_valid, missing_required, missing_optional

    @staticmethod
    def check_python_version(min_version: Tuple[int, int, int] = (3, 10, 0)) -> bool:
        """
        Check if Python version meets minimum requirement.

        Args:
            min_version: Minimum version as (major, minor, patch)

        Returns:
            True if version meets requirement
        """
        current = sys.version_info[:3]
        return current >= min_version

    @staticmethod
    def check_cuda_available() -> Tuple[bool, Optional[str]]:
        """
        Check if CUDA is available.

        Returns:
            Tuple of (is_available, cuda_version)
        """
        try:
            import torch

            if torch.cuda.is_available():
                cuda_version = torch.version.cuda
                return True, cuda_version
            return False, None
        except ImportError:
            return False, None

    @staticmethod
    def validate_model_files(
        model_path: Optional[str], model_extensions: List[str] = None
    ) -> bool:
        """
        Validate that model files exist.

        Args:
            model_path: Path to model file or directory
            model_extensions: List of valid extensions (e.g., ['.pth', '.pt'])

        Returns:
            True if model files exist
        """
        if model_extensions is None:
            model_extensions = [".pth", ".pt", ".h5", ".pb", ".onnx"]

        if not model_path:
            return False

        from pathlib import Path

        model_path_obj = Path(model_path)
        if not model_path_obj.exists():
            return False

        if model_path_obj.is_file():
            return model_path_obj.suffix.lower() in model_extensions

        if model_path_obj.is_dir():
            # Check if directory contains model files
            for ext in model_extensions:
                if list(model_path_obj.rglob(f"*{ext}")):
                    return True
            return False

        return False

