"""
Settings API Routes
Handles application settings and preferences
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

try:
    from ..optimization import cache_response
except ImportError:

    def cache_response(ttl: int = 300):
        def decorator(func):
            return func

        return decorator


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["settings"])

# Settings file path
SETTINGS_FILE = Path("data/settings.json")

# Cache for settings to reduce file I/O
_settings_cache: Optional["SettingsData"] = None
_cache_timestamp: float = 0.0
_cache_ttl: float = 60.0  # Cache for 60 seconds

# Maximum settings file size (10MB)
_MAX_SETTINGS_FILE_SIZE = 10 * 1024 * 1024


class GeneralSettings(BaseModel):
    theme: str = "Dark"
    language: str = "en-US"
    auto_save: bool = True
    auto_save_interval: int = 300


class EngineSettings(BaseModel):
    default_audio_engine: str = "xtts"
    default_image_engine: str = "sdxl"
    default_video_engine: str = "svd"
    quality_level: int = 5


class AudioSettings(BaseModel):
    output_device: str = "Default"
    input_device: str = "Default"
    sample_rate: int = 44100
    buffer_size: int = 1024


class TimelineSettings(BaseModel):
    time_format: str = "Timecode"
    snap_enabled: bool = True
    snap_interval: float = 0.1
    grid_enabled: bool = True
    grid_interval: float = 1.0


class BackendSettings(BaseModel):
    api_url: str = "http://localhost:8000"
    timeout: int = 30
    retry_count: int = 3


class PerformanceSettings(BaseModel):
    caching_enabled: bool = True
    cache_size: int = 512
    max_threads: int = 4
    memory_limit: int = 4096

    @field_validator("cache_size")
    @classmethod
    def validate_cache_size(cls, v: int) -> int:
        """Validate cache size."""
        if not 64 <= v <= 4096:
            raise ValueError("Cache size must be between 64 and 4096 MB")
        return v

    @field_validator("max_threads")
    @classmethod
    def validate_threads(cls, v: int) -> int:
        """Validate thread count."""
        if not 1 <= v <= 32:
            raise ValueError("Max threads must be between 1 and 32")
        return v

    @field_validator("memory_limit")
    @classmethod
    def validate_memory(cls, v: int) -> int:
        """Validate memory limit."""
        if not 512 <= v <= 32768:
            raise ValueError("Memory limit must be between 512 and 32768 MB")
        return v


class PluginSettings(BaseModel):
    enabled_plugins: list[str] = []


class McpSettings(BaseModel):
    enabled: bool = False
    server_url: str = "http://localhost:8080"


class QualitySettings(BaseModel):
    """Quality management settings for voice cloning."""

    # fast, standard, high, ultra, professional
    default_preset: str = "standard"
    # Automatically enhance quality
    auto_enhance: bool = True
    # Automatically optimize parameters
    auto_optimize: bool = False
    # Minimum acceptable MOS score
    min_mos_score: float = 3.5
    # Minimum acceptable similarity
    min_similarity: float = 0.75
    # Minimum acceptable naturalness
    min_naturalness: float = 0.70
    # Minimum acceptable SNR
    min_snr_db: float = 25.0
    # Prefer speed over quality
    prefer_speed: bool = False
    # Quality tier preference
    quality_tier: str = "standard"
    # Show quality metrics in UI
    show_quality_metrics: bool = True
    # Automatically compare synthesis results
    auto_compare: bool = False

    @field_validator("default_preset")
    @classmethod
    def validate_preset(cls, v: str) -> str:
        """Validate preset name."""
        valid_presets = ["fast", "standard", "high", "ultra", "professional"]
        if v not in valid_presets:
            raise ValueError(f"Invalid preset: {v}. Must be one of {valid_presets}")
        return v

    @field_validator("min_mos_score")
    @classmethod
    def validate_mos_score(cls, v: float) -> float:
        """Validate MOS score range."""
        if not 1.0 <= v <= 5.0:
            raise ValueError("MOS score must be between 1.0 and 5.0")
        return v

    @field_validator("min_similarity", "min_naturalness")
    @classmethod
    def validate_ratio(cls, v: float) -> float:
        """Validate similarity/naturalness range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Value must be between 0.0 and 1.0")
        return v

    @field_validator("min_snr_db")
    @classmethod
    def validate_snr(cls, v: float) -> float:
        """Validate SNR range."""
        if not 0.0 <= v <= 100.0:
            raise ValueError("SNR must be between 0.0 and 100.0 dB")
        return v

    @field_validator("quality_tier")
    @classmethod
    def validate_tier(cls, v: str) -> str:
        """Validate quality tier."""
        valid_tiers = ["fast", "standard", "high", "ultra"]
        if v not in valid_tiers:
            raise ValueError(f"Invalid tier: {v}. Must be one of {valid_tiers}")
        return v


class SettingsData(BaseModel):
    general: Optional[GeneralSettings] = None
    engine: Optional[EngineSettings] = None
    audio: Optional[AudioSettings] = None
    timeline: Optional[TimelineSettings] = None
    backend: Optional[BackendSettings] = None
    performance: Optional[PerformanceSettings] = None
    plugins: Optional[PluginSettings] = None
    mcp: Optional[McpSettings] = None
    quality: Optional[QualitySettings] = None


def load_settings(force_reload: bool = False) -> SettingsData:
    """Load settings from file with caching."""
    global _settings_cache, _cache_timestamp

    current_time = time.time()

    # Return cached settings if valid
    if (
        not force_reload
        and _settings_cache is not None
        and (current_time - _cache_timestamp) < _cache_ttl
    ):
        return _settings_cache

    try:
        if SETTINGS_FILE.exists():
            # Check file size to prevent DoS
            file_size = SETTINGS_FILE.stat().st_size
            if file_size > _MAX_SETTINGS_FILE_SIZE:
                logger.error(
                    f"Settings file too large: {file_size} bytes "
                    f"(max: {_MAX_SETTINGS_FILE_SIZE})"
                )
                raise HTTPException(
                    status_code=500,
                    detail="Settings file is corrupted or too large",
                )

            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                settings = SettingsData(**data)
                # Update cache
                _settings_cache = settings
                _cache_timestamp = current_time
                return settings
        else:
            # Return default settings
            default_settings = SettingsData(
                general=GeneralSettings(),
                engine=EngineSettings(),
                audio=AudioSettings(),
                timeline=TimelineSettings(),
                backend=BackendSettings(),
                performance=PerformanceSettings(),
                plugins=PluginSettings(),
                mcp=McpSettings(),
                quality=QualitySettings(),
            )
            _settings_cache = default_settings
            _cache_timestamp = current_time
            return default_settings
    except Exception as e:
        logger.error(f"Failed to load settings: {e}", exc_info=True)
        # Return default settings on error
        default_settings = SettingsData(
            general=GeneralSettings(),
            engine=EngineSettings(),
            audio=AudioSettings(),
            timeline=TimelineSettings(),
            backend=BackendSettings(),
            performance=PerformanceSettings(),
            plugins=PluginSettings(),
            mcp=McpSettings(),
        )
        _settings_cache = default_settings
        _cache_timestamp = current_time
        return default_settings


def save_settings(settings: SettingsData) -> None:
    """Save settings to file and update cache."""
    global _settings_cache, _cache_timestamp

    try:
        # Ensure directory exists
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Validate settings before saving
        try:
            # Validate by creating a new instance
            SettingsData(**settings.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(f"Invalid settings data: {e}")
            error_msg = str(e)
            if "validation" in error_msg.lower() or "value" in error_msg.lower():
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid settings values: {error_msg}. Please check your input and try again.",
                ) from e
            raise HTTPException(
                status_code=400,
                detail=f"Invalid settings format: {error_msg}. Please verify your settings data.",
            ) from e

        # Save settings atomically using a temporary file
        temp_file = SETTINGS_FILE.with_suffix(".tmp")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(settings.model_dump(exclude_none=True), f, indent=2)

            # Check temp file size
            temp_size = temp_file.stat().st_size
            if temp_size > _MAX_SETTINGS_FILE_SIZE:
                temp_file.unlink()
                raise HTTPException(
                    status_code=400,
                    detail="Settings data too large to save",
                )

            # Atomic replace
            temp_file.replace(SETTINGS_FILE)
        except Exception:
            # Clean up temp file on error
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    ...
            raise

        # Update cache
        _settings_cache = settings
        _cache_timestamp = time.time()

        logger.info("Settings saved successfully")
    except Exception as e:
        logger.error(f"Failed to save settings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to save settings: {str(e)}"
        )


@router.get("", response_model=SettingsData)
@cache_response(ttl=60)  # Cache for 60 seconds (settings change infrequently)
async def get_settings():
    """Get all settings."""
    try:
        settings = load_settings()
        return settings
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get settings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Unable to load application settings. Please try again or reset to defaults.",
        )


@router.get("/{category}")
@cache_response(ttl=60)  # Cache for 60 seconds (settings change infrequently)
async def get_settings_category(category: str):
    """Get settings for a specific category."""
    try:
        settings = load_settings()

        category_map = {
            "general": settings.general,
            "engine": settings.engine,
            "audio": settings.audio,
            "timeline": settings.timeline,
            "backend": settings.backend,
            "performance": settings.performance,
            "plugins": settings.plugins,
            "mcp": settings.mcp,
            "quality": settings.quality,
        }

        if category not in category_map:
            valid_categories = ", ".join(category_map.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Settings category '{category}' not found. Valid categories: {valid_categories}",
            )

        result = category_map[category]
        if result is None:
            # Return defaults for category
            defaults = {
                "general": GeneralSettings(),
                "engine": EngineSettings(),
                "audio": AudioSettings(),
                "timeline": TimelineSettings(),
                "backend": BackendSettings(),
                "performance": PerformanceSettings(),
                "plugins": PluginSettings(),
                "mcp": McpSettings(),
                "quality": QualitySettings(),
            }
            return defaults[category]

        return result
    except HTTPException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get settings category '{category}': {e}", exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load settings for category '{category}'. Please try again.",
        )


@router.post("", response_model=SettingsData)
async def save_settings_endpoint(settings: SettingsData):
    """Save all settings."""
    try:
        save_settings(settings)
        return settings
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save settings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to save settings: {str(e)}"
        )


@router.put("/{category}")
async def update_settings_category(category: str, data: Dict):
    """Update settings for a specific category."""
    try:
        settings = load_settings()

        category_map = {
            "general": GeneralSettings,
            "engine": EngineSettings,
            "audio": AudioSettings,
            "timeline": TimelineSettings,
            "backend": BackendSettings,
            "performance": PerformanceSettings,
            "plugins": PluginSettings,
            "mcp": McpSettings,
            "quality": QualitySettings,
        }

        if category not in category_map:
            valid_categories = ", ".join(category_map.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Settings category '{category}' not found. Valid categories: {valid_categories}",
            )

        # Update the category with validation
        category_class = category_map[category]
        try:
            updated = category_class(**data)
        except Exception as e:
            logger.error(f"Invalid {category} settings: {e}")
            error_msg = str(e)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid {category} settings: {error_msg}. Please check the values and try again.",
            ) from e

        if category == "general":
            settings.general = updated
        elif category == "engine":
            settings.engine = updated
        elif category == "audio":
            settings.audio = updated
        elif category == "timeline":
            settings.timeline = updated
        elif category == "backend":
            settings.backend = updated
        elif category == "performance":
            settings.performance = updated
        elif category == "plugins":
            settings.plugins = updated
        elif category == "mcp":
            settings.mcp = updated
        elif category == "quality":
            settings.quality = updated

        save_settings(settings)
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update settings category: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to update settings: {str(e)}"
        )


@router.post("/reset")
async def reset_settings():
    """Reset all settings to defaults."""
    try:
        default_settings = SettingsData(
            general=GeneralSettings(),
            engine=EngineSettings(),
            audio=AudioSettings(),
            timeline=TimelineSettings(),
            backend=BackendSettings(),
            performance=PerformanceSettings(),
            plugins=PluginSettings(),
            mcp=McpSettings(),
            quality=QualitySettings(),
        )
        save_settings(default_settings)
        logger.info("Settings reset to defaults")
        return default_settings
    except Exception as e:
        logger.error(f"Failed to reset settings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to reset settings: {str(e)}"
        )
