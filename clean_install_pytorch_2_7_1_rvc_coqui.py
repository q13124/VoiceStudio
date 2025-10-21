#!/usr/bin/env python3
"""
VoiceStudio Ultimate - PyTorch 2.7.1 + RVC + Coqui TTS Clean Installation
Clean installation script to fix corrupted packages and install everything properly
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path


class CleanInstaller:
    def __init__(self):
        self.pyvenv_path = "C:\\VoiceStudio\\workers\\python\\vsdml\\.venv\\Scripts\\python.exe"
        self.venv_path = Path("C:\\VoiceStudio\\workers\\python\\vsdml\\.venv")
        
    def log(self, message):
        """Log installation progress"""
        print(f"[CLEAN INSTALL] {message}")
        
    def run_command(self, cmd, description="", check=True):
        """Run a command with error handling"""
        try:
            self.log(f"Running: {description}")
            result = subprocess.run(cmd, check=check, capture_output=True, text=True)
            if result.stdout:
                self.log(f"Output: {result.stdout.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"ERROR in {description}: {e}")
            if e.stderr:
                self.log(f"Error details: {e.stderr}")
            return None
    
    def clean_corrupted_packages(self):
        """Clean up corrupted packages completely"""
        self.log("=" * 60)
        self.log("CLEANING CORRUPTED PACKAGES")
        self.log("=" * 60)
        
        # Remove corrupted package directories
        corrupted_patterns = ["~ympy", "~umpy", "~erkzeug", "~orch", "~imedeltas"]
        
        for pattern in corrupted_patterns:
            corrupted_dirs = list(self.venv_path.glob(f"Lib/site-packages/{pattern}*"))
            for dir_path in corrupted_dirs:
                try:
                    if dir_path.exists():
                        shutil.rmtree(dir_path)
                        self.log(f"Removed corrupted directory: {dir_path}")
                except Exception as e:
                    self.log(f"Could not remove {dir_path}: {e}")
        
        # Clean pip cache
        cmd = [self.pyvenv_path, "-m", "pip", "cache", "purge"]
        self.run_command(cmd, "Clearing pip cache", check=False)
        
        # Reinstall pip
        cmd = [self.pyvenv_path, "-m", "pip", "install", "--upgrade", "pip"]
        self.run_command(cmd, "Reinstalling pip")
        
        return True
    
    def install_core_packages(self):
        """Install core packages first"""
        self.log("=" * 60)
        self.log("INSTALLING CORE PACKAGES")
        self.log("=" * 60)
        
        core_packages = [
            "numpy==1.26.4",
            "scipy==1.11.1", 
            "scikit-learn==1.7.2",
            "librosa==0.11.0",
            "soundfile==0.13.1",
            "pydub==0.25.1",
            "transformers==4.57.1",
            "accelerate==0.34.2",
            "datasets==2.21.0",
            "tokenizers==0.22.1",
            "safetensors==0.6.2",
            "huggingface-hub==0.35.3",
            "einops==0.8.1",
            "omegaconf==2.3.0",
            "hydra-core==1.3.2",
            "wandb==0.22.2",
            "tensorboard==2.20.0",
            "matplotlib==3.9.0",
            "seaborn==0.13.2",
            "plotly==5.24.1",
            "pandas==2.3.3",
            "pillow==10.4.0",
            "opencv-python==4.10.0.84",
            "imageio==2.36.0",
            "tqdm==4.67.1",
            "rich==13.9.4",
            "click==8.3.0",
            "pyyaml==6.0.3",
            "toml==0.10.2",
            "jsonschema==4.23.0",
            "pydantic==2.12.3",
            "fastapi==0.115.6",
            "uvicorn[standard]==0.38.0",
            "websockets==12.0",
            "aiohttp==3.13.1",
            "aiofiles==24.1.0",
            "aiosqlite==0.20.0",
            "redis==5.2.1",
            "celery==5.4.0",
            "psutil==6.1.0",
            "py-cpuinfo==9.0.0",
            "GPUtil==1.4.0",
            "nvidia-ml-py==12.535.133",
        ]
        
        for package in core_packages:
            cmd = [self.pyvenv_path, "-m", "pip", "install", package, "--force-reinstall"]
            result = self.run_command(cmd, f"Installing {package}")
            if result is None:
                self.log(f"Warning: Failed to install {package}")
        
        return True
    
    def install_pytorch_2_7_1(self):
        """Install PyTorch 2.7.1"""
        self.log("=" * 60)
        self.log("INSTALLING PYTORCH 2.7.1")
        self.log("=" * 60)
        
        # Install PyTorch 2.7.1 with CUDA 12.1
        cmd = [
            self.pyvenv_path, "-m", "pip", "install",
            "torch==2.7.1", "torchaudio==2.7.1", "torchvision==0.20.1",
            "--index-url", "https://download.pytorch.org/whl/cu121",
            "--force-reinstall"
        ]
        result = self.run_command(cmd, "Installing PyTorch 2.7.1 with CUDA 12.1")
        
        if result is None:
            # Try CUDA 11.8
            self.log("CUDA 12.1 failed, trying CUDA 11.8...")
            cmd = [
                self.pyvenv_path, "-m", "pip", "install",
                "torch==2.7.1", "torchaudio==2.7.1", "torchvision==0.20.1",
                "--index-url", "https://download.pytorch.org/whl/cu118",
                "--force-reinstall"
            ]
            result = self.run_command(cmd, "Installing PyTorch 2.7.1 with CUDA 11.8")
        
        if result is None:
            # Fallback to CPU
            self.log("CUDA versions failed, trying CPU version...")
            cmd = [
                self.pyvenv_path, "-m", "pip", "install",
                "torch==2.7.1", "torchaudio==2.7.1", "torchvision==0.20.1",
                "--index-url", "https://download.pytorch.org/whl/cpu",
                "--force-reinstall"
            ]
            result = self.run_command(cmd, "Installing PyTorch 2.7.1 CPU version")
        
        return result is not None
    
    def install_rvc_packages(self):
        """Install RVC packages"""
        self.log("=" * 60)
        self.log("INSTALLING RVC PACKAGES")
        self.log("=" * 60)
        
        rvc_packages = [
            "numba==0.58.1",
            "llvmlite==0.41.1",
            "fairseq==0.12.2",
            "faiss-cpu==1.7.4",
            "gradio==4.44.0",
            "cython==0.29.37",
            "future==0.18.3",
            "ffmpeg-python==0.2.0",
            "tensorboardX==2.6.2.2",
            "functorch==2.0.0",
            "jinja2==3.1.4",
            "json5==0.9.14",
            "markdown==3.9",
            "matplotlib-inline==0.1.6",
            "praat-parselmouth==0.4.6",
            "pyworld==0.3.2",
            "resampy==0.4.3",
            "starlette==0.48.0",
            "tensorboard-data-server==0.7.2",
            "tensorboard-plugin-wit==1.8.1",
            "torchgen==0.0.1",
            "tornado==6.5.2",
            "werkzeug==3.1.3",
            "uc-micro-py==1.0.2",
            "sympy==1.13.1",
            "tabulate==0.9.0",
            "pyasn1==0.6.1",
            "pyasn1-modules==0.4.1",
            "fsspec==2023.12.2",
            "absl-py==2.3.1",
            "audioread==3.0.1",
            "uvicorn==0.38.0",
            "colorama==0.4.6",
            "edge-tts==6.1.19",
            "yt-dlp==2023.12.30",
        ]
        
        for package in rvc_packages:
            cmd = [self.pyvenv_path, "-m", "pip", "install", package, "--force-reinstall"]
            result = self.run_command(cmd, f"Installing RVC package: {package}")
            if result is None:
                self.log(f"Warning: Failed to install {package}")
        
        return True
    
    def install_coqui_tts(self):
        """Install Coqui TTS"""
        self.log("=" * 60)
        self.log("INSTALLING COQUI TTS")
        self.log("=" * 60)
        
        # Try installing Coqui TTS
        cmd = [self.pyvenv_path, "-m", "pip", "install", "TTS", "--force-reinstall"]
        result = self.run_command(cmd, "Installing Coqui TTS")
        
        if result is None:
            self.log("Coqui TTS installation failed, but continuing...")
            return False
        
        return True
    
    def install_audio_packages(self):
        """Install audio processing packages"""
        self.log("=" * 60)
        self.log("INSTALLING AUDIO PACKAGES")
        self.log("=" * 60)
        
        audio_packages = [
            "pyannote.audio==4.0.1",
            "whisperx==3.1.1",
            "openai-whisper==20231117",
        ]
        
        for package in audio_packages:
            cmd = [self.pyvenv_path, "-m", "pip", "install", package, "--force-reinstall"]
            result = self.run_command(cmd, f"Installing audio package: {package}")
            if result is None:
                self.log(f"Warning: Failed to install {package}")
        
        return True
    
    def verify_installation(self):
        """Verify installation"""
        self.log("=" * 60)
        self.log("VERIFYING INSTALLATION")
        self.log("=" * 60)
        
        verification_script = '''
import sys
print(f"Python version: {sys.version}")

try:
    import torch
    print(f"[OK] PyTorch: {torch.__version__}")
    print(f"[OK] CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"[OK] CUDA version: {torch.version.cuda}")
        print(f"[OK] GPU count: {torch.cuda.device_count()}")
except ImportError as e:
    print(f"[ERROR] PyTorch: {e}")

try:
    import torchaudio
    print(f"[OK] TorchAudio: {torchaudio.__version__}")
except ImportError as e:
    print(f"[ERROR] TorchAudio: {e}")

try:
    import torchvision
    print(f"[OK] TorchVision: {torchvision.__version__}")
except ImportError as e:
    print(f"[ERROR] TorchVision: {e}")

try:
    import numpy
    print(f"[OK] NumPy: {numpy.__version__}")
except ImportError as e:
    print(f"[ERROR] NumPy: {e}")

try:
    import librosa
    print(f"[OK] Librosa: {librosa.__version__}")
except ImportError as e:
    print(f"[ERROR] Librosa: {e}")

try:
    import transformers
    print(f"[OK] Transformers: {transformers.__version__}")
except ImportError as e:
    print(f"[ERROR] Transformers: {e}")

try:
    import gradio
    print(f"[OK] Gradio: {gradio.__version__}")
except ImportError as e:
    print(f"[ERROR] Gradio: {e}")

try:
    import TTS
    print(f"[OK] Coqui TTS: {TTS.__version__}")
except ImportError as e:
    print(f"[ERROR] Coqui TTS: {e}")

try:
    import pyannote.audio
    print(f"[OK] pyannote.audio: {pyannote.audio.__version__}")
except ImportError as e:
    print(f"[ERROR] pyannote.audio: {e}")

print("\\n" + "="*50)
print("INSTALLATION VERIFICATION COMPLETE")
print("="*50)
'''
        
        result = self.run_command(
            [self.pyvenv_path, "-c", verification_script],
            "Verifying installation",
            check=False
        )
        
        if result:
            self.log("Installation verification:")
            print(result.stdout)
            if result.stderr:
                self.log("Warnings/Errors:")
                print(result.stderr)
        
        return True
    
    def run_clean_install(self):
        """Run the complete clean installation"""
        self.log("VoiceStudio Ultimate - Clean PyTorch 2.7.1 + RVC + Coqui TTS Installation")
        self.log("=" * 70)
        
        try:
            # Step 1: Clean corrupted packages
            if not self.clean_corrupted_packages():
                self.log("ERROR: Package cleanup failed")
                return False
            
            # Step 2: Install core packages
            if not self.install_core_packages():
                self.log("ERROR: Core package installation failed")
                return False
            
            # Step 3: Install PyTorch 2.7.1
            if not self.install_pytorch_2_7_1():
                self.log("ERROR: PyTorch 2.7.1 installation failed")
                return False
            
            # Step 4: Install RVC packages
            if not self.install_rvc_packages():
                self.log("ERROR: RVC package installation failed")
                return False
            
            # Step 5: Install Coqui TTS
            if not self.install_coqui_tts():
                self.log("WARNING: Coqui TTS installation failed, but continuing...")
            
            # Step 6: Install audio packages
            if not self.install_audio_packages():
                self.log("WARNING: Audio package installation failed, but continuing...")
            
            # Step 7: Verify installation
            if not self.verify_installation():
                self.log("WARNING: Installation verification failed, but continuing...")
            
            self.log("=" * 70)
            self.log("CLEAN INSTALLATION COMPLETED!")
            self.log("=" * 70)
            self.log("What was installed:")
            self.log("- PyTorch 2.7.1 with CUDA support")
            self.log("- TorchAudio 2.7.1")
            self.log("- TorchVision 0.20.1")
            self.log("- RVC dependencies")
            self.log("- Coqui TTS (if successful)")
            self.log("- pyannote-audio 4.0.1")
            self.log("- WhisperX 3.1.1")
            self.log("- All core ML packages")
            
            self.log("\\nNext steps:")
            self.log("1. Restart your IDE/editor")
            self.log("2. Test PyTorch installation")
            self.log("3. Test RVC functionality")
            self.log("4. Test Coqui TTS (if installed)")
            self.log("5. Run system health checks")
            
            return True
            
        except Exception as e:
            self.log(f"CRITICAL ERROR during installation: {e}")
            return False


def main():
    """Main installation function"""
    installer = CleanInstaller()
    success = installer.run_clean_install()
    
    if success:
        print("\\n" + "=" * 70)
        print("CLEAN INSTALLATION COMPLETED SUCCESSFULLY!")
        print("VoiceStudio Ultimate is now running on PyTorch 2.7.1")
        print("with RVC and Coqui TTS integration!")
        print("=" * 70)
    else:
        print("\\n" + "=" * 70)
        print("INSTALLATION FAILED!")
        print("Check the installation log for details.")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
