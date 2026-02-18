"""
Standardized Test Data for VoiceStudio UI Tests.

Provides consistent test data fixtures for UI testing:
- Profile configurations
- Voice settings
- Training datasets
- Application settings

Usage:
    from tests.ui.fixtures.test_data import PROFILES, DATASETS, SETTINGS

    # Access test profile
    profile = PROFILES["basic"]

    # Access test dataset
    dataset = DATASETS["small"]
"""

from __future__ import annotations

from dataclasses import dataclass, field

# =============================================================================
# Profile Test Data
# =============================================================================

@dataclass
class TestProfile:
    """Test profile configuration."""
    name: str
    description: str = "Test profile"
    engine: str = "xtts"
    voice_model: str | None = None
    language: str = "en"
    speaker_id: int = 0
    sample_rate: int = 22050

    # Voice settings
    pitch: float = 1.0
    speed: float = 1.0
    energy: float = 1.0


PROFILES = {
    "basic": TestProfile(
        name="Test Profile Basic",
        description="Basic test profile for smoke tests",
        engine="xtts",
    ),
    "custom_voice": TestProfile(
        name="Test Profile Custom Voice",
        description="Profile with custom voice model",
        engine="xtts",
        voice_model="custom_test_voice",
        language="en",
    ),
    "rvc": TestProfile(
        name="Test Profile RVC",
        description="RVC engine test profile",
        engine="rvc",
        voice_model="test_rvc_model",
    ),
    "multilingual": TestProfile(
        name="Test Profile Multilingual",
        description="Multilingual test profile",
        engine="xtts",
        language="es",
    ),
    "modified_settings": TestProfile(
        name="Test Profile Modified",
        description="Profile with modified voice settings",
        engine="xtts",
        pitch=1.2,
        speed=0.9,
        energy=1.1,
    ),
}


# =============================================================================
# Dataset Test Data
# =============================================================================

@dataclass
class TestDataset:
    """Test dataset configuration."""
    name: str
    description: str = "Test dataset"
    audio_files: list[str] = field(default_factory=list)
    total_duration_seconds: float = 0.0
    sample_rate: int = 22050
    format: str = "wav"


DATASETS = {
    "small": TestDataset(
        name="Small Test Dataset",
        description="Small dataset for quick tests",
        audio_files=["sample_01.wav", "sample_02.wav"],
        total_duration_seconds=60.0,
    ),
    "medium": TestDataset(
        name="Medium Test Dataset",
        description="Medium dataset for integration tests",
        audio_files=[
            "sample_01.wav", "sample_02.wav", "sample_03.wav",
            "sample_04.wav", "sample_05.wav",
        ],
        total_duration_seconds=300.0,
    ),
    "multilingual": TestDataset(
        name="Multilingual Test Dataset",
        description="Dataset with multiple languages",
        audio_files=["en_sample.wav", "es_sample.wav", "fr_sample.wav"],
        total_duration_seconds=180.0,
    ),
    "empty": TestDataset(
        name="Empty Test Dataset",
        description="Empty dataset for error handling tests",
        audio_files=[],
        total_duration_seconds=0.0,
    ),
}


# =============================================================================
# Settings Test Data
# =============================================================================

@dataclass
class TestSettings:
    """Test application settings configuration."""
    theme: str = "dark"
    language: str = "en"
    auto_save: bool = True
    audio_device: str | None = None
    models_path: str = ""
    cache_enabled: bool = True
    telemetry_enabled: bool = False


SETTINGS = {
    "default": TestSettings(),
    "light_theme": TestSettings(theme="light"),
    "no_auto_save": TestSettings(auto_save=False),
    "custom_models_path": TestSettings(
        models_path="C:\\VoiceStudio\\CustomModels"
    ),
    "minimal": TestSettings(
        cache_enabled=False,
        telemetry_enabled=False,
        auto_save=False,
    ),
}


# =============================================================================
# Form Input Test Data
# =============================================================================

@dataclass
class FormInput:
    """Test form input data."""
    field_id: str
    value: str
    expected_valid: bool = True
    error_message: str | None = None


FORM_INPUTS = {
    "profile_name_valid": FormInput(
        field_id="ProfileNameTextBox",
        value="My Test Profile",
        expected_valid=True,
    ),
    "profile_name_empty": FormInput(
        field_id="ProfileNameTextBox",
        value="",
        expected_valid=False,
        error_message="Name is required",
    ),
    "profile_name_long": FormInput(
        field_id="ProfileNameTextBox",
        value="A" * 256,
        expected_valid=False,
        error_message="Name too long",
    ),
    "profile_name_special_chars": FormInput(
        field_id="ProfileNameTextBox",
        value="Profile <Test> \"Special\"",
        expected_valid=True,  # Should handle special characters
    ),
}


# =============================================================================
# Navigation Test Data
# =============================================================================

@dataclass
class NavigationPath:
    """Test navigation path."""
    name: str
    steps: list[str]
    expected_panel: str
    description: str = ""


NAVIGATION_PATHS = {
    "to_profiles": NavigationPath(
        name="Navigate to Profiles",
        steps=["NavProfiles"],
        expected_panel="ProfilesView_Root",
    ),
    "to_training": NavigationPath(
        name="Navigate to Training",
        steps=["NavTraining"],
        expected_panel="TrainingView_Root",
    ),
    "to_settings_via_studio": NavigationPath(
        name="Navigate to Settings via Studio",
        steps=["NavStudio", "NavSettings"],
        expected_panel="SettingsView_Root",
    ),
    "round_trip": NavigationPath(
        name="Round Trip Navigation",
        steps=["NavProfiles", "NavTraining", "NavProfiles"],
        expected_panel="ProfilesView_Root",
        description="Navigate away and back",
    ),
}


# =============================================================================
# Keyboard Shortcut Test Data
# =============================================================================

@dataclass
class KeyboardShortcut:
    """Test keyboard shortcut."""
    shortcut: str
    action: str
    expected_result: str
    requires_focus: str | None = None


KEYBOARD_SHORTCUTS = {
    "command_palette": KeyboardShortcut(
        shortcut="Ctrl+Shift+P",
        action="Open command palette",
        expected_result="CommandPaletteDialog",
    ),
    "save": KeyboardShortcut(
        shortcut="Ctrl+S",
        action="Save current item",
        expected_result="SaveConfirmation",
    ),
    "escape": KeyboardShortcut(
        shortcut="Escape",
        action="Cancel/close dialog",
        expected_result="DialogClosed",
    ),
    "new_profile": KeyboardShortcut(
        shortcut="Ctrl+N",
        action="Create new profile",
        expected_result="NewProfileDialog",
        requires_focus="ProfilesView_Root",
    ),
}


# =============================================================================
# Error Scenario Test Data
# =============================================================================

@dataclass
class ErrorScenario:
    """Test error scenario."""
    name: str
    trigger: str
    expected_error_type: str
    expected_message: str | None = None
    recovery_action: str | None = None


ERROR_SCENARIOS = {
    "invalid_file": ErrorScenario(
        name="Invalid Audio File",
        trigger="Load corrupted audio file",
        expected_error_type="ValidationError",
        expected_message="Invalid audio format",
        recovery_action="Close error dialog",
    ),
    "network_timeout": ErrorScenario(
        name="Network Timeout",
        trigger="Backend unavailable",
        expected_error_type="ConnectionError",
        expected_message="Unable to connect",
        recovery_action="Retry or work offline",
    ),
    "disk_full": ErrorScenario(
        name="Disk Full",
        trigger="Attempt large save operation",
        expected_error_type="IOError",
        expected_message="Insufficient disk space",
    ),
}


# =============================================================================
# Utility Functions
# =============================================================================

def get_test_profile(name: str = "basic") -> TestProfile:
    """Get a test profile by name."""
    return PROFILES.get(name, PROFILES["basic"])


def get_test_dataset(name: str = "small") -> TestDataset:
    """Get a test dataset by name."""
    return DATASETS.get(name, DATASETS["small"])


def get_test_settings(name: str = "default") -> TestSettings:
    """Get test settings by name."""
    return SETTINGS.get(name, SETTINGS["default"])


def get_all_profile_names() -> list[str]:
    """Get all available test profile names."""
    return list(PROFILES.keys())


def get_all_dataset_names() -> list[str]:
    """Get all available test dataset names."""
    return list(DATASETS.keys())
