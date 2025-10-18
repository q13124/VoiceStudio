#!/usr/bin/env python3
"""
Dependency installation script for VSDML.

This script ensures all required dependencies are installed in the virtual environment.
Run this script whenever you encounter import errors or when setting up the project.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    """Install all required dependencies from requirements.txt"""
    script_dir = Path(__file__).parent
    requirements_file = script_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"Error: {requirements_file} not found!")
        return False
    
    print("Installing VSDML dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ All dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def verify_imports():
    """Verify that critical imports work"""
    critical_imports = [
        "docutils",
        "sphinx", 
        "torch",
        "torchaudio",
        "pyannote.audio",
        "whisperx",
        "soundfile",
        "numpy",
        "pandas"
    ]
    
    print("Verifying critical imports...")
    failed_imports = []
    
    for module in critical_imports:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n⚠️  Failed imports: {', '.join(failed_imports)}")
        print("Run this script again to install missing dependencies.")
        return False
    else:
        print("\n🎉 All critical imports verified successfully!")
        return True

if __name__ == "__main__":
    print("VSDML Dependency Installer")
    print("=" * 40)
    
    # Install dependencies
    if install_dependencies():
        # Verify imports
        verify_imports()
    else:
        sys.exit(1)
