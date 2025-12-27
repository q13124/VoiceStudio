#!/usr/bin/env python3
"""
Generate comprehensive test data for VoiceStudio Quantum+.

This script generates:
- Test voice profiles
- Test projects
- Audio metadata
- Test data index
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

# Get script directory
SCRIPT_DIR = Path(__file__).parent
TEST_DATA_DIR = SCRIPT_DIR.parent
PROFILES_DIR = TEST_DATA_DIR / "profiles"
PROJECTS_DIR = TEST_DATA_DIR / "projects"
METADATA_DIR = TEST_DATA_DIR / "metadata"


def generate_profile_id(index: int) -> str:
    """Generate a test profile ID."""
    return f"test-profile-{index:03d}"


def generate_project_id(index: int) -> str:
    """Generate a test project ID."""
    return f"test-project-{index:03d}"


def create_test_profile(
    index: int,
    name: str,
    language: str,
    emotion: str = "neutral",
    quality_score: float = 0.85,
    tags: List[str] = None,
) -> Dict[str, Any]:
    """Create a test voice profile."""
    if tags is None:
        tags = ["test"]
    
    return {
        "id": generate_profile_id(index),
        "name": name,
        "language": language,
        "emotion": emotion,
        "quality_score": quality_score,
        "tags": tags,
        "reference_audio_url": f"audio/reference/test_ref_{index:03d}.wav",
    }


def create_test_profiles() -> List[Dict[str, Any]]:
    """Create test voice profiles."""
    profiles = [
        create_test_profile(
            index=1,
            name="Test Voice Profile 1 - Male English",
            language="en",
            emotion="neutral",
            quality_score=0.85,
            tags=["test", "male", "english", "neutral"],
        ),
        create_test_profile(
            index=2,
            name="Test Voice Profile 2 - Female English",
            language="en",
            emotion="happy",
            quality_score=0.88,
            tags=["test", "female", "english", "happy"],
        ),
        create_test_profile(
            index=3,
            name="Test Voice Profile 3 - Male Spanish",
            language="es",
            emotion="neutral",
            quality_score=0.82,
            tags=["test", "male", "spanish", "neutral"],
        ),
        create_test_profile(
            index=4,
            name="Test Voice Profile 4 - Female French",
            language="fr",
            emotion="neutral",
            quality_score=0.87,
            tags=["test", "female", "french", "neutral"],
        ),
        create_test_profile(
            index=5,
            name="Test Voice Profile 5 - Male English Sad",
            language="en",
            emotion="sad",
            quality_score=0.83,
            tags=["test", "male", "english", "sad"],
        ),
        create_test_profile(
            index=6,
            name="Test Voice Profile 6 - Female English Excited",
            language="en",
            emotion="excited",
            quality_score=0.90,
            tags=["test", "female", "english", "excited"],
        ),
        create_test_profile(
            index=7,
            name="Test Voice Profile 7 - Male German",
            language="de",
            emotion="neutral",
            quality_score=0.81,
            tags=["test", "male", "german", "neutral"],
        ),
        create_test_profile(
            index=8,
            name="Test Voice Profile 8 - Female Italian",
            language="it",
            emotion="neutral",
            quality_score=0.86,
            tags=["test", "female", "italian", "neutral"],
        ),
    ]
    
    return profiles


def create_test_project(
    index: int,
    name: str,
    description: str,
    profile_ids: List[str],
    num_tracks: int = 1,
) -> Dict[str, Any]:
    """Create a test project."""
    now = datetime.now(timezone.utc).isoformat()
    
    tracks = []
    for i in range(num_tracks):
        tracks.append({
            "id": f"track-{index:03d}-{i+1:02d}",
            "name": f"Track {i+1}",
            "project_id": generate_project_id(index),
            "track_number": i + 1,
            "clips": [],
        })
    
    return {
        "id": generate_project_id(index),
        "name": name,
        "description": description,
        "created_at": now,
        "updated_at": now,
        "voice_profile_ids": profile_ids,
        "tracks": tracks,
    }


def create_test_projects(profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create test projects."""
    profile_ids = [p["id"] for p in profiles]
    
    projects = [
        create_test_project(
            index=1,
            name="Test Project 1 - Simple",
            description="Simple test project with one track",
            profile_ids=[profile_ids[0]],
            num_tracks=1,
        ),
        create_test_project(
            index=2,
            name="Test Project 2 - Multiple Tracks",
            description="Test project with multiple tracks",
            profile_ids=profile_ids[:2],
            num_tracks=3,
        ),
        create_test_project(
            index=3,
            name="Test Project 3 - Effects",
            description="Test project with effects",
            profile_ids=profile_ids[:3],
            num_tracks=2,
        ),
        create_test_project(
            index=4,
            name="Test Project 4 - Macros",
            description="Test project with macros",
            profile_ids=profile_ids[:2],
            num_tracks=2,
        ),
        create_test_project(
            index=5,
            name="Test Project 5 - Complex",
            description="Complex test project with all features",
            profile_ids=profile_ids[:4],
            num_tracks=5,
        ),
    ]
    
    return projects


def create_audio_metadata() -> List[Dict[str, Any]]:
    """Create audio file metadata."""
    metadata = []
    
    # Reference audio files
    for i in range(1, 9):
        metadata.append({
            "id": f"audio-ref-{i:03d}",
            "path": f"audio/reference/test_ref_{i:03d}.wav",
            "format": "wav",
            "category": "reference",
            "duration": 5.0 + (i * 0.5),  # 5.5 to 9.0 seconds
            "sample_rate": 44100,
            "channels": 1,
            "bit_depth": 16,
            "size_bytes": 500000 + (i * 50000),  # Approximate
        })
    
    # Synthesized audio files
    for i in range(1, 6):
        metadata.append({
            "id": f"audio-synth-{i:03d}",
            "path": f"audio/synthesized/test_synth_{i:03d}.wav",
            "format": "wav",
            "category": "synthesized",
            "duration": 3.0 + (i * 0.3),
            "sample_rate": 22050,
            "channels": 1,
            "bit_depth": 16,
            "size_bytes": 200000 + (i * 20000),
        })
    
    return metadata


def create_test_data_index(
    profiles: List[Dict[str, Any]],
    projects: List[Dict[str, Any]],
    audio_metadata: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Create test data index."""
    return {
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "audio_files": audio_metadata,
        "profiles": [
            {
                "id": p["id"],
                "name": p["name"],
                "path": "profiles/sample_profiles.json",
            }
            for p in profiles
        ],
        "projects": [
            {
                "id": p["id"],
                "name": p["name"],
                "path": "projects/sample_projects.json",
            }
            for p in projects
        ],
    }


def main():
    """Generate all test data."""
    print("Generating test data for VoiceStudio Quantum+...")
    
    # Create directories
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate profiles
    print("Generating test profiles...")
    profiles = create_test_profiles()
    profiles_path = PROFILES_DIR / "sample_profiles.json"
    with open(profiles_path, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)
    print(f"  Created {len(profiles)} profiles: {profiles_path}")
    
    # Generate projects
    print("Generating test projects...")
    projects = create_test_projects(profiles)
    projects_path = PROJECTS_DIR / "sample_projects.json"
    with open(projects_path, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2, ensure_ascii=False)
    print(f"  Created {len(projects)} projects: {projects_path}")
    
    # Generate audio metadata
    print("Generating audio metadata...")
    audio_metadata = create_audio_metadata()
    audio_metadata_path = METADATA_DIR / "audio_metadata.json"
    with open(audio_metadata_path, "w", encoding="utf-8") as f:
        json.dump(audio_metadata, f, indent=2, ensure_ascii=False)
    print(f"  Created metadata for {len(audio_metadata)} audio files: {audio_metadata_path}")
    
    # Generate test data index
    print("Generating test data index...")
    index = create_test_data_index(profiles, projects, audio_metadata)
    index_path = METADATA_DIR / "test_data_index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"  Created test data index: {index_path}")
    
    print("\nTest data generation complete!")
    print(f"  Profiles: {len(profiles)}")
    print(f"  Projects: {len(projects)}")
    print(f"  Audio files: {len(audio_metadata)}")


if __name__ == "__main__":
    main()

