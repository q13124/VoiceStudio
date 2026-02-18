"""
Path configuration module for VoiceStudio.

Provides centralized path resolution for models, FFmpeg, logs, artifacts, and more.
Follows local-first principle with environment variable overrides.

Environment Variables:
    VOICESTUDIO_MODELS_PATH: Base models directory
    VOICESTUDIO_FFMPEG_PATH: FFmpeg executable path
    VOICESTUDIO_CACHE_PATH: Cache directory
    VOICESTUDIO_LOGS_PATH: Logs directory
    VOICESTUDIO_ARTIFACTS_PATH: Artifacts directory

Examples:
    >>> get_models_path()
    WindowsPath('C:/ProgramData/VoiceStudio/models')

    >>> get_path("ffmpeg")
    WindowsPath('C:/ProgramData/VoiceStudio/bin/ffmpeg.exe')

    >>> get_path("logs")
    WindowsPath('C:/Users/Tyler/AppData/Roaming/VoiceStudio/logs')
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


class PathResolutionError(RuntimeError):
    """Raised when path resolution fails."""


def get_models_path() -> Path:
    """
    Return the base models path (local-first, configurable via env).

    Resolution order:
    1. VOICESTUDIO_MODELS_PATH environment variable
    2. Windows: %PROGRAMDATA%\\VoiceStudio\\models
    3. Other: ~/.voicestudio/models

    Returns:
        Path to models directory (created if necessary)
    """
    env_path = os.getenv("VOICESTUDIO_MODELS_PATH")
    if env_path:
        path = Path(env_path)
    elif os.name == "nt":
        program_data = os.getenv("PROGRAMDATA", "C:\\ProgramData")
        path = Path(program_data) / "VoiceStudio" / "models"
    else:
        path = Path(os.path.expanduser("~/.voicestudio/models"))

    path.mkdir(parents=True, exist_ok=True)
    return path


def get_ffmpeg_path() -> Path:
    """
    Resolve FFmpeg executable path with fallback discovery.

    Resolution order:
    1. VOICESTUDIO_FFMPEG_PATH environment variable (explicit path)
    2. System PATH (via shutil.which)
    3. Known Windows install locations
    4. Bundled FFmpeg (if packaged with app)

    Returns:
        Path to FFmpeg executable

    Raises:
        PathResolutionError: If FFmpeg not found

    Examples:
        >>> get_ffmpeg_path()
        WindowsPath('C:/ProgramData/VoiceStudio/bin/ffmpeg.exe')
    """
    # 1. Explicit environment variable
    env_path = os.getenv("VOICESTUDIO_FFMPEG_PATH")
    if env_path:
        path = Path(env_path)
        if path.exists() and _is_ffmpeg(path):
            return path

    # 2. System PATH
    which = shutil.which("ffmpeg")
    if which:
        path = Path(which)
        if _is_ffmpeg(path):
            return path

    # 3. Known Windows locations
    if os.name == "nt":
        search_dirs = [
            Path(os.getenv("PROGRAMDATA", "C:\\ProgramData")) / "VoiceStudio" / "bin",
            Path(os.getenv("PROGRAMFILES", "C:\\Program Files")) / "ffmpeg" / "bin",
            Path(os.getenv("PROGRAMFILES(X86)", "C:\\Program Files (x86)")) / "ffmpeg" / "bin",
            Path(os.getenv("LOCALAPPDATA", "")) / "Programs" / "ffmpeg" / "bin",
        ]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            ffmpeg_exe = search_dir / "ffmpeg.exe"
            if ffmpeg_exe.exists() and _is_ffmpeg(ffmpeg_exe):
                return ffmpeg_exe

    # 4. Bundled (relative to this module)
    bundled = Path(__file__).resolve().parents[2] / "bin" / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
    if bundled.exists() and _is_ffmpeg(bundled):
        return bundled

    raise PathResolutionError(
        "FFmpeg not found. Install FFmpeg or set VOICESTUDIO_FFMPEG_PATH environment variable."
    )


def get_path(path_type: str) -> Path:
    """
    Get path for specific type with environment variable override.

    Supported path types:
        - "models" or "base": Base models directory
        - "ffmpeg": FFmpeg executable
        - "cache": Cache directory
        - "checkpoints": Model checkpoints directory
        - "logs": Log files directory
        - "artifacts": Output artifacts directory
        - "data": User data directory
        - "config": Configuration directory
        - "jobs": Job state storage directory
        - "temp": Temporary files directory (GAP-PY-002)
        - "output": Default output directory (GAP-PY-002)
        - "bin": Executables/binaries directory (GAP-PY-002)
        - "plugins": Plugins directory (GAP-PY-002)

    Args:
        path_type: Type of path to resolve

    Returns:
        Resolved path (directories created if necessary)

    Raises:
        ValueError: If path_type unknown
        PathResolutionError: If path cannot be resolved

    Examples:
        >>> get_path("models")
        WindowsPath('C:/ProgramData/VoiceStudio/models')

        >>> get_path("logs")
        WindowsPath('C:/Users/Tyler/AppData/Roaming/VoiceStudio/logs')
    """
    path_type_lower = path_type.lower()

    if path_type_lower in ("models", "base"):
        return get_models_path()

    elif path_type_lower == "ffmpeg":
        return get_ffmpeg_path()

    elif path_type_lower == "cache":
        env_path = os.getenv("VOICESTUDIO_CACHE_PATH")
        path = Path(env_path) if env_path else get_models_path() / "cache"
        path.mkdir(parents=True, exist_ok=True)
        return path

    elif path_type_lower == "checkpoints":
        path = get_models_path() / "checkpoints"
        path.mkdir(parents=True, exist_ok=True)
        return path

    elif path_type_lower == "logs":
        env_path = os.getenv("VOICESTUDIO_LOGS_PATH")
        if env_path:
            path = Path(env_path)
        elif os.name == "nt":
            appdata = os.getenv("APPDATA", os.path.expanduser("~"))
            path = Path(appdata) / "VoiceStudio" / "logs"
        else:
            path = Path(os.path.expanduser("~/.voicestudio/logs"))
        path.mkdir(parents=True, exist_ok=True)
        return path

    elif path_type_lower == "artifacts":
        env_path = os.getenv("VOICESTUDIO_ARTIFACTS_PATH")
        if env_path:
            path = Path(env_path)
        elif os.name == "nt":
            appdata = os.getenv("APPDATA", os.path.expanduser("~"))
            path = Path(appdata) / "VoiceStudio" / "artifacts"
        else:
            path = Path(os.path.expanduser("~/.voicestudio/artifacts"))
        path.mkdir(parents=True, exist_ok=True)
        return path

    elif path_type_lower == "data":
        if os.name == "nt":
            appdata = os.getenv("APPDATA", os.path.expanduser("~"))
            path = Path(appdata) / "VoiceStudio" / "data"
        else:
            path = Path(os.path.expanduser("~/.voicestudio/data"))
        path.mkdir(parents=True, exist_ok=True)
        return path

    elif path_type_lower == "config":
        if os.name == "nt":
            appdata = os.getenv("APPDATA", os.path.expanduser("~"))
            path = Path(appdata) / "VoiceStudio" / "config"
        else:
            path = Path(os.path.expanduser("~/.voicestudio/config"))
        path.mkdir(parents=True, exist_ok=True)
        return path

    elif path_type_lower == "jobs":
        env_path = os.getenv("VOICESTUDIO_JOBS_DIR")
        if env_path:
            path = Path(env_path)
        else:
            # Fall back to cache/jobs
            cache_dir = os.getenv("VOICESTUDIO_CACHE_DIR")
            if cache_dir:
                path = Path(cache_dir) / "jobs"
            elif os.name == "nt":
                appdata = os.getenv("APPDATA", os.path.expanduser("~"))
                path = Path(appdata) / "VoiceStudio" / "jobs"
            else:
                path = Path(os.path.expanduser("~/.voicestudio/jobs"))
        path.mkdir(parents=True, exist_ok=True)
        return path

    # GAP-PY-002: Centralized temp/output paths
    elif path_type_lower == "temp":
        env_path = os.getenv("VOICESTUDIO_TEMP_PATH")
        if env_path:
            path = Path(env_path)
        elif os.name == "nt":
            path = Path(os.getenv("TEMP", "C:\\Temp")) / "VoiceStudio"
        else:
            path = Path("/tmp/VoiceStudio")
        path.mkdir(parents=True, exist_ok=True)
        return path

    elif path_type_lower == "output":
        env_path = os.getenv("VOICESTUDIO_OUTPUT_PATH")
        if env_path:
            path = Path(env_path)
        else:
            path = get_path("temp") / "output"
        path.mkdir(parents=True, exist_ok=True)
        return path

    elif path_type_lower == "bin":
        env_path = os.getenv("VOICESTUDIO_BIN_PATH")
        if env_path:
            path = Path(env_path)
        elif os.name == "nt":
            program_data = os.getenv("PROGRAMDATA", "C:\\ProgramData")
            path = Path(program_data) / "VoiceStudio" / "bin"
        else:
            path = Path(os.path.expanduser("~/.voicestudio/bin"))
        path.mkdir(parents=True, exist_ok=True)
        return path

    elif path_type_lower == "plugins":
        env_path = os.getenv("VOICESTUDIO_PLUGINS_PATH")
        if env_path:
            path = Path(env_path)
        elif os.name == "nt":
            appdata = os.getenv("APPDATA", os.path.expanduser("~"))
            path = Path(appdata) / "VoiceStudio" / "plugins"
        else:
            path = Path(os.path.expanduser("~/.voicestudio/plugins"))
        path.mkdir(parents=True, exist_ok=True)
        return path

    else:
        raise ValueError(f"Unknown path type: {path_type}")


def validate_path(path: Path, must_exist: bool = False, must_be_writable: bool = False) -> bool:
    """
    Validate path meets requirements.

    Args:
        path: Path to validate
        must_exist: Require path exists
        must_be_writable: Require write permission

    Returns:
        True if valid, False otherwise
    """
    if must_exist and not path.exists():
        return False

    if must_be_writable:
        if path.is_dir():
            # Test write to directory
            test_file = path / ".write_test"
            try:
                test_file.touch()
                test_file.unlink()
                return True
            except (PermissionError, OSError):
                return False
        else:
            # Test write to file's parent
            return validate_path(path.parent, must_exist=False, must_be_writable=True)

    return True


def _is_ffmpeg(path: Path) -> bool:
    """
    Verify path is a valid FFmpeg executable.

    Args:
        path: Path to check

    Returns:
        True if valid FFmpeg executable
    """
    if not path.exists():
        return False

    if not path.is_file():
        return False

    # Quick validation: run ffmpeg -version
    try:
        result = subprocess.run(
            [str(path), "-version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return "ffmpeg version" in result.stdout.lower()
    except (subprocess.TimeoutExpired, OSError, FileNotFoundError):
        return False
