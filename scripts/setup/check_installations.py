#!/usr/bin/env python
"""Check if required packages are installed"""

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
        print(f"✅ {package_name}: INSTALLED")
        return True
    except ImportError:
        print(f"❌ {package_name}: NOT INSTALLED")
        return False

print("=" * 60)
print("VoiceStudio Dependency Check")
print("=" * 60)
print()

# Critical packages
print("CRITICAL PACKAGES:")
print("-" * 60)
tortoise_installed = check_package("tortoise-tts", "tortoise")
moviepy_installed = check_package("moviepy", "moviepy")

print()
print("OTHER IMPORTANT PACKAGES:")
print("-" * 60)
check_package("torch", "torch")
check_package("transformers", "transformers")
check_package("coqui-tts", "TTS")
check_package("librosa", "librosa")
check_package("numpy", "numpy")
check_package("soundfile", "soundfile")

print()
print("=" * 60)
if not tortoise_installed:
    print("⚠️  WARNING: tortoise-tts is NOT installed")
    print("   Note: According to requirements_engines.txt, tortoise-tts")
    print("   is commented out because it conflicts with PyTorch 2.2.2 stack")
    print("   It should be isolated in a separate venv if needed.")
    print()
if not moviepy_installed:
    print("⚠️  WARNING: moviepy is NOT installed")
    print("   Install with: pip install moviepy>=1.0.3")
    print()
if tortoise_installed and moviepy_installed:
    print("✅ All critical packages are installed!")
    print()
print("=" * 60)

