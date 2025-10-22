@echo off
echo VoiceStudio Ultimate Voice Cloning System
echo ==========================================

REM Set optimal environment variables
set PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
set CUDA_VISIBLE_DEVICES=0
set TORCH_CUDNN_V8_API_ENABLED=1

REM Add FFmpeg to PATH
set PATH=C:\Program Files\ffmpeg\bin;%PATH%
set PATH=C:\Program Files (x86)\ffmpeg\bin;%PATH%
set PATH=C:\ffmpeg\bin;%PATH%

REM Start VoiceStudio services
echo Starting VoiceStudio services...
cd /d "C:\Users\Tyler\VoiceStudio"
python start-voice-studio-ultimate.py

pause
