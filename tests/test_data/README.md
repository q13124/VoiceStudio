# VoiceStudio Quantum+ Test Data

Comprehensive test data sets for VoiceStudio Quantum+ testing.

**Version:** 1.0  
**Last Updated:** 2025-01-28  
**Status:** Ready for Use

---

## Table of Contents

1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Test Data Types](#test-data-types)
4. [Using Test Data](#using-test-data)
5. [Generating Test Data](#generating-test-data)
6. [Test Data Guidelines](#test-data-guidelines)

---

## Overview

This directory contains test data for VoiceStudio Quantum+ including:

- **Test Audio Files**: Sample audio files in various formats
- **Test Voice Profiles**: JSON files with voice profile data
- **Test Projects**: JSON files with project data
- **Test Scripts**: Python scripts to generate test data
- **Documentation**: Test data structure and usage guides

### Purpose

Test data is used for:
- Integration testing
- End-to-end testing
- Performance testing
- Quality testing
- API testing
- UI testing

---

## Directory Structure

```
tests/test_data/
├── README.md                    # This file
├── audio/                       # Test audio files
│   ├── reference/              # Reference audio for voice cloning
│   ├── synthesized/            # Synthesized audio samples
│   ├── effects/                 # Audio with effects applied
│   └── formats/                 # Audio in various formats
│       ├── wav/                 # WAV files
│       ├── mp3/                 # MP3 files
│       └── flac/                # FLAC files
├── profiles/                    # Test voice profiles
│   ├── sample_profiles.json    # Sample profile data
│   └── generated/              # Generated profiles
├── projects/                   # Test projects
│   ├── sample_projects.json    # Sample project data
│   └── generated/              # Generated projects
├── scripts/                    # Test data generation scripts
│   ├── generate_test_data.py   # Main generation script
│   ├── generate_profiles.py    # Profile generation
│   ├── generate_projects.py    # Project generation
│   └── generate_audio_metadata.py  # Audio metadata generation
└── metadata/                    # Test data metadata
    ├── audio_metadata.json     # Audio file metadata
    └── test_data_index.json    # Index of all test data
```

---

## Test Data Types

### Audio Files

**Location:** `tests/test_data/audio/`

**Formats:**
- WAV (uncompressed, high quality)
- MP3 (compressed, common format)
- FLAC (lossless compression)

**Categories:**
- **Reference Audio**: High-quality reference audio for voice cloning
- **Synthesized Audio**: Generated audio from synthesis
- **Effects Audio**: Audio with effects applied
- **Format Samples**: Same audio in different formats

**Requirements:**
- Sample rate: 22050 Hz or 44100 Hz
- Channels: Mono or Stereo
- Duration: 1-30 seconds (varies by test)
- Quality: High quality (no artifacts)

**Naming Convention:**
- `{category}_{description}_{format}.{ext}`
- Example: `reference_male_voice_en.wav`

---

### Voice Profiles

**Location:** `tests/test_data/profiles/`

**Format:** JSON

**Structure:**
```json
{
  "id": "test-profile-001",
  "name": "Test Voice Profile 1",
  "language": "en",
  "emotion": "neutral",
  "quality_score": 0.85,
  "tags": ["test", "male", "english"],
  "reference_audio_url": "audio/reference/test_ref_001.wav"
}
```

**Test Profiles:**
- `test-profile-001`: Male voice, English, neutral emotion
- `test-profile-002`: Female voice, English, happy emotion
- `test-profile-003`: Male voice, Spanish, neutral emotion
- `test-profile-004`: Female voice, French, neutral emotion
- `test-profile-005`: Male voice, English, sad emotion

**See:** `profiles/sample_profiles.json` for complete list

---

### Projects

**Location:** `tests/test_data/projects/`

**Format:** JSON

**Structure:**
```json
{
  "id": "test-project-001",
  "name": "Test Project 1",
  "description": "Test project for integration testing",
  "created_at": "2025-01-28T00:00:00Z",
  "updated_at": "2025-01-28T00:00:00Z",
  "voice_profile_ids": ["test-profile-001", "test-profile-002"],
  "tracks": [
    {
      "id": "track-001",
      "name": "Track 1",
      "clips": []
    }
  ]
}
```

**Test Projects:**
- `test-project-001`: Simple project with one track
- `test-project-002`: Project with multiple tracks
- `test-project-003`: Project with effects
- `test-project-004`: Project with macros
- `test-project-005`: Complex project with all features

**See:** `projects/sample_projects.json` for complete list

---

## Using Test Data

### In Tests

**Python Tests:**
```python
import json
from pathlib import Path

# Load test profile
test_data_dir = Path(__file__).parent.parent / "test_data"
profile_path = test_data_dir / "profiles" / "sample_profiles.json"

with open(profile_path) as f:
    profiles = json.load(f)
    test_profile = profiles[0]
```

**C# Tests:**
```csharp
using System.IO;
using System.Text.Json;

// Load test profile
var testDataDir = Path.Combine("tests", "test_data");
var profilePath = Path.Combine(testDataDir, "profiles", "sample_profiles.json");

var json = await File.ReadAllTextAsync(profilePath);
var profiles = JsonSerializer.Deserialize<List<VoiceProfile>>(json);
var testProfile = profiles[0];
```

### In Fixtures

**Pytest Fixtures:**
```python
@pytest.fixture
def test_profile():
    """Load test profile."""
    test_data_dir = Path(__file__).parent.parent / "test_data"
    profile_path = test_data_dir / "profiles" / "sample_profiles.json"
    
    with open(profile_path) as f:
        profiles = json.load(f)
        return profiles[0]
```

---

## Generating Test Data

### Using Generation Scripts

**Generate All Test Data:**
```bash
cd tests/test_data/scripts
python generate_test_data.py
```

**Generate Specific Data:**
```bash
# Generate profiles only
python generate_profiles.py

# Generate projects only
python generate_projects.py

# Generate audio metadata
python generate_audio_metadata.py
```

### Manual Generation

**Create Test Profile:**
```python
from scripts.generate_profiles import create_test_profile

profile = create_test_profile(
    name="Test Profile",
    language="en",
    emotion="neutral"
)
```

**Create Test Project:**
```python
from scripts.generate_projects import create_test_project

project = create_test_project(
    name="Test Project",
    profile_ids=["test-profile-001"]
)
```

---

## Test Data Guidelines

### Audio Files

**Requirements:**
- Use high-quality audio (no artifacts, clear speech)
- Include various languages and emotions
- Cover different audio formats
- Include edge cases (short, long, silence)

**Best Practices:**
- Keep file sizes reasonable (< 10 MB per file)
- Use consistent naming conventions
- Include metadata files
- Document audio characteristics

### Voice Profiles

**Requirements:**
- Include diverse voices (male, female, various ages)
- Cover multiple languages
- Include various emotions
- Include quality scores

**Best Practices:**
- Use realistic quality scores (0.5-0.95)
- Include relevant tags
- Link to reference audio
- Document profile characteristics

### Projects

**Requirements:**
- Include simple and complex projects
- Cover all features (tracks, effects, macros)
- Include edge cases (empty, large)
- Use realistic data

**Best Practices:**
- Keep projects manageable
- Use consistent structure
- Include metadata
- Document project purpose

---

## Test Data Index

**Location:** `tests/test_data/metadata/test_data_index.json`

**Purpose:** Index of all test data for easy discovery.

**Structure:**
```json
{
  "audio_files": [
    {
      "id": "audio-001",
      "path": "audio/reference/test_ref_001.wav",
      "format": "wav",
      "duration": 5.2,
      "sample_rate": 44100,
      "channels": 1
    }
  ],
  "profiles": [
    {
      "id": "test-profile-001",
      "path": "profiles/sample_profiles.json",
      "name": "Test Voice Profile 1"
    }
  ],
  "projects": [
    {
      "id": "test-project-001",
      "path": "projects/sample_projects.json",
      "name": "Test Project 1"
    }
  ]
}
```

---

## Maintenance

### Updating Test Data

1. **Add New Data:**
   - Add files to appropriate directories
   - Update metadata/index files
   - Document in README

2. **Remove Old Data:**
   - Remove files
   - Update metadata/index files
   - Update documentation

3. **Validate Data:**
   - Run validation scripts
   - Check file integrity
   - Verify JSON structure

### Validation

**Validate Test Data:**
```bash
cd tests/test_data/scripts
python validate_test_data.py
```

**Checks:**
- JSON structure validity
- File existence
- Reference integrity
- Metadata consistency

---

## Summary

This test data directory provides:

1. **Comprehensive Test Data**: Audio files, profiles, projects
2. **Generation Scripts**: Automated test data creation
3. **Documentation**: Complete usage guides
4. **Metadata**: Index and metadata files
5. **Guidelines**: Best practices for test data

**Key Features:**
- ✅ Organized directory structure
- ✅ Multiple data types
- ✅ Generation scripts
- ✅ Usage examples
- ✅ Validation tools

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-28  
**Maintainer:** Test Team

