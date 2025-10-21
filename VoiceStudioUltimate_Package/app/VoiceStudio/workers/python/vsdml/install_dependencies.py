#!/usr/bin/env python3
"""
Enhanced dependency installer for VSDML voice cloning system
Handles complex dependencies and ensures proper installation
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(command, description=""):
    """Run a command and handle errors gracefully"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed: {e.stderr}")
        return False

def install_core_dependencies():
    """Install core dependencies with proper handling"""
    print("🚀 Installing core dependencies for VSDML voice cloning system...")

    # Core ML dependencies
    core_deps = [
        "torch>=2.0.0,<3.0.0",
        "torchaudio>=2.0.0,<3.0.0",
        "numpy>=1.20.0,<2.0.0",
        "pandas>=1.3.0,<3.0.0",
        "scipy>=1.7.0,<2.0.0",
        "scikit-learn>=1.0.0,<2.0.0",
        "huggingface-hub>=0.15.0,<1.0.0"
    ]

    for dep in core_deps:
        run_command(f"pip install '{dep}'", f"Installing {dep.split('>=')[0]}")

    return True

def install_audio_dependencies():
    """Install audio processing dependencies"""
    print("🎵 Installing audio processing dependencies...")

    audio_deps = [
        "soundfile>=0.13.0,<1.0.0",
        "pydub>=0.25.0,<1.0.0",
        "librosa>=0.10.0,<1.0.0",
        "webrtcvad>=2.0.10,<3.0.0"
    ]

    for dep in audio_deps:
        run_command(f"pip install '{dep}'", f"Installing {dep.split('>=')[0]}")

    # Special handling for pyannote-audio and whisperx
    run_command("pip install 'pyannote-audio>=4.0.0,<5.0.0'", "Installing pyannote-audio")
    run_command("pip install 'whisperx>=3.0.0,<4.0.0'", "Installing whisperx")

    return True

def install_async_dependencies():
    """Install async processing dependencies"""
    print("⚡ Installing async processing dependencies...")

    async_deps = [
        "aiofiles>=23.0.0,<24.0.0",
        "aiohttp>=3.8.0,<4.0.0"
    ]

    for dep in async_deps:
        run_command(f"pip install '{dep}'", f"Installing {dep.split('>=')[0]}")

    # Handle asyncio-mqtt separately as it might need special handling
    run_command("pip install 'asyncio-mqtt>=0.13.0,<1.0.0'", "Installing asyncio-mqtt")

    return True

def install_optimization_dependencies():
    """Install optimization and caching dependencies"""
    print("🔧 Installing optimization dependencies...")

    opt_deps = [
        "cachetools>=5.0.0,<6.0.0",
        "joblib>=1.2.0,<2.0.0",
        "psutil>=5.9.0,<6.0.0",
        "redis>=4.0.0,<5.0.0",
        "cryptography>=3.4.8,<42.0.0"
    ]

    for dep in opt_deps:
        run_command(f"pip install '{dep}'", f"Installing {dep.split('>=')[0]}")

    return True

def install_testing_dependencies():
    """Install testing and development dependencies"""
    print("🧪 Installing testing dependencies...")

    test_deps = [
        "pytest>=7.0.0,<8.0.0",
        "pytest-asyncio>=0.21.0,<1.0.0",
        "pytest-cov>=4.0.0,<5.0.0",
        "black>=22.0.0,<24.0.0",
        "flake8>=5.0.0,<7.0.0",
        "mypy>=1.0.0,<2.0.0"
    ]

    for dep in test_deps:
        run_command(f"pip install '{dep}'", f"Installing {dep.split('>=')[0]}")

    return True

def install_documentation_dependencies():
    """Install documentation dependencies"""
    print("📚 Installing documentation dependencies...")

    doc_deps = [
        "docutils>=0.20.0,<1.0.0",
        "sphinx>=8.0.0,<9.0.0",
        "jinja2>=3.0.0,<4.0.0"
    ]

    for dep in doc_deps:
        run_command(f"pip install '{dep}'", f"Installing {dep.split('>=')[0]}")

    return True

def verify_installation():
    """Verify that all dependencies are properly installed"""
    print("🔍 Verifying installation...")

    critical_packages = [
        "torch", "torchaudio", "numpy", "pandas", "scipy",
        "soundfile", "pydub", "librosa", "pytest", "pytest-asyncio"
    ]

    all_good = True
    for package in critical_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - Missing")
            all_good = False

    return all_good

def main():
    """Main installation process"""
    print("🎯 VSDML Voice Cloning System - Enhanced Dependency Installer")
    print("=" * 60)

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)

    print(f"🐍 Python version: {sys.version}")
    print(f"💻 Platform: {platform.system()} {platform.release()}")

    # Install dependencies in order
    success = True

    success &= install_core_dependencies()
    success &= install_audio_dependencies()
    success &= install_async_dependencies()
    success &= install_optimization_dependencies()
    success &= install_testing_dependencies()
    success &= install_documentation_dependencies()

    if success:
        print("\n🎉 All dependencies installed successfully!")
        verify_installation()
    else:
        print("\n⚠️ Some dependencies failed to install. Check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
