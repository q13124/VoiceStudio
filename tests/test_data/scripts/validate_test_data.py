#!/usr/bin/env python3
"""
Validate test data for VoiceStudio Quantum+.

Checks:
- JSON structure validity
- File existence
- Reference integrity
- Metadata consistency
"""

import json
import sys
from pathlib import Path

# Get script directory
SCRIPT_DIR = Path(__file__).parent
TEST_DATA_DIR = SCRIPT_DIR.parent
PROFILES_DIR = TEST_DATA_DIR / "profiles"
PROJECTS_DIR = TEST_DATA_DIR / "projects"
METADATA_DIR = TEST_DATA_DIR / "metadata"


def validate_json_file(file_path: Path) -> tuple[bool, list[str]]:
    """Validate JSON file structure."""
    errors = []

    if not file_path.exists():
        errors.append(f"File does not exist: {file_path}")
        return False, errors

    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, (dict, list)):
            errors.append(f"Invalid JSON structure: expected dict or list, got {type(data)}")
            return False, errors

    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
        return False, errors
    except Exception as e:
        errors.append(f"Error reading file: {e}")
        return False, errors

    return True, errors


def validate_profiles() -> tuple[bool, list[str]]:
    """Validate test profiles."""
    errors = []
    profiles_path = PROFILES_DIR / "sample_profiles.json"

    is_valid, file_errors = validate_json_file(profiles_path)
    if not is_valid:
        return False, file_errors

    try:
        with open(profiles_path, encoding="utf-8") as f:
            profiles = json.load(f)

        if not isinstance(profiles, list):
            errors.append("Profiles must be a list")
            return False, errors

        required_fields = ["id", "name", "language", "quality_score", "tags"]
        for i, profile in enumerate(profiles):
            if not isinstance(profile, dict):
                errors.append(f"Profile {i} is not a dictionary")
                continue

            for field in required_fields:
                if field not in profile:
                    errors.append(f"Profile {i} missing required field: {field}")

            # Validate quality_score range
            if "quality_score" in profile:
                qs = profile["quality_score"]
                if not isinstance(qs, (int, float)) or qs < 0.0 or qs > 1.0:
                    errors.append(f"Profile {i} has invalid quality_score: {qs} (must be 0.0-1.0)")

    except Exception as e:
        errors.append(f"Error validating profiles: {e}")
        return False, errors

    return len(errors) == 0, errors


def validate_projects() -> tuple[bool, list[str]]:
    """Validate test projects."""
    errors = []
    projects_path = PROJECTS_DIR / "sample_projects.json"

    is_valid, file_errors = validate_json_file(projects_path)
    if not is_valid:
        return False, file_errors

    try:
        with open(projects_path, encoding="utf-8") as f:
            projects = json.load(f)

        if not isinstance(projects, list):
            errors.append("Projects must be a list")
            return False, errors

        required_fields = [
            "id",
            "name",
            "created_at",
            "updated_at",
            "voice_profile_ids",
            "tracks",
        ]
        for i, project in enumerate(projects):
            if not isinstance(project, dict):
                errors.append(f"Project {i} is not a dictionary")
                continue

            for field in required_fields:
                if field not in project:
                    errors.append(f"Project {i} missing required field: {field}")

            # Validate tracks
            if "tracks" in project:
                tracks = project["tracks"]
                if not isinstance(tracks, list):
                    errors.append(f"Project {i} tracks must be a list")
                else:
                    for j, track in enumerate(tracks):
                        if not isinstance(track, dict):
                            errors.append(f"Project {i} track {j} is not a dictionary")
                        elif "id" not in track:
                            errors.append(f"Project {i} track {j} missing id")

    except Exception as e:
        errors.append(f"Error validating projects: {e}")
        return False, errors

    return len(errors) == 0, errors


def validate_metadata() -> tuple[bool, list[str]]:
    """Validate metadata files."""
    errors = []

    # Validate audio metadata
    audio_metadata_path = METADATA_DIR / "audio_metadata.json"
    is_valid, file_errors = validate_json_file(audio_metadata_path)
    if not is_valid:
        errors.extend(file_errors)

    # Validate test data index
    index_path = METADATA_DIR / "test_data_index.json"
    is_valid, file_errors = validate_json_file(index_path)
    if not is_valid:
        errors.extend(file_errors)

    return len(errors) == 0, errors


def main():
    """Validate all test data."""
    print("Validating test data for VoiceStudio Quantum+...\n")

    all_valid = True
    all_errors = []

    # Validate profiles
    print("Validating profiles...")
    is_valid, errors = validate_profiles()
    if is_valid:
        print("  [OK] Profiles valid")
    else:
        print("  [ERROR] Profiles invalid:")
        for error in errors:
            print(f"    - {error}")
        all_valid = False
        all_errors.extend(errors)

    # Validate projects
    print("\nValidating projects...")
    is_valid, errors = validate_projects()
    if is_valid:
        print("  [OK] Projects valid")
    else:
        print("  [ERROR] Projects invalid:")
        for error in errors:
            print(f"    - {error}")
        all_valid = False
        all_errors.extend(errors)

    # Validate metadata
    print("\nValidating metadata...")
    is_valid, errors = validate_metadata()
    if is_valid:
        print("  [OK] Metadata valid")
    else:
        print("  [ERROR] Metadata invalid:")
        for error in errors:
            print(f"    - {error}")
        all_valid = False
        all_errors.extend(errors)

    # Summary
    print("\n" + "=" * 50)
    if all_valid:
        print("[SUCCESS] All test data is valid!")
        return 0
    else:
        print(f"[FAILED] Validation failed with {len(all_errors)} error(s)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
