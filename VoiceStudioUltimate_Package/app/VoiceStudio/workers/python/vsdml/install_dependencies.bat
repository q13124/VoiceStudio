@echo off
echo 🎯 VSDML Voice Cloning System - Windows Dependency Installer
echo ============================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo 🐍 Python found, proceeding with installation...

REM Upgrade pip first
echo 🔄 Upgrading pip...
python -m pip install --upgrade pip

REM Install core dependencies
echo 🚀 Installing core dependencies...
python -m pip install "torch>=2.0.0,<3.0.0"
python -m pip install "torchaudio>=2.0.0,<3.0.0"
python -m pip install "numpy>=1.20.0,<2.0.0"
python -m pip install "pandas>=1.3.0,<3.0.0"
python -m pip install "scipy>=1.7.0,<2.0.0"
python -m pip install "scikit-learn>=1.0.0,<2.0.0"
python -m pip install "huggingface-hub>=0.15.0,<1.0.0"

REM Install audio processing dependencies
echo 🎵 Installing audio processing dependencies...
python -m pip install "soundfile>=0.13.0,<1.0.0"
python -m pip install "pydub>=0.25.0,<1.0.0"
python -m pip install "librosa>=0.10.0,<1.0.0"
python -m pip install "webrtcvad>=2.0.10,<3.0.0"
python -m pip install "pyannote-audio>=4.0.0,<5.0.0"
python -m pip install "whisperx>=3.0.0,<4.0.0"

REM Install async dependencies
echo ⚡ Installing async dependencies...
python -m pip install "aiofiles>=23.0.0,<24.0.0"
python -m pip install "aiohttp>=3.8.0,<4.0.0"

REM Install optimization dependencies
echo 🔧 Installing optimization dependencies...
python -m pip install "cachetools>=5.0.0,<6.0.0"
python -m pip install "joblib>=1.2.0,<2.0.0"
python -m pip install "psutil>=5.9.0,<6.0.0"
python -m pip install "redis>=4.0.0,<5.0.0"
python -m pip install "cryptography>=3.4.8,<42.0.0"

REM Optional: Install testing dependencies
echo 🧪 Installing testing dependencies (optional)...
python -m pip install "pytest>=7.0.0,<8.0.0"
python -m pip install "pytest-asyncio>=0.21.0,<1.0.0"
python -m pip install "pytest-cov>=4.0.0,<5.0.0"
python -m pip install "black>=22.0.0,<24.0.0"
python -m pip install "flake8>=5.0.0,<7.0.0"
python -m pip install "mypy>=1.0.0,<2.0.0"

REM Optional: Install documentation dependencies
echo 📚 Installing documentation dependencies (optional)...
python -m pip install "docutils>=0.20.0,<1.0.0"
python -m pip install "sphinx>=8.0.0,<9.0.0"
python -m pip install "jinja2>=3.0.0,<4.0.0"

echo.
echo 🎉 Installation complete!
echo.
echo To verify installation, run:
echo python install_dependencies.py
echo.
pause
