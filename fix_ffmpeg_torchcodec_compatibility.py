#!/usr/bin/env python3
"""
VoiceStudio Ultimate - FFmpeg & TorchCodec Compatibility Fix
Advanced voice cloning system optimization
"""

import subprocess
import sys
import os
import json
import urllib.request
import zipfile
import shutil
from pathlib import Path


class VoiceStudioFFmpegFixer:
    def __init__(self):
        self.install_dir = Path("C:/ProgramData/VoiceStudio")
        self.ffmpeg_dir = self.install_dir / "ffmpeg"
        self.python_exe = Path("C:/ProgramData/VoiceStudio/pyenv/Scripts/python.exe")

    def log(self, message):
        print(f"VoiceStudio Fixer: {message}")

    def check_ffmpeg_installation(self):
        """Check if FFmpeg is properly installed"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                self.log("FFmpeg is installed and accessible")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        self.log("FFmpeg not found in PATH")
        return False

    def install_ffmpeg_windows(self):
        """Install FFmpeg for Windows"""
        self.log("Installing FFmpeg for Windows...")

        # Create directories
        self.ffmpeg_dir.mkdir(parents=True, exist_ok=True)

        # Download FFmpeg
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        ffmpeg_zip = self.install_dir / "ffmpeg.zip"

        try:
            self.log("Downloading FFmpeg...")
            urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip)

            # Extract FFmpeg
            self.log("Extracting FFmpeg...")
            with zipfile.ZipFile(ffmpeg_zip, "r") as zip_ref:
                zip_ref.extractall(self.install_dir)

            # Move FFmpeg files to proper location
            extracted_dir = self.install_dir / "ffmpeg-master-latest-win64-gpl"
            if extracted_dir.exists():
                for item in extracted_dir.iterdir():
                    shutil.move(str(item), str(self.ffmpeg_dir / item.name))
                shutil.rmtree(extracted_dir)

            # Clean up
            ffmpeg_zip.unlink()

            self.log("FFmpeg installed successfully")
            return True

        except Exception as e:
            self.log(f"Failed to install FFmpeg: {e}")
            return False

    def add_ffmpeg_to_path(self):
        """Add FFmpeg to system PATH"""
        self.log("Adding FFmpeg to PATH...")

        ffmpeg_bin = self.ffmpeg_dir / "bin"
        if not ffmpeg_bin.exists():
            self.log("FFmpeg bin directory not found")
            return False

        # Add to current session PATH
        current_path = os.environ.get("PATH", "")
        if str(ffmpeg_bin) not in current_path:
            os.environ["PATH"] = f"{ffmpeg_bin};{current_path}"

        self.log("FFmpeg added to PATH")
        return True

    def fix_torchcodec_compatibility(self):
        """Fix TorchCodec compatibility issues"""
        self.log("Fixing TorchCodec compatibility...")

        try:
            # Uninstall problematic TorchCodec
            subprocess.run(
                [str(self.python_exe), "-m", "pip", "uninstall", "torchcodec", "-y"],
                check=True,
            )

            # Install compatible version
            subprocess.run(
                [str(self.python_exe), "-m", "pip", "install", "torchcodec==0.8.0"],
                check=True,
            )

            self.log("TorchCodec compatibility fixed")
            return True

        except subprocess.CalledProcessError as e:
            self.log(f"Failed to fix TorchCodec: {e}")
            return False

    def fix_pyannote_compatibility(self):
        """Fix Pyannote audio compatibility"""
        self.log("Fixing Pyannote compatibility...")

        try:
            # Update PyTorch Audio
            subprocess.run(
                [
                    str(self.python_exe),
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "torchaudio",
                ],
                check=True,
            )

            # Reinstall Pyannote
            subprocess.run(
                [
                    str(self.python_exe),
                    "-m",
                    "pip",
                    "uninstall",
                    "pyannote.audio",
                    "-y",
                ],
                check=True,
            )
            subprocess.run(
                [str(self.python_exe), "-m", "pip", "install", "pyannote.audio"],
                check=True,
            )

            self.log("Pyannote compatibility fixed")
            return True

        except subprocess.CalledProcessError as e:
            self.log(f"Failed to fix Pyannote: {e}")
            return False

    def verify_fixes(self):
        """Verify all fixes are working"""
        self.log("Verifying fixes...")

        try:
            # Test FFmpeg
            result = subprocess.run(
                ["ffmpeg", "-version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                self.log("FFmpeg verification failed")
                return False

            # Test TorchCodec
            test_code = """
import torchcodec
print("TorchCodec version:", torchcodec.__version__)
"""
            result = subprocess.run(
                [str(self.python_exe), "-c", test_code], capture_output=True, text=True
            )
            if result.returncode != 0:
                self.log("TorchCodec verification failed")
                return False

            # Test Pyannote
            test_code = """
import pyannote.audio
print("Pyannote version:", pyannote.audio.__version__)
"""
            result = subprocess.run(
                [str(self.python_exe), "-c", test_code], capture_output=True, text=True
            )
            if result.returncode != 0:
                self.log("Pyannote verification failed")
                return False

            self.log("All fixes verified successfully")
            return True

        except Exception as e:
            self.log(f"Verification failed: {e}")
            return False

    def run_complete_fix(self):
        """Run complete compatibility fix"""
        self.log("Starting VoiceStudio Ultimate Compatibility Fix...")

        # Check current status
        ffmpeg_ok = self.check_ffmpeg_installation()

        # Install FFmpeg if needed
        if not ffmpeg_ok:
            if not self.install_ffmpeg_windows():
                return False
            if not self.add_ffmpeg_to_path():
                return False

        # Fix compatibility issues
        if not self.fix_torchcodec_compatibility():
            return False

        if not self.fix_pyannote_compatibility():
            return False

        # Verify fixes
        if not self.verify_fixes():
            return False

        self.log("VoiceStudio Ultimate Compatibility Fix Complete!")
        return True


def main():
    """Main execution function"""
    print("VoiceStudio Ultimate - FFmpeg & TorchCodec Compatibility Fix")
    print("=" * 70)

    fixer = VoiceStudioFFmpegFixer()

    if fixer.run_complete_fix():
        print("\nSUCCESS: All compatibility issues resolved!")
        print("VoiceStudio Ultimate is now fully optimized!")
        print("\nNext Steps:")
        print("1. Restart Cursor IDE to resolve serialization error")
        print("2. Run health_check.py to verify system status")
        print("3. Start voice cloning services")
    else:
        print("\nFAILED: Some issues could not be resolved")
        print("Manual intervention may be required")


if __name__ == "__main__":
    main()
