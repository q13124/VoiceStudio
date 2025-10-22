"""
VoiceStudio Ultimate Setup Script
Automated setup for VoiceStudio with real XTTS v2 integration
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major != 3 or version.minor < 10:
        print(f"❌ Python 3.10+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor} detected")
    return True


def install_dependencies():
    """Install required dependencies"""
    commands = [
        (
            "pip install TTS==0.24.1 torch==2.2.2+cu121 torchaudio==2.2.2+cu121 -f https://download.pytorch.org/whl/torch_stable.html",
            "Installing TTS and PyTorch",
        ),
        (
            "pip install soundfile fastapi uvicorn pydantic==1.* pytest",
            "Installing additional dependencies",
        ),
    ]

    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    return True


def create_directories():
    """Create necessary directories"""
    dirs = ["config", "services/adapters", "tests", "logs", "models", "cache", "web"]

    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")

    return True


def verify_config():
    """Verify configuration files exist"""
    config_files = ["config/voicestudio.yaml", "config/engines.yaml"]

    for config_file in config_files:
        if not Path(config_file).exists():
            print(f"⚠️  Configuration file missing: {config_file}")
            return False
        print(f"✅ Configuration file exists: {config_file}")

    return True


def run_tests():
    """Run the test suite"""
    test_commands = [
        (
            "python -c \"import TTS; print('TTS version:', TTS.__version__)\"",
            "Verifying TTS installation",
        ),
        (
            "python -c \"import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available())\"",
            "Verifying PyTorch installation",
        ),
        ("pytest tests/ -v", "Running test suite"),
    ]

    for cmd, desc in test_commands:
        if not run_command(cmd, desc):
            print(f"⚠️  {desc} failed, but continuing...")

    return True


def start_router():
    """Start the VoiceStudio router"""
    print("🚀 Starting VoiceStudio Router with real XTTS...")
    print("   Run this command in a separate terminal:")
    print("   python -m services.run_router_with_xtts")
    print()
    print("   Then test with:")
    print("   curl http://127.0.0.1:5090/health")
    print(
        '   curl -X POST http://127.0.0.1:5090/tts -H "content-type: application/json" -d \'{"text":"Hello VoiceStudio", "language":"en", "quality":"balanced", "mode":"sync"}\''
    )
    print()
    print("   Web Dashboard:")
    print("   Open web/dashboard.html in your browser")
    print("   Or run: cd web && npm install && npm run dev")


def main():
    """Main setup function"""
    print("🎤 VoiceStudio Ultimate Setup")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        return False

    # Create directories
    if not create_directories():
        return False

    # Install dependencies
    if not install_dependencies():
        return False

    # Verify configuration
    if not verify_config():
        print("⚠️  Some configuration files are missing, but setup can continue")

    # Run tests
    if not run_tests():
        print("⚠️  Some tests failed, but setup can continue")

    # Start instructions
    start_router()

    print("\n🎉 VoiceStudio setup completed!")
    print("   Check SETUP_AND_TEST.md for detailed usage instructions")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
