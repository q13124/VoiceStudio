#!/usr/bin/env python3
"""
VoiceStudio Environment Verification Script

Checks that the environment is properly configured for VoiceStudio.
Verifies model storage paths, engine manifests, and dependencies.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple

# Colors for output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def check_model_storage() -> Tuple[bool, List[str]]:
    """Check model storage directory."""
    issues = []
    programdata = os.getenv("PROGRAMDATA", os.path.expanduser("~"))
    models_dir = Path(programdata) / "VoiceStudio" / "models"
    
    if not models_dir.exists():
        issues.append(f"Model storage directory does not exist: {models_dir}")
        try:
            models_dir.mkdir(parents=True, exist_ok=True)
            issues.append(f"Created model storage directory: {models_dir}")
        except Exception as e:
            issues.append(f"Failed to create model storage directory: {e}")
            return False, issues
    
    # Check if directory is writable
    try:
        test_file = models_dir / ".test_write"
        test_file.write_text("test")
        test_file.unlink()
    except Exception as e:
        issues.append(f"Model storage directory is not writable: {e}")
        return False, issues
    
    return True, issues


def check_engine_manifests() -> Tuple[bool, List[str]]:
    """Check engine manifest files."""
    issues = []
    engines_dir = Path("engines")
    
    if not engines_dir.exists():
        issues.append(f"Engines directory does not exist: {engines_dir}")
        return False, issues
    
    # Find all engine manifests
    manifests = list(engines_dir.rglob("engine.manifest.json"))
    
    if not manifests:
        issues.append("No engine manifest files found")
        return False, issues
    
    # Verify each manifest
    for manifest_path in manifests:
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            
            # Check required fields
            required_fields = ["engine_id", "name", "type", "entry_point"]
            for field in required_fields:
                if field not in manifest:
                    issues.append(f"Manifest {manifest_path} missing required field: {field}")
            
            # Check model paths use PROGRAMDATA
            if "model_paths" in manifest:
                for key, path in manifest["model_paths"].items():
                    if "%PROGRAMDATA%" not in path:
                        issues.append(f"Manifest {manifest_path} model path '{key}' does not use %PROGRAMDATA%: {path}")
        
        except json.JSONDecodeError as e:
            issues.append(f"Invalid JSON in manifest {manifest_path}: {e}")
        except Exception as e:
            issues.append(f"Error reading manifest {manifest_path}: {e}")
    
    return len(issues) == 0, issues


def check_python_dependencies() -> Tuple[bool, List[str]]:
    """Check Python dependencies."""
    issues = []
    
    # Check for required packages
    required_packages = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "pydantic": "Pydantic",
        "torch": "PyTorch (optional but recommended)"
    }
    
    for package, name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            issues.append(f"Missing package: {name} ({package})")
    
    return len(issues) == 0, issues


def check_model_storage_paths() -> Tuple[bool, List[str]]:
    """Check that model storage paths are properly configured."""
    issues = []
    programdata = os.getenv("PROGRAMDATA", os.path.expanduser("~"))
    models_base = Path(programdata) / "VoiceStudio" / "models"
    
    # Expected engine directories
    expected_engines = [
        "xtts_v2",
        "chatterbox",
        "tortoise",
        "piper",
        "openvoice",
        "sdxl",
        "realesrgan",
        "svd"
    ]
    
    for engine in expected_engines:
        engine_dir = models_base / engine
        if not engine_dir.exists():
            issues.append(f"Engine model directory does not exist (will be created on first use): {engine_dir}")
    
    return True, issues  # Not critical, directories will be created as needed


def main():
    """Run all checks."""
    print(f"{GREEN}VoiceStudio Environment Verification{RESET}\n")
    
    all_passed = True
    results = []
    
    # Check model storage
    print("Checking model storage...")
    passed, issues = check_model_storage()
    results.append(("Model Storage", passed, issues))
    if passed:
        print(f"  {GREEN}✓{RESET} Model storage OK")
    else:
        print(f"  {RED}✗{RESET} Model storage issues:")
        for issue in issues:
            print(f"    - {issue}")
        all_passed = False
    
    # Check engine manifests
    print("\nChecking engine manifests...")
    passed, issues = check_engine_manifests()
    results.append(("Engine Manifests", passed, issues))
    if passed:
        print(f"  {GREEN}✓{RESET} Engine manifests OK")
    else:
        print(f"  {RED}✗{RESET} Engine manifest issues:")
        for issue in issues:
            print(f"    - {issue}")
        all_passed = False
    
    # Check Python dependencies
    print("\nChecking Python dependencies...")
    passed, issues = check_python_dependencies()
    results.append(("Python Dependencies", passed, issues))
    if passed:
        print(f"  {GREEN}✓{RESET} Python dependencies OK")
    else:
        print(f"  {YELLOW}⚠{RESET} Missing Python packages:")
        for issue in issues:
            print(f"    - {issue}")
        # Not critical, just a warning
    
    # Check model storage paths
    print("\nChecking model storage paths...")
    passed, issues = check_model_storage_paths()
    results.append(("Model Storage Paths", passed, issues))
    if passed and not issues:
        print(f"  {GREEN}✓{RESET} Model storage paths OK")
    else:
        print(f"  {YELLOW}⚠{RESET} Model storage path notes:")
        for issue in issues:
            print(f"    - {issue}")
    
    # Summary
    print(f"\n{GREEN}{'='*50}{RESET}")
    if all_passed:
        print(f"{GREEN}✓ All critical checks passed!{RESET}")
    else:
        print(f"{YELLOW}⚠ Some checks failed. Please review above.{RESET}")
    print(f"{GREEN}{'='*50}{RESET}\n")
    
    # Print model storage location
    programdata = os.getenv("PROGRAMDATA", os.path.expanduser("~"))
    models_dir = Path(programdata) / "VoiceStudio" / "models"
    print(f"Model storage location: {models_dir}")
    print(f"PROGRAMDATA: {programdata}\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

