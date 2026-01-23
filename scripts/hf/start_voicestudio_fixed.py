#!/usr/bin/env python3
"""
VoiceStudio Startup Script with Hugging Face API Fix

This script applies the Hugging Face API endpoint fix and then starts VoiceStudio.
Run this instead of the normal startup script to ensure the fix is always applied.
"""

import os
import sys
import subprocess
from pathlib import Path

def apply_hf_fix():
    """Apply the Hugging Face API endpoint fix."""
    print("Applying Hugging Face API endpoint fix...")

    # Import and run the fix script
    try:
        # Import the fix function directly
        sys.path.insert(0, str(Path(__file__).parent))

        # Set environment variables (minimal version of the fix)
        os.environ["HF_INFERENCE_API_BASE"] = "https://router.huggingface.co"
        os.environ["HF_ENDPOINT"] = "https://router.huggingface.co"

        # Try to run the full fix script
        try:
            from fix_huggingface_api import (
                force_environment_variables,
                patch_requests_if_needed,
                patch_urllib_if_needed,
                test_huggingface_hub,
                test_transformers
            )

            force_environment_variables()
            patch_requests_if_needed()
            patch_urllib_if_needed()
            test_huggingface_hub()
            test_transformers()

            print("Hugging Face API fix applied successfully!")
            return True

        except ImportError:
            print("Warning: Could not import full fix script, using minimal fix")
            print("Environment variables set to router endpoint")
            return True

    except Exception as e:
        print(f"Warning: Fix application failed: {e}")
        print("Continuing with startup anyway...")
        return False

def start_voicestudio():
    """Start VoiceStudio backend."""
    print("\nStarting VoiceStudio...")

    # Try different startup methods
    startup_commands = [
        ["python", "-m", "backend.api.main"],
        ["python", "backend/api/main.py"],
        ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"],
    ]

    for cmd in startup_commands:
        try:
            print(f"Trying: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {e}")
            continue
        except FileNotFoundError:
            continue

    # If none worked, try the PowerShell startup script
    try:
        ps_script = Path("start_backend.ps1")
        if ps_script.exists():
            print("Trying PowerShell startup script...")
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_script)], check=True)
            return True
    except Exception as e:
        print(f"PowerShell startup failed: {e}")

    print("Could not start VoiceStudio automatically.")
    print("Please start it manually with one of these commands:")
    print("  python -m backend.api.main")
    print("  python backend/api/main.py")
    print("  uvicorn backend.api.main:app --host 0.0.0.0 --port 8000")
    return False

def main():
    """Main startup function."""
    print("=" * 60)
    print("VoiceStudio Startup with Hugging Face API Fix")
    print("=" * 60)

    # Change to project root
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Apply the fix
    fix_applied = apply_hf_fix()

    if fix_applied:
        print("\n" + "=" * 60)
        print("READY TO START VOICESTUDIO")
        print("=" * 60)
        print("The Hugging Face API endpoint has been fixed.")
        print("You should no longer see the 'api-inference.huggingface.co is no longer supported' error.")
    else:
        print("\n" + "!" * 60)
        print("WARNING: Fix may not have been applied completely")
        print("!" * 60)

    print("\nStarting VoiceStudio backend...")
    print("Press Ctrl+C to stop the server")
    print()

    # Start VoiceStudio
    success = start_voicestudio()

    if not success:
        print("\n" + "=" * 60)
        print("MANUAL STARTUP REQUIRED")
        print("=" * 60)
        print("Please run one of these commands manually:")
        print("  python -m backend.api.main")
        print("  python backend/api/main.py")
        print("  ./start_backend.ps1 (Windows PowerShell)")

if __name__ == "__main__":
    main()