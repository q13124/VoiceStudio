"""
VoiceStudio Test Fixtures.

Provides standardized test data for all test scenarios:
- Audio samples and datasets
- Voice profiles and presets
- SSML test cases
- Multi-language content
- Workflow scenarios
"""

from pathlib import Path

FIXTURES_DIR = Path(__file__).parent
DATA_DIR = FIXTURES_DIR / "data"
AUDIO_DIR = DATA_DIR / "audio"
PROFILES_DIR = DATA_DIR / "profiles"
PRESETS_DIR = DATA_DIR / "presets"

# Create directories if they don't exist
for dir_path in [DATA_DIR, AUDIO_DIR, PROFILES_DIR, PRESETS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

__all__ = [
    "AUDIO_DIR",
    "DATA_DIR",
    "FIXTURES_DIR",
    "PRESETS_DIR",
    "PROFILES_DIR",
]
