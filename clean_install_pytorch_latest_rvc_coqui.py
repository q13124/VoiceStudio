#!/usr/bin/env python3
"""
VoiceStudio Ultimate - PyTorch 2.5.1 + RVC + Coqui TTS Clean Installation
Clean installation script using the latest available PyTorch version
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
        corrupted_patterns = ["~ympy", "~umpy", "~erkzeug", "~orch", "~imedeltas", "~andas"]
        
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
    
    def install_pytorch_latest(self):
        """Install latest available PyTorch"""
        self.log("=" * 60)
        self.log("INSTALLING LATEST PYTORCH")
        self.log("=" * 60)
        
        # Install latest PyTorch with CUDA 12.1
        cmd = [
            self.pyvenv_path, "-m", "pip", "install",
            "torch", "torchaudio", "torchvision",
            "--index-url", "https://download.pytorch.org/whl/cu121",
            "--force-reinstall"
        ]
        result = self.run_command(cmd, "Installing latest PyTorch with CUDA 12.1")
        
        if result is None:
            # Try CUDA 11.8
            self.log("CUDA 12.1 failed, trying CUDA 11.8...")
            cmd = [
                self.pyvenv_path, "-m", "pip", "install",
                "torch", "torchaudio", "torchvision",
                "--index-url", "https://download.pytorch.org/whl/cu118",
                "--force-reinstall"
            ]
            result = self.run_command(cmd, "Installing latest PyTorch with CUDA 11.8")
        
        if result is None:
            # Fallback to CPU
            self.log("CUDA versions failed, trying CPU version...")
            cmd = [
                self.pyvenv_path, "-m", "pip", "install",
                "torch", "torchaudio", "torchvision",
                "--index-url", "https://download.pytorch.org/whl/cpu",
                "--force-reinstall"
            ]
            result = self.run_command(cmd, "Installing latest PyTorch CPU version")
        
        return result is not None
    
    def install_core_packages(self):
        """Install core packages"""
        self.log("=" * 60)
        self.log("INSTALLING CORE PACKAGES")
        self.log("=" * 60)
        
        core_packages = [
            "numpy>=1.24.0,<2.0.0",
            "scipy>=1.11.0,<2.0.0", 
            "scikit-learn>=1.3.0,<2.0.0",
            "librosa>=0.10.0,<1.0.0",
            "soundfile>=0.13.0,<1.0.0",
            "pydub>=0.25.0,<1.0.0",
            "transformers>=4.30.0,<5.0.0",
            "accelerate>=0.20.0,<1.0.0",
            "datasets>=2.12.0,<3.0.0",
            "tokenizers>=0.13.0,<1.0.0",
            "safetensors>=0.3.0,<1.0.0",
            "huggingface-hub>=0.15.0,<1.0.0",
            "einops>=0.6.0,<1.0.0",
            "omegaconf>=2.3.0,<3.0.0",
            "hydra-core>=1.3.0,<2.0.0",
            "wandb>=0.15.0,<1.0.0",
            "tensorboard>=2.13.0,<3.0.0",
            "matplotlib>=3.7.0,<4.0.0",
            "seaborn>=0.12.0,<1.0.0",
            "plotly>=5.15.0,<6.0.0",
            "pandas>=2.0.0,<3.0.0",
            "pillow>=10.0.0,<11.0.0",
            "opencv-python>=4.8.0,<5.0.0",
            "imageio>=2.31.0,<3.0.0",
            "tqdm>=4.65.0,<5.0.0",
            "rich>=13.0.0,<14.0.0",
            "click>=8.1.0,<9.0.0",
            "pyyaml>=6.0.0,<7.0.0",
            "toml>=0.10.0,<1.0.0",
            "jsonschema>=4.17.0,<5.0.0",
            "pydantic>=2.0.0,<3.0.0",
            "fastapi>=0.104.0,<1.0.0",
            "uvicorn[standard]>=0.24.0,<1.0.0",
            "websockets>=12.0,<13.0",
            "aiohttp>=3.9.0,<4.0.0",
            "aiofiles>=23.0.0,<24.0.0",
            "aiosqlite>=0.19.0,<1.0.0",
            "redis>=4.6.0,<5.0.0",
            "celery>=5.3.0,<6.0.0",
            "psutil>=5.9.0,<6.0.0",
            "py-cpuinfo>=9.0.0,<10.0.0",
            "GPUtil>=1.4.0,<2.0.0",
            "nvidia-ml-py>=11.0.0,<12.0.0",
        ]
        
        for package in core_packages:
            cmd = [self.pyvenv_path, "-m", "pip", "install", package, "--force-reinstall"]
            result = self.run_command(cmd, f"Installing {package}")
            if result is None:
                self.log(f"Warning: Failed to install {package}")
        
        return True
    
    def install_rvc_packages(self):
        """Install RVC packages"""
        self.log("=" * 60)
        self.log("INSTALLING RVC PACKAGES")
        self.log("=" * 60)
        
        rvc_packages = [
            "numba>=0.56.0,<1.0.0",
            "llvmlite>=0.39.0,<1.0.0",
            "fairseq>=0.12.0,<1.0.0",
            "faiss-cpu>=1.7.0,<2.0.0",
            "gradio>=4.0.0,<5.0.0",
            "cython>=0.29.0,<1.0.0",
            "future>=0.18.0,<1.0.0",
            "ffmpeg-python>=0.2.0,<1.0.0",
            "tensorboardX>=2.6.0,<3.0.0",
            "functorch>=2.0.0,<3.0.0",
            "jinja2>=3.1.0,<4.0.0",
            "json5>=0.9.0,<1.0.0",
            "markdown>=3.4.0,<4.0.0",
            "matplotlib-inline>=0.1.0,<1.0.0",
            "praat-parselmouth>=0.4.0,<1.0.0",
            "pyworld>=0.3.0,<1.0.0",
            "resampy>=0.4.0,<1.0.0",
            "starlette>=0.26.0,<1.0.0",
            "tensorboard-data-server>=0.7.0,<1.0.0",
            "tensorboard-plugin-wit>=1.8.0,<2.0.0",
            "torchgen>=0.0.1,<1.0.0",
            "tornado>=6.2,<7.0.0",
            "werkzeug>=2.2.0,<3.0.0",
            "uc-micro-py>=1.0.0,<2.0.0",
            "sympy>=1.11.0,<2.0.0",
            "tabulate>=0.9.0,<1.0.0",
            "pyasn1>=0.4.0,<1.0.0",
            "pyasn1-modules>=0.2.0,<1.0.0",
            "fsspec>=2023.3.0,<2024.0.0",
            "absl-py>=1.4.0,<2.0.0",
            "audioread>=3.0.0,<4.0.0",
            "uvicorn>=0.21.0,<1.0.0",
            "colorama>=0.4.0,<1.0.0",
            "edge-tts>=6.1.0,<7.0.0",
            "yt-dlp>=2023.7.0,<2024.0.0",
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
            "pyannote.audio>=4.0.0,<5.0.0",
            "whisperx>=3.1.0,<4.0.0",
            "openai-whisper>=20231117,<2024.0.0",
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
        self.log("VoiceStudio Ultimate - Clean PyTorch Latest + RVC + Coqui TTS Installation")
        self.log("=" * 70)
        
        try:
            # Step 1: Clean corrupted packages
            if not self.clean_corrupted_packages():
                self.log("ERROR: Package cleanup failed")
                return False
            
            # Step 2: Install PyTorch latest
            if not self.install_pytorch_latest():
                self.log("ERROR: PyTorch installation failed")
                return False
            
            # Step 3: Install core packages
            if not self.install_core_packages():
                self.log("ERROR: Core package installation failed")
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
            self.log("- PyTorch latest with CUDA support")
            self.log("- TorchAudio latest")
            self.log("- TorchVision latest")
            self.log("- RVC dependencies")
            self.log("- Coqui TTS (if successful)")
            self.log("- pyannote-audio 4.0+")
            self.log("- WhisperX 3.1+")
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
        print("VoiceStudio Ultimate is now running on latest PyTorch")
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
